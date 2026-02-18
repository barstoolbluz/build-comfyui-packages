# Patched nixpkgs with platform-specific fixes
# ==============================================
# This module provides a nixpkgs instance with fixes applied for platform-specific
# build issues. Use this instead of direct function arguments when you need
# these fixes (e.g., pyarrow test failures on darwin).
#
# Usage in .flox/pkgs/*.nix:
#   let
#     patchedPkgs = import ../lib/pkgs.nix { inherit system; };
#   in
#   patchedPkgs.callPackage ./my-package.nix {}
#
# Or for direct use:
#   let
#     patchedPkgs = import ../lib/pkgs.nix { inherit system; };
#     inherit (patchedPkgs) lib python3 stdenv;
#   in
#   ...

{ system ? builtins.currentSystem }:

let
  # Fetch nixpkgs - this should match what flox uses
  nixpkgs = fetchTarball {
    url = "https://github.com/NixOS/nixpkgs/archive/nixos-unstable.tar.gz";
    # Note: hash omitted for flexibility; add for reproducibility if needed
  };

  # Overlay to fix pyarrow tests on darwin
  # test_timezone_absent fails because macOS handles timezone lookups differently
  pyarrowDarwinFix = final: prev:
    if prev.stdenv.hostPlatform.isDarwin then {
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

in
import nixpkgs {
  inherit system;
  overlays = [ pyarrowDarwinFix ];
  config = {
    allowUnfree = true;
  };
}
