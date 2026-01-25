# comfyui-impact-subpack: Additional Nodes for ComfyUI Impact Pack
# ==================================================================
# This package provides ComfyUI-Impact-Subpack, which extends
# Impact Pack with additional detection and segmentation nodes.
#
# Impact Subpack provides:
#   - UltralyticsDetectorProvider (YOLO-based detection)
#   - SAMLoader (Segment Anything Model loader)
#   - Additional segmentation utilities
#
# Note: Impact Subpack requires:
#   - ComfyUI-Impact-Pack (provided by comfyui-plugins)
#   - Python dependencies from comfyui-extras (ultralytics, segment-anything)
#
# Version tracks ComfyUI release for compatibility.
# Impact Subpack source version noted in comments.

{ lib
, stdenv
, fetchFromGitHub
}:

stdenv.mkDerivation rec {
  pname = "comfyui-impact-subpack";
  version = "0.9.2";  # Tracks ComfyUI version

  # Impact Subpack v1.3.4
  src = fetchFromGitHub {
    owner = "ltdrdata";
    repo = "ComfyUI-Impact-Subpack";
    rev = "1.3.4";
    hash = "sha256-BHtfkaqCPf/YXfGbF/xyryjt+M8izkdoUAKNJLfyvqI=";
  };

  dontBuild = true;
  dontConfigure = true;

  installPhase = ''
    runHook preInstall

    # Create directory structure
    mkdir -p $out/share/comfyui/custom_nodes

    # Install Impact Subpack
    cp -r . $out/share/comfyui/custom_nodes/ComfyUI-Impact-Subpack

    # Remove unnecessary files from the installed copy
    rm -rf $out/share/comfyui/custom_nodes/ComfyUI-Impact-Subpack/.git
    rm -rf $out/share/comfyui/custom_nodes/ComfyUI-Impact-Subpack/.github

    runHook postInstall
  '';

  meta = with lib; {
    description = "Additional nodes for ComfyUI Impact Pack (Subpack)";
    longDescription = ''
      ComfyUI-Impact-Subpack extends Impact Pack with additional nodes:
      - UltralyticsDetectorProvider: YOLO-based object detection
      - SAMLoader: Segment Anything Model loader
      - Additional segmentation and detection utilities

      Requires:
      - comfyui-plugins (Impact Pack)
      - comfyui-extras (ultralytics, segment-anything)

      Impact Subpack source version: 1.3.4
    '';
    homepage = "https://github.com/ltdrdata/ComfyUI-Impact-Subpack";
    license = licenses.gpl3Only;
    platforms = platforms.all;
  };
}
