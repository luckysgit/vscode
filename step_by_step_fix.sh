#!/bin/bash

# GITHUB PUSH PROTECTION - STEP BY STEP FIX
# Run this script step by step in your terminal

cd ~/Documents/vscode/git/vscode

echo "=========================================="
echo "🔒 RESOLVING GITHUB PUSH PROTECTION"
echo "=========================================="
echo ""

# STEP 1: Show current status
echo "📊 STEP 1: Current Git Status"
echo "---"
git log --oneline -10
echo ""

# STEP 2: Explain the problem
echo "⚠️  STEP 2: Understanding the Problem"
echo "---"
echo "Commit 3b2460b contains SECRETS in old notebook files"
echo "Your new commit has FIXES but GitHub still rejects push"
echo "Why? Because Git checks ENTIRE history for secrets"
echo ""

# STEP 3: Create backup
echo "🛡️  STEP 3: Creating Backup (Safety First!)"
echo "---"
BACKUP_BRANCH="backup-$(date +%s)"
git branch "$BACKUP_BRANCH"
echo "✅ Backup created: $BACKUP_BRANCH"
echo "If you mess up: git reset --hard $BACKUP_BRANCH"
echo ""

# STEP 4: Install git-filter-repo
echo "📦 STEP 4: Installing git-filter-repo"
echo "---"
if command -v git-filter-repo &> /dev/null; then
    echo "✅ git-filter-repo already installed"
else
    echo "⏳ Installing git-filter-repo..."
    pip install git-filter-repo
    echo "✅ Installation complete"
fi
echo ""

# STEP 5: Count commits back
echo "📍 STEP 5: Finding commit 3b2460b"
echo "---"
COMMITS_BACK=$(git rev-list --all --pretty=format: | grep -n "^" | grep "3b2460b" | cut -d: -f1 | head -1)
if [ -z "$COMMITS_BACK" ]; then
    # Alternative method
    COMMITS_BACK=$(git log --all --oneline | grep -n "3b2460b" | cut -d: -f1)
fi

if [ -n "$COMMITS_BACK" ]; then
    echo "Found 3b2460b at position $COMMITS_BACK"
else
    echo "Position unknown - will use 10 commits back as default"
    COMMITS_BACK=10
fi
echo ""

# STEP 6: Interactive Rebase Instructions
echo "🔨 STEP 6: Start Interactive Rebase"
echo "---"
echo "Run this command:"
echo "  git rebase -i HEAD~$COMMITS_BACK"
echo ""
echo "When the editor opens:"
echo "1. Find the line with commit 3b2460b"
echo "2. Change 'pick' to 'edit' at the START of that line"
echo "3. Save: Ctrl+O, Enter, Ctrl+X (nano)"
echo "   OR    :wq (vim)"
echo ""
echo "Then when Git stops, verify the files are clean:"
echo "  grep 'gsk_' Graph_Database/**/*.ipynb"
echo "  # Should show nothing"
echo ""
echo "Then continue rebase:"
echo "  git rebase --continue"
echo ""

# STEP 7: Force push
echo "🚀 STEP 7: Force Push"
echo "---"
echo "After rebase completes, verify no secrets remain:"
echo "  git grep -n 'gsk_' \$(git rev-list --all) || echo '✅ No Groq keys found'"
echo ""
echo "Then force push:"
echo "  git push --force-with-lease"
echo ""

echo "=========================================="
echo "✅ GOOD LUCK!"
echo "=========================================="
echo ""
echo "Questions? See: GITHUB_PUSH_PROTECTION_FIX.md"
echo ""
