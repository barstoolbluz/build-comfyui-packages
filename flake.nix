{
  description = "ComfyUI packages build environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        # Overlay to fix pyarrow tests on darwin
        # test_timezone_absent fails because macOS handles timezone lookups differently
        pyarrowDarwinFix = final: prev:
          if prev.stdenv.hostPlatform.isDarwin then {
            # Override python3Packages (used by default python3)
            python3Packages = prev.python3Packages.override {
              overrides = pfinal: pprev: {
                pyarrow = pprev.pyarrow.overridePythonAttrs (old: {
                  doCheck = false;
                });
              };
            };
            python313Packages = prev.python313Packages.override {
              overrides = pfinal: pprev: {
                pyarrow = pprev.pyarrow.overridePythonAttrs (old: {
                  doCheck = false;
                });
              };
            };
            python312Packages = prev.python312Packages.override {
              overrides = pfinal: pprev: {
                pyarrow = pprev.pyarrow.overridePythonAttrs (old: {
                  doCheck = false;
                });
              };
            };
            python311Packages = prev.python311Packages.override {
              overrides = pfinal: pprev: {
                pyarrow = pprev.pyarrow.overridePythonAttrs (old: {
                  doCheck = false;
                });
              };
            };
          } else {};

        pkgs = import nixpkgs {
          inherit system;
          overlays = [ pyarrowDarwinFix ];
          config = {
            allowUnfree = true;
          };
        };

      in {
        # Re-export pkgs with the overlay applied
        legacyPackages = pkgs;

        # Build packages using pkgs with pyarrow darwin fix overlay applied
        packages = {
          comfyui-extras = pkgs.callPackage ./.flox/pkgs/comfyui-extras.nix {};
          comfyui-ultralytics = pkgs.callPackage ./.flox/pkgs/comfyui-ultralytics.nix {};
          comfyui-workflows = pkgs.callPackage ./.flox/pkgs/comfyui-workflows.nix {};
        };
      }
    );
}
