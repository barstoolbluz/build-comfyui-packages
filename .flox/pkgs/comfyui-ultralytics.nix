# comfyui-ultralytics: Ultralytics YOLO for ComfyUI
# ==================================================
# This package is built WITHOUT torch/torchvision dependencies.
# The runtime environment (comfyui-repo) provides these, allowing
# the user to choose CUDA-enabled versions.
#
# This solves the problem where Flox catalog packages pull in
# CPU-only torchvision as a transitive dependency.

{ lib
, python3
, fetchFromGitHub
}:

python3.pkgs.buildPythonPackage rec {
  pname = "comfyui-ultralytics";
  version = "0.10.0";
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
    # Core dependencies (excluding torch/torchvision - provided by runtime)
    numpy
    matplotlib
    opencv-python
    pillow
    pyyaml
    requests
    scipy
    psutil
    # Removed: polars (not essential, causes issues)
    # Removed: ultralytics-thop (pulls in torch)
    tqdm
    py-cpuinfo
    pandas
  ];

  # Remove torch/torchvision from package requirements entirely
  # This ensures they won't be pulled in as transitive deps
  pythonRemoveDeps = [
    "torch"
    "torchvision"
    "ultralytics-thop"  # This pulls in torch, remove it
  ];

  # Disable tests - they require downloading models and torch
  doCheck = false;

  # Don't check imports - torch won't be available at build time
  # pythonImportsCheck = [ "ultralytics" ];

  meta = with lib; {
    description = "Ultralytics YOLO for ComfyUI (torch/torchvision provided by runtime)";
    homepage = "https://github.com/ultralytics/ultralytics";
    license = licenses.agpl3Only;
    platforms = platforms.linux;
  };
}
