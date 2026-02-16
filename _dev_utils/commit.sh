#!/usr/bin/env bash
# commit.sh

# Robust commit script: git add, commit with WIP message, push to main branch

set -euo pipefail

# Check for commit message argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 \"commit message\""
    exit 1
fi

COMMIT_MSG="$1"

# Stage all changes
git add .

# Check if there is anything to commit
if git diff-index --quiet HEAD --; then
    echo "No changes to commit."
    exit 0
fi

# Commit with message
git commit -m ":construction: work in progress : $COMMIT_MSG"

# Push to upstream branch
git push
