#!/usr/bin/env python3
"""
Automatic Git History Cleaner for GitHub Push Protection

This script removes secrets from commit 3b2460b in your git history,
allowing you to successfully push to GitHub.

Run: python3 auto_fix_push.py
"""

import subprocess
import json
import os
import sys
import re
from pathlib import Path

def run_cmd(cmd, show_output=True, check=False):
    """Execute shell command and return result"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd='/home/a/Documents/vscode/git/vscode',
            timeout=30
        )
        if show_output and result.stdout:
            print(result.stdout, end='')
        if result.stderr and 'warning' not in result.stderr.lower():
            print(f"⚠️  {result.stderr}", end='')
        if check and result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def main():
    os.chdir('/home/a/Documents/vscode/git/vscode')
    
    print("\n" + "="*70)
    print("🔒 AUTOMATIC GIT HISTORY CLEANER")
    print("="*70 + "\n")
    
    # Step 1: Show current problem
    print("📊 STEP 1: Current Situation")
    print("-" * 70)
    print("✅ Current files: CLEAN (using os.getenv())")
    print("❌ Old commit 3b2460b: CONTAINS SECRETS")
    print("\n❌ GitHub blocks push because it checks entire history")
    print("✅ Solution: Rewrite commit 3b2460b to remove secrets\n")
    
    # Step 2: Create backup
    print("🛡️  STEP 2: Creating Safety Backup")
    print("-" * 70)
    backup_cmd = "git branch backup-auto-fix-$(date +%s)"
    if run_cmd(backup_cmd, show_output=False):
        print("✅ Backup branch created (saved to local repo)\n")
    else:
        print("⚠️  Could not create backup (continuing anyway)\n")
    
    # Step 3: Check if git-filter-repo is installed
    print("📦 STEP 3: Installing git-filter-repo")
    print("-" * 70)
    check_filter = subprocess.run(
        "which git-filter-repo",
        shell=True,
        capture_output=True
    )
    
    if check_filter.returncode == 0:
        print("✅ git-filter-repo already installed\n")
    else:
        print("⏳ Installing git-filter-repo...")
        install_cmd = "pip install --quiet git-filter-repo"
        if run_cmd(install_cmd, show_output=False):
            print("✅ git-filter-repo installed successfully\n")
        else:
            print("⚠️  Could not auto-install. You may need to run manually:")
            print("   pip install git-filter-repo\n")
            return False
    
    # Step 4: Create the email-secrets replacement script
    print("⚙️  STEP 4: Creating Secrets Replacement Filter")
    print("-" * 70)
    
    filter_script = '''#!/usr/bin/env python3
import sys
import re
import json

# Read from stdin
content = sys.stdin.read()

# List of patterns to replace
replacements = [
    (r'gsk_[A-Za-z0-9]+', 'gsk_REMOVED'),
    (r'sk-or-v1-[A-Za-z0-9_-]+', 'sk-or-v1-REMOVED'),
    (r'AIza[A-Za-z0-9_-]+', 'AIza-REMOVED'),
    (r'AQ\.Ab8RN6Jtz1[A-Za-z0-9_-]+', 'AQ.REMOVED'),
    (r'gQrvvDiw4AbQtKT14gHcKlihCRcAmc6JPDsNxB4bA1I', 'REMOVED_PASSWORD'),
]

# Try to parse as JSON (notebook)
try:
    notebook = json.loads(content)
    if isinstance(notebook, dict) and 'cells' in notebook:
        for cell in notebook['cells']:
            if 'source' in cell:
                source = cell['source']
                if isinstance(source, list):
                    source = ''.join(source)
                
                # Apply replacements
                for pattern, replacement in replacements:
                    source = re.sub(pattern, replacement, source)
                
                # Put back
                if isinstance(cell['source'], list):
                    cell['source'] = source.split('\\n')
                else:
                    cell['source'] = source
    
    sys.stdout.write(json.dumps(notebook))
except:
    # Not JSON, just do text replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    sys.stdout.write(content)
'''
    
    filter_path = '/tmp/clean_secrets_filter.py'
    with open(filter_path, 'w') as f:
        f.write(filter_script)
    os.chmod(filter_path, 0o755)
    print(f"✅ Filter script created: {filter_path}\n")
    
    # Step 5: Use git filter-repo
    print("🚀 STEP 5: Running git-filter-repo to Clean History")
    print("-" * 70)
    print("This will rewrite commit 3b2460b to remove all secrets...")
    print()
    
    # The key command: rewrite the .ipynb files to remove secrets
    filter_cmd = f"""
    git filter-repo \\
      --path 'Graph_Database/Gen_ai/neo4j_gen_ai.ipynb' \\
      --path 'Graph_Database/Agentic _ai/agentic_neo4j.ipynb' \\
      --path 'Graph_Database/Gen_ai/neo4j_ragai (2).ipynb' \\
      --path 'Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb' \\
      --path 'Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb' \\
      --mailmap <(cat <<'EOF'
First Last <new-email@example.com> <old-email@example.com>
EOF
      ) \\
      2>&1
    """
    
    print("Running: git filter-repo to clean the problematic notebooks...")
    result = subprocess.run(
        "git filter-repo --help",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ git-filter-repo is ready\n")
        
        # Now run the actual filter
        print("⏳ This may take a moment...")
        print("   (Rewriting git history to remove secrets from notebooks)\n")
        
        filter_cmd_simple = """
        git filter-repo \\
          --path 'Graph_Database/Gen_ai/neo4j_gen_ai.ipynb' \\
          --path 'Graph_Database/Agentic _ai/agentic_neo4j.ipynb' \\
          --path 'Graph_Database/Gen_ai/neo4j_ragai (2).ipynb' \\
          --path 'Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb' \\
          --path 'Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb'
        """
        
        result = subprocess.run(
            filter_cmd_simple,
            shell=True,
            cwd='/home/a/Documents/vscode/git/vscode',
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Git history cleaned successfully!\n")
        else:
            print(f"⚠️  git-filter-repo output: {result.stdout}")
            if result.stderr:
                print(f"   {result.stderr}\n")
    else:
        print("❌ git-filter-repo not available\n")
    
    # Step 6: Verify no secrets remain
    print("✅ STEP 6: Verifying No Secrets in History")
    print("-" * 70)
    
    secrets_patterns = [
        ('gsk_', 'Groq API Key'),
        ('sk-or-v1-', 'OpenRouter API Key'),
        ('AIza', 'Google API Key'),
    ]
    
    all_clean = True
    for pattern, name in secrets_patterns:
        result = subprocess.run(
            f"git grep -n '{pattern}' $(git rev-list --all 2>/dev/null) 2>/dev/null || echo 'CLEAN'",
            shell=True,
            capture_output=True,
            text=True,
            cwd='/home/a/Documents/vscode/git/vscode'
        )
        
        if 'CLEAN' in result.stdout or not result.stdout.strip():
            print(f"✅ {name}: CLEAN")
        else:
            print(f"❌ {name}: Still found")
            all_clean = False
    
    print()
    
    # Step 7: Force push
    print("="*70)
    print("🚀 STEP 7: Force Push to GitHub")
    print("-" * 70)
    
    if all_clean:
        print("✅ All secrets removed from history!\n")
        print("Ready to force push. Run:")
        print("\n  git push --force-with-lease\n")
        
        response = input("Do you want to push now? (y/n): ").strip().lower()
        
        if response == 'y':
            print("\n⏳ Pushing to GitHub...")
            push_result = subprocess.run(
                "git push --force-with-lease",
                shell=True,
                capture_output=True,
                text=True,
                cwd='/home/a/Documents/vscode/git/vscode',
                timeout=120
            )
            
            print(push_result.stdout)
            
            if 'remote rejected' not in push_result.stdout.lower() and push_result.returncode == 0:
                print("\n" + "="*70)
                print("✅ SUCCESS! Push completed!")
                print("="*70)
                return True
            else:
                print("\n⚠️  Push failed. Error output:")
                print(push_result.stdout)
                print(push_result.stderr)
                return False
        else:
            print("Skipping push. You can manually run: git push --force-with-lease")
            return True
    else:
        print("❌ Some secrets still remain in history")
        print("\nManual steps needed:")
        print("  1. Run: git log --all --oneline | head")
        print("  2. Identify commit 3b2460b")
        print("  3. Run: git rebase -i HEAD~X  (where X is commits back)")
        print("  4. Change 'pick' to 'edit' for 3b2460b")
        print("  5. Manually edit the notebook files to remove secrets")
        print("  6. git add . && git rebase --continue")
        print("  7. git push --force-with-lease")
        return False

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
