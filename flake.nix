{
    description = "iLAB API integration testing environment";
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
                            jsons
                            django
                            detect-secrets
                            ruff
                            python-dotenv
                        ]);
               in {
                    devShells.default = pkgs.mkShell {
                        buildInputs = core_deps ++ [pythonDeps];
                        shellHook = ''
                            echo iLAB dev Shell
                        '';
                    };
               }
                
        );
}