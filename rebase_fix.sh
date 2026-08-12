#!/bin/bash
# Simple approach: Use git rebase to fix the old commit

cd /home/a/Documents/vscode/git/vscode

echo "================================"
echo "Checking commit history..."
echo "================================"

# Get the number of commits since the problem commit
# This is a rough estimate - adjust if needed
COMMITS_BACK=$(git rev-list --all --count)
echo "Total commits: $COMMITS_BACK"

echo ""
echo "Attempting to use git rebase to fix commit 3b2460b..."
echo ""
echo "If you see an interactive editor, change 'pick' to 'edit' for commit 3b2460b"
echo "Then run:"
echo "  git rebase --continue"
echo ""

# Try to initiate interactive rebase
# Count how many commits back 3b2460b is
COMMITS_BACK=$(git rev-list 3b2460b..HEAD --count)
COMMITS_BACK=$((COMMITS_BACK + 1))

echo "Number of commits to go back: $COMMITS_BACK"

if [ $COMMITS_BACK -gt 0 ]; then
    git rebase -i HEAD~$COMMITS_BACK
else
    echo "Error: Could not find commit 3b2460b in history"
    exit 1
fi
