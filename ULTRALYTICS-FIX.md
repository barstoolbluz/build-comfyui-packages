# Fix: ultralytics pyexpat symbol mismatch in comfyui-extras

## Problem

`import ultralytics` fails with:

```
ImportError: /home/daedalus/dev/comfyui4all/.flox/run/x86_64-linux.comfyui4all.dev/lib/python3.13/lib-dynload/pyexpat.cpython-313-x86_64-linux-gnu.so: undefined symbol: XML_SetAllocTrackerActivationThreshold
```

## Root Cause

The `pyexpat` C extension in the Flox runtime environment was linked against a different version of `libexpat` than the one available at runtime. The symbol `XML_SetAllocTrackerActivationThreshold` was added in expat 2.7.0. Either:

- **pyexpat.so was built against expat >= 2.7.0** but the runtime has an older expat, OR
- **pyexpat.so was built against expat < 2.7.0** but the runtime has a newer expat that removed/renamed the symbol

Most likely: the Python 3.13 (`python313Full`) package in the Flox catalog was built against a newer expat than what ends up in the `comfyui-extras` closure at runtime. The layered environment exposes a mismatched `pyexpat.so`.

## Where ultralytics lives

- **Package**: `comfyui-extras` (version 0.11.0)
- **Manifest entry**: `comfyui-extras.pkg-path = "flox/comfyui-extras"`
- **Build repo**: `https://github.com/barstoolbluz/build-comfyui-packages.git`
- **Nix store path**: `/nix/store/2r82996qi5mnaq8xbs67zfwzblvasr1g-python3.13-comfyui-extras-0.11.0`

ultralytics is bundled inside `comfyui-extras` along with timm, open-clip-torch, accelerate, segment-anything, spandrel, peft, rembg, albumentations, and others.

## How to fix

In the `build-comfyui-packages` repo, in the Nix derivation for `comfyui-extras`:

1. **Ensure expat version consistency.** The `comfyui-extras` derivation must use the same `expat` and `python313` as the consuming `comfyui4all` environment. If the derivation pins its own python or expat, align them.

2. **Check for stale expat in the closure.** Run:
   ```bash
   nix-store -qR /nix/store/2r82996qi5mnaq8xbs67zfwzblvasr1g-python3.13-comfyui-extras-0.11.0 | grep expat
   ```
   Compare the expat version in that closure with the one in the runtime environment:
   ```bash
   # Inside flox activate
   ls -la $(dirname $(python3 -c "import pyexpat; print(pyexpat.__file__)"))/
   ldd $(python3 -c "import pyexpat; print(pyexpat.__file__)") | grep expat
   ```

3. **Pin expat explicitly** in the derivation's `buildInputs` or `propagatedBuildInputs` to match the python313Full package's expat, or inherit it from python's own dependencies:
   ```nix
   # Use python's own expat to guarantee ABI match
   expat = python3.pkgs.expat or python3.passthru.expat
   ```

4. **Rebuild and republish** `comfyui-extras`.

## How to verify

```bash
flox activate
python3 -c "import ultralytics; print(ultralytics.__version__)"
```

## Not an architecture issue

This is a library ABI mismatch, not an AVX/FMA instruction set problem. It affects all x86_64-linux systems regardless of CPU capabilities.
