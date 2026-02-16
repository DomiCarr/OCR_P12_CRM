#!/bin/zsh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/directories.txt"

rm -f "$OUTPUT_FILE"

echo "Generated $(date '+%Y-%m-%d %H:%M:%S')" >> "$OUTPUT_FILE"
echo "\nListing all files and folders (excluding env/, __pycache__, .git/, and _dev_utils/):\n" >> "$OUTPUT_FILE"

print_tree() {
    local dir="$1"
    local indent="$2"

    for f in "$dir"/*(ND); do
        [[ ! -e "$f" ]] && continue
        local base_f="$(basename "$f")"

        # Exclusions
        [[ "$base_f" == "env" ]] && continue
        [[ "$base_f" == ".venv" ]] && continue
        [[ "$base_f" == "__pycache__" ]] && continue
        [[ "$base_f" == ".git" ]] && continue
        [[ "$base_f" == "_dev_utils" ]] && continue

        echo "${indent}${f#$PROJECT_ROOT/}" >> "$OUTPUT_FILE"
        [[ -d "$f" ]] && print_tree "$f" "${indent}    "
    done
}

print_tree "$PROJECT_ROOT" ""