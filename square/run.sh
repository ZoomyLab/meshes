#!/bin/bash
SIZE_FACTOR=${1:-1}

for geo in *.geo; do
    base="${geo%.geo}"
    echo "Generating mesh: $base (size_factor=$SIZE_FACTOR)"
    if [[ "$base" == *3d* ]]; then
        gmsh -3 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    else
        gmsh -2 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
    fi
done
