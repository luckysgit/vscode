#!/bin/bash
set -e

echo "=== Step 1: Installing dependencies ==="
sudo apt update
sudo apt install -y postgresql postgresql-contrib redis-server nodejs npm python3

echo "=== Step 2: Checking Node version ==="
node --version || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs)

echo "=== Step 3: Starting services ==="
sudo systemctl start postgresql || sudo service postgresql start || echo "Trying to find postgresql service..."
sudo systemctl start redis-server || sudo service redis-server start || sudo systemctl start redis || sudo service redis start

echo "=== Step 4: Creating database ==="
# Try different ways to run psql as postgres user
sudo -u postgres psql -c "CREATE USER codebattle WITH PASSWORD 'codebattle';" 2>/dev/null || sudo su - postgres -c "psql -c \"CREATE USER codebattle WITH PASSWORD 'codebattle';\""
sudo -u postgres psql -c "CREATE DATABASE codebattle OWNER codebattle;" 2>/dev/null || sudo su - postgres -c "psql -c \"CREATE DATABASE codebattle OWNER codebattle;\""
sudo -u postgres psql -d codebattle -f database/schema.sql 2>/dev/null || sudo su - postgres -c "psql -d codebattle -f $(pwd)/database/schema.sql"
sudo -u postgres psql -d codebattle -f database/seed.sql 2>/dev/null || sudo su - postgres -c "psql -d codebattle -f $(pwd)/database/seed.sql"

echo "=== Step 5: Installing backend ==="
cd backend
cp .env.local .env 2>/dev/null || echo "NODE_ENV=development\nPORT=3001\nDATABASE_URL=postgresql://codebattle:codebattle@localhost:5432/codebattle\nREDIS_URL=redis://localhost:6379\nJUDGE0_URL=\nJUDGE0_API_KEY=" > .env
npm install

echo "=== Step 6: Installing frontend ==="
cd ../frontend
npm install

echo ""
echo "=========================================="
echo "SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "Now run these in SEPARATE terminals:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd ~/Documents/vscode/git/vscode/codebattle/codebattle-mvp/backend"
echo "  node src/server-local.js"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd ~/Documents/vscode/git/vscode/codebattle/codebattle-mvp/frontend"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
echo "=========================================="
