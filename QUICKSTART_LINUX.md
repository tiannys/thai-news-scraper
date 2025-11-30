# Quick Start Guide - Linux Deployment

## สำหรับ Ubuntu/Debian

### 1. ติดตั้ง Docker

```bash
# Update packages
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (ไม่ต้อง sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### 2. Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/thai-news-scraper.git
cd thai-news-scraper

# หรือถ้า clone แล้ว
cd thai-news-scraper
git pull
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

**สิ่งที่ต้องแก้ไข**:

```bash
# Webhook (n8n) - สำคัญ!
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://your-n8n-server.com/webhook/thai-news
WEBHOOK_SECRET=your-secret-key-123

# Scraper
SCRAPER_USER_AGENT=ThaiNewsBot/1.0 (+https://yoursite.com/bot; contact@email.com)

# Optional: เปลี่ยน password
# แก้ใน .env และ docker-compose.yml ให้ตรงกัน
```

กด `Ctrl+X` → `Y` → `Enter` เพื่อบันทึก

### 4. Start Services

```bash
# Build and start
docker compose up -d

# Check status
docker compose ps

# Should see:
# thai-news-db    running
# thai-news-api   running
```

### 5. Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# Expected output:
# {"status":"healthy","version":"1.0.0","scheduler":"running"}

# View API documentation
curl http://localhost:8000/docs

# Trigger manual fetch
curl -X POST http://localhost:8000/articles/fetch
```

### 6. View Logs

```bash
# All services
docker compose logs -f

# API only
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api
```

## สำหรับ CentOS/RHEL

```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Continue with step 2 above
```

## การตั้งค่า Firewall

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 8000/tcp
sudo ufw allow 5432/tcp  # ถ้าต้องการเข้า DB จากภายนอก
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
```

## การตั้งค่า Reverse Proxy (Nginx)

```bash
# Install Nginx
sudo apt-get install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/thai-news-api
```

**Nginx Configuration**:

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

# Test config
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured automatically
```

## Systemd Service (Auto-start on Boot)

Docker Compose services จะ restart อัตโนมัติ แต่ถ้าต้องการให้ Docker เริ่มตอน boot:

```bash
# Enable Docker on boot
sudo systemctl enable docker

# Verify
sudo systemctl is-enabled docker
```

## การ Update

```bash
# Pull latest code
cd thai-news-scraper
git pull

# Rebuild and restart
docker compose down
docker compose build
docker compose up -d

# Check logs
docker compose logs -f api
```

## Database Backup

```bash
# Create backup
docker compose exec db pg_dump -U newsuser thai_news > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore backup
docker compose exec -T db psql -U newsuser thai_news < backup_20241130_100000.sql
```

## Monitoring

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a
```

## Troubleshooting

### Port already in use

```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use 8001 instead
```

### Permission denied

```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Out of disk space

```bash
# Check disk usage
df -h

# Clean Docker
docker system prune -a --volumes

# Remove old logs
docker compose exec api rm -rf /app/logs/*.log
```

## Production Checklist

- [ ] Change default passwords in `.env` and `docker-compose.yml`
- [ ] Set strong `WEBHOOK_SECRET`
- [ ] Configure proper `SCRAPER_USER_AGENT` with contact info
- [ ] Set up firewall (UFW/firewalld)
- [ ] Configure Nginx reverse proxy
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Configure automatic backups
- [ ] Set up monitoring (optional)
- [ ] Test webhook to n8n
- [ ] Verify scheduler is running

## Next Steps

1. **Configure n8n webhook** - See [N8N_CONNECTION_GUIDE.md](N8N_CONNECTION_GUIDE.md)
2. **Customize news sources** - Edit `sources.yaml`
3. **Set up monitoring** - Use Prometheus/Grafana (optional)
4. **Configure backups** - Set up cron job for daily backups

---

**Need help?** Check [DEPLOYMENT.md](DEPLOYMENT.md) for detailed guide or open an issue on GitHub.
