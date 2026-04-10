#!/bin/bash
SIZE_FACTOR=${1:-1}

# Build the standalone and monolithic meshes (they Merge sub-files internally)
for geo in channel_standalone.geo inflow_standalone.geo monolithic.geo channel_2d.geo; do
    base="${geo%.geo}"
    echo "Generating mesh: $base (size_factor=$SIZE_FACTOR)"
    if [[ "$base" == "channel_2d" ]]; then
        gmsh -2 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    else
        gmsh -3 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    fi
done
