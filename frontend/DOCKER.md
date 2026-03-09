# Frontend Docker Quick Start Guide

## Local Development with Docker

### Prerequisites
- Docker & Docker Compose installed
- Terminal/PowerShell access

### Build & Run Locally

```bash
# From project root
docker-compose up -d

# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### View Logs
```bash
# Frontend logs
docker logs -f pickle-frontend

# Backend logs
docker logs -f pickle-backend

# Both
docker-compose logs -f
```

### Stop Services
```bash
docker-compose down
```

### Rebuild After Code Changes
```bash
docker-compose up -d --build
```

---

## Docker Image Information

### Frontend Image
- **Base**: nginx:alpine (minimal, ~40MB)
- **Port**: 80 (HTTP)
- **Files**: Serve static HTML/CSS/JS
- **Features**:
  - Gzip compression enabled
  - Security headers configured
  - Cache optimization for static assets
  - Health check endpoint at `/health`

### Building Manually
```bash
# Build
cd frontend
docker build -t pickle-frontend:latest .

# Run
docker run -d -p 80:80 --name frontend pickle-frontend:latest

# Stop
docker stop frontend
docker rm frontend
```

---

## Environment Variables

### Frontend (config.js)
- **PRODUCTION_API_URL**: API server URL for production
- **DEVELOPMENT_API_URL**: API server URL for development
- Auto-detects based on hostname

### Backend
Set in docker-compose.yml or .env file:
```
ENVIRONMENT=production
DATABASE_URL=sqlite:///./pickleball_league.db
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000,http://your-domain.com
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=secure-password
DEFAULT_ADMIN_EMAIL=admin@example.com
```

---

## Health Checks

Frontend health endpoint:
```bash
curl http://localhost/health
# Response: healthy
```

Backend health endpoint:
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy"}
```

---

## Deployment to Production

See [DEPLOYMENT.md](./frontend/DEPLOYMENT.md) for:
- DigitalOcean App Platform (Easiest)
- Docker Droplet (More Control)
- Kubernetes (Advanced)
