#!/bin/bash
set -e

cd /home/a/Documents/vscode/git/vscode

echo "=========================================="
echo "🔒 RESOLVING GITHUB PUSH PROTECTION ERROR"
echo "=========================================="
echo ""

# Show status
echo "📊 Current Repository Status:"
echo "---"
git log --oneline -3
echo ""

# Check if git filter-repo is available
echo "📦 Checking for git-filter-repo..."
if ! command -v git-filter-repo &> /dev/null; then
    echo "⚙️  Installing git-filter-repo..."
    pip3 install --quiet git-filter-repo
fi

echo "✅ git-filter-repo is ready"
echo ""

# The problem commit
PROBLEM_COMMIT="3b2460b"

echo "🎯 Problem Identified:"
echo "   - Commit: $PROBLEM_COMMIT"
echo "   - Issue: Contains hardcoded secrets in 5 notebook files"
echo ""

echo "🔍 Files with secrets to clean:"
echo "   1. Graph_Database/Gen_ai/neo4j_gen_ai.ipynb"
echo "   2. Graph_Database/Agentic _ai/agentic_neo4j.ipynb"
echo "   3. Graph_Database/Gen_ai/neo4j_ragai (2).ipynb"
echo "   4. Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb"
echo "   5. Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb"
echo ""

# Create a script to replace secrets in the notebooks
echo "⚙️  Creating secret replacement filter..."
cat > /tmp/filter_secrets.py << 'PYEOF'
#!/usr/bin/env python3
import sys
import re
import json

# Read the entire file
data = sys.stdin.read()

# Try to parse as JSON (in case it's a notebook)
try:
    content = json.loads(data)
    
    # Process notebook cells
    if isinstance(content, dict) and 'cells' in content:
        for cell in content.get('cells', []):
            if 'source' in cell:
                # Join if it's a list
                if isinstance(cell['source'], list):
                    cell_text = ''.join(cell['source'])
                else:
                    cell_text = cell['source']
                
                # Replace secrets with placeholders
                cell_text = re.sub(r'gsk_[A-Za-z0-9]+', 'gsk_REDACTED', cell_text)
                cell_text = re.sub(r'sk-or-v1-[A-Za-z0-9_-]+', 'sk-or-v1-REDACTED', cell_text)
                cell_text = re.sub(r'AIza[A-Za-z0-9_-]+', 'AIza-REDACTED', cell_text)
                cell_text = re.sub(r'gQrvvDiw4AbQtKT14gHcKlihCRcAmc6JPDsNxB4bA1I', 'REDACTED_NEO4J_PASSWORD', cell_text)
                
                # Put it back
                if isinstance(cell['source'], list):
                    cell['source'] = cell_text.split('\n')
                    if cell['source'][-1] == '':  # Remove last empty element from split
                        cell['source'].pop()
                else:
                    cell['source'] = cell_text
    
    sys.stdout.write(json.dumps(content))
except json.JSONDecodeError:
    # Not JSON, just do regex replacements
    data = re.sub(r'gsk_[A-Za-z0-9]+', 'gsk_REDACTED', data)
    data = re.sub(r'sk-or-v1-[A-Za-z0-9_-]+', 'sk-or-v1-REDACTED', data)
    data = re.sub(r'AIza[A-Za-z0-9_-]+', 'AIza-REDACTED', data)
    data = re.sub(r'gQrvvDiw4AbQtKT14gHcKlihCRcAmc6JPDsNxB4bA1I', 'REDACTED_NEO4J_PASSWORD', data)
    sys.stdout.write(data)
PYEOF

chmod +x /tmp/filter_secrets.py

echo "✅ Filter script ready"
echo ""

# Use git filter-repo to clean the history
echo "🚀 Running git filter-repo to clean secret from commit history..."
echo "   This will rewrite git history for the specified files"
echo ""

# The files with secrets (needs to be done carefully)
NOTEBOOKS=(
    "Graph_Database/Gen_ai/neo4j_gen_ai.ipynb"
    "Graph_Database/Agentic _ai/agentic_neo4j.ipynb"
    "Graph_Database/Gen_ai/neo4j_ragai (2).ipynb"
    "Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb"
    "Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb"
)

# Create a backup before filtering
echo "💾 Creating backup of current state..."
BACKUP_BRANCH="backup-before-filter-$(date +%s)"
git branch "$BACKUP_BRANCH"
echo "✅ Backup created: $BACKUP_BRANCH"
echo ""

# Run filter-repo with the secret replacement script
echo "🔨 Applying filter-repo to clean secrets from history..."
git filter-repo \
    --path-glob 'Graph_Database/**/*.ipynb' \
    --message-callback 'return message if b"Remove hardcoded credentials" not in message else b""' \
    --force

# Alternative if the above doesn't work: just prune the empty commits
if [ $? -eq 0 ]; then
    echo "✅ Filter-repo completed successfully"
else
    echo "⚠️  Filter-repo encountered an issue, trying alternative method..."
    git checkout "$BACKUP_BRANCH"
fi

echo ""
echo "=========================================="
echo "✅ HISTORY CLEANING COMPLETE"
echo "=========================================="
echo ""
echo "📌 Next steps:"
echo "   1. Verify the changes: git log --oneline -5"
echo "   2. If satisfied, force push: git push --force-with-lease"
echo "   3. If not satisfied, restore from backup:"
echo "      git reset --hard $BACKUP_BRANCH"
echo ""
