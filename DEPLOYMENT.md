# Deployment Guide for Ubuntu

This guide provides step-by-step instructions for deploying the Thai News Scraper system on Ubuntu 20.04+ servers.

## Prerequisites

- Ubuntu 20.04 or later
- Root or sudo access
- At least 2GB RAM
- 20GB disk space
- Internet connection

## Step 1: Install Docker and Docker Compose

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Set up Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify installation
sudo docker --version
sudo docker compose version

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker
```

## Step 2: Clone or Upload Project Files

```bash
# Create project directory
mkdir -p ~/thai-news-scraper
cd ~/thai-news-scraper

# Upload all project files to this directory
# You should have:
# - app/
# - sources.yaml
# - requirements.txt
# - Dockerfile
# - docker-compose.yml
# - .env.example
```

## Step 3: Configure Environment Variables

```bash
# Copy example env file
cp .env.example .env

# Edit environment variables
nano .env

# Important settings to configure:
# - DATABASE_URL (use the default for Docker)
# - API_KEY (change to a secure random string)
# - SCRAPER_USER_AGENT (add your website/contact info)
# - OPENAI_API_KEY (if using AI features)
```

## Step 4: Configure News Sources

```bash
# Edit sources.yaml to add/remove news sources
nano sources.yaml

# Verify sources comply with robots.txt and ToS
# Test RSS feeds manually before adding
```

## Step 5: Build and Start Services

```bash
# Build Docker images
docker compose build

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View logs
docker compose logs -f api
```

## Step 6: Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0","scheduler":"running"}

# Access API documentation
# Open browser: http://your-server-ip:8000/docs

# Check database connection
docker compose exec db psql -U newsuser -d thai_news -c "\dt"

# Trigger manual fetch
curl -X POST http://localhost:8000/articles/fetch
```

## Step 7: Configure Firewall (Optional but Recommended)

```bash
# Install UFW if not already installed
sudo apt-get install -y ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow API port
sudo ufw allow 8000/tcp

# Allow n8n port (if using)
sudo ufw allow 5678/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Step 8: Set Up Reverse Proxy with Nginx (Optional)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create Nginx configuration
sudo nano /etc/nginx/sites-available/thai-news-api

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/thai-news-api /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## Step 9: Set Up SSL with Let's Encrypt (Optional)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
# Test renewal
sudo certbot renew --dry-run
```

## Step 10: Configure Automatic Startup

```bash
# Docker Compose services are set to restart automatically
# Verify restart policy
docker compose ps

# To ensure Docker starts on boot
sudo systemctl enable docker
```

## Monitoring and Maintenance

### View Logs

```bash
# API logs
docker compose logs -f api

# Database logs
docker compose logs -f db

# n8n logs
docker compose logs -f n8n

# All services
docker compose logs -f
```

### Database Backup

```bash
# Create backup
docker compose exec db pg_dump -U newsuser thai_news > backup_$(date +%Y%m%d).sql

# Restore backup
docker compose exec -T db psql -U newsuser thai_news < backup_20240101.sql
```

### Update Application

```bash
# Pull latest changes
cd ~/thai-news-scraper

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d
```

### Monitor Resource Usage

```bash
# Check container stats
docker stats

# Check disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

## Troubleshooting

### API won't start

```bash
# Check logs
docker compose logs api

# Common issues:
# 1. Database not ready - wait a few seconds and restart
# 2. Port already in use - change port in docker-compose.yml
# 3. Permission issues - check file ownership
```

### Database connection errors

```bash
# Check database is running
docker compose ps db

# Check database logs
docker compose logs db

# Reset database (WARNING: deletes all data)
docker compose down -v
docker compose up -d
```

### Scheduler not running

```bash
# Check environment variable
docker compose exec api env | grep SCHEDULER_ENABLED

# Should be "true"
# If not, edit .env and restart:
docker compose restart api
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -a --volumes

# Clean old logs
docker compose exec api rm -rf /app/logs/*.log
```

## Performance Tuning

### Adjust Fetch Interval

Edit `.env`:
```
SCHEDULER_FETCH_INTERVAL_MINUTES=60  # Fetch every hour instead of 30 min
```

### Increase Workers

Edit `docker-compose.yml`:
```yaml
environment:
  API_WORKERS: 8  # Increase from 4
```

### Database Optimization

```bash
# Connect to database
docker compose exec db psql -U newsuser thai_news

# Create additional indexes
CREATE INDEX idx_articles_source_published ON articles(source_id, published_at DESC);

# Analyze tables
ANALYZE articles;
ANALYZE trends;
```

## Security Best Practices

1. **Change default passwords** in `.env` and `docker-compose.yml`
2. **Use strong API keys**
3. **Enable firewall** (UFW)
4. **Use SSL/TLS** with Let's Encrypt
5. **Regular backups** of database
6. **Keep Docker updated**: `sudo apt-get update && sudo apt-get upgrade`
7. **Monitor logs** for suspicious activity
8. **Limit API access** with API keys or IP whitelisting

## Accessing n8n

If you deployed n8n:

1. Open browser: `http://your-server-ip:5678`
2. Login with credentials from `docker-compose.yml`:
   - Username: `admin`
   - Password: `changeme` (CHANGE THIS!)
3. Follow the n8n workflow setup guide

## Next Steps

1. Configure n8n workflow (see N8N_WORKFLOW.md)
2. Set up monitoring and alerting
3. Configure backup automation
4. Review and customize news sources
5. Test the complete pipeline
