#!/usr/bin/env python3
"""
Download FLUX.1 Dev model for ComfyUI

This downloads FLUX.1 Dev model with quantized text encoder option for reduced VRAM usage.
Also downloads:
  - 4x-UltraSharp upscale model for upscaling workflows
  - face_yolov8m.pt face detection model for face-enhance workflows
"""
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

def get_hf_token():
    """
    Get HuggingFace token from multiple sources with fallback to interactive prompt.

    Returns:
        str or None: The token if found/provided, None if user skips
    """
    # 1. Check HF_TOKEN environment variable
    if token := os.environ.get("HF_TOKEN"):
        print("✓ Using HF_TOKEN from environment variable")
        return token

    # 2. Check HUGGING_FACE_HUB_TOKEN environment variable
    if token := os.environ.get("HUGGING_FACE_HUB_TOKEN"):
        print("✓ Using HUGGING_FACE_HUB_TOKEN from environment variable")
        return token

    # 3. Check HuggingFace CLI cache
    token_paths = [
        Path.home() / ".cache" / "huggingface" / "token",
        Path.home() / ".huggingface" / "token",
    ]

    for token_path in token_paths:
        if token_path.exists():
            try:
                token = token_path.read_text().strip()
                if token:
                    print(f"✓ Using token from {token_path}")
                    return token
            except Exception:
                pass

    # 4. Interactive prompt
    print()
    print("=" * 70)
    print("HuggingFace Token Required")
    print("=" * 70)
    print()
    print("FLUX models require authentication with HuggingFace.")
    print()
    print("To get a token:")
    print("  1. Visit: https://huggingface.co/settings/tokens")
    print("  2. Create a new token (or use existing)")
    print("  3. Accept the model license at:")
    print("     https://huggingface.co/black-forest-labs/FLUX.1-dev")
    print()
    print("You can also set the token permanently:")
    print("  export HF_TOKEN=hf_your_token_here")
    print("  # Add to ~/.bashrc or ~/.zshrc to persist")
    print()

    try:
        token = input("Enter your HuggingFace token (or press Enter to skip): ").strip()
        return token if token else None
    except (KeyboardInterrupt, EOFError):
        print("\n\n❌ Cancelled by user")
        return None

# Configuration
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
unet_dir = MODELS_DIR / "unet"
vae_dir = MODELS_DIR / "vae"
clip_dir = MODELS_DIR / "clip"
upscale_dir = MODELS_DIR / "upscale_models"

unet_dir.mkdir(parents=True, exist_ok=True)
vae_dir.mkdir(parents=True, exist_ok=True)
clip_dir.mkdir(parents=True, exist_ok=True)
upscale_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading FLUX.1 Dev for ComfyUI")
print("=" * 70)
print(f"Target: {MODELS_DIR}")
print()

# Get token with interactive fallback
HF_TOKEN = get_hf_token()

if HF_TOKEN is None:
    print()
    print("⚠️  No token provided. Download will likely fail.")
    print()
    sys.exit(1)

# Files to download - using quantized FP8 for reduced VRAM
files_to_download = [
    # Main FLUX model (FP8 quantized)
    ("flux1-dev-fp8.safetensors", unet_dir, "black-forest-labs/FLUX.1-dev"),
    # VAE
    ("ae.safetensors", vae_dir, "black-forest-labs/FLUX.1-dev"),
    # CLIP models
    ("text_encoder/model.safetensors", clip_dir, "black-forest-labs/FLUX.1-dev"),
    # T5 text encoder (FP8 quantized for lower VRAM)
    ("t5xxl_fp8_e4m3fn.safetensors", clip_dir, "comfyanonymous/flux_text_encoders"),
]

# Upscale model (no token required - CC BY-NC-SA 4.0 license)
upscale_files = [
    ("4x-UltraSharp.pth", upscale_dir, "Kim2091/UltraSharp"),
]

# Face detection model for face-enhance workflow (AGPL-3.0 license)
ultralytics_dir = MODELS_DIR / "ultralytics" / "bbox"
ultralytics_dir.mkdir(parents=True, exist_ok=True)

face_detection_files = [
    ("face_yolov8m.pt", ultralytics_dir, "Bingsu/adetailer"),
]

print("Will download:")
for filename, _, repo_id in files_to_download:
    print(f"  • {filename} from {repo_id}")
print()
print("Will also download upscale model (for upscaling workflows):")
for filename, _, repo_id in upscale_files:
    print(f"  • {filename} from {repo_id}")
print()
print("Will also download face detection model (for face-enhance workflow):")
for filename, _, repo_id in face_detection_files:
    print(f"  • {filename} from {repo_id}")
print()
print("Note: Using FP8 quantized models for reduced VRAM usage")
print()

try:
    for filename, target_dir, repo_id in files_to_download:
        print(f"📥 Downloading {filename}...")

        # Extract just the filename for local storage
        local_filename = Path(filename).name

        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=HF_TOKEN,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )

        print(f"   ✓ Saved to: {downloaded_path}")
        print()

    # Download upscale model (no token required)
    for filename, target_dir, repo_id in upscale_files:
        print(f"📥 Downloading {filename} (upscale model)...")

        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=None,  # Public model, no token needed
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )

        print(f"   ✓ Saved to: {downloaded_path}")
        print()

    # Download face detection model (no token required)
    for filename, target_dir, repo_id in face_detection_files:
        print(f"📥 Downloading {filename} (face detection model)...")

        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=None,  # Public model, no token needed
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )

        print(f"   ✓ Saved to: {downloaded_path}")
        print()

    print("=" * 70)
    print("✅ All files downloaded successfully!")
    print()
    print("Downloaded files:")
    print(f"  UNet:      {unet_dir}/flux1-dev-fp8.safetensors")
    print(f"  VAE:       {vae_dir}/ae.safetensors")
    print(f"  CLIP:      {clip_dir}/model.safetensors")
    print(f"  T5-XXL:    {clip_dir}/t5xxl_fp8_e4m3fn.safetensors")
    print(f"  Upscale:   {upscale_dir}/4x-UltraSharp.pth")
    print(f"  FaceDet:   {ultralytics_dir}/face_yolov8m.pt")
    print()
    print("Next steps:")
    print("  1. Start ComfyUI")
    print("  2. Use FLUX workflow from ~/comfyui-work/user/default/workflows/FLUX/")
    print("  3. FP8 models reduce VRAM usage significantly")
    print()
    print("Licenses:")
    print("  • 4x-UltraSharp: CC BY-NC-SA 4.0 (non-commercial)")
    print("  • face_yolov8m.pt: AGPL-3.0 (from adetailer)")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error downloading: {e}")
    print()
    print("Possible issues:")
    print("  • You may need to accept the model license at:")
    print("    https://huggingface.co/black-forest-labs/FLUX.1-dev")
    print("  • Your token may not have the required permissions")
    print("  • Check your internet connection")
    sys.exit(1)
