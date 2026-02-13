# Quick Reference - Agentic RAG API

Fast reference for common operations and commands.

---

## 🚀 Quick Start

### Local Development
```bash
# Setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Set OPENAI_API_KEY

# Run
python main.py
```

### Docker Production
```bash
# Setup
cp .env.production .env
# Edit .env: Set OPENAI_API_KEY

# Deploy
docker-compose up -d

# Monitor
docker-compose logs -f
```

---

## 🐳 Docker Commands

### Basic Operations
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs (all services)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f agentic-rag-api

# Restart service
docker-compose restart agentic-rag-api

# Rebuild after code changes
docker-compose up -d --build

# Stop and remove everything
docker-compose down -v
```

### Container Management
```bash
# List running containers
docker-compose ps

# Execute command in container
docker-compose exec agentic-rag-api bash

# Run Python script in container
docker-compose exec agentic-rag-api python db/init_databases.py

# View resource usage
docker stats agentic-rag-api

# Copy files to/from container
docker cp local-file.txt agentic-rag-api:/app/
docker cp agentic-rag-api:/app/logs/app.log ./
```

### Troubleshooting
```bash
# View last 100 log lines
docker-compose logs --tail=100 agentic-rag-api

# Follow logs from specific time
docker-compose logs -f --since 30m agentic-rag-api

# Inspect container
docker inspect agentic-rag-api

# Check health status
docker-compose ps
curl http://localhost:9080/health
```

---

## 🧪 Testing

### Run All Tests
```bash
# With pytest
pytest tests/ -v

# Specific test file
pytest tests/test_phase4.py -v

# With coverage report
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html  # View coverage
```

### Run Individual Phase Tests
```bash
# Phase 1: Configuration
python tests/test_phase1.py

# Phase 2: Services & Tools
python tests/test_phase2.py

# Phase 3: API Layer
python tests/test_phase3.py

# Phase 4: Error Handling
python tests/test_phase4.py

# Integration Tests
python tests/test_integration.py

# API Endpoint Tests
python tests/test_api.py
```

---

## 🔧 Configuration

### Environment Variables (Essential)
```bash
# Required
OPENAI_API_KEY=sk-proj-xxxxx

# API Server
API_PORT=9080
API_ENV=production
API_WORKERS=4

# Security
RATE_LIMIT_ENABLED=true
DOCS_ENABLED=false  # Disable in production

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Quick Config Changes
```bash
# Edit environment
nano .env  # or vim, code, etc.

# Restart to apply changes (Docker)
docker-compose restart agentic-rag-api

# Restart to apply changes (manual)
# Ctrl+C and restart: python main.py
```

---

## 🌐 API Endpoints

### Health Check
```bash
curl http://localhost:9080/health
```

### Get Available Tools
```bash
curl http://localhost:9080/tools
```

### Chat (Synchronous)
```bash
curl -X POST http://localhost:9080/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How many active customers do we have?",
    "conversation_history": []
  }'
```

### Chat Stream (SSE)
```bash
curl -X POST http://localhost:9080/chat-stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search for information about Python",
    "conversation_history": []
  }'
```

### Access Documentation (Development Only)
- Swagger UI: http://localhost:9080/docs
- ReDoc: http://localhost:9080/redoc

---

## 🗄️ Database Operations

### Initialize Databases
```bash
# Local
python db/init_databases.py

# Docker
docker-compose exec agentic-rag-api python db/init_databases.py
```

### Backup Databases
```bash
# Local
cp db/crm.db backups/crm_$(date +%Y%m%d).db
cp db/chinook.db backups/chinook_$(date +%Y%m%d).db

# Docker
docker-compose exec agentic-rag-api cp db/crm.db /tmp/crm_backup.db
docker cp agentic-rag-api:/tmp/crm_backup.db ./backups/
```

### Restore Databases
```bash
# Local
cp backups/crm_20260213.db db/crm.db

# Docker
docker cp ./backups/crm_20260213.db agentic-rag-api:/app/db/crm.db
docker-compose restart agentic-rag-api
```

---

## 📊 Monitoring

### View Logs
```bash
# Docker logs
docker-compose logs -f --tail=100 agentic-rag-api

# Local logs
tail -f logs/agentic_rag_api.log

# Filter by log level
grep "ERROR" logs/agentic_rag_api.log
grep "WARNING" logs/agentic_rag_api.log
```

### Resource Usage
```bash
# Docker stats
docker stats agentic-rag-api

# Local (Linux/Mac)
top -p $(pgrep -f "uvicorn main:app")
```

### Health Monitoring
```bash
# Continuous health check
watch -n 5 'curl -s http://localhost:9080/health | jq'

# Simple monitor script
while true; do
  curl -s http://localhost:9080/health | jq '.status'
  sleep 10
done
```

---

## 🔐 Security

### Secure API Key
```bash
# Never commit .env
git status  # Ensure .env not tracked

# Use environment variable (Docker)
export OPENAI_API_KEY=sk-proj-xxxxx
docker-compose up -d

# Use secrets file (Docker)
echo "sk-proj-xxxxx" | docker secret create openai_key -
```

### Enable Production Security
```bash
# In .env file
RATE_LIMIT_ENABLED=true
DOCS_ENABLED=false
CORS_ORIGINS=https://yourdomain.com
API_ENV=production
```

---

## 🚨 Troubleshooting

### API Won't Start
```bash
# Check logs
docker-compose logs agentic-rag-api

# Common issues:
# 1. Missing OPENAI_API_KEY
grep OPENAI_API_KEY .env

# 2. Port already in use
lsof -i :9080  # Linux/Mac
netstat -ano | findstr :9080  # Windows

# 3. Docker not running
docker --version
docker-compose --version
```

### Database Errors
```bash
# Reinitialize databases
docker-compose exec agentic-rag-api python db/init_databases.py

# Check database files exist
docker-compose exec agentic-rag-api ls -la db/
```

### FAISS Errors (Non-Critical)
```bash
# Check urls.txt exists
cat urls.txt

# FAISS is optional - API continues without it
# Check logs for FAISS warnings
docker-compose logs agentic-rag-api | grep FAISS
```

### High Memory Usage
```bash
# Reduce workers
# In .env: API_WORKERS=2
docker-compose restart agentic-rag-api

# Monitor memory
docker stats agentic-rag-api
```

---

## 🔄 Updates & Maintenance

### Update Dependencies
```bash
# Update requirements
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker-compose up -d --build
```

### Clean Up Docker
```bash
# Remove stopped containers
docker-compose down

# Remove unused images
docker image prune -a

# Remove all (containers, networks, volumes)
docker-compose down -v
```

### Backup Workflow
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR
docker cp agentic-rag-api:/app/db/crm.db $BACKUP_DIR/
docker cp agentic-rag-api:/app/db/chinook.db $BACKUP_DIR/
docker cp agentic-rag-api:/app/logs $BACKUP_DIR/

echo "Backup complete: $BACKUP_DIR"
```

---

## 📈 Performance Tuning

### Optimize Workers
```bash
# Formula: (2 × CPU cores) + 1
# For 4 cores: API_WORKERS=9

# Edit .env
API_WORKERS=9

# Restart
docker-compose restart agentic-rag-api
```

### Database Optimization
```bash
# Analyze queries
# Enable query logging in settings.py
LOG_LEVEL=DEBUG

# Check slow queries in logs
grep "slow query" logs/agentic_rag_api.log
```

---

## 🌍 Deployment Platforms

### AWS EC2
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Deploy
git clone <repo>
cd agentic-rag-usecase/back-end
cp .env.production .env
# Edit .env
docker-compose up -d
```

### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/PROJECT-ID/agentic-rag-api
gcloud run deploy agentic-rag-api \
  --image gcr.io/PROJECT-ID/agentic-rag-api \
  --platform managed \
  --set-env-vars OPENAI_API_KEY=xxx
```

### Azure Container Instances
```bash
az acr build --registry myregistry --image agentic-rag-api:latest .
az container create \
  --resource-group myRG \
  --name agentic-rag-api \
  --image myregistry.azurecr.io/agentic-rag-api:latest
```

---

## 📚 Documentation Links

- **README.md** - Quick start guide
- **DEPLOYMENT_GUIDE.md** - Production deployment
- **PRODUCTION_CHECKLIST.md** - Pre-deploy checklist
- **PROJECT_SUMMARY.md** - Complete project overview
- **API_GUIDE.md** - API usage examples

---

## 💡 Useful One-Liners

```bash
# Quick deploy
cp .env.production .env && docker-compose up -d && docker-compose logs -f

# Health check with timestamp
date && curl -s http://localhost:9080/health | jq

# Count log errors
docker-compose logs agentic-rag-api | grep ERROR | wc -l

# Find container IP
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' agentic-rag-api

# Open shell in container
docker-compose exec agentic-rag-api /bin/bash

# View environment variables
docker-compose exec agentic-rag-api env | grep API_

# Restart and follow logs
docker-compose restart agentic-rag-api && docker-compose logs -f agentic-rag-api
```

---

**Quick Reference Version 1.0** - Last Updated: February 13, 2026
