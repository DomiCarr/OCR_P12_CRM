#!/bin/zsh
# export_code.sh
# Generates a single review bundle file containing:
# 1) Project structure (directory tree)
# 2) Concatenation of all relevant source/config files
#
# Usage:
#   ./_dev_utils/export_code.sh
#
# Output:
#   ./_dev_utils/export_code.txt

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OUTPUT_FILE="$SCRIPT_DIR/export_code.txt"

# File extensions to include in the bundle
INCLUDE_EXTS=("py" "html" "css" "js" "md" "json" "yml" "yaml" "toml" "ini" "cfg" "txt" "sql" "sh")

# Directories to exclude from traversal
EXCLUDE_DIRS=(
  ".git"
  "__pycache__"
  "_dev_utils"
  "env"
  ".venv"
  ".pytest_cache"
  ".mypy_cache"
  ".ruff_cache"
  "node_modules"
  "dist"
  "build"
)

# Specific files to include even if they have no extension
SPECIAL_FILES=(
  ".gitignore"
  ".env.example"
  "Dockerfile"
  "docker-compose.yml"
  "docker-compose.yaml"
  "Makefile"
)

# -------------------------------
# NEW: ignore problematic/noisy files (minimal change)
# -------------------------------
EXCLUDE_FILE_NAMES=(
  ".DS_Store"
  ".coverage"
  "coverage.xml"
)

EXCLUDE_FILE_GLOBS=(
  "*.pyc"
  "*.pyo"
  "*.pyd"
  "*.log"
  "*.sqlite"
  "*.sqlite3"
  "*.db"
  "*.pem"
  "*.key"
  "*.p12"
)

rm -f "$OUTPUT_FILE"

now="$(date '+%Y-%m-%d %H:%M:%S')"

# ------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------

write_header() {
  {
    echo "================================================================================"
    echo "EXPORT STRUCTURE & CODE APP"
    echo "Generated: $now"
    echo "Project root: $PROJECT_ROOT"
    echo "================================================================================"
    echo
  } >> "$OUTPUT_FILE"
}

# Recursively prints the project tree with indentation
print_tree() {
  local dir="$1"
  local indent="$2"

  for f in "$dir"/*(ND); do
    [[ ! -e "$f" ]] && continue
    local base_f="$(basename "$f")"

    # Skip excluded directories
    for ex in "${EXCLUDE_DIRS[@]}"; do
      [[ "$base_f" == "$ex" ]] && continue 2
    done

    echo "${indent}${f#$PROJECT_ROOT/}" >> "$OUTPUT_FILE"
    [[ -d "$f" ]] && print_tree "$f" "${indent}    "
  done
}

write_tree_section() {
  {
    echo "SECTION 1 — PROJECT STRUCTURE"
    echo "--------------------------------------------------------------------------------"
    echo "Listing all files and folders (excluded: ${EXCLUDE_DIRS[*]})"
    echo
  } >> "$OUTPUT_FILE"

  print_tree "$PROJECT_ROOT" ""

  {
    echo
    echo "END SECTION 1"
    echo
  } >> "$OUTPUT_FILE"
}

# -------------------------------
# NEW: helpers to skip noisy/problematic files
# -------------------------------
is_excluded_filename() {
  local rel_path="$1"
  local base_name
  base_name="$(basename "$rel_path")"

  local n
  for n in "${EXCLUDE_FILE_NAMES[@]}"; do
    [[ "$base_name" == "$n" ]] && return 0
  done
  return 1
}

matches_excluded_glob() {
  local rel_path="$1"
  local g
  for g in "${EXCLUDE_FILE_GLOBS[@]}"; do
    [[ "$rel_path" == $~g ]] && return 0
  done
  return 1
}

write_concat_section() {
  {
    echo "SECTION 2 — CONCATENATED FILES"
    echo "--------------------------------------------------------------------------------"
    echo "Included extensions: ${INCLUDE_EXTS[*]}"
    echo "Included special files: ${SPECIAL_FILES[*]}"
    echo "Excluded directories: ${EXCLUDE_DIRS[*]}"
    echo "Excluded file names: ${EXCLUDE_FILE_NAMES[*]}"
    echo "Excluded file globs: ${EXCLUDE_FILE_GLOBS[*]}"
    echo
  } >> "$OUTPUT_FILE"

  cd "$PROJECT_ROOT" || exit 1

  # Build prune expression for excluded directories
  local prune_expr=""
  for d in "${EXCLUDE_DIRS[@]}"; do
    prune_expr="$prune_expr -name $d -o"
  done
  prune_expr="${prune_expr% -o}"

  # Build match expression for extensions
  local match_expr=""
  for ext in "${INCLUDE_EXTS[@]}"; do
    match_expr="$match_expr -name '*.$ext' -o"
  done

  # Add special files by exact name
  for sf in "${SPECIAL_FILES[@]}"; do
    match_expr="$match_expr -name '$sf' -o"
  done
  match_expr="${match_expr% -o}"

  # Execute find, sort results, and concatenate
  # shellcheck disable=SC2086
  eval "find . \
    -type d \\( $prune_expr \\) -prune -o \
    -type f \\( $match_expr \\) -print" \
  | sort \
  | while IFS= read -r f; do
      [[ -z "$f" ]] && continue

      # NEW: skip noisy/problematic files
      if is_excluded_filename "$f"; then
        continue
      fi
      if matches_excluded_glob "$f"; then
        continue
      fi

      {
        echo "==============================================================================="
        echo "FILE: $f"
        echo "------------------------------------------------------------------------------"

        # Add file metadata (size + last modification date)
        # macOS uses stat -f, Linux uses stat -c
        if stat -f "%z bytes | modified: %Sm" -t "%Y-%m-%d %H:%M:%S" "$f" >/dev/null 2>&1; then
          echo "META: $(stat -f "%z bytes | modified: %Sm" -t "%Y-%m-%d %H:%M:%S" "$f")"
        elif stat -c "%s bytes | modified: %y" "$f" >/dev/null 2>&1; then
          echo "META: $(stat -c "%s bytes | modified: %y" "$f")"
        fi

        echo "==============================================================================="
        echo

        # NEW: do not fail the whole script if a file is unreadable/binary
        if [[ ! -r "$f" ]]; then
          echo "***SKIPPED (not readable)***"
        else
          # cat can fail on some binary/odd files; do not abort due to set -e
          cat "$f" 2>/dev/null || echo "***SKIPPED (cat failed)***"
        fi

        echo
        echo
      } >> "$OUTPUT_FILE"
    done

  {
    echo "END SECTION 2"
    echo
  } >> "$OUTPUT_FILE"
}

write_footer() {
  {
    echo "================================================================================"
    echo "END OF REVIEW BUNDLE"
    echo "================================================================================"
  } >> "$OUTPUT_FILE"
}

# ------------------------------------------------------------
# Main Execution
# ------------------------------------------------------------

write_header
write_tree_section
write_concat_section
write_footer

echo "Export code generated → $OUTPUT_FILE"