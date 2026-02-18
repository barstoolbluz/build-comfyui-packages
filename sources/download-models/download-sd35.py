#!/usr/bin/env python3
"""
Download Stable Diffusion 3.5 Large model for ComfyUI

This downloads the main checkpoint file and text encoders needed for SD 3.5.
Also downloads the 4x-UltraSharp upscale model for upscaling workflows.
Includes interactive token handling with multiple fallback options.
"""
import os
import sys
from pathlib import Path
from huggingface_hub import hf_hub_download

def get_hf_token():
    """
    Get HuggingFace token from multiple sources with fallback to interactive prompt.

    Priority order:
    1. HF_TOKEN environment variable
    2. HUGGING_FACE_HUB_TOKEN environment variable
    3. HuggingFace CLI cache (~/.cache/huggingface/token or ~/.huggingface/token)
    4. Interactive prompt with instructions

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
    print("This model requires authentication with HuggingFace.")
    print()
    print("To get a token:")
    print("  1. Visit: https://huggingface.co/settings/tokens")
    print("  2. Create a new token (or use existing)")
    print("  3. Accept the model license at:")
    print("     https://huggingface.co/stabilityai/stable-diffusion-3.5-large")
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
MODEL_ID = "stabilityai/stable-diffusion-3.5-large"
MODELS_DIR = Path(os.environ.get("COMFYUI_MODELS_DIR",
                  os.environ.get("COMFYUI_WORK_DIR", str(Path.home() / "comfyui-work")) + "/models"))

# Create model directories
checkpoints_dir = MODELS_DIR / "checkpoints"
clip_dir = MODELS_DIR / "clip"
vae_dir = MODELS_DIR / "vae"
upscale_dir = MODELS_DIR / "upscale_models"

checkpoints_dir.mkdir(parents=True, exist_ok=True)
clip_dir.mkdir(parents=True, exist_ok=True)
vae_dir.mkdir(parents=True, exist_ok=True)
upscale_dir.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("Downloading Stable Diffusion 3.5 Large for ComfyUI")
print("=" * 70)
print(f"Model: {MODEL_ID}")
print(f"Target: {MODELS_DIR}")
print()

# Files to download
files_to_download = [
    ("sd3.5_large.safetensors", checkpoints_dir, MODEL_ID),
    ("text_encoders/clip_l.safetensors", clip_dir, MODEL_ID),
    ("text_encoders/clip_g.safetensors", clip_dir, MODEL_ID),
    ("text_encoders/t5xxl_fp16.safetensors", clip_dir, MODEL_ID),
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

# Get token with interactive fallback
HF_TOKEN = get_hf_token()

if HF_TOKEN is None:
    print()
    print("⚠️  No token provided. Download may fail if model requires authentication.")
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

    print("=" * 70)
    print("✅ All files downloaded successfully!")
    print()
    print("Downloaded files:")
    print(f"  Checkpoint: {checkpoints_dir}/sd3.5_large.safetensors")
    print(f"  CLIP-L:     {clip_dir}/clip_l.safetensors")
    print(f"  CLIP-G:     {clip_dir}/clip_g.safetensors")
    print(f"  T5XXL:      {clip_dir}/t5xxl_fp16.safetensors")
    print(f"  Upscale:    {upscale_dir}/4x-UltraSharp.pth")
    print()
    print("Next steps:")
    print("  1. Start ComfyUI")
    print("  2. In ComfyUI, load the SD 3.5 checkpoint")
    print()
    print("Note: 4x-UltraSharp is licensed CC BY-NC-SA 4.0 (non-commercial)")
    print("=" * 70)

except Exception as e:
    print(f"❌ Error downloading: {e}")
    print()
    print("Possible issues:")
    print("  • You may need to accept the model license at:")
    print(f"    https://huggingface.co/{MODEL_ID}")
    print("  • Your token may not have the required permissions")
    print("  • Check your internet connection")
    print()
    if not HF_TOKEN:
        print("TIP: Provide a HuggingFace token for authenticated access:")
        print("  export HF_TOKEN=hf_your_token_here")
        print("  python3 download-sd35.py")
    sys.exit(1)
