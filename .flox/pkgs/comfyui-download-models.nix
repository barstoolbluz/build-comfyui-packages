{ lib, stdenv }:

stdenv.mkDerivation {
  pname = "comfyui-download-models";
  version = "1.0.0";

  src = ../../sources/download-models;

  dontBuild = true;
  dontConfigure = true;

  installPhase = ''
    runHook preInstall
    mkdir -p $out/bin
    for script in *.py; do
      # Transform download-flux.py -> comfyui-download-flux
      name="comfyui-$(basename "$script" .py)"
      cp "$script" "$out/bin/$name"
      chmod +x "$out/bin/$name"
    done
    runHook postInstall
  '';

  meta = with lib; {
    description = "Model download scripts for ComfyUI (SD15, SDXL, SD3.5, FLUX) - includes upscale models";
    license = licenses.mit;
    platforms = platforms.all;
  };
}
