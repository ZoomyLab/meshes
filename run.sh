#!/bin/bash
# Generate all meshes in the repository.
#
# Usage:
#   ./run.sh              # default size factor
#   ./run.sh 0.5          # finer meshes
#   ./run.sh 2            # coarser meshes
#
# Cascades into each subdirectory that has a run.sh.

SIZE_FACTOR=${1:-1}
DIR="$(cd "$(dirname "$0")" && pwd)"
FAILED=0

for sub in "$DIR"/*/; do
    name=$(basename "$sub")
    [ "$name" = "old" ] && continue
    if [ -f "$sub/run.sh" ]; then
        echo ""
        echo "========================================"
        echo " $name"
        echo "========================================"
        (cd "$sub" && bash run.sh "$SIZE_FACTOR") || FAILED=$((FAILED + 1))
    fi
done

echo ""
if [ $FAILED -eq 0 ]; then
    echo "All meshes generated successfully."
else
    echo "$FAILED directory(ies) had errors."
    exit 1
fi
