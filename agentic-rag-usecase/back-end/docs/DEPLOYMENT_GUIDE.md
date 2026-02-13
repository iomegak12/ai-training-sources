# Deployment Guide - Agentic RAG REST API

Complete guide for deploying the Agentic RAG API to production environments.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Docker Deployment](#docker-deployment)
3. [Manual Deployment](#manual-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration](#configuration)
6. [Security](#security)
7. [Monitoring](#monitoring)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.11+** (for manual deployment)
- **Docker & Docker Compose** (for containerized deployment)
- **OpenAI API Key** (required for LLM functionality)
- **4GB RAM minimum** (8GB recommended)
- **2 CPU cores minimum** (4 recommended)

### Optional

- **Reverse proxy** (nginx, Caddy) for HTTPS
- **LangSmith account** for tracing and monitoring
- **Domain name** for production deployment

---

## Docker Deployment

Docker is the **recommended** deployment method for production.

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd agentic-rag-usecase/back-end
   ```

2. **Configure environment**
   ```bash
   # Copy production template
   cp .env.production .env
   
   # Edit .env and set your OPENAI_API_KEY
   nano .env  # or vim, code, etc.
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Verify deployment**
   ```bash
   # Check logs
   docker-compose logs -f
   
   # Check health
   curl http://localhost:9080/health
   ```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f agentic-rag-api

# Restart service
docker-compose restart agentic-rag-api

# Rebuild after code changes
docker-compose up -d --build

# View resource usage
docker stats agentic-rag-api

# Execute command in container
docker-compose exec agentic-rag-api python -c "print('Hello')"
```

### Docker Production Best Practices

1. **Use specific image tags** (not `latest`)
2. **Set resource limits** in docker-compose.yml
3. **Enable health checks**
4. **Use volumes for persistent data**
5. **Run as non-root user** (already configured)
6. **Keep base images updated**

---

## Manual Deployment

For deployment without Docker.

### 1. System Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Python 3.11
sudo apt-get install -y python3.11 python3.11-venv python3-pip

# Install system dependencies
sudo apt-get install -y gcc g++ make curl
```

### 2. Application Setup

```bash
# Create application directory
sudo mkdir -p /opt/agentic-rag-api
cd /opt/agentic-rag-api

# Clone repository
git clone <repository-url> .

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy and edit production config
cp .env.production .env
nano .env

# Set OPENAI_API_KEY and other production values
```

### 4. Initialize Databases

```bash
# Run from back-end directory
python db/init_databases.py
```

### 5. Create Systemd Service

Create `/etc/systemd/system/agentic-rag-api.service`:

```ini
[Unit]
Description=Agentic RAG REST API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/agentic-rag-api
Environment="PATH=/opt/agentic-rag-api/venv/bin"
ExecStart=/opt/agentic-rag-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 9080 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 6. Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable agentic-rag-api

# Start service
sudo systemctl start agentic-rag-api

# Check status
sudo systemctl status agentic-rag-api

# View logs
sudo journalctl -u agentic-rag-api -f
```

---

## Cloud Deployment

### AWS EC2

1. **Launch EC2 instance**
   - AMI: Ubuntu 22.04 LTS
   - Instance type: t3.medium or larger
   - Security group: Allow port 9080 (or 80/443 with reverse proxy)

2. **Install Docker**
   ```bash
   sudo apt-get update
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy with Docker Compose**
   ```bash
   git clone <repository-url>
   cd agentic-rag-usecase/back-end
   cp .env.production .env
   # Edit .env with your OPENAI_API_KEY
   docker-compose up -d
   ```

### Google Cloud Run

1. **Build container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT-ID/agentic-rag-api
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy agentic-rag-api \
     --image gcr.io/PROJECT-ID/agentic-rag-api \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars OPENAI_API_KEY=your-key
   ```

### Azure Container Instances

1. **Build and push to ACR**
   ```bash
   az acr build --registry myregistry --image agentic-rag-api:latest .
   ```

2. **Deploy to ACI**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name agentic-rag-api \
     --image myregistry.azurecr.io/agentic-rag-api:latest \
     --dns-name-label agentic-rag \
     --ports 9080
   ```

### DigitalOcean App Platform

1. **Connect repository** to DigitalOcean
2. **Configure build**
   - Build command: `docker build -t agentic-rag-api .`
   - Run command: `uvicorn main:app --host 0.0.0.0 --port 9080`
3. **Set environment variables** (OPENAI_API_KEY, etc.)
4. **Deploy**

---

## Configuration

### Production Environment Variables

Key settings for production in `.env`:

```bash
# Security
RATE_LIMIT_ENABLED=true
DOCS_ENABLED=false  # Disable API docs in production

# Performance
API_WORKERS=4  # Adjust based on CPU cores
API_RELOAD=false

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=https://yourdomain.com
```

### Reverse Proxy (Nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:9080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Streaming support
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### SSL/TLS with Let's Encrypt

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d api.yourdomain.com

# Auto-renewal is configured automatically
```

---

## Security

### Security Checklist

- [ ] **Never expose OPENAI_API_KEY** in logs or responses
- [ ] **Disable API docs** in production (`DOCS_ENABLED=false`)
- [ ] **Enable rate limiting** (`RATE_LIMIT_ENABLED=true`)
- [ ] **Use HTTPS** (via reverse proxy)
- [ ] **Configure CORS** properly (restrict origins)
- [ ] **Run as non-root user** (Docker: already configured)
- [ ] **Keep dependencies updated** (`pip install --upgrade -r requirements.txt`)
- [ ] **Monitor logs** for suspicious activity
- [ ] **Set resource limits** (CPU, memory)
- [ ] **Use environment variables** for secrets (never hardcode)

### Secrets Management

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name /agentic-rag/openai-key \
  --secret-string "sk-proj-xxxx"
```

**Azure Key Vault:**
```bash
az keyvault secret set \
  --vault-name mykeyvault \
  --name openai-api-key \
  --value "sk-proj-xxxx"
```

**Docker Secrets:**
```bash
echo "sk-proj-xxxx" | docker secret create openai_api_key -
```

---

## Monitoring

### Health Checks

```bash
# Check API health
curl http://localhost:9080/health

# Expected response
{
  "status": "healthy",
  "components": {
    "agent_service": {"status": "healthy"},
    "database": {"status": "healthy"},
    "faiss_service": {"status": "healthy"}
  }
}
```

### Logging

**View Docker logs:**
```bash
docker-compose logs -f --tail=100 agentic-rag-api
```

**View systemd logs:**
```bash
sudo journalctl -u agentic-rag-api -f --since "1 hour ago"
```

### LangSmith Monitoring

Enable tracing in `.env`:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=agentic-rag-api-prod
LANGCHAIN_API_KEY=your_langsmith_key
```

### Metrics and Alerts

**Prometheus + Grafana** (optional):

1. Add prometheus-fastapi-instrumentator:
   ```bash
   pip install prometheus-fastapi-instrumentator
   ```

2. Update `main.py`:
   ```python
   from prometheus_fastapi_instrumentator import Instrumentator
   Instrumentator().instrument(app).expose(app)
   ```

---

## Troubleshooting

### Common Issues

**1. API won't start**
```bash
# Check logs
docker-compose logs agentic-rag-api

# Common causes:
# - Missing OPENAI_API_KEY
# - Port 9080 already in use
# - Insufficient memory
```

**2. Database errors**
```bash
# Reinitialize databases
docker-compose exec agentic-rag-api python db/init_databases.py
```

**3. FAISS initialization fails**
```bash
# Check FAISS logs (non-critical, API continues without it)
# Verify urls.txt exists and contains valid URLs
```

**4. High memory usage**
```bash
# Reduce workers in docker-compose.yml
API_WORKERS=2

# Restart container
docker-compose restart agentic-rag-api
```

**5. Slow responses**
```bash
# Check OpenAI API status
# Increase timeout settings
# Monitor logs for errors
```

### Debug Mode

Enable debug logging:

```bash
# In .env
LOG_LEVEL=DEBUG

# Restart service
docker-compose restart agentic-rag-api
```

### Performance Tuning

**Optimize workers:**
```bash
# Rule of thumb: (2 × CPU cores) + 1
# For 4 cores: 9 workers
API_WORKERS=9
```

**Database optimization:**
```bash
# Use connection pooling for high traffic
# Consider PostgreSQL for production at scale
```

---

## Backup and Recovery

### Backup Databases

```bash
# Backup CRM database
docker-compose exec agentic-rag-api cp db/crm.db /backup/crm_$(date +%Y%m%d).db

# Backup Chinook database
docker-compose exec agentic-rag-api cp db/chinook.db /backup/chinook_$(date +%Y%m%d).db
```

### Restore Databases

```bash
# Restore from backup
docker-compose exec agentic-rag-api cp /backup/crm_20260213.db db/crm.db
docker-compose restart agentic-rag-api
```

---

## Support

For issues and questions:

- Check logs: `docker-compose logs -f`
- Review health endpoint: `curl http://localhost:9080/health`
- Verify configuration: `.env` file
- Test OpenAI API key manually

---

**Deployment Complete!** 🚀

Your Agentic RAG API is now running in production.
