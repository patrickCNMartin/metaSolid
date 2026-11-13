# OCI image of metaSolid: always Linux, for the host's CPU (aarch64-darwin -> aarch64-linux).
# Its packages come prebuilt from the Linux cache and only the assembly runs on the host, so a
# Mac needs no Linux builder - as long as nothing here has to be compiled for Linux.
# Python packages come from nixpkgs, not uv.lock: keep `deps` equal to
# [project.dependencies] in pyproject.toml, nothing else will catch a drift.
{ nixpkgs, system, version, src }:
let
    pkgs = import nixpkgs { inherit system; };
    p = import nixpkgs { system = builtins.replaceStrings [ "darwin" ] [ "linux" ] system; };
    py = p.python313;
    deps = with py.pkgs; [
        numpy
        scipy
        matplotlib
        pyyaml
        requests
        python-dotenv
    ];
    app = pkgs.runCommand "metasolid-src" { } ''
        mkdir -p $out/app
        cp -r ${src} $out/app/metasolid
    '';
in
pkgs.dockerTools.buildLayeredImage {
    name = "metasolid";
    tag = version;
    contents = [ p.cacert p.bashInteractive p.coreutils p.pandoc p.typst py app ] ++ deps;
    # matplotlib writes a cache; the store is read-only.
    extraCommands = "mkdir -m 1777 tmp";
    config = {
        Entrypoint = [ "${py}/bin/python" "-m" "metasolid" ];
        WorkingDir = "/app";
        Env = [
            "PYTHONPATH=/app:${py.pkgs.makePythonPath deps}"
            "PYTHONDONTWRITEBYTECODE=1"
            "PYTHONUNBUFFERED=1"
            "MPLCONFIGDIR=/tmp/matplotlib"
            "SSL_CERT_FILE=${p.cacert}/etc/ssl/certs/ca-bundle.crt"
        ];
        Labels = {
            "org.opencontainers.image.title" = "metasolid";
            "org.opencontainers.image.version" = version;
        };
    };
}
