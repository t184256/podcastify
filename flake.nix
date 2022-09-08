{
  description = "podcast generator based on yt-dlp";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  #inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          podcastify = pkgs.python3Packages.buildPythonPackage {
            pname = "podcastify";
            version = "0.0.1";
            src = ./.;
            propagatedBuildInputs = with pkgs.python3Packages; [
              flask yt-dlp feedgen ruamel-yaml
            ];
            doCheck = false;
          };
        in
        {
          packages.podcastify = podcastify;
          defaultPackage = podcastify;
          apps.podcastify = flake-utils.lib.mkApp { drv = podcastify; };
          defaultApp = podcastify;
          devShell = import ./shell.nix { inherit pkgs; };
        }
      );
}
