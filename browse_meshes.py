import requests
import os
import meshio


GITHUB_REPO = "ZoomyLab/meshes"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"


def _get_latest_release():
    """Fetch metadata for the latest release from GitHub."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()


def show_meshes():
    """
    List all mesh assets available in the latest release.
    Returns a list of asset names.
    """
    release = _get_latest_release()
    assets = release.get("assets", [])

    print(f"Latest release: {release.get('tag_name')}")

    mesh_files = []
    for asset in assets:
        name = asset["name"]
        mesh_files.append(name)
        print(" -", name)

    return mesh_files


def download_mesh(mesh_name: str, out_path: str):
    """
    Download a mesh from the latest release by matching the asset name.
    mesh_name: e.g. "square/mesh.msh"
    out_path: output file path to save mesh
    """
    release = _get_latest_release()

    # Find asset with exact name
    for asset in release.get("assets", []):
        if asset["name"] == mesh_name:
            url = asset["browser_download_url"]

            print(f"Downloading {mesh_name} → {out_path}")
            r = requests.get(url)
            r.raise_for_status()

            # Ensure target directory exists
            os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)

            with open(out_path, "wb") as f:
                f.write(r.content)

            print("Download complete.")
            return out_path

    raise ValueError(f"Mesh '{mesh_name}' not found in latest release.")


def get_boundary_names(mesh_path: str):
    """
    Read a mesh file with meshio and list all physical groups / tags.
    Returns a dict of cell_block_name → physical tag sets.
    """
    print(f"Reading mesh: {mesh_path}")
    mesh = meshio.read(mesh_path)

    tags = {}

    # meshio stores physical tags in cell_data["gmsh:physical"]
    if "gmsh:physical" in mesh.cell_data:
        for block, phys in zip(mesh.cells, mesh.cell_data["gmsh:physical"]):
            cell_type = block.type
            unique_tags = sorted(set(phys))
            tags[cell_type] = unique_tags

    print("Found physical tags:")
    for cell_type, names in tags.items():
        print(f" - {cell_type}: {names}")

    return tags
