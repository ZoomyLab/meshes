import requests
import os
import meshio

GITHUB_REPO = "ZoomyLab/meshes"
API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

ALLOWED_TYPES = {"msh", "geo", "h5"}


def _get_latest_release():
    """Fetch metadata for the latest release from GitHub."""
    response = requests.get(API_URL)
    response.raise_for_status()
    return response.json()


def _split_mesh_base(name: str):
    """
    Takes an asset filename like 'square/mesh.msh' and returns ('square/mesh', 'msh').
    """
    base, ext = os.path.splitext(name)
    return base, ext.lstrip(".")


def show_meshes(do_print=True):
    """
    List all *base mesh names* (without extensions) available in the latest release.
    Returns a sorted list of unique base names.
    """
    release = _get_latest_release()
    assets = release.get("assets", [])

    if do_print:
        print(f"Latest release: {release.get('tag_name')}")

    base_names = set()

    for asset in assets:
        base, ext = _split_mesh_base(asset["name"])
        if ext in ALLOWED_TYPES:
            base_names.add(base)

    base_names = sorted(base_names)

    if do_print:
        print("Available meshes:")
        for name in base_names:
            print(f" - {name}")

    return base_names


def download_mesh(mesh_name: str, folder: str = "./", filetype: str = "msh"):
    """
    Download a mesh with a specific file type.

    mesh_name: base name like 'square/mesh'
    folder: directory to save to (default './')
    filetype: one of {'msh', 'geo', 'h5'}
    """
    if filetype not in ALLOWED_TYPES:
        print(
            f"Invalid file type '{filetype}'. \
        Allowed: {ALLOWED_TYPES}"
        )
        return

    release = _get_latest_release()
    assets = release.get("assets", [])

    # Collect all filetypes that exist for this mesh base
    available_types = {}
    for asset in assets:
        base, ext = _split_mesh_base(asset["name"])
        if base == mesh_name:
            available_types[ext] = asset["browser_download_url"]

    if not available_types:
        print(f"Mesh '{mesh_name}' not found in latest release.")

    # Check if requested type exists
    if filetype not in available_types:
        print(
            f"Requested filetype '{filetype}' \
            not available for '{mesh_name}'. "
            f"Available types: {sorted(available_types.keys())}"
        )
        return

    url = available_types[filetype]

    # Construct output path
    os.makedirs(folder, exist_ok=True)
    filename = f"{mesh_name}.{filetype}".split("/")[-1]
    out_path = os.path.join(folder, filename)

    print(f"Downloading {mesh_name}.{filetype} → {out_path}")

    r = requests.get(url)
    r.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(r.content)

    print("Download complete.")
    return out_path


def get_boundary_names(mesh_path: str, do_print=True):
    """
    Read a mesh file with meshio and list all physical groups / tags.
    Returns a dict of cell_block_name → physical tag sets.
    """
    if do_print:
        print(f"Reading mesh: {mesh_path}")
    mesh = meshio.read(mesh_path)

    tags = {}

    if "gmsh:physical" in mesh.cell_data:
        for block, phys in zip(mesh.cells, mesh.cell_data["gmsh:physical"]):
            cell_type = block.type
            unique_tags = sorted(set(phys))
            tags[cell_type] = unique_tags

    if do_print:
        print("Found physical tags:")
        for cell_type, names in tags.items():
            print(f" - {cell_type}: {names}")

    return tags
