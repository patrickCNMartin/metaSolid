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
                    config = {
                        allowUnfree = true;
                    };
                };
                
                core_deps = builtins.attrValues {
                    inherit (pkgs)
                        gcc
                        gfortran
                        cmake
                        pkg-config
                        gettext
                        pandoc
                        which
                        pre-commit
                        git;
                };
               
                pythonDeps = pkgs.python313.withPackages (packages: with packages; [
                            requests
                            pandas
                            polars
                            numpy
                            seaborn
                            matplotlib
                            jupyterlab
                            ipython
                            ipykernel
                            jsons
                            django
                            detect-secrets
                            ruff
                            python-dotenv
                            python-dateutil
                            python-pptx
                            scipy
                        ]);
               in {
                    devShells.default = pkgs.mkShell {
                        buildInputs = core_deps ++ [pythonDeps];
                        shellHook = ''
                            echo "====> metaSolid dev Shell <===="
                            echo "Activating python environment"

                            KERNEL_STAMP=".nix-kernel-stamp"
                            NIX_PYTHON="${pythonDeps}"

                            if [ ! -f "$KERNEL_STAMP" ] || [ "$(cat $KERNEL_STAMP)" != "$NIX_PYTHON" ]; then
                                echo "Registering Jupyter kernel..."
                                ${pythonDeps}/bin/python -m ipykernel install --user --name ilab-nix --display-name "iLAB Nix (3.13)"
                                echo "$NIX_PYTHON" > "$KERNEL_STAMP"
                            fi

                            echo "METASOLID shell ready!"
                        '';
                    };
               }
                
        );
}