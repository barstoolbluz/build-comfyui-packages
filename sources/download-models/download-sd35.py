#!/usr/bin/env python3
"""
Download Stable Diffusion 3.5 Large model for ComfyUI

This downloads the main checkpoint file and text encoders needed for SD 3.5.
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
checkpoints_dir = MODELS_DIR / "checkpoints"
clip_dir = MODELS_DIR / "clip"
vae_dir = MODELS_DIR / "vae"

checkpoints_dir.mkdir(parents=True, exist_ok=True)
clip_dir.mkdir(parents=True, exist_ok=True)
vae_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading Stable Diffusion 3.5 Large for ComfyUI")
print("=" * 70)
print(f"Model: {MODEL_ID}")
print(f"Target: {MODELS_DIR}")
print()

# Files to download
files_to_download = [
    ("sd3.5_large.safetensors", checkpoints_dir),
    ("text_encoders/clip_l.safetensors", clip_dir),
    ("text_encoders/clip_g.safetensors", clip_dir),
    ("text_encoders/t5xxl_fp16.safetensors", clip_dir),
]

print("Will download:")
for filename, target_dir in files_to_download:
    print(f"  • {filename}")
print()

try:
    for filename, target_dir in files_to_download:
        print(f"📥 Downloading {filename}...")

        # Extract just the filename for local storage
        local_filename = Path(filename).name

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
    print(f"  Checkpoint: {checkpoints_dir}/sd3.5_large.safetensors")
    print(f"  CLIP-L:     {clip_dir}/clip_l.safetensors")
    print(f"  CLIP-G:     {clip_dir}/clip_g.safetensors")
    print(f"  T5XXL:      {clip_dir}/t5xxl_fp16.safetensors")
    print()
    print("Next steps:")
    print("  1. Start ComfyUI: flox services start comfyui")
    print("  2. Open http://0.0.0.0:8188 in your browser")
    print("  3. In ComfyUI, load the SD 3.5 checkpoint")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error downloading: {e}")
    print()
    print("NOTE: You may need to accept the model license at:")
    print(f"  https://huggingface.co/{MODEL_ID}")
    if not HF_TOKEN:
        print()
        print("TIP: Set HF_TOKEN environment variable with your HuggingFace token:")
        print("  export HF_TOKEN=hf_your_token_here")
        print("  python3 download-sd35.py")
    exit(1)
