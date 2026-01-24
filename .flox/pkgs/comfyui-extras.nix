# comfyui-extras: Torch-Agnostic Dependencies for ComfyUI Custom Nodes
# =====================================================================
#
# This meta-package provides all Python dependencies needed by popular
# ComfyUI custom nodes (Impact Pack, WAS Node Suite, Efficiency Nodes, etc.)
# built WITHOUT torch/torchvision in their closures.
#
# WHY TORCH-AGNOSTIC?
# -------------------
# Many Python ML packages (ultralytics, timm, open-clip, accelerate, etc.)
# depend on PyTorch. When installed from standard channels, they pull in
# CPU-only torch/torchvision, which conflicts with CUDA-enabled PyTorch
# and causes GPU operations (like NMS) to fail silently on CPU.
#
# This package rebuilds all torch-dependent packages from source using
# pythonRemoveDeps to strip torch requirements. At runtime, these packages
# use whatever PyTorch the environment provides (CUDA, MPS, or CPU).
#
# INCLUDED PACKAGES:
# ------------------
# ML/Vision (torch-agnostic builds):
#   - ultralytics (YOLO object detection)
#   - timm (PyTorch Image Models)
#   - open-clip-torch (OpenAI CLIP)
#   - accelerate (HuggingFace distributed training)
#   - segment-anything (Meta SAM)
#   - clip-interrogator (image-to-prompt)
#   - transparent-background (background removal)
#   - pixeloe (pixel art conversion)
#   - rembg (background removal)
#
# Image Processing:
#   - colour-science, color-matcher, albumentations, pymatting
#   - pillow-heif (HEIF/HEIC support)
#
# Utilities:
#   - ffmpy (FFmpeg wrapper), img2texture, cstr
#   - piexif, simpleeval, numba, gitpython, easydict, onnxruntime

{ lib
, python3
, callPackage
, stdenv
}:

let
  # Torch-agnostic ML packages (rebuilt from source without torch deps)
  comfyui-ultralytics = callPackage ./comfyui-ultralytics.nix { };
  comfyui-timm = callPackage ./timm.nix { };
  comfyui-open-clip-torch = callPackage ./open-clip-torch.nix { };
  comfyui-accelerate = callPackage ./comfyui-accelerate.nix { };
  comfyui-segment-anything = callPackage ./segment-anything.nix { };
  comfyui-clip-interrogator = callPackage ./comfyui-clip-interrogator.nix { };
  comfyui-transparent-background = callPackage ./comfyui-transparent-background.nix { };
  comfyui-pixeloe = callPackage ./comfyui-pixeloe.nix { };

  # Clean packages (no torch dependencies)
  colour-science = callPackage ./colour-science.nix { };
  rembg = callPackage ./rembg.nix { };
  ffmpy = callPackage ./ffmpy.nix { };
  color-matcher = callPackage ./color-matcher.nix { };
  img2texture = callPackage ./img2texture.nix { };
  cstr = callPackage ./cstr.nix { };
in

python3.pkgs.buildPythonPackage rec {
  pname = "comfyui-extras";
  version = "0.9.1";
  format = "other";

  # No source - this is a meta-package
  dontUnpack = true;
  dontBuild = true;
  doCheck = false;

  propagatedBuildInputs = (with python3.pkgs; [
    # From nixpkgs - standard packages (no torch contamination)
    piexif          # EXIF metadata handling
    simpleeval      # Safe expression evaluation
    numba           # JIT compilation for numerical code
    gitpython       # Git repository access
    onnxruntime     # ONNX model inference
    easydict        # Dict with attribute access
    pymatting       # Image matting algorithms
    pillow-heif     # HEIF/HEIC image support
    rich            # Terminal formatting (needed by ComfyUI-Manager)
  ]) ++ lib.optionals (!stdenv.hostPlatform.isDarwin) (with python3.pkgs; [
    # Broken on Darwin due to stringzilla compilation issues
    albumentations  # Image augmentation library
  ]) ++ [
    # Torch-agnostic ML packages (always included)
    comfyui-ultralytics       # YOLO object detection
    comfyui-timm              # PyTorch Image Models
    comfyui-open-clip-torch   # OpenAI CLIP implementation
    comfyui-accelerate        # HuggingFace Accelerate
    comfyui-segment-anything  # Meta SAM segmentation
    comfyui-clip-interrogator # Image to prompt
    colour-science            # Color science library
    rembg                     # Background removal
    ffmpy                     # FFmpeg wrapper
    color-matcher             # Color matching algorithms
    img2texture               # Seamless texture generation
    cstr                      # Colored terminal strings
  ] ++ lib.optionals (stdenv.hostPlatform.system == "x86_64-linux") [
    # x86_64-linux only (kornia-rs build issues on other platforms)
    comfyui-pixeloe               # Pixel art conversion
    comfyui-transparent-background # Background removal (ML-based)
  ];

  installPhase = ''
    mkdir -p $out
    echo "${version}" > $out/version
  '';

  meta = with lib; {
    description = "Torch-agnostic Python dependencies for ComfyUI custom nodes";
    longDescription = ''
      A comprehensive collection of Python packages required by popular ComfyUI
      custom nodes including Impact Pack, WAS Node Suite, and Efficiency Nodes.

      All ML packages that normally depend on PyTorch (ultralytics, timm,
      open-clip, accelerate, segment-anything, clip-interrogator, etc.) have
      been rebuilt WITHOUT torch/torchvision in their closures. This ensures
      they use the CUDA-enabled PyTorch provided by the runtime environment,
      avoiding conflicts with CPU-only torch that can cause GPU operations
      to silently fall back to CPU.

      Includes: ultralytics, timm, open-clip-torch, accelerate, segment-anything,
      clip-interrogator, transparent-background, pixeloe, rembg, colour-science,
      color-matcher, albumentations, pymatting, pillow-heif, ffmpy, and more.
    '';
    homepage = "https://github.com/barstoolbluz/build-comfyui-packages";
    license = licenses.mit;
    platforms = platforms.unix;
  };
}
