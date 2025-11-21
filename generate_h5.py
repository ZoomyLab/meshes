import glob
from zoomy_core.mesh.mesh import msh_to_h5

files = glob.glob("**/*.msh", recursive=True)
for f in files:
    print(f"Converting {f} → h5")
    msh_to_h5(f)
