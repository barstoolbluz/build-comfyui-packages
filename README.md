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

## Release-Tracked Packages

This repo produces **five meta-packages** consumed by the Flox runtime environment. Four of them (`comfyui-extras`, `comfyui-plugins`, `comfyui-custom-nodes`, `comfyui-videogen`) are **version-locked to the upstream ComfyUI release**: their `version` field in the nix file must be set to the ComfyUI release version (e.g., `version = "0.11.0"` for ComfyUI v0.11.0), and all four must be bumped in lockstep. The fifth (`comfyui-impact-subpack`) tracks its own upstream version independently. The runtime manifest (`comfyui/.flox/env/manifest.toml`) also pins the version-locked packages and must match.

### Version-Locked (bump together on each ComfyUI release)

| Meta-Package | Build Recipe | Aggregates |
|--------------|-------------|------------|
| `comfyui-extras` | [`comfyui-extras.nix`](.flox/pkgs/comfyui-extras.nix) | All torch-agnostic ML packages ([`comfyui-ultralytics`](.flox/pkgs/comfyui-ultralytics.nix), [`comfyui-timm`](.flox/pkgs/timm.nix), [`comfyui-open-clip-torch`](.flox/pkgs/open-clip-torch.nix), [`comfyui-accelerate`](.flox/pkgs/comfyui-accelerate.nix), [`comfyui-segment-anything`](.flox/pkgs/segment-anything.nix), [`comfyui-clip-interrogator`](.flox/pkgs/comfyui-clip-interrogator.nix), [`comfyui-spandrel`](.flox/pkgs/spandrel.nix), [`comfyui-peft`](.flox/pkgs/comfyui-peft.nix), [`comfyui-facexlib`](.flox/pkgs/comfyui-facexlib.nix), [`comfyui-transparent-background`](.flox/pkgs/comfyui-transparent-background.nix), [`comfyui-pixeloe`](.flox/pkgs/comfyui-pixeloe.nix)) + clean utility packages ([`colour-science`](.flox/pkgs/colour-science.nix), [`rembg`](.flox/pkgs/rembg.nix), [`ffmpy`](.flox/pkgs/ffmpy.nix), [`color-matcher`](.flox/pkgs/color-matcher.nix), [`img2texture`](.flox/pkgs/img2texture.nix), [`cstr`](.flox/pkgs/cstr.nix), [`pyloudnorm`](.flox/pkgs/pyloudnorm.nix), [`onnxruntime-noexecstack`](.flox/pkgs/onnxruntime-noexecstack.nix)) + nixpkgs deps (piexif, simpleeval, numba, gitpython, onnx, easydict, pymatting, pillow-heif, rich, albumentations, imageio-ffmpeg, gguf) |
| `comfyui-plugins` | [`comfyui-plugins.nix`](.flox/pkgs/comfyui-plugins.nix) | ComfyUI-Impact-Pack (FaceDetailer, detection, mask ops, batch processing) |
| `comfyui-custom-nodes` | [`comfyui-custom-nodes.nix`](.flox/pkgs/comfyui-custom-nodes.nix) | 15 community nodes: rgthree-comfy, images-grid, Image-Saver, UltimateSDUpscale, KJNodes, essentials, Custom-Scripts, Comfyroll, efficiency-nodes, was-node-suite, mxToolkit, IPAdapter_plus, IPAdapter-Flux, SafeCLIP-SDXL, LayerForge |
| `comfyui-videogen` | [`comfyui-videogen.nix`](.flox/pkgs/comfyui-videogen.nix) | 4 video nodes: AnimateDiff-Evolved, VideoHelperSuite, LTXVideo, WanVideoWrapper |

### Independently Versioned

| Meta-Package | Build Recipe | Version Scheme | Aggregates |
|--------------|-------------|----------------|------------|
| `comfyui-impact-subpack` | [`comfyui-impact-subpack.nix`](.flox/pkgs/comfyui-impact-subpack.nix) | Upstream + `_flox_build` suffix | Impact Subpack (UltralyticsDetectorProvider, SAMLoader) + bundled Python deps ([`comfyui-sam2`](.flox/pkgs/comfyui-sam2.nix), [`comfyui-thop`](.flox/pkgs/comfyui-thop.nix)) |
| `comfyui-controlnet-aux` | [`comfyui-controlnet-aux.nix`](.flox/pkgs/comfyui-controlnet-aux.nix) | Upstream | ControlNet preprocessors (Canny, Depth, Pose, etc.) |
| `comfyui-workflows` | [`comfyui-workflows.nix`](.flox/pkgs/comfyui-workflows.nix) | Own semver (`1.0.1`) | Example workflows in dual format: Web UI (for browser) + API (for CI) |

## Workflow Formats

The `comfyui-workflows` package provides example workflows in **two formats**:

| Format | Location | Purpose |
|--------|----------|---------|
| **Web UI** | `$out/share/comfyui/workflows/` | For rendering in ComfyUI browser (has node positions, links array) |
| **API** | `$out/share/comfyui/workflows-api/` | For CI/programmatic execution (minimal, just nodes and inputs) |

### Format Details

**API format** (source of truth in `sources/workflows/`):
```json
{
  "1": { "class_type": "CheckpointLoaderSimple", "inputs": { "ckpt_name": "model.safetensors" } },
  "2": { "class_type": "KSampler", "inputs": { "model": ["1", 0], ... } }
}
```

**Web UI format** (generated at build time):
```json
{
  "last_node_id": 7,
  "last_link_id": 6,
  "nodes": [{ "id": 1, "type": "CheckpointLoaderSimple", "pos": [100, 50], ... }],
  "links": [[1, 1, 0, 2, 0, "*"], ...],
  "version": 0.4
}
```

### Converter Script

The build runs `sources/workflows/convert_to_webui.py` to generate Web UI format from API format:

```bash
# Manual conversion (for testing)
python3 sources/workflows/convert_to_webui.py sources/workflows /tmp/webui-output
```

The converter auto-arranges nodes in a grid layout. For complex workflows, you may want to manually export from ComfyUI's UI after loading the API format via the queue endpoint.

### Using Workflows

**In the browser:** Workflows are copied to `~/comfyui-work/user/default/workflows/` on activation. Open ComfyUI and load from the workflow browser.

**For CI/automation:**
```bash
# Execute workflow via API
curl -X POST http://localhost:8188/prompt \
  -H "Content-Type: application/json" \
  -d @"$FLOX_ENV/share/comfyui/workflows-api/SD15/sd15-txt2img.json"
```

## Dependency Strategy

Each package in this repo follows a specific dependency pattern:

### What Gets Bundled

Standard Python packages from nixpkgs are included in each package's `dependencies`:
- numpy, pillow, scipy, opencv, matplotlib, pandas, pyyaml, requests, tqdm, psutil, etc.

These packages have no torch contamination and are safe to bundle.

### What Gets Removed

Packages are stripped via `pythonRemoveDeps` and provided by the runtime environment:

| Removed Dependency | Provided By |
|--------------------|-------------|
| `torch` | Runtime's CUDA/MPS/CPU PyTorch |
| `torchvision` | Runtime's CUDA/MPS/CPU PyTorch |
| `timm` | `comfyui-timm` (in comfyui-extras) |
| `accelerate` | `comfyui-accelerate` (in comfyui-extras) |
| `open_clip_torch` | `comfyui-open-clip-torch` (in comfyui-extras) |
| `kornia` | Runtime environment (nixpkgs or separate install) |
| `transformers` | Runtime environment (nixpkgs or separate install) |

### Dependency Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Runtime Environment                            │
├─────────────────────────────────────────────────────────────────────┤
│  CUDA PyTorch          comfyui-extras           nixpkgs            │
│  ├── torch             ├── comfyui-ultralytics  ├── transformers   │
│  └── torchvision       ├── comfyui-timm         ├── kornia         │
│                        ├── comfyui-accelerate   └── (other deps)   │
│                        ├── comfyui-open-clip-torch                 │
│                        ├── comfyui-segment-anything                │
│                        └── (bundled: numpy, pillow, scipy, etc.)   │
└─────────────────────────────────────────────────────────────────────┘
```

### Example Package Pattern

```nix
dependencies = with python3.pkgs; [
  # Bundled: standard Python packages (no torch contamination)
  numpy
  pillow
  scipy
];

pythonRemoveDeps = [
  # Removed: provided by runtime's PyTorch
  "torch"
  "torchvision"
  # Removed: provided by comfyui-extras (torch-agnostic rebuilds)
  "timm"
  "accelerate"
];
```

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
│       ├── comfyui-workflows.nix
│       ├── ...                # Individual package definitions
│       └── timm.nix
├── sources/
│   ├── color_matcher-0.6.0-py3-none-any.whl  # Vendored wheels
│   ├── cstr-*.tar.gz
│   ├── img2texture-*.tar.gz
│   ├── ComfyUI-SafeCLIP-SDXL/  # Vendored custom node (no upstream repo)
│   └── workflows/              # Example workflows (API format, source of truth)
│       ├── convert_to_webui.py # Converter script (run at build time)
│       ├── SD15/
│       │   ├── sd15-txt2img.json
│       │   ├── sd15-img2img.json
│       │   └── ...
│       ├── SDXL/
│       ├── SD35/
│       └── FLUX/
└── result-*                   # Build output symlinks (gitignored)
```

## Packages

### Meta-Packages

See [Release-Tracked Packages](#release-tracked-packages) for the version-lockstep requirements and build recipe links.

| Meta-Package | Description | Platforms |
|--------------|-------------|-----------|
| `comfyui-extras` | Torch-agnostic ML packages + clean utilities | x86_64-linux |
| `comfyui-plugins` | Impact Pack (FaceDetailer, detection nodes) | x86_64-linux |
| `comfyui-impact-subpack` | Impact Subpack (YOLO detector, SAM loader) | x86_64-linux |
| `comfyui-videogen` | 4 video generation custom nodes from GitHub | All platforms |
| `comfyui-custom-nodes` | 15 community custom nodes from GitHub | All platforms |

#### comfyui-extras

Aggregates all torch-agnostic ML packages plus these from nixpkgs:
- piexif, simpleeval, numba, gitpython, onnxruntime, easydict, pymatting, pillow-heif, rich, albumentations, imageio-ffmpeg, gguf, onnx

#### comfyui-plugins

Provides ComfyUI-Impact-Pack, the essential custom node collection with FaceDetailer, object detection, mask operations, and batch processing. Requires `comfyui-extras` for Python dependencies (ultralytics, segment-anything).

#### comfyui-impact-subpack

Provides ComfyUI-Impact-Subpack with UltralyticsDetectorProvider (YOLO detection) and SAMLoader nodes. Bundles [`comfyui-sam2`](.flox/pkgs/comfyui-sam2.nix) and [`comfyui-thop`](.flox/pkgs/comfyui-thop.nix) as Python dependencies. Requires `comfyui-plugins` (Impact Pack) and `comfyui-extras` at runtime.

#### comfyui-videogen

Bundles 4 video generation/processing custom nodes:
- ComfyUI-AnimateDiff-Evolved, ComfyUI-VideoHelperSuite, ComfyUI-LTXVideo, ComfyUI-WanVideoWrapper

Python dependencies (peft, facexlib, pyloudnorm, imageio-ffmpeg) are provided by `comfyui-extras`. Runtime manifest provides diffusers, transformers, av (PyAV), and ffmpeg.

#### comfyui-custom-nodes

Bundles 15 essential community custom nodes:
- rgthree-comfy, images-grid-comfy-plugin, ComfyUI-Image-Saver, ComfyUI_UltimateSDUpscale
- ComfyUI-KJNodes, ComfyUI_essentials, ComfyUI-Custom-Scripts, ComfyUI_Comfyroll_CustomNodes
- efficiency-nodes-comfyui, was-node-suite-comfyui, ComfyUI-mxToolkit
- ComfyUI_IPAdapter_plus, ComfyUI-IPAdapter-Flux, ComfyUI-SafeCLIP-SDXL
- Comfyui-LayerForge (Photoshop-like layer editor)

**Note:** `comfyui-extras` and `comfyui-plugins` are **x86_64-linux only** due to torch-agnostic ML package constraints.

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
| `comfyui-spandrel` | Upscaler architectures | Linux | [chaiNNer-org/spandrel](https://github.com/chaiNNer-org/spandrel) |
| `comfyui-peft` | Parameter-efficient fine-tuning | Linux | [huggingface/peft](https://github.com/huggingface/peft) |
| `comfyui-facexlib` | Face processing library | Linux | [xinntao/facexlib](https://github.com/xinntao/facexlib) |
| `comfyui-sam2` | Segment Anything 2 | Linux | [facebookresearch/sam2](https://github.com/facebookresearch/sam2) |
| `comfyui-thop` | FLOPs counter for PyTorch | Linux | [Lyken17/pytorch-OpCounter](https://github.com/Lyken17/pytorch-OpCounter) |

### Standalone Custom Node Packages

These are custom node packages with their own Python dependencies, built separately from `comfyui-custom-nodes`:

| Package | Description | Platforms | Source |
|---------|-------------|-----------|--------|
| `comfyui-controlnet-aux` | ControlNet preprocessors (Canny, Depth, Pose, etc.) | x86_64-linux | [Fannovel16/comfyui_controlnet_aux](https://github.com/Fannovel16/comfyui_controlnet_aux) |

**Note:** `comfyui-controlnet-aux` excludes MediaPipe (not in nixpkgs). DWPose and some face detection nodes require manual mediapipe installation.

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
| `pyloudnorm` | Audio loudness normalization | [csteinmetz1/pyloudnorm](https://github.com/csteinmetz1/pyloudnorm) |

### Build-Time Patches

Some upstream packages require patches to build correctly or run without warnings. These patches are applied automatically during the Nix build using `substituteInPlace --replace-fail` (which fails the build if the pattern isn't found, catching upstream changes).

#### ComfyUI_Comfyroll_CustomNodes

Fixes Python 3.12+ SyntaxWarnings caused by invalid escape sequences in string literals:

| File | Original | Patched | Reason |
|------|----------|---------|--------|
| `nodes/nodes_list.py` | `C:\Windows\Fonts` | `C:/Windows/Fonts` | `\W` is invalid escape |
| `nodes/nodes_xygrid.py` | `fonts\Roboto-Regular.ttf` | `fonts/Roboto-Regular.ttf` | `\R` is invalid escape |

These are Windows-style paths in string literals that worked in Python <3.12 but now trigger `SyntaxWarning: invalid escape sequence`. The forward slash replacement is cross-platform compatible and functionally equivalent.

#### onnxruntime-noexecstack

The nixpkgs `onnxruntime` shared library (`onnxruntime_pybind11_state.so`) has its ELF `GNU_STACK` header set to `RWE` (read/write/execute). Hardened kernels (Debian 13+) refuse to load shared libraries with executable stacks:

```
cannot enable executable stack as shared object requires: Invalid argument
```

The `onnxruntime-noexecstack` wrapper fixes this by:

1. Copying the nixpkgs onnxruntime package
2. Patching the ELF `GNU_STACK` flag from `RWE` to `RW` (clearing `PF_X`)
3. Using `remove-references-to` to strip the Nix reference to the original `python3.pkgs.onnxruntime`, preventing both the patched and unpatched versions from appearing in the environment's `site-packages/` (which would cause a symlink collision where the unpatched version wins)

The C library (`onnxruntime-1.22.0`, providing `lib/libonnxruntime.so`) is retained in the closure — it does not collide because it has no `site-packages/` content.

This is a temporary fix. When nixpkgs corrects the `GNU_STACK` flags upstream, remove `onnxruntime-noexecstack.nix`, revert `rembg.nix` to use `python3.pkgs.onnxruntime` directly, and remove the wrapper from `comfyui-extras.nix`.

### Runtime Behavior

#### Custom Node Installation Patterns

The runtime hook installs custom nodes using two patterns depending on the node's requirements:

**Copied to user directory (writable):** Most custom nodes are copied from the Nix store to `~/comfyui-work/custom_nodes/` and then symlinked into `comfyui-runtime/custom_nodes/`. This allows nodes to write to their own directories at runtime (caches, configs, `__pycache__/`, downloaded models).

**Symlinked read-only to runtime:** Impact Pack and Impact Subpack are symlinked directly from the Nix store to `comfyui-runtime/custom_nodes/`. These nodes have internal model paths and subpack dependencies that resolve relative to their install location — copying them would break those references. Their writable data (models, whitelists) is stored in separate user directories configured via ComfyUI's folder paths.

#### WanVideoWrapper Duplicate Warning

When ComfyUI starts, WanVideoWrapper may emit:

```
WARNING: Found 1 other WanVideoWrapper directories:
  - /path/to/comfyui-runtime/custom_nodes/ComfyUI-WanVideoWrapper
Please remove duplicates to avoid possible conflicts.
```

This is a false positive. WanVideoWrapper's `check_duplicate_nodes()` scans `comfyui-runtime/custom_nodes/` and compares each entry against `Path(__file__).parent`. The runtime entry is a symlink to the user copy, but `Path.iterdir()` returns the unresolved symlink path while `__file__` resolves to the real user directory path. The two paths point to the same directory but differ as strings, triggering the warning.

**This warning is harmless and can be ignored.** There is only one copy of WanVideoWrapper (in the user directory). The symlink-read-only approach used for Impact Pack cannot be applied here because WanVideoWrapper writes `text_embed_cache/*.pt` files relative to its own `__file__` location, which would fail in the immutable Nix store.

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
comfyui-extras.store-path = "/nix/store/...-python3.13-comfyui-extras-0.10.0"
comfyui-extras.systems = ["x86_64-linux"]
```

### Package Priority Configuration

Some meta-packages have dependencies that conflict with other packages in the environment. To resolve these conflicts, assign a `priority` value in the manifest (lower number = higher priority):

```toml
# Required priority settings for conflict resolution
comfyui-extras.priority = 1
comfyui-plugins.priority = 2
comfyui-impact-subpack.priority = 3
```

| Package | Priority | Reason |
|---------|----------|--------|
| `comfyui-extras` | 1 | Contains authoritative versions of torch-agnostic ML packages |
| `comfyui-plugins` | 2 | Impact Pack may have conflicting utility scripts |
| `comfyui-impact-subpack` | 3 | Bundles dependencies also in comfyui-extras |

**Note:** Without priority settings, Flox may fail to activate the environment due to file conflicts between packages.

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
    # Bundled: standard Python packages (no torch contamination)
    numpy
    pillow
    pyyaml
    requests
  ];

  # Removed: these are provided by the runtime environment
  # - torch/torchvision: from runtime's CUDA PyTorch
  # - Other torch-contaminated packages: from comfyui-extras
  pythonRemoveDeps = [
    "torch"
    "torchvision"
    # Add any other torch-contaminated deps the package requires
    # "timm"        # if needed - provided by comfyui-extras
    # "accelerate"  # if needed - provided by comfyui-extras
  ];

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

## Versioning Policy

This repository follows two versioning conventions depending on the package type:

### Upstream Packages (Official Third-Party Libraries)

Packages that wrap official upstream libraries **retain their upstream version numbers**:

| Package | Version Example | Meaning |
|---------|-----------------|---------|
| `comfyui-ultralytics` | `8.3.68` | Upstream ultralytics v8.3.68 |
| `comfyui-timm` | `1.0.15` | Upstream timm v1.0.15 |
| `comfyui-segment-anything` | `1.0` | Upstream segment-anything v1.0 |
| `comfyui-impact-subpack` | `1.3.5_flox_build` | Based on upstream Impact Subpack v1.3.4 |

The `_flox_build` suffix indicates our packaging adds something beyond the upstream source (e.g., bundled dependencies via `propagatedBuildInputs`).

**Rationale**: Using upstream versions makes it clear which version of the underlying library is included, simplifying compatibility tracking and debugging.

### Internal Packages (ComfyUI-Specific Bundles)

Packages that bundle multiple components or are specific to our build infrastructure use **ComfyUI-tracking versions** (see [Release-Tracked Packages](#release-tracked-packages)):

| Package | Version Example | Meaning |
|---------|-----------------|---------|
| `comfyui-extras` | `0.10.0` | Targets ComfyUI v0.10.0 |
| `comfyui-plugins` | `0.10.0` | Targets ComfyUI v0.10.0 |
| `comfyui-custom-nodes` | `0.10.0` | Targets ComfyUI v0.10.0 |
| `comfyui-videogen` | `0.10.0` | Targets ComfyUI v0.10.0 |

**Rationale**: These packages bundle multiple upstream sources with ComfyUI-specific configuration, so their version reflects the ComfyUI release they're validated against.

### Version Suffix Conventions

| Suffix | Meaning |
|--------|---------|
| (none) | Direct upstream version, minimal modifications |
| `_flox_build` | Upstream version + Flox-specific enhancements (bundled deps, patches) |

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
