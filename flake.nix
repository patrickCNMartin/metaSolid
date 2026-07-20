{
    description = "Meta Data Consolidation - IDS - METASOLID";
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = {self, nixpkgs, flake-utils}:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs {
                    inherit system;
                    config.allowUnfree = true;
                };

                # System-level tools.
                #
                # THIS LIST IS FOR NON-PYTHON SYSTEM DEPENDENCIES ONLY.
                # Every Python package and every Python-based tool (pytest,
                # ruff, pre-commit, jupyter) belongs in pyproject.toml, which is
                # the single declaration shared by the uv / nix / pixi paths.
                # Adding a Python application here re-creates the PYTHONPATH
                # shadowing bug fixed on 2026-07-20: Nix propagates its closure
                # into the shell, where it overrides the venv.
                #
                # The project currently has no system dependencies, so this is
                # deliberately just the toolchain needed to bootstrap.
                core_deps = builtins.attrValues {
                    inherit (pkgs)
                        git
                        uv;
                };
                
                pythonBase = pkgs.python313;

                # ── OCI image targets ────────────────────────────────────────
                # An OCI image always contains *Linux* binaries: Docker Desktop
                # on macOS runs a Linux VM, so there is no runnable "macOS
                # image". The axis that actually varies is therefore the CPU
                # architecture, not the OS.
                #
                # Default: match the host's architecture, so building on an
                # Apple Silicon Mac yields an arm64 image and building on an
                # x86 Linux box yields an amd64 one. Override by selecting an
                # explicit attribute (see `packages` below).
                hostToImageSystem = {
                    "x86_64-linux"   = "x86_64-linux";
                    "aarch64-linux"  = "aarch64-linux";
                    "x86_64-darwin"  = "x86_64-linux";
                    "aarch64-darwin" = "aarch64-linux";
                };
                defaultImageSystem =
                    hostToImageSystem.${system} or "x86_64-linux";

                mkImage = targetSystem:
                    let
                        targetPkgs = import nixpkgs {
                            system = targetSystem;
                            config.allowUnfree = true;
                        };

                        # Runtime deps for the OCI image (devShell layer equivalent)
                        oci_deps = [
                            targetPkgs.python313
                            targetPkgs.uv
                            targetPkgs.cacert # HTTPS for python/uv
                            targetPkgs.bashInteractive
                            targetPkgs.coreutils
                        ];

                        # Entrypoint that injects env/.env at runtime.
                        entrypointScript =
                            targetPkgs.writeScriptBin "entrypoint.sh" ''
                                #!${targetPkgs.bashInteractive}/bin/bash
                                set -e

                                ENV_FILE="env/.env"

                                if [ -f "$ENV_FILE" ]; then
                                    echo "====> Loading runtime environment from $ENV_FILE <===="
                                    # `set -a` exports everything the file defines.
                                    # The previous `export $(grep -v '^#' ... | xargs)`
                                    # word-split on spaces, so values such as
                                    # REQUEST_TYPE = ["new", "assigned"] parsed wrong.
                                    set -a
                                    . "$ENV_FILE"
                                    set +a
                                else
                                    echo "====> Warning: Runtime configuration file '$ENV_FILE' not found. <===="
                                fi

                                # Execute the passed CMD/arguments container-side
                                exec "$@"
                            '';
                    in
                    targetPkgs.dockerTools.buildLayeredImage {
                        name = "metasolid";
                        tag  = "v0.0.1";

                        contents = oci_deps ++ [ entrypointScript ];

                        config = {
                            Entrypoint = [ "${entrypointScript}/bin/entrypoint.sh" ];
                            Cmd = [ "${targetPkgs.bashInteractive}/bin/bash" ];
                            WorkingDir = "/app";
                        };
                    };

            in {
                
                devShells.default = pkgs.mkShell {
                    buildInputs = core_deps ++ [ pythonBase ];

                    shellHook = ''
                        echo "====> metaSolid dev Shell <===="

                        # Nix propagates the closure of every Python application in
                        # buildInputs (pre-commit) onto PYTHONPATH, which shadows the
                        # venv -- notably nixpkgs' pytest over the one uv installs.
                        # The Nix layer owns the interpreter; pyproject/uv.lock own the
                        # packages. Keep that boundary by starting from a clean path.
                        unset PYTHONPATH

                        export UV_PYTHON="${pythonBase}/bin/python3"
                        export VIRTUAL_ENV=".venv"

                        if [ ! -d ".venv" ]; then
                            echo "====> Creating uv venv <===="
                            uv venv .venv --python "${pythonBase}/bin/python3"
                        fi

                        source .venv/bin/activate

                        if [ -f "pyproject.toml" ]; then
                            echo "====> Syncing deps from pyproject.toml <===="
                            # --extra dev: a bare `uv sync` prunes anything not in the
                            # default dependency set, which uninstalled pytest/ruff/
                            # ipykernel on every shell entry.
                            uv sync --extra dev
                        fi

                        KERNEL_STAMP=".nix-kernel-stamp"
                        VENV_HASH=$(echo "$VIRTUAL_ENV" | md5sum | cut -d' ' -f1)

                        if [ ! -f "$KERNEL_STAMP" ] || [ "$(cat $KERNEL_STAMP)" != "$VENV_HASH" ]; then
                            echo "====> Registering Jupyter kernel <===="
                            uv run python -m ipykernel install --user \
                                --name metasolid-nix \
                                --display-name "metaSolid Nix (3.13)"
                            echo "$VENV_HASH" > "$KERNEL_STAMP"
                        fi

                        if [ ! -d "ollama-models" ]; then
                            mkdir -p ollama-models/logs
                        fi

                        if ! command -v ollama &> /dev/null; then
                            echo "ollama not found — install via: brew install ollama on Mac"
                            echo "Then run: ollama serve & disown"
                        fi

                        if ! pgrep -x "ollama" > /dev/null; then
                            echo "====> Start Ollama <===="
                            ollama serve >> ollama-models/logs/ollama.log 2>&1 & disown
                        fi

                        ollama pull nomic-embed-text
                        ollama pull qwen2.5:7b
                        ollama pull gemma4:12b 

                        if [ ! -f ollama-models/qwen2.5_7B.modelfile ]; then
                                echo "====> Initializing Qwen Modelfile <===="
                                cat > ollama-models/qwen2.5_7B.modelfile << 'EOF'
FROM qwen2.5:7b
PARAMETER num_ctx 8000
PARAMETER temperature 0.7
PARAMETER repeat_penalty 1.1
EOF
                                ollama create qwen:v0.0.1 -f ollama-models/qwen2.5_7B.modelfile
                        fi

                        if [ ! -f ollama-models/gemma4_12B.modelfile ]; then
                                echo "====> Initializing Gemma Modelfile <===="
                                cat > ollama-models/gemma4_12B.modelfile << 'EOF'
FROM gemma4:12b
PARAMETER num_ctx 8000
PARAMETER temperature 0.7
PARAMETER repeat_penalty 1.1
EOF
                                ollama create gemma:v0.0.1 -f ollama-models/gemma4_12B.modelfile
                        fi
                        
                        trap 'pkill -x ollama' EXIT INT TERM
                        
                        echo -e "====> Available Models through Ollama: <====\n"
                        ollama ls
                        echo "====> METASOLID shell ready! <===="
                    '';
                };

                # ── Robust OCI Image ─────────────────────────────────────────
                #
                #   nix build .#metaSolid          -> host architecture (default)
                #   nix build .#metaSolid-amd64    -> force x86_64 image
                #   nix build .#metaSolid-arm64    -> force aarch64 image
                #
                # NOTE (macOS): the explicit targets, and the default target on
                # a Mac, build *Linux* binaries. Nix cannot produce those on a
                # Darwin host by itself -- it needs a Linux builder. Either
                # enable nix-darwin's `nix.linux-builder`, or configure a remote
                # builder. Without one, `nix build .#metaSolid` on a Mac fails
                # with "a 'aarch64-linux' with features {} is required to build".
                packages = {
                    metaSolid       = mkImage defaultImageSystem;
                    metaSolid-amd64 = mkImage "x86_64-linux";
                    metaSolid-arm64 = mkImage "aarch64-linux";
                    default         = mkImage defaultImageSystem;
                };
            }
        );
}