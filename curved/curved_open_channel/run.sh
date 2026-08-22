#!/bin/bash
SIZE_FACTOR=${1:-1}

for geo in *.geo; do
    base="${geo%.geo}"
    echo "Generating mesh: $base (size_factor=$SIZE_FACTOR)"
    if [[ "$base" == *3d* ]]; then
        gmsh -3 -bin "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    else
        gmsh -2 -bin "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    fi

    # Second export, gmsh 2.2 ASCII.
    #
    # WHY. The binary export above is gmsh 4.1, which writes the geometry as one
    # block PER ENTITY. This surface is built from 14 transfinite patches, and
    # zoomy_core's LSQMesh.from_msh reads only the FIRST block, so the published
    # 4.1 file loads a fragment of the bend and the solver runs on it without
    # complaining. Measured 2026-08-22 against the deployed catalog:
    #
    #     curved_curved_open_channel_mesh__coarse.msh   ->  14 cells
    #     curved_curved_open_channel_mesh.msh           -> 143 cells
    #     this msh2.2 export                            -> 710 cells
    #
    # msh2.2 has no entity blocks, so the whole surface arrives. Any GUI case
    # that fetches this bend from the mesh catalog needs the _v2 name.
    if [[ "$base" != *3d* ]]; then
        echo "Generating mesh: ${base}_v2 (gmsh 2.2 ASCII, flat -- LSQMesh reads all 14 patches)"
        gmsh -2 -format msh2 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}_v2.msh"
    fi
done
