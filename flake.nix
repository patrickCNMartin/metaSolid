{
    description = "metaSolid - metadata field harmonization";
    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
        flake-utils.url = "github:numtide/flake-utils";
    };

    outputs = { self, nixpkgs, flake-utils }:
        flake-utils.lib.eachDefaultSystem (system:
            let
                pkgs = import nixpkgs { inherit system; };
                python = pkgs.python313;
                version = (builtins.fromTOML (builtins.readFile ./pyproject.toml)).project.version;
                oci = import ./oci.nix { inherit nixpkgs system version; src = ./metasolid; };
            in {
                # System tools only. Every Python package is in pyproject.toml, synced by uv.
                # Ollama is not here: install it on the host.
                devShells.default = pkgs.mkShell {
                    packages = [ python pkgs.uv pkgs.git pkgs.pandoc pkgs.typst ];
                    shellHook = ''
                        # Nix puts Python closures on PYTHONPATH, which shadows the venv.
                        unset PYTHONPATH
                        export UV_PYTHON="${python}/bin/python3"
                        ${pkgs.lib.optionalString pkgs.stdenv.hostPlatform.isLinux ''
                            # uv's numpy and scipy wheels link libstdc++, which a nix Python cannot find.
                            export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath [ pkgs.stdenv.cc.cc.lib pkgs.zlib ]}"
                        ''}
                        [ -d .venv ] || uv venv .venv --python "$UV_PYTHON"
                        source .venv/bin/activate
                        uv sync --extra dev
                    '';
                };

                #   nix build .#oci && docker load < result
                packages = {
                    inherit oci;
                    default = oci;
                };
            });
}
