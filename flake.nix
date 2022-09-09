{
  description = "podcast generator based on yt-dlp";

  inputs.flake-utils.url = "github:numtide/flake-utils";
  #inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs, flake-utils }:
    (flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        podcastify = pkgs.python3Packages.buildPythonPackage {
          pname = "podcastify";
          version = "0.0.1";
          src = ./.;
          propagatedBuildInputs = with pkgs.python3Packages; [
            flask yt-dlp-light feedgen ruamel-yaml
          ];
          doCheck = false;
        };
        waitressEnv = pkgs.python3.withPackages (p: with p; [
          waitress podcastify
        ]);
        app = flake-utils.lib.mkApp { drv = podcastify; };
      in
      {
        packages.podcastify = podcastify;
        packages.waitressEnv = waitressEnv;
        defaultPackage = podcastify;
        apps.podcastify = app;
        defaultApp = app;
        devShell = import ./shell.nix { inherit pkgs; };
      }
    )) // (
    let
      nixosModule = { config, lib, pkgs, ... }:
        let
          cfg = config.services.podcastify;
          system = pkgs.system;
        in {
          options.services.podcastify = {
            enable = lib.mkOption {
              description = "Enable podcastify service";
              type = lib.types.bool;
              default = false;
            };
            configFile = lib.mkOption {
              description = "Configuration file to use.";
              type = lib.types.str;
            };
            address = lib.mkOption {
              description = "Address to listen to";
              type = lib.types.str;
              default = "127.0.0.1";
            };
            port = lib.mkOption {
              description = "Port to listen to";
              type = lib.types.int;
              default = 8080;
            };
          };
          config = lib.mkIf cfg.enable {
            users = {
              users.podcastify.isSystemUser = true;
              users.podcastify.group = "podcastify";
              groups.podcastify = {};
            };
            systemd.services.podcastify = {
              path = [ pkgs.yt-dlp-light ];  # move to wrapper?
              description = "Podcast generator based on yt-dlp";
              wantedBy = [ "multi-user.target" ];
              after = [ "network.target" ];
              environment.PODCASTIFY_CONFIG = cfg.configFile;
              serviceConfig = {
                ExecStart = lib.escapeShellArgs [
                  "${self.packages.${system}.waitressEnv}/bin/waitress-serve"
                  "--listen" "${cfg.address}:${builtins.toString cfg.port}"
                  "podcastify.main:app"
                ];
                Restart = "on-failure";
                User = "podcastify";
                Group = "podcastify";
              };
            };
          };
        };
      in
      {
        inherit nixosModule;
        nixosModules = { podcastify = nixosModule; default = nixosModule; };
      }
    );
}
