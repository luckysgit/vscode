#!/usr/bin/env python3
"""
Interactive script to resolve GitHub Push Protection - Secret Detection in History

This script will:
1. Show your current commit history
2. Help you identify which commit contains the secrets
3. Guide you through fixing it
4. Prepare for force push
"""

import subprocess
import sys
import os
import re

def run_git(cmd, show_output=True):
    """Run a git command and return output"""
    try:
        result = subprocess.run(
            ['git'] + cmd.split(),
            cwd='/home/a/Documents/vscode/git/vscode',
            capture_output=True,
            text=True,
            timeout=10
        )
        if show_output and result.stdout:
            print(result.stdout)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        print(f"❌ Error running git: {e}")
        return False, "", str(e)

def main():
    os.chdir('/home/a/Documents/vscode/git/vscode')
    
    print("\n" + "="*70)
    print("🔒 GITHUB PUSH PROTECTION RESOLUTION")
    print("="*70 + "\n")
    
    # Step 1: Show current history
    print("📊 STEP 1: Analyzing your git history...")
    print("-" * 70)
    success, output, _ = run_git('log --oneline -15')
    if not success:
        print("❌ Failed to read git history")
        return False
    
    print("Current commits (most recent first):")
    print(output)
    
    # Step 2: Show the problem
    print("\n" + "="*70)
    print("🎯 STEP 2: Problem Identification")
    print("-" * 70)
    print("""
GitHub Push Protection detected:
- Secrets in commit: 3b2460b
- Issue: Old commit contains hardcoded API keys and Neo4j credentials
- Files affected:
  1. Graph_Database/Gen_ai/neo4j_gen_ai.ipynb
  2. Graph_Database/Agentic _ai/agentic_neo4j.ipynb
  3. Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb
  4. Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb
  5. Graph_Database/Gen_ai/neo4j_ragai (2).ipynb

Solution: Rewrite the old commit to remove secrets, then force-push.
""")
    
    # Step 3: Create backup
    print("="*70)
    print("🛡️  STEP 3: Creating Safety Backup")
    print("-" * 70)
    import time
    backup_name = f"backup-{int(time.time())}"
    success, _, _ = run_git(f'branch {backup_name}', show_output=False)
    if success:
        print(f"✅ Backup branch created: {backup_name}")
        print(f"   If anything goes wrong, you can restore with:")
        print(f"   git reset --hard {backup_name}")
    else:
        print("⚠️  Could not create backup (continuing anyway)")
    
    # Step 4: Count commits back to 3b2460b
    print("\n" + "="*70)
    print("📍 STEP 4: Finding the Problematic Commit")
    print("-" * 70)
    
    success, output, _ = run_git('log --all --pretty=format:%h')
    if success:
        commits = output.strip().split('\n')
        if any('3b2460b' in c or c.startswith('3b2460b') for c in commits):
            # Find position
            for i, c in enumerate(commits):
                if '3b2460b' in c or c.startswith('3b2460b'):
                    print(f"✅ Found commit 3b2460b at position {i} in history")
                    print(f"   Need to go back {i+1} commits")
                    commits_back = i + 1
                    break
        else:
            print("⚠️  Could not find commit 3b2460b in current branch")
            print("   It may be in a different branch or history")
            commits_back = None
    else:
        commits_back = None
    
    # Step 5: Provide instructions
    print("\n" + "="*70)
    print("🚀 STEP 5: Resolution - Choose Your Method")
    print("="*70 + "\n")
    
    print("""
METHOD 1: Use git-filter-repo (Recommended - Most Clean)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Install tool:
   pip install git-filter-repo

2. Create a Python script to replace secrets in files (see fix_history.sh)

3. Run filter-repo to clean the history

METHOD 2: Use git rebase -i (Interactive - More Control)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
    
    if commits_back:
        print(f"1. Start interactive rebase (go back {commits_back} commits):")
        print(f"\n   git rebase -i HEAD~{commits_back}\n")
    else:
        print(f"1. Start interactive rebase:")
        print(f"\n   git rebase -i HEAD~10\n")
    
    print("""
2. In the editor, find commit 3b2460b and change:
   FROM: pick 3b2460b ...
   TO:   edit 3b2460b ...

3. Save and exit (Ctrl+O, Enter, Ctrl+X if using nano)

4. Git will stop at that commit. Now you can:
   - Check which files have secrets: git status
   - The notebook files are already cleaned from our earlier edits
   - Just verify they're clean and continue:

5. Continue rebase:
   git rebase --continue

6. Force push (this will overwrite the remote):
   git push --force-with-lease


METHOD 3: Reset and Rebuild (Nuclear Option - Fastest)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Only use if the commit history is not important!

1. Find a good commit before 3b2460b:
   git log --oneline | grep -B 10 "3b2460b" | tail -1

2. Reset to that commit:
   git reset --hard <commit-hash>

3. Re-apply fixes from current branch:
   git checkout HEAD@{1} -- .env.example SETUP_ENV.md setup-secure.sh
   git add Graph_Database/**/*.ipynb  # These are already fixed

4. Commit:
   git commit -m "Remove hardcoded credentials and use environment variables"

5. Force push:
   git push --force-with-lease

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ AFTER FIXING: Verify No Secrets in History
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run this to verify secrets are gone:

   git grep -n 'gsk_' $(git rev-list --all)
   git grep -n 'sk-or-v1-' $(git rev-list --all)
   git grep -n 'AIza' $(git rev-list --all)

If nothing is returned, secrets are fully removed!

Then try push again:
   git push --force-with-lease

✅ SUCCESS: GitHub will allow the push!
""")
    
    print("\n" + "="*70)
    print("📚 IMPORTANT REMINDERS")
    print("="*70)
    print("""
1. ✅ Create .env with NEW rotated credentials (from your providers)
2. ✅ Verify .env is NOT committed (should be in .gitignore)
3. ✅ Run notebooks with: load_dotenv() and os.getenv('VARIABLE_NAME')
4. ✅ NEVER commit .env file to Git
5. ✅ Share .env.example as reference template only
6. ✅ Rotate ALL exposed credentials at their respective providers immediately
""")

if __name__ == '__main__':
    main()
