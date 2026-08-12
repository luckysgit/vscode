# Environment Setup Guide

## Overview
This project uses environment variables to manage sensitive credentials like API keys and database passwords. **Never commit these values to Git.**

## Setup Instructions

### 1. Install python-dotenv
```bash
pip install python-dotenv
```

### 2. Create a `.env` file
Copy the `.env.example` file and fill in your actual credentials:

```bash
cp .env.example .env
```

### 3. Edit `.env` with your credentials
Open `.env` and replace the placeholder values with your actual credentials:

```env
# API Keys
GROQ_API_KEY=your_actual_groq_api_key
OPENROUTER_API_KEY=your_actual_openrouter_api_key
GOOGLE_API_KEY=your_actual_google_api_key

# Neo4j Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=your_username
NEO4J_PASSWORD=your_actual_password
NEO4J_DATABASE=your_database_name
AURA_INSTANCEID=your_instance_id
AURA_INSTANCENAME=Your Instance Name
```

### 4. Security Best Practices

✅ **DO:**
- Store `.env` locally only
- Add `.env` to `.gitignore` (already done)
- Rotate compromised credentials immediately
- Use `.env.example` as a reference for required variables

❌ **DON'T:**
- Commit `.env` to Git
- Share `.env` files via email or messaging
- Log credentials in code or console output
- Use credentials from old commits

### 5. How Notebooks Load Environment Variables

All notebooks now follow this pattern:

```python
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access credentials safely
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY is not configured")
```

### 6. Git Configuration

The following are already configured in `.gitignore`:
```
.env           # Don't track environment files
.env.*         # Don't track any variant env files
!.env.example  # But DO track the example file
```

## Security Incident Summary

### What Happened
Real API keys and database credentials were committed to Git:
- **Groq API Keys** (2 unique keys exposed)
- **OpenRouter API Key** (1 key exposed)
- **Neo4j Credentials** (URI, username, password exposed)
- **Google API Key** (1 key exposed)

### Files That Were Fixed
1. ✅ Graph_Database/Gen_ai/neo4j_gen_ai.ipynb
2. ✅ Graph_Database/Agentic _ai/agentic_neo4j.ipynb
3. ✅ Graph_Database/Agentic _ai/self_correcting_agent/notebooks/01_graphrag_benchmark.ipynb
4. ✅ Graph_Database/Agentic _ai/self_correcting_agent/notebooks/02_agentic_graphrag_pipeline.ipynb
5. ✅ Graph_Database/Gen_ai/neo4j_ragai (2).ipynb

### What Was Fixed
- ✅ Replaced all hardcoded API keys with `os.getenv()` calls
- ✅ Replaced all hardcoded credentials with environment variable references
- ✅ Added `.env.example` file as a reference
- ✅ Updated `.gitignore` to prevent future commits of secrets

### Important: Rotate Your Credentials

Since the API keys were committed to Git history, **even though GitHub blocked the push**, you should:

1. **Revoke/Rotate the exposed keys:**
   - Log into Groq console and delete the exposed API keys
   - Log into OpenRouter console and delete the exposed API keys
   - Log into Google Cloud Console and delete/regenerate the API keys
   - Rotate your Neo4j Aura instance credentials

2. **Generate new credentials** and add them to `.env`

## Testing Your Setup

Run this in Python to verify environment variables load correctly:

```python
import os
from dotenv import load_dotenv

load_dotenv()

required_vars = [
    "GROQ_API_KEY",
    "OPENROUTER_API_KEY", 
    "GOOGLE_API_KEY",
    "NEO4J_URI",
    "NEO4J_USERNAME",
    "NEO4J_PASSWORD"
]

for var in required_vars:
    value = os.getenv(var)
    status = "✓" if value else "✗"
    print(f"{status} {var}: {len(value)} characters" if value else f"{status} {var}: NOT SET")
```

## Next Steps

1. **Rotate all credentials** with your service providers
2. **Create `.env` file** with your new credentials
3. **Run test** to verify everything loads correctly
4. **Commit the changes** once verified:
   ```bash
   git add .
   git commit -m "Remove hardcoded credentials and use environment variables"
   git push
   ```

## Support

If you have questions about environment variable setup, refer to the Python `dotenv` documentation:
https://github.com/theskumar/python-dotenv
