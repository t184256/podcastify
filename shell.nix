{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    yt-dlp-light
    (python3.withPackages (ps: with ps; [
      flask
      feedgen
      cachetools
      ruamel-yaml
      requests
    ]))
  ];
  nativeBuildInputs = with pkgs.python3Packages; [
    coverage
    flake8
    flake8-import-order
    codespell
  ];
}
