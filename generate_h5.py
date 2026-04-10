"""Convert .msh files to HDF5 using the new mesh hierarchy (no PETSc)."""

import glob
import os
from zoomy_core.mesh import BaseMesh


def msh_to_h5(msh_path):
    """Convert a .msh file to .h5 via BaseMesh (topology-only, format v2)."""
    h5_path = os.path.splitext(msh_path)[0] + ".h5"
    mesh = BaseMesh.from_msh(msh_path)
    mesh.write_to_hdf5(h5_path)
    return h5_path


files = glob.glob("**/*.msh", recursive=True)
for f in files:
    print(f"Converting {f} → h5")
    msh_to_h5(f)
