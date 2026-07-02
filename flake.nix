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

                # System-level tools
                core_deps = builtins.attrValues {
                    inherit (pkgs)
                        pkg-config
                        gettext
                        pandoc
                        which
                        pre-commit
                        git
                        uv;         
                };
                
                pythonBase = pkgs.python313;

                # Runtime dependencies for the OCI Image (equivalent to devShell layers)
                oci_deps = [
                    pythonBase
                    pkgs.uv
                    pkgs.cacert # Essential for HTTPS requests within python/uv
                    pkgs.bashInteractive
                    pkgs.coreutils
                ];

                # A robust entrypoint script that dynamically injects the .env file from env/ at runtime
                entrypointScript = pkgs.writeScriptBin "entrypoint.sh" ''
                    #!${pkgs.bashInteractive}/bin/bash
                    set -e

                    ENV_FILE="env/.env"

                    if [ -f "$ENV_FILE" ]; then
                        echo "====> Loading runtime environment from $ENV_FILE <===="
                        # Export variables while ignoring comments and empty lines
                        export $(grep -v '^#' "$ENV_FILE" | xargs)
                    else
                        echo "====> Warning: Runtime configuration file '$ENV_FILE' not found. <===="
                    fi

                    # Execute the passed CMD/arguments container-side
                    exec "$@"
                '';

            in {
                
                devShells.default = pkgs.mkShell {
                    buildInputs = core_deps ++ [ pythonBase ];

                    shellHook = ''
                        echo "====> metaSolid dev Shell <===="
                    
                        export UV_PYTHON="${pythonBase}/bin/python3"
                        export VIRTUAL_ENV=".venv"

                        if [ ! -d ".venv" ]; then
                            echo "====> Creating uv venv <===="
                            uv venv .venv --python "${pythonBase}/bin/python3"
                        fi

                        source .venv/bin/activate

                        if [ -f "pyproject.toml" ]; then
                            echo "====> Syncing deps from pyproject.toml <===="
                            uv sync
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
                
                packages.metaSolid = pkgs.dockerTools.buildLayeredImage {
                    name = "metasolid";
                    tag  = "v0.0.1";

                    contents = oci_deps ++ [ entrypointScript ];

                    config = {
                        Entrypoint = [ "${entrypointScript}/bin/entrypoint.sh" ];
                        Cmd = [ "${pkgs.bashInteractive}/bin/bash" ];
                        WorkingDir = "/app";
                    };
                };
            }
        );
}