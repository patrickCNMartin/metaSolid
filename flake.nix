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

                # Ollama runtime for dev phase
                llm_deps = builtins.attrValues {
                    inherit (pkgs) ollama;
                };
                # python only - not sure if i want to add packages here or not
                pythonBase = pkgs.python313;

            in {
                
                devShells.default = pkgs.mkShell {
                    buildInputs = core_deps ++ llm_deps ++ [ pythonBase ];

                    shellHook = ''
                        echo "====> metaSolid dev Shell <===="

                        # Point uv at the nix python so it doesn't download its own
                        export UV_PYTHON="${pythonBase}/bin/python3"
                        export VIRTUAL_ENV=".venv"

                        # Create venv if it doesn't exist
                        if [ ! -d ".venv" ]; then
                            echo "Creating uv venv..."
                            uv venv .venv --python "${pythonBase}/bin/python3"
                        fi

                        # Activate venv
                        source .venv/bin/activate

                        # Sync deps from pyproject.toml if it exists
                        if [ -f "pyproject.toml" ]; then
                            echo "Syncing deps from pyproject.toml..."
                            uv sync
                        fi

                        # Register Jupyter kernel from venv
                        KERNEL_STAMP=".nix-kernel-stamp"
                        VENV_HASH=$(echo "$VIRTUAL_ENV" | md5sum | cut -d' ' -f1)

                        if [ ! -f "$KERNEL_STAMP" ] || [ "$(cat $KERNEL_STAMP)" != "$VENV_HASH" ]; then
                            echo "Registering Jupyter kernel..."
                            uv run python -m ipykernel install --user \
                                --name metasolid-nix \
                                --display-name "metaSolid Nix (3.13)"
                            echo "$VENV_HASH" > "$KERNEL_STAMP"
                        fi
                        
                        if ! pgrep -x "ollama" > /dev/null; then
                            echo "Starting ollama serve..."
                            ollama serve &> /tmp/ollama.log &
                            disown
                        fi
                        echo "Remeber to pull the embeds: ollama pull nomic-embed-text"
                        echo "METASOLID shell ready!"
                    '';
                };

                # ── Thin OCI Image ───────────────────────────────────────────
                # Contains: Python 3.13 + uv + your pyproject.toml deps
                # Provides base image to run metaSolid
                packages.ociThin = pkgs.dockerTools.buildLayeredImage {
                    name = "metasolid";
                    tag  = "thin";

                    contents = [
                        pythonBase
                        pkgs.uv
                        pkgs.cacert          # needed for HTTPS in uv/pip
                        pkgs.bash
                        pkgs.coreutils
                    ];

                    config = {
                        # OLLAMA_HOST lets users point at a remote/local Ollama instance
                        Env = [
                            "LLM_BACKEND=ollama"          # ollama | anthropic | openai
                            "LLM_HOST=http://host.docker.internal:11434"  # ignored if not ollama
                            "LLM_MODEL=llama3.2"
                            "EMBED_MODEL=nomic-embed-text"
                            "ANTHROPIC_API_KEY="          # empty, user provides
                            "OPENAI_API_KEY="             # empty, user provides
                        ];

                        # Entrypoint TBD — drops to bash for now
                        # Replace with: Cmd = [ "python" "-m" "metasolid" ];
                        Cmd = [ "${pkgs.bash}/bin/bash" ];

                        WorkingDir = "/app";
                    };
                };

            }
        );
}
