# build-comfyui-packages

Torch-agnostic Python packages for ComfyUI, built with Flox.

## Purpose

This repository builds Python packages required by ComfyUI custom nodes (Impact Pack, WAS Node Suite, Efficiency Nodes, etc.) **without torch/torchvision in their closures**. This allows the runtime environment to provide CUDA-enabled PyTorch, avoiding silent GPU operation failures.

## The Problem

Many Python ML packages depend on PyTorch:
- ultralytics, timm, open-clip-torch, accelerate, segment-anything, clip-interrogator, transparent-background, pixeloe

When installed from standard channels (pip, conda, nixpkgs), these packages pull in CPU-only torch/torchvision as transitive dependencies. Even if you install CUDA PyTorch separately, the CPU versions remain in the dependency closure and can cause:

1. **Silent GPU fallback**: Operations like NMS (Non-Maximum Suppression) run on CPU instead of GPU
2. **Memory issues**: Tensors created on different torch installations can't interoperate
3. **Performance degradation**: What should be milliseconds becomes seconds

## The Solution

This repo rebuilds torch-dependent packages from source using Nix's `pythonRemoveDeps` to strip torch requirements. At runtime, these packages use whatever PyTorch the environment provides (CUDA, MPS, or CPU).

## Repository Structure

```
build-comfyui-packages/
├── .flox/
│   ├── env/
│   │   └── manifest.toml      # Flox build environment config
│   └── pkgs/                  # Nix package definitions
│       ├── comfyui-extras.nix # Meta-package aggregating all deps
│       ├── comfyui-ultralytics.nix
│       ├── comfyui-accelerate.nix
│       ├── ...                # Individual package definitions
│       └── timm.nix
├── sources/                   # Vendored packages (wheels/tarballs/code)
│   ├── color_matcher-0.6.0-py3-none-any.whl
│   ├── cstr-*.tar.gz
│   ├── img2texture-*.tar.gz
│   └── ComfyUI-SafeCLIP-SDXL/  # Vendored custom node (no upstream repo)
└── result-*                   # Build output symlinks (gitignored)
```

## Packages

### Torch-Agnostic ML Packages

These packages normally depend on PyTorch but are rebuilt without it:

| Package | Description | Platforms | Source |
|---------|-------------|-----------|--------|
| `comfyui-ultralytics` | YOLO object detection | Linux | [ultralytics/ultralytics](https://github.com/ultralytics/ultralytics) |
| `comfyui-timm` | PyTorch Image Models | Linux | [huggingface/pytorch-image-models](https://github.com/huggingface/pytorch-image-models) |
| `comfyui-open-clip-torch` | OpenAI CLIP implementation | Linux | [mlfoundations/open_clip](https://github.com/mlfoundations/open_clip) |
| `comfyui-accelerate` | HuggingFace distributed training | Linux | [huggingface/accelerate](https://github.com/huggingface/accelerate) |
| `comfyui-segment-anything` | Meta SAM segmentation | Linux | [facebookresearch/segment-anything](https://github.com/facebookresearch/segment-anything) |
| `comfyui-clip-interrogator` | Image to prompt | Linux | [pharmapsychotic/clip-interrogator](https://github.com/pharmapsychotic/clip-interrogator) |
| `comfyui-transparent-background` | ML-based background removal | x86_64-linux, Darwin | [plemeri/transparent-background](https://github.com/plemeri/transparent-background) |
| `comfyui-pixeloe` | Pixel art conversion | x86_64-linux, Darwin | [KohakuBlueleaf/PixelOE](https://github.com/KohakuBlueleaf/PixelOE) |

**Built separately (not in meta-package):**

| Package | Description | Platforms | Source |
|---------|-------------|-----------|--------|
| `comfyui-spandrel` | Upscaler architectures | Linux | [chaiNNer-org/spandrel](https://github.com/chaiNNer-org/spandrel) |

### Clean Packages

These packages have no torch dependencies but aren't in nixpkgs or need specific versions:

| Package | Description | Source |
|---------|-------------|--------|
| `colour-science` | Color science library | [colour-science/colour](https://github.com/colour-science/colour) |
| `rembg` | Background removal | [danielgatis/rembg](https://github.com/danielgatis/rembg) |
| `ffmpy` | FFmpeg wrapper | [Ch00k/ffmpy](https://github.com/Ch00k/ffmpy) |
| `color-matcher` | Color matching algorithms | Vendored wheel |
| `img2texture` | Seamless texture generation | Vendored tarball |
| `cstr` | Colored terminal strings | Vendored tarball |

### Meta-Packages

This repository provides four meta-packages that aggregate different categories of ComfyUI dependencies:

| Meta-Package | Description | Platforms |
|--------------|-------------|-----------|
| `comfyui-extras` | Torch-agnostic ML packages + clean utilities | x86_64-linux |
| `comfyui-plugins` | Impact Pack (FaceDetailer, detection nodes) | x86_64-linux |
| `comfyui-impact-subpack` | Impact Subpack (YOLO detector, SAM loader) | x86_64-linux |
| `comfyui-custom-nodes` | 14 community custom nodes from GitHub | All platforms |

#### comfyui-extras

Aggregates all torch-agnostic ML packages (except spandrel) plus these from nixpkgs:
- piexif, simpleeval, numba, gitpython, onnxruntime, easydict, pymatting, pillow-heif, rich, albumentations

#### comfyui-plugins

Provides ComfyUI-Impact-Pack, the essential custom node collection with FaceDetailer, object detection, mask operations, and batch processing. Requires `comfyui-extras` for Python dependencies (ultralytics, segment-anything).

#### comfyui-impact-subpack

Provides ComfyUI-Impact-Subpack with UltralyticsDetectorProvider (YOLO detection) and SAMLoader nodes. Requires `comfyui-plugins` (Impact Pack) and `comfyui-extras` for Python dependencies.

#### comfyui-custom-nodes

Bundles 14 essential community custom nodes:
- rgthree-comfy, images-grid-comfy-plugin, ComfyUI-Image-Saver, ComfyUI_UltimateSDUpscale
- ComfyUI-KJNodes, ComfyUI_essentials, ComfyUI-Custom-Scripts, ComfyUI_Comfyroll_CustomNodes
- efficiency-nodes-comfyui, was-node-suite-comfyui, ComfyUI-mxToolkit
- ComfyUI_IPAdapter_plus, ComfyUI-IPAdapter-Flux, ComfyUI-SafeCLIP-SDXL

**Note:** `comfyui-extras` and `comfyui-plugins` are **x86_64-linux only** due to torch-agnostic ML package constraints.

### Platform Support Summary

| Category | x86_64-linux | aarch64-linux | x86_64-darwin | aarch64-darwin |
|----------|:------------:|:-------------:|:-------------:|:--------------:|
| Core ML packages (ultralytics, timm, etc.) | ✓ | ✓ | ✗ | ✗ |
| `comfyui-pixeloe` | ✓ | ✗ | ✓ | ✓ |
| `comfyui-transparent-background` | ✓ | ✗ | ✓ | ✓ |
| Clean packages (colour-science, rembg, etc.) | ✓ | ✓ | ✓ | ✓ |
| `albumentations` (from nixpkgs) | ✓ | ✓ | ✗ | ✗ |
| **`comfyui-extras` meta-package** | ✓ | ✗ | ✗ | ✗ |

Notes:
- Most torch-agnostic ML packages are Linux-only due to build/test constraints
- kornia-rs build issues exclude pixeloe and transparent-background from aarch64-linux
- The meta-package only includes pixeloe and transparent-background on x86_64-linux

## Building Packages

### Prerequisites

- [Flox](https://flox.dev) installed
- x86_64-linux system (for full package set)

### Build Commands

```bash
# Enter the build environment
cd /path/to/build-comfyui-packages
flox activate

# Build a specific package
flox build comfyui-ultralytics

# Build the meta-package (includes all dependencies)
flox build comfyui-extras

# Build outputs appear as result-<package-name> symlinks
ls -la result-*
```

### Verify No Torch Contamination

```bash
# Check that a package has no torch in its closure
nix-store -qR ./result-comfyui-ultralytics | grep -E 'torch|vision'
# Should return empty (no matches)

# Check the meta-package
nix-store -qR ./result-comfyui-extras | grep -E 'torch|vision' | grep -v 'comfyui'
# Should return empty
```

## Using Built Packages

Built packages are consumed by the `comfyui-repo` runtime environment via store-path references in its manifest:

```toml
# In comfyui-repo/.flox/env/manifest.toml

# Reference the built meta-package by its store path
comfyui-extras.store-path = "/nix/store/...-python3.13-comfyui-extras-1.0.0"
comfyui-extras.systems = ["x86_64-linux"]
```

After updating the manifest, activate the environment:

```bash
cd /path/to/comfyui-repo
flox activate

# Verify imports work with CUDA PyTorch
python -c "
import torch
print(f'PyTorch device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')

from ultralytics import YOLO
from segment_anything import sam_model_registry
from clip_interrogator import Config
import colour
print('All imports successful - using runtime CUDA PyTorch')
"
```

## Adding New Packages

### Torch-Dependent Package

1. Create `.flox/pkgs/<package-name>.nix`:

```nix
{ lib, python3, fetchFromGitHub }:

python3.pkgs.buildPythonPackage rec {
  pname = "comfyui-<package>";
  version = "1.0.0";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "<owner>";
    repo = "<repo>";
    tag = "v${version}";
    hash = "";  # Build will fail with correct hash
  };

  build-system = with python3.pkgs; [ setuptools wheel ];

  dependencies = with python3.pkgs; [
    # Include non-torch dependencies
    numpy
    pillow
  ];

  # Remove torch from requirements
  pythonRemoveDeps = [ "torch" "torchvision" ];

  doCheck = false;

  meta = with lib; {
    description = "<Package> for ComfyUI (torch provided by runtime)";
    homepage = "https://github.com/<owner>/<repo>";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
```

2. Build to get the correct hash:
```bash
flox build <package-name>
# Copy hash from error message, update nix file, rebuild
```

3. Add to `comfyui-extras.nix` if it should be included in the meta-package.

### Vendored Package

For packages not available via fetchFromGitHub:

1. Download the wheel/tarball to `sources/`
2. Reference it in the nix file:
```nix
src = ../../sources/<package>-<version>.whl;
format = "wheel";
```

## Branching Strategy

This repository uses a two-track branching model to support both cutting-edge and stable package builds.

### Goals

- **`latest`**: Newer upstream ComfyUI, for users who want early access and can tolerate occasional churn
- **`main`**: Stable track, validated more thoroughly, intentionally behind `latest`

### Branch Definitions

#### Rolling Branches

| Branch | Purpose |
|--------|---------|
| `latest` | Tracks cutting-edge upstream ComfyUI. Validated, but not as deeply as `main`. |
| `latest-testing` | Feeder branch for `latest`. Where new upstream pins are iterated on. |
| `latest-staging` | Final gate before `latest`. Receives release candidates for pre-promotion validation. |
| `main` | Stable track. Inherits from `latest` with deliberate lag. Recommended default. |

**Promotion flow:**
```
latest-testing → latest-staging → latest
```

#### Historical Snapshots

When `main` advances, the prior state is preserved as an **annotated tag** (e.g., `v0.9.3`, `v0.10.0`) for reproducibility and rollback.

### Standard Promotion Cycle

When upstream releases a new ComfyUI version (e.g., 0.10.3):

#### Phase 1: Prepare and Validate

1. **Pin and iterate in `latest-testing`**
   - Update upstream ComfyUI pin
   - Fix build recipes, packaging, integration issues
   - Repeat until candidate is ready

2. **Promote to `latest-staging`**
   - Fast-forward merge from `latest-testing`
   - Run staging validation (install flows, smoke tests)

3. **Fix forward as needed**
   - Issues found in staging → fix in `latest-testing` → re-promote

#### Phase 2: Rotate and Publish

When `latest-staging` is ready, rotate branches in order:

1. **Archive current `main`**
   ```bash
   git checkout main && git pull
   git tag -a v0.9.3 -m "Stable snapshot: v0.9.3"
   git push origin v0.9.3
   ```

2. **Advance `main` to current `latest`**
   ```bash
   git checkout main
   git merge --ff-only origin/latest
   git push origin main
   ```

3. **Advance `latest` to `latest-staging`**
   ```bash
   git checkout latest
   git merge --ff-only origin/latest-staging
   git push origin latest
   ```

**Net effect:**
- `main` → what was `latest`
- `latest` → newly vetted upstream-aligned build
- Former `main` → preserved as `vX.Y.Z` tag

### Git Operations

Use **fast-forward merges** for promotions, not rebases:

| Do | Don't |
|----|-------|
| "fast-forward `main` to match `latest`" | "rebase `main` onto `latest`" |
| "promote by fast-forward merge" | "rebase and force-push" |
| "move the branch pointer" | "rewrite history" |

### Branch Protection

- Protect `main`, `latest`, and `*-staging` from force-pushes
- Prefer fast-forward merges so history reads as linear sequence of vetted candidates
- Encode upstream ComfyUI version in machine-readable location

### Optional: Maintenance Path for `main`

For patches that should land in stable without waiting for a new upstream cycle (security fixes, build recipe corrections):

```
main-testing → main-staging → main
```

## Related Repositories

- **build-comfyui**: ComfyUI source distribution package (provides the core application)
- **comfyui-repo**: Runtime environment that consumes these packages
- **ComfyUI**: The upstream ComfyUI application

## License

Individual packages retain their original licenses. The build infrastructure is MIT licensed.
