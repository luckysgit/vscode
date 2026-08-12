#!/usr/bin/env python3
"""
Script to clean git history of secrets using git-filter-repo
This removes the problematic notebook files from the old commit
"""

import subprocess
import sys
import os

os.chdir('/home/a/Documents/vscode/git/vscode')

def run_cmd(cmd, description=""):
    """Run a shell command and return output"""
    print(f"\n{'='*60}")
    if description:
        print(f"📋 {description}")
    print(f"🔧 Running: {cmd}")
    print('='*60)
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("Output:")
        print(result.stdout)
    if result.stderr:
        print("Errors/Warnings:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"\n❌ Command failed with code {result.returncode}")
        return False
    
    print(f"✅ Command succeeded")
    return True

print("\n" + "="*60)
print("🔒 GIT HISTORY CLEANING SCRIPT")
print("="*60)

# Step 1: Show current status
run_cmd("git status", "Current git status")
run_cmd("git log --oneline -5", "Recent commits")

# Step 2: Show what secrets are where
print("\n" + "="*60)
print("📍 CHECKING FOR REMAINING SECRETS IN HISTORY")
print("="*60)

secrets_patterns = [
    ('gsk_', 'Groq API Key'),
    ('sk-or-v1-', 'OpenRouter API Key'),
    ('AIza', 'Google API Key'),
]

for pattern, name in secrets_patterns:
    print(f"\n🔍 Searching for {name} ({pattern})...")
    result = subprocess.run(
        f"git grep -n '{pattern}' $(git rev-list --all 2>/dev/null || echo '')",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print(f"⚠️  Found {name}:")
        for line in result.stdout.split('\n')[:10]:  # Show first 10
            if line:
                print(f"   {line}")
    else:
        print(f"✅ No {name} found in history")

print("\n" + "="*60)
print("📌 NEXT STEPS TO RESOLVE")
print("="*60)
print("""
GitHub Push Protection detected secrets in OLD COMMIT (3b2460b).

OPTION 1: Force history rewrite (Recommended for this repo)
  1. Install git-filter-repo:
     pip install git-filter-repo

  2. Create a script to clean the specific notebooks:
     git filter-repo --path Graph_Database/Gen_ai/neo4j_gen_ai.ipynb \\
                     --path Graph_Database/Agentic _ai/agentic_neo4j.ipynb \\
                     --path Graph_Database/Gen_ai/neo4j_ragai\ \\(2\\).ipynb \\
                     --path Graph_Database/Agentic\ _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb \\
                     --path Graph_Database/Agentic\ _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb \\
                     --prune-empty

  3. Force push to GitHub:
     git push --force-with-lease

OPTION 2: Reset and cherry-pick (Simpler for small repos)
  1. Save your current fixes to a patch
  2. Reset to a commit before 3b2460b
  3. Re-apply your changes
  4. Push

OPTION 3: Use GitHub UI
  - Click the link in the error to use GitHub's secret blocking interface
  - Unresolve the blocked secret to allow push
  - Then rotate the credentials

⚠️  WARNING: Only do force-push if this is a small team repository!
""")
