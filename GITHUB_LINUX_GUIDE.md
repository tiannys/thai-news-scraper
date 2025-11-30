# วิธีอัพโหลดขึ้น GitHub และรันบน Linux

## ขั้นตอนที่ 1: เตรียม Repository บน GitHub

### 1.1 สร้าง Repository ใหม่

1. ไปที่ https://github.com
2. คลิก **"New repository"**
3. ตั้งชื่อ: `thai-news-scraper`
4. เลือก **Public** หรือ **Private**
5. **ไม่ต้อง** เลือก "Initialize with README" (เพราะเรามีแล้ว)
6. คลิก **"Create repository"**

### 1.2 คัดลอก Repository URL

คัดลอก URL ที่ได้ เช่น:
```
https://github.com/YOUR_USERNAME/thai-news-scraper.git
```

## ขั้นตอนที่ 2: อัพโหลดโค้ดจาก Windows

### 2.1 เปิด PowerShell

```powershell
# ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# Initialize git (ถ้ายังไม่ได้ทำ)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Thai News Scraper with n8n webhook integration"

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/thai-news-scraper.git

# Push to GitHub
git push -u origin main
```

**หมายเหตุ**: ถ้า branch ชื่อ `master` ให้ใช้:
```powershell
git branch -M main
git push -u origin main
```

### 2.2 ตรวจสอบบน GitHub

เปิดเว็บ GitHub → ควรเห็นไฟล์ทั้งหมดอัพโหลดแล้ว

## ขั้นตอนที่ 3: รันบน Linux Server

### 3.1 เชื่อมต่อ Linux Server

```bash
# SSH เข้า server
ssh username@your-server-ip

# หรือถ้าใช้ key
ssh -i your-key.pem username@your-server-ip
```

### 3.2 ติดตั้ง Docker (ถ้ายังไม่มี)

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker compose version
```

### 3.3 Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/YOUR_USERNAME/thai-news-scraper.git

# เข้า directory
cd thai-news-scraper
```

### 3.4 ตั้งค่า Environment

```bash
# Copy environment template
cp .env.example .env

# แก้ไข configuration
nano .env
```

**แก้ไขสิ่งเหล่านี้**:

```bash
# Database (ใช้ค่า default ได้)
DATABASE_URL=postgresql+asyncpg://newsuser:newspassword@db:5432/thai_news

# Webhook - สำคัญ!
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://your-n8n-server.com/webhook/thai-news
WEBHOOK_SECRET=your-secret-key-123

# Scraper
SCRAPER_USER_AGENT=ThaiNewsBot/1.0 (+https://yoursite.com/bot; contact@email.com)
```

กด `Ctrl+X` → `Y` → `Enter` เพื่อบันทึก

### 3.5 Start Services

```bash
# Build and start
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api
```

### 3.6 ทดสอบ

```bash
# Check health
curl http://localhost:8000/health

# Trigger fetch
curl -X POST http://localhost:8000/articles/fetch

# Check articles
curl http://localhost:8000/articles?limit=5
```

## ขั้นตอนที่ 4: ตั้งค่าเพิ่มเติม (Optional)

### 4.1 ตั้งค่า Firewall

```bash
# Ubuntu (UFW)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 8000/tcp # API
sudo ufw enable
```

### 4.2 ตั้งค่า Nginx Reverse Proxy

```bash
# Install Nginx
sudo apt-get update
sudo apt-get install -y nginx

# Create config
sudo nano /etc/nginx/sites-available/thai-news-api
```

**Nginx Config**:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/thai-news-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4.3 ตั้งค่า SSL (Let's Encrypt)

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is set up automatically
```

## ขั้นตอนที่ 5: เชื่อมต่อกับ n8n

### 5.1 สร้าง Webhook ใน n8n

1. เปิด n8n workflow
2. เพิ่ม **Webhook node**
3. ตั้งค่า:
   - Method: **POST**
   - Path: `thai-news`
   - Authentication: Header Auth (optional)
     - Name: `X-Webhook-Secret`
     - Value: `your-secret-key-123`

4. คัดลอก **Production Webhook URL**

### 5.2 อัพเดท .env บน Linux

```bash
# แก้ไข .env
nano .env

# เปลี่ยน WEBHOOK_URL เป็น URL ที่ได้จาก n8n
WEBHOOK_URL=https://your-n8n-server.com/webhook/thai-news

# Save และ restart
docker compose restart api
```

### 5.3 ทดสอบ Webhook

```bash
# Trigger fetch
curl -X POST http://localhost:8000/articles/fetch

# Check logs
docker compose logs -f api

# ควรเห็น: "Sent X articles to webhook: https://..."
```

## การอัพเดทโค้ด

### บน Windows (Local)

```powershell
# แก้ไขโค้ด
# ...

# Commit และ push
git add .
git commit -m "Update: description of changes"
git push
```

### บน Linux (Server)

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

## Backup & Restore

### Backup Database

```bash
# Create backup
docker compose exec db pg_dump -U newsuser thai_news > backup_$(date +%Y%m%d).sql

# Download to local (จาก local machine)
scp username@server-ip:~/thai-news-scraper/backup_20241130.sql ./
```

### Restore Database

```bash
# Upload backup to server
scp backup_20241130.sql username@server-ip:~/thai-news-scraper/

# Restore
docker compose exec -T db psql -U newsuser thai_news < backup_20241130.sql
```

## Monitoring

### View Logs

```bash
# Real-time logs
docker compose logs -f api

# Last 100 lines
docker compose logs --tail=100 api

# All services
docker compose logs -f
```

### Check Status

```bash
# Container status
docker compose ps

# Resource usage
docker stats

# Disk usage
docker system df
```

## Troubleshooting

### ปัญหา: Git push ไม่ได้

```powershell
# ตั้งค่า Git credentials
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# ถ้าใช้ HTTPS อาจต้อง Personal Access Token
# ไปที่ GitHub Settings → Developer settings → Personal access tokens
```

### ปัญหา: Docker ไม่ทำงานบน Linux

```bash
# Check Docker status
sudo systemctl status docker

# Start Docker
sudo systemctl start docker

# Enable on boot
sudo systemctl enable docker
```

### ปัญหา: Port 8000 ถูกใช้แล้ว

```bash
# Check what's using the port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
```

### ปัญหา: Webhook ไม่ทำงาน

```bash
# Check logs
docker compose logs -f api

# Test webhook manually
curl -X POST http://localhost:8000/articles/fetch

# Verify .env settings
cat .env | grep WEBHOOK
```

## Security Checklist

- [ ] เปลี่ยน password ใน `.env` และ `docker-compose.yml`
- [ ] ตั้ง `WEBHOOK_SECRET` ที่แข็งแรง
- [ ] ตั้งค่า firewall (UFW/firewalld)
- [ ] ใช้ HTTPS (SSL certificate)
- [ ] ไม่ commit `.env` ขึ้น GitHub (มี `.gitignore` แล้ว)
- [ ] ตั้งค่า backup อัตโนมัติ
- [ ] Monitor logs เป็นประจำ

## Production Checklist

- [ ] Repository อัพโหลดบน GitHub แล้ว
- [ ] Clone ลง Linux server แล้ว
- [ ] Docker และ Docker Compose ติดตั้งแล้ว
- [ ] `.env` ตั้งค่าครบถ้วน
- [ ] Services รันอยู่ (`docker compose ps`)
- [ ] API health check ผ่าน
- [ ] Webhook เชื่อมต่อกับ n8n แล้ว
- [ ] Firewall ตั้งค่าแล้ว
- [ ] Nginx reverse proxy (optional)
- [ ] SSL certificate (optional)
- [ ] Backup strategy กำหนดแล้ว

## คำสั่งที่ใช้บ่อย

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f api

# Check status
docker compose ps

# Update code
git pull && docker compose down && docker compose build && docker compose up -d

# Backup database
docker compose exec db pg_dump -U newsuser thai_news > backup.sql

# Clean up
docker system prune -a
```

## สรุป

1. **Windows**: แก้โค้ด → commit → push to GitHub
2. **Linux**: git pull → docker compose up -d
3. **n8n**: สร้าง webhook → ใส่ URL ใน `.env`
4. **Monitor**: docker compose logs -f api

---

**ใช้งานได้เลยครับ!** 🚀

ถ้ามีปัญหาให้ดู logs หรือเปิด issue บน GitHub
