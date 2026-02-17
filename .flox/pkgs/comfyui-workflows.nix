{ lib, stdenv, python3 }:

stdenv.mkDerivation {
  pname = "comfyui-workflows";
  version = "1.0.1";

  src = ../../sources/workflows;

  nativeBuildInputs = [ python3 ];

  dontConfigure = true;

  buildPhase = ''
    runHook preBuild

    # Generate Web UI format workflows from API format
    # Web UI format has node positions and links array needed for rendering
    python3 convert_to_webui.py . webui-output

    runHook postBuild
  '';

  installPhase = ''
    runHook preInstall

    # Install Web UI format workflows (for user workflow browser)
    mkdir -p $out/share/comfyui/workflows
    cp -r webui-output/* $out/share/comfyui/workflows/

    # Install API format workflows (for CI/programmatic use)
    mkdir -p $out/share/comfyui/workflows-api
    for dir in */; do
      if [ "$dir" != "webui-output/" ]; then
        cp -r "$dir" $out/share/comfyui/workflows-api/
      fi
    done
    # Copy any top-level json files (if any)
    find . -maxdepth 1 -name "*.json" -exec cp {} $out/share/comfyui/workflows-api/ \;

    runHook postInstall
  '';

  meta = with lib; {
    description = "Bundled example workflows for ComfyUI (Web UI + API formats)";
    license = licenses.mit;
    platforms = platforms.all;
  };
}
