#!/usr/bin/env python3
"""
Download Stable Diffusion XL model for ComfyUI

This downloads SDXL 1.0 base model (6.9GB).
Also downloads the 4x-UltraSharp upscale model for upscaling workflows.
"""
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

def get_hf_token_optional():
    """
    Get HuggingFace token if available (optional for SDXL).

    Returns:
        str or None: The token if found, None otherwise
    """
    # Check environment variables
    if token := os.environ.get("HF_TOKEN"):
        return token
    if token := os.environ.get("HUGGING_FACE_HUB_TOKEN"):
        return token

    # Check HuggingFace CLI cache
    token_paths = [
        Path.home() / ".cache" / "huggingface" / "token",
        Path.home() / ".huggingface" / "token",
    ]

    for token_path in token_paths:
        if token_path.exists():
            try:
                token = token_path.read_text().strip()
                if token:
                    return token
            except Exception:
                pass

    return None

# Configuration
MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
checkpoints_dir = MODELS_DIR / "checkpoints"
upscale_dir = MODELS_DIR / "upscale_models"

checkpoints_dir.mkdir(parents=True, exist_ok=True)
upscale_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading Stable Diffusion XL 1.0 for ComfyUI")
print("=" * 70)
print(f"Model: {MODEL_ID}")
print(f"Target: {MODELS_DIR}")
print()

# Files to download
files_to_download = [
    ("sd_xl_base_1.0.safetensors", checkpoints_dir, MODEL_ID),
]

# Upscale model (no token required - CC BY-NC-SA 4.0 license)
upscale_files = [
    ("4x-UltraSharp.pth", upscale_dir, "Kim2091/UltraSharp"),
]

print("Will download:")
for filename, _, repo_id in files_to_download:
    print(f"  • {filename} from {repo_id}")
print()
print("Will also download upscale model (for upscaling workflows):")
for filename, _, repo_id in upscale_files:
    print(f"  • {filename} from {repo_id}")
print()

# Get token (optional for SDXL)
HF_TOKEN = get_hf_token_optional()
if HF_TOKEN:
    print("✓ Using HuggingFace token for authenticated access")
    print()

try:
    for filename, target_dir, repo_id in files_to_download:
        print(f"📥 Downloading {filename}...")

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

    print("=" * 70)
    print("✅ All files downloaded successfully!")
    print()
    print("Downloaded files:")
    print(f"  Checkpoint: {checkpoints_dir}/sd_xl_base_1.0.safetensors")
    print(f"  Upscale:    {upscale_dir}/4x-UltraSharp.pth")
    print()
    print("Next steps:")
    print("  1. In ComfyUI, load the checkpoint: sd_xl_base_1.0.safetensors")
    print("  2. SDXL works with regular CheckpointLoaderSimple")
    print("  3. Use 1024x1024 resolution for best results")
    print()
    print("Note: 4x-UltraSharp is licensed CC BY-NC-SA 4.0 (non-commercial)")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error downloading: {e}")
    print()
    print("NOTE: You may need to accept the model license at:")
    print(f"  https://huggingface.co/{MODEL_ID}")
    if not HF_TOKEN:
        print()
        print("TIP: Set HF_TOKEN environment variable if you need authentication:")
        print("  export HF_TOKEN=hf_your_token_here")
        print("  python3 download-sdxl.py")
    sys.exit(1)
