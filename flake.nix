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
                # This is remove for now because of how nix handles the new xcode requirement with 
                # metalToolChain
                # Currently being fixed - but not working yet
                # llm_deps = builtins.attrValues {
                #     inherit (pkgs) ollama;
                # };
                
                # python only - not sure if i want to add packages here or not
                pythonBase = pkgs.python313;

            in {
                
                devShells.default = pkgs.mkShell {
                    # darwin_frameworks will evaluate to [] on Linux, keeping it perfectly pure and agnostic
                    buildInputs = core_deps  ++ [ pythonBase ];

                    shellHook = ''
                        echo "====> metaSolid dev Shell <===="
                    
                        # Point uv at the nix python so it doesn't download its own
                        export UV_PYTHON="${pythonBase}/bin/python3"
                        export VIRTUAL_ENV=".venv"

                        # Create venv if it doesn't exist
                        if [ ! -d ".venv" ]; then
                            echo "====> Creating uv venv <===="
                            uv venv .venv --python "${pythonBase}/bin/python3"
                        fi

                        # Activate venv
                        source .venv/bin/activate

                        # Sync deps from pyproject.toml if it exists
                        if [ -f "pyproject.toml" ]; then
                            echo "====> Syncing deps from pyproject.toml <===="
                            uv sync
                        fi

                        # Register Jupyter kernel from venv
                        KERNEL_STAMP=".nix-kernel-stamp"
                        VENV_HASH=$(echo "$VIRTUAL_ENV" | md5sum | cut -d' ' -f1)

                        if [ ! -f "$KERNEL_STAMP" ] || [ "$(cat $KERNEL_STAMP)" != "$VENV_HASH" ]; then
                            echo "====> Registering Jupyter kernel <===="
                            uv run python -m ipykernel install --user \
                                --name metasolid-nix \
                                --display-name "metaSolid Nix (3.13)"
                            echo "$VENV_HASH" > "$KERNEL_STAMP"
                        fi
                        
                        # Ollama set up
                        # Only for dev
                        if [ ! -d "ollama-models" ]; then
                            mkdir -p ollama-models/logs
                        fi

                        if ! command -v ollama &> /dev/null; then
                            echo "ollama not found — install via: brew install ollama on Mac"
                            echo "Then run: ollama serve & disown"
                            # Nix does not support this new metalToolChain require by the latest version of Ollama
                            # To make a pure nix build use nixos-25.11 which calls Ollama 0.21.1
                            # Don't forget to un-comment the llm-deps above and add them to the mkShell
                        fi
                        # Start up Ollama if not already running
                        # This should not be the case but just in case
                        if ! pgrep -x "ollama" > /dev/null; then
                            echo "====> Start Ollama <===="
                            ollama serve >> ollama-models/logs/ollama.log 2>&1 & disown
                        fi
                        # Pull models - if already there they won't downloaded again 
                        # Ollama handles that check. 
                        ollama pull nomic-embed-text
                        ollama pull qwen2.5:7b
                        ollama pull gemma4:12b 

                        # Initialize Model File if they are not present
                        # Can be customized later but he autobuild the "defaults"

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
                        
                        # Trap ollama to kill on nix session exit
                        trap 'pkill -x ollama' EXIT INT TERM
                        
                        echo -e "====> Available Models through Ollama: <====\n"
                        ollama ls
                        echo "====> METASOLID shell ready! <===="
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