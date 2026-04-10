#!/bin/bash
SIZE_FACTOR=${1:-1}

for geo in *.geo; do
    base="${geo%.geo}"
    echo "Generating mesh: $base (size_factor=$SIZE_FACTOR)"
    gmsh -3 "$geo" -setnumber size_factor "$SIZE_FACTOR" -o "${base}.msh"
done
