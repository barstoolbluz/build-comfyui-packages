# onnxruntime-noexecstack: Patched onnxruntime for hardened kernels
# ================================================================
# The nixpkgs onnxruntime .so has GNU_STACK with RWE (executable stack).
# Hardened kernels (Debian 13+) refuse to load it:
#   "cannot enable executable stack as shared object requires: Invalid argument"
#
# This wrapper copies the nixpkgs onnxruntime and patches the single byte
# in the ELF header to clear PF_X from GNU_STACK (RWE -> RW).
#
# It also removes the Nix-level reference to the original python3.pkgs.onnxruntime
# so that only this patched copy appears in the environment's site-packages.
# The C library (onnxruntime-1.22.0) is kept — it provides libonnxruntime.so
# under lib/ and does not collide.
#
# When nixpkgs fixes this upstream, remove this wrapper and use
# python3.pkgs.onnxruntime directly.

{ lib
, stdenv
, python3
, removeReferencesTo
}:

stdenv.mkDerivation {
  pname = "onnxruntime-noexecstack";
  inherit (python3.pkgs.onnxruntime) version;

  dontUnpack = true;
  dontBuild = true;

  installPhase = ''
    runHook preInstall

    # Copy the entire onnxruntime package
    cp -r ${python3.pkgs.onnxruntime} $out
    chmod -R u+w $out

    # Find and patch all .so files that have executable stack
    find $out -name '*.so' | while read so; do
      # Check if this .so has PT_GNU_STACK with PF_X set
      python3 << PYEOF
import struct, sys

with open("$so", "r+b") as f:
    f.seek(0)
    magic = f.read(4)
    if magic != b'\x7fELF':
        sys.exit(0)
    ei_class = struct.unpack('B', f.read(1))[0]
    if ei_class != 2:
        sys.exit(0)
    f.seek(32)
    e_phoff = struct.unpack('<Q', f.read(8))[0]
    f.seek(54)
    e_phentsize = struct.unpack('<H', f.read(2))[0]
    e_phnum = struct.unpack('<H', f.read(2))[0]
    for i in range(e_phnum):
        offset = e_phoff + i * e_phentsize
        f.seek(offset)
        p_type = struct.unpack('<I', f.read(4))[0]
        if p_type == 0x6474e551:  # PT_GNU_STACK
            f.seek(offset + 4)
            p_flags = struct.unpack('<I', f.read(4))[0]
            if p_flags & 1:  # PF_X set
                f.seek(offset + 4)
                f.write(struct.pack('<I', p_flags & ~1))
                print(f"Cleared execstack: $so")
            break
PYEOF
    done

    # Remove the Nix reference to the original Python onnxruntime package.
    # Without this, both our patched copy and the original end up in the
    # environment's site-packages, and the original (unpatched) wins the
    # symlink collision. The C library (onnxruntime-1.22.0) is NOT removed —
    # it provides lib/libonnxruntime.so which the .so files need at runtime.
    find $out -type f -exec remove-references-to \
      -t ${python3.pkgs.onnxruntime} {} +

    runHook postInstall
  '';

  nativeBuildInputs = [ python3 removeReferencesTo ];

  meta = python3.pkgs.onnxruntime.meta // {
    description = "ONNX Runtime with execstack flag cleared for hardened kernels";
  };
}
