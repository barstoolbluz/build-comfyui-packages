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
        # We override the python interpreters so their .pkgs attribute has the fix
        pyarrowFix = pfinal: pprev: {
          pyarrow = pprev.pyarrow.overridePythonAttrs (old: {
            doCheck = false;
          });
        };

        pyarrowDarwinFix = final: prev:
          if prev.stdenv.hostPlatform.isDarwin then {
            # Override python interpreters so python.pkgs has the fix
            python3 = prev.python3.override {
              packageOverrides = pyarrowFix;
            };
            python313 = prev.python313.override {
              packageOverrides = pyarrowFix;
            };
            python312 = prev.python312.override {
              packageOverrides = pyarrowFix;
            };
            python311 = prev.python311.override {
              packageOverrides = pyarrowFix;
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
