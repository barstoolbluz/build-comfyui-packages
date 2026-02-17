#!/usr/bin/env python3
"""
Download FLUX.1-dev model for ComfyUI

This downloads the main UNET, VAE, and text encoders needed for FLUX.1-dev.
"""
import os
from pathlib import Path
from huggingface_hub import hf_hub_download

# Configuration
HF_TOKEN = os.environ.get("HF_TOKEN", "")
MODEL_ID = "black-forest-labs/FLUX.1-dev"
TEXT_ENCODER_REPO = "comfyanonymous/flux_text_encoders"
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
unet_dir = MODELS_DIR / "unet"
clip_dir = MODELS_DIR / "clip"
vae_dir = MODELS_DIR / "vae"

unet_dir.mkdir(parents=True, exist_ok=True)
clip_dir.mkdir(parents=True, exist_ok=True)
vae_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading FLUX.1-dev for ComfyUI")
print("=" * 70)
print(f"Model: {MODEL_ID}")
print(f"Target: {MODELS_DIR}")
print()

# Files to download - (repo_id, remote_filename, target_dir, local_filename)
files_to_download = [
    (MODEL_ID, "flux1-dev.safetensors", unet_dir, "flux1-dev.safetensors"),
    (MODEL_ID, "ae.safetensors", vae_dir, "ae.safetensors"),
    (MODEL_ID, "text_encoder/model.safetensors", clip_dir, "clip_l.safetensors"),
    (TEXT_ENCODER_REPO, "t5xxl_fp16.safetensors", clip_dir, "t5xxl_fp16.safetensors"),
]

print("Will download:")
for repo_id, remote_file, target_dir, local_file in files_to_download:
    print(f"  • {remote_file} → {target_dir}/{local_file}")
print()

try:
    for repo_id, remote_file, target_dir, local_file in files_to_download:
        print(f"📥 Downloading {remote_file}...")

        # Download directly to target directory
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=remote_file,
            token=HF_TOKEN if HF_TOKEN else None,
            local_dir=target_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
        )

        # Rename if the downloaded filename doesn't match desired name
        # (needed for text_encoder/model.safetensors → clip_l.safetensors)
        downloaded_file = Path(downloaded_path)
        final_path = target_dir / local_file

        if downloaded_file != final_path:
            if final_path.exists():
                final_path.unlink()
            downloaded_file.rename(final_path)

        print(f"   ✓ Saved to: {final_path}")
        print()

    print("=" * 70)
    print("✅ All files downloaded successfully!")
    print()
    print("Downloaded files:")
    print(f"  UNET:     {unet_dir}/flux1-dev.safetensors")
    print(f"  VAE:      {vae_dir}/ae.safetensors")
    print(f"  CLIP-L:   {clip_dir}/clip_l.safetensors")
    print(f"  T5XXL:    {clip_dir}/t5xxl_fp16.safetensors")
    print()
    print("Next steps:")
    print("  1. Start ComfyUI: flox services start comfyui")
    print("  2. Open http://0.0.0.0:8188 in your browser")
    print("  3. In ComfyUI, use UNETLoader for FLUX models")
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
        print("  python3 download-flux.py")
    exit(1)
