# comfyui-nunchaku: 4-bit Quantized FLUX/SDXL Inference for ComfyUI
# ==================================================================
# MIT-HAN-Lab's nunchaku quantization engine for ComfyUI.
# Provides 4-bit quantized inference for FLUX and SDXL models.
#
# This is a source-only install (custom node files) with Python deps.
# The nunchaku inference engine itself must be installed separately
# (pip install nunchaku) as it requires matching CUDA/torch versions.
#
# Dependencies provided by:
#   - comfyui-extras: peft, facexlib, accelerate, timm, onnxruntime
#   - Runtime manifest: diffusers, transformers
#   - This package: insightface, protobuf, sentencepiece, tomli

{ lib
, python3
, fetchFromGitHub
}:

python3.pkgs.buildPythonPackage rec {
  pname = "comfyui-nunchaku";
  version = "1.2.1";
  format = "other";

  src = fetchFromGitHub {
    owner = "mit-han-lab";
    repo = "ComfyUI-nunchaku";
    tag = "v${version}";
    hash = "sha256-Lh5YhCWVyHI8NW9Cuu/gg/2GWX+EBzxcYznXmkaOekI=";
  };

  dontBuild = true;
  dontConfigure = true;
  doCheck = false;

  propagatedBuildInputs = with python3.pkgs; [
    # Deps not already in comfyui-extras or runtime manifest
    insightface       # Face analysis
    protobuf          # Protocol buffers
    sentencepiece     # Tokenizer
    tomli             # TOML parser
  ];

  installPhase = ''
    runHook preInstall

    mkdir -p $out/share/comfyui/custom_nodes/ComfyUI-nunchaku
    cp -r . $out/share/comfyui/custom_nodes/ComfyUI-nunchaku
    rm -rf $out/share/comfyui/custom_nodes/ComfyUI-nunchaku/.git
    rm -rf $out/share/comfyui/custom_nodes/ComfyUI-nunchaku/.github

    runHook postInstall
  '';

  meta = with lib; {
    description = "4-bit quantized FLUX/SDXL inference for ComfyUI";
    homepage = "https://github.com/mit-han-lab/ComfyUI-nunchaku";
    license = licenses.mit;
    platforms = platforms.unix;
  };
}
