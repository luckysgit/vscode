#!/bin/bash
# Quick Setup Script - Run this after fixing credentials

echo "🔒 Security Remediation Steps"
echo "=============================="
echo ""
echo "STEP 1: Install python-dotenv"
pip install python-dotenv

echo ""
echo "STEP 2: Create .env file from template"
cp .env.example .env
echo "✓ Created .env file"

echo ""
echo "STEP 3: Edit .env file with your NEW credentials"
echo "⚠️  IMPORTANT: Use NEW API keys (rotate the old ones from your provider accounts)"
echo ""
echo "Edit .env and replace placeholder values with:"
echo "  - New Groq API key from https://console.groq.com"
echo "  - New OpenRouter API key from https://openrouter.ai"
echo "  - New Google API key from https://cloud.google.com"
echo "  - New Neo4j credentials from your Aura instance"
echo ""

read -p "Press ENTER when you've updated .env with new credentials..."

echo ""
echo "STEP 4: Verify environment variables load correctly"
python3 << 'EOF'
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = {
    "GROQ_API_KEY": "Groq API",
    "OPENROUTER_API_KEY": "OpenRouter API",
    "GOOGLE_API_KEY": "Google API",
    "NEO4J_URI": "Neo4j URI",
    "NEO4J_USERNAME": "Neo4j Username",
    "NEO4J_PASSWORD": "Neo4j Password"
}

print("\n📋 Environment Variables Status:")
print("=" * 50)

all_good = True
for var, desc in required_vars.items():
    value = os.getenv(var)
    if value:
        print(f"✓ {desc:20} configured ({len(value)} chars)")
    else:
        print(f"✗ {desc:20} MISSING")
        all_good = False

if all_good:
    print("\n✅ All environment variables configured correctly!")
else:
    print("\n❌ Some variables are missing. Please update .env file.")
    exit(1)
EOF

echo ""
echo "STEP 5: Add all changes and commit"
git add .
git add -u
echo "Git status before commit:"
git status

echo ""
echo "STEP 6: Commit changes"
git commit -m "Remove hardcoded credentials and use environment variables

- Replace all hardcoded API keys with os.getenv()
- Update all notebooks to load from .env
- Add .env.example as reference template
- Update .gitignore to exclude .env files

Security: All exposed credentials must be rotated immediately
with their respective providers."

echo ""
echo "STEP 7: Push to GitHub"
git push

echo ""
echo "✅ All done! Your repository is now secure."
echo ""
echo "📝 Remember:"
echo "  - Never commit .env file"
echo "  - Keep .env.example as a reference"
echo "  - Rotate compromised API keys"
echo "  - For new team members: give them .env.example only"
