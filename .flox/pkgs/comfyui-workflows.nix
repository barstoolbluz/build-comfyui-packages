{ lib, stdenv }:

stdenv.mkDerivation {
  pname = "comfyui-workflows";
  version = "1.0.0";

  src = ../../sources/workflows;

  dontBuild = true;
  dontConfigure = true;

  installPhase = ''
    runHook preInstall
    mkdir -p $out/share/comfyui/workflows
    cp -r . $out/share/comfyui/workflows/
    runHook postInstall
  '';

  meta = with lib; {
    description = "Bundled example workflows for ComfyUI";
    license = licenses.mit;
    platforms = platforms.all;
  };
}
