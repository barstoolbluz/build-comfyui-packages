# comfyui-ultralytics: Ultralytics YOLO for ComfyUI Impact Pack
# Built as a Nix expression for Flox
{ lib
, python3
, fetchFromGitHub
}:

python3.pkgs.buildPythonPackage rec {
  pname = "ultralytics";
  version = "8.3.162";
  pyproject = true;

  src = fetchFromGitHub {
    owner = "ultralytics";
    repo = "ultralytics";
    rev = "v${version}";
    hash = "sha256-it9yxKXcFF6qO+np0ii6Sg8JymqXAqhk8KJnl9upmgs=";
  };

  build-system = with python3.pkgs; [
    setuptools
    wheel
  ];

  dependencies = with python3.pkgs; [
    # Core dependencies from pyproject.toml
    numpy
    matplotlib
    opencv4
    pillow
    pyyaml
    requests
    scipy
    torch
    torchvision
    psutil
    polars
    ultralytics-thop
  ];

  # Disable tests - they require downloading models
  doCheck = false;

  pythonImportsCheck = [ "ultralytics" ];

  meta = with lib; {
    description = "Ultralytics YOLO for ComfyUI Impact Pack";
    homepage = "https://github.com/ultralytics/ultralytics";
    license = licenses.agpl3Only;
    platforms = platforms.linux;
  };
}
