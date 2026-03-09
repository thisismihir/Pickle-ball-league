# Frontend Deployment Guide - DigitalOcean

## Prerequisites
- DigitalOcean account (https://www.digitalocean.com)
- Docker installed locally (for testing)
- Git installed

---

## Option 1: Deploy Using DigitalOcean App Platform (Easiest - No Server Management)

### Step 1: Push Code to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit with Docker config"
git remote add origin https://github.com/YOUR_USERNAME/pickle-ball-league.git
git push -u origin main
```

### Step 2: Connect DigitalOcean to GitHub
1. Go to https://cloud.digitalocean.com
2. Click **Apps** in left sidebar
3. Click **Create App**
4. Select **GitHub** as source
5. Authorize DigitalOcean to access your GitHub
6. Select your `pickle-ball-league` repository
7. Select branch: `main`

### Step 3: Configure the Frontend Service
1. Click **Edit** on the Auto-detected service
2. Set **Source Directory**: `frontend`
3. Set **Build Command**: (leave empty - no build needed)
4. Set **Run Command**: (leave empty - Docker handles it)
5. Configure environment variables if needed (none required for basic setup)

### Step 4: Set Up Resource Plan
1. Select **Basic** plan (suitable for testing)
2. Review pricing: ~$5-12/month depending on traffic
3. Click **Create Resource**

### Step 5: Add Custom Domain (Optional)
1. Go to App Settings
2. Click **Domains**
3. Add your domain (e.g., `pickleball.yourdomain.com`)
4. Update DNS records as instructed

### Step 6: Deploy
- DigitalOcean automatically deploys when you push to GitHub
- Monitor deployment progress in the **Deployments** tab
- Your app will be live at the provided URL

---

## Option 2: Deploy Using Docker on DigitalOcean Droplet (More Control)

### Step 1: Create a Droplet
1. Go to https://cloud.digitalocean.com
2. Click **Create** → **Droplet**
3. Choose image: **Docker on Ubuntu 22.04**
4. Select plan: **Basic** ($5/month for starter)
5. Select region: Closest to your users
6. Add SSH key or use password
7. Click **Create Droplet**
8. Wait 2-3 minutes for setup to complete

### Step 2: Connect via SSH
```bash
# On your local machine
ssh root@YOUR_DROPLET_IP

# Or if using SSH key
ssh -i ~/.ssh/id_rsa root@YOUR_DROPLET_IP
```

### Step 3: Clone Your Repository
```bash
cd /root
git clone https://github.com/YOUR_USERNAME/pickle-ball-league.git
cd pickle-ball-league/frontend
```

### Step 4: Build Docker Image
```bash
# Build the image
docker build -t pickle-frontend:latest .

# Test locally (optional)
docker run -d -p 80:80 --name frontend pickle-frontend:latest
# Visit http://YOUR_DROPLET_IP in browser
# Stop: docker stop frontend
```

### Step 5: Set Up Nginx Reverse Proxy (Optional but Recommended)
```bash
# Install docker-compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    image: pickle-frontend:latest
    container_name: pickle-frontend
    ports:
      - "3000:80"
    restart: always
    environment:
      - NODE_ENV=production
    labels:
      - "com.example.description=Pickle Ball Frontend"

  backend:
    image: pickle-backend:latest
    container_name: pickle-backend
    ports:
      - "8000:8000"
    restart: always
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:password@db:5432/pickleball

networks:
  default:
    name: pickle-network
EOF
```

### Step 6: Run with Docker Compose
```bash
docker-compose up -d
```

### Step 7: Set Up Nginx Reverse Proxy (For Multiple Services)
```bash
# Install nginx
apt-get update && apt-get install -y nginx

# Create nginx config
cat > /etc/nginx/sites-available/pickleball << 'EOF'
server {
    listen 80;
    server_name YOUR_DOMAIN.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # API Backend
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

# Enable config
ln -s /etc/nginx/sites-available/pickleball /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 8: Set Up SSL/HTTPS (Using Let's Encrypt)
```bash
# Install certbot
apt-get install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d YOUR_DOMAIN.com

# Auto-renewal
systemctl enable certbot.timer
systemctl start certbot.timer
```

### Step 9: Add Firewall Rules
```bash
# Enable UFW firewall
ufw enable

# Allow SSH, HTTP, HTTPS
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Check status
ufw status
```

---

## Option 3: Deploy Using DigitalOcean Container Registry

### Step 1: Create Container Registry
1. Go to https://cloud.digitalocean.com
2. Click **Container Registry**
3. Click **Create Registry**
4. Name: `pickleball`
5. Datacenter: Choose closest region

### Step 2: Build and Push Image
```bash
# Authenticate with DO
doctl registry login

# Build image with registry prefix
docker build -t registry.digitalocean.com/YOUR_REGISTRY_NAME/pickle-frontend:latest .

# Push to registry
docker push registry.digitalocean.com/YOUR_REGISTRY_NAME/pickle-frontend:latest
```

### Step 3: Deploy to Kubernetes (Optional - Advanced)
```bash
# Create DigitalOcean Kubernetes cluster
doctl kubernetes cluster create pickle-cluster --region nyc1 --node-pool name=worker-pool size=s-1vcpu-2gb count=3

# Get kubeconfig
doctl kubernetes cluster kubeconfig save pickle-cluster

# Deploy
kubectl apply -f deployment.yaml
```

---

## Configuration Updates

### Update API URL for Production
Edit `frontend/js/config.js`:
```javascript
// Before deployment to production
const PRODUCTION_API_URL = 'https://YOUR_DOMAIN.com';  // Your DigitalOcean backend URL
const DEVELOPMENT_API_URL = 'http://localhost:8000';
```

---

## Monitoring & Maintenance

### View Logs (Docker)
```bash
docker logs -f pickle-frontend
```

### Update Application
```bash
# Pull latest changes
git pull origin main

# Rebuild image
docker build -t pickle-frontend:latest .

# Restart container
docker-compose up -d --build
```

### Monitor Performance
- **App Platform**: Built-in metrics dashboard
- **Droplet**: Use DigitalOcean monitoring tab or install Prometheus

---

## Cost Breakdown

| Option | Cost/Month | Effort | Maintenance |
|--------|-----------|--------|-------------|
| App Platform | $5-12 | ⭐ Easy | ⭐ Minimal |
| Basic Droplet | $5 | ⭐⭐ Medium | ⭐⭐ Moderate |
| Kubernetes | $10-50 | ⭐⭐⭐ Complex | ⭐⭐⭐ High |

---

## Troubleshooting

### Frontend not loading
```bash
# Check container status
docker ps

# View logs
docker logs pickle-frontend

# Check if port is accessible
curl http://localhost:80
```

### Connection to backend fails
1. Verify backend is running and accessible
2. Update `PRODUCTION_API_URL` in config.js
3. Check CORS settings in backend
4. Verify firewall allows traffic

### SSL certificate issues
```bash
# Check certificate status
certbot certificates

# Renew manually if needed
certbot renew
```

---

## Production Checklist

- [ ] Update `config.js` with production URLs
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall
- [ ] Enable backups
- [ ] Set up monitoring
- [ ] Configure email notifications
- [ ] Test all features
- [ ] Set up CI/CD pipeline
- [ ] Document deployment process
- [ ] Create backup strategy

---

**Recommended**: Start with **Option 1 (App Platform)** for simplicity, then migrate to **Option 2** when you need more control.
