#!/bin/zsh
# concat.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/code.txt"

EXTS=("py" "html" "css" "js" "md" "json")

rm -f "$OUTPUT_FILE"

printf "Generated %s\n\n" "$(date '+%Y-%m-%d %H:%M:%S')" \
    >> "$OUTPUT_FILE"

cd "$PROJECT_ROOT" || exit 1

find . \
    -type d \( \
        -name ".git" -o \
        -name "__pycache__" -o \
        -name "_dev_utils" -o \
        -name "env" \
    \) -prune -o \
    -type f \( \
        -name "*.py" -o \
        -name "*.html" -o \
        -name "*.css" -o \
        -name "*.js" -o \
        -name "*.md" \
    \) -print \
| sort \
| while IFS= read -r f; do
    {
        printf "%s\n" "==============================================================================="
        printf "    %s\n" "$f"
        printf "%s\n" "==============================================================================="
        cat "$f"
        printf "\n\n"
    } >> "$OUTPUT_FILE"
done

echo "Concaténation terminée → $OUTPUT_FILE généré"
