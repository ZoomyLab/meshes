#!/bin/bash
# Run mesh generation in all subdirectories
SIZE_FACTOR=${1:-1}
DIR="$(cd "$(dirname "$0")" && pwd)"

for sub in "$DIR"/*/; do
    if [ -f "$sub/run.sh" ]; then
        echo "=== $(basename "$sub") ==="
        (cd "$sub" && bash run.sh "$SIZE_FACTOR")
    fi
done
