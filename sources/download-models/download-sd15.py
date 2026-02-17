#!/usr/bin/env python3
"""
Download Stable Diffusion 1.5 model for ComfyUI

This downloads SD 1.5 model (4.3GB) - smaller and faster than SDXL/SD3.5.
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL_ID = "runwayml/stable-diffusion-v1-5"
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
checkpoints_dir = MODELS_DIR / "checkpoints"
vae_dir = MODELS_DIR / "vae"

checkpoints_dir.mkdir(parents=True, exist_ok=True)
vae_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading Stable Diffusion 1.5 for ComfyUI")
print("=" * 70)
print(f"Model: {MODEL_ID}")
print(f"Target: {MODELS_DIR}")
print()

# Files to download
files_to_download = [
    ("v1-5-pruned-emaonly.safetensors", checkpoints_dir),
]

print("Will download:")
for filename, target_dir in files_to_download:
    print(f"  • {filename}")
print()

try:
    for filename, target_dir in files_to_download:
        print(f"📥 Downloading {filename}...")

        downloaded_path = hf_hub_download(
            repo_id=MODEL_ID,
            filename=filename,
            token=HF_TOKEN if HF_TOKEN else None,
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
    print(f"  Checkpoint: {checkpoints_dir}/v1-5-pruned-emaonly.safetensors")
    print()
    print("Next steps:")
    print("  1. In ComfyUI, load the checkpoint: v1-5-pruned-emaonly.safetensors")
    print("  2. SD 1.5 works with regular CheckpointLoaderSimple")
    print("  3. Use 512x512 resolution for best results")
    print("  4. Higher CFG scale (7-11) works well with SD 1.5")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error downloading: {e}")
    print()
    print("NOTE: You may need to accept the model license at:")
    print(f"  https://huggingface.co/{MODEL_ID}")
    if not HF_TOKEN:
        print()
        print("TIP: Set HF_TOKEN environment variable if you need authentication")
    exit(1)
