# 🚀 Deployment Guide - อัปเดตไฟล์ไปยัง Server

## 📋 ไฟล์ที่ต้อง Deploy

ไฟล์ที่เพิ่ม/แก้ไขใหม่:
- ✅ `app/api/sources.py` - **ไฟล์ใหม่** (Source Management API)
- ✅ `app/api/__init__.py` - แก้ไข (เพิ่ม sources_router)
- ✅ `app/api/articles.py` - แก้ไข (เพิ่ม fetch by source_id)
- ✅ `app/main.py` - แก้ไข (register sources_router)
- ✅ `sources.yaml` - แก้ไข (เพิ่ม weird news sources)

---

## 🔧 วิธีที่ 1: ใช้ SCP (แนะนำ)

### Windows (PowerShell):

```powershell
# ตั้งค่า
$SERVER_USER = "root"
$SERVER_HOST = "your-server-ip"  # แก้เป็น IP จริง
$SERVER_PATH = "/opt/thai-news-scraper/thai-news-scraper"

# Upload ไฟล์
scp app/api/sources.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/
scp app/api/__init__.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/
scp app/api/articles.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/api/
scp app/main.py ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/app/
scp sources.yaml ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/

# Restart container
ssh ${SERVER_USER}@${SERVER_HOST} "cd ${SERVER_PATH} && docker-compose restart api"
```

### Linux/Mac (Bash):

```bash
# ให้สิทธิ์ execute
chmod +x deploy_updates.sh

# แก้ไข SERVER_HOST ในไฟล์ก่อน
nano deploy_updates.sh

# รันสคริปต์
./deploy_updates.sh
```

---

## 🔧 วิธีที่ 2: Manual Copy บน Server

### 1. SSH เข้า Server:

```bash
ssh root@your-server-ip
cd /opt/thai-news-scraper/thai-news-scraper
```

### 2. สร้างไฟล์ `app/api/sources.py`:

```bash
nano app/api/sources.py
```

**Copy เนื้อหาจากไฟล์ local** แล้ว Ctrl+X, Y, Enter

### 3. แก้ไข `app/api/__init__.py`:

```bash
nano app/api/__init__.py
```

เปลี่ยนเป็น:
```python
# API package initialization
from app.api.articles import router as articles_router
from app.api.trends import router as trends_router
from app.api.sources import router as sources_router

__all__ = ['articles_router', 'trends_router', 'sources_router']
```

### 4. แก้ไข `app/main.py`:

```bash
nano app/main.py
```

เปลี่ยนบรรทัด 11:
```python
from app.api import articles_router, trends_router, sources_router
```

เพิ่มบรรทัด 148:
```python
app.include_router(sources_router)
```

### 5. อัปเดต `sources.yaml`:

```bash
nano sources.yaml
```

**Copy เนื้อหาจากไฟล์ local**

### 6. Restart Container:

```bash
docker-compose restart api
```

---

## 🔧 วิธีที่ 3: Git Pull (ถ้าใช้ Git)

```bash
# บน server
cd /opt/thai-news-scraper/thai-news-scraper
git pull origin main
docker-compose restart api
```

---

## ✅ ตรวจสอบหลัง Deploy

### 1. เช็ค logs:

```bash
docker logs -f thai-news-api
```

ต้องเห็น:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. ทดสอบ API:

```bash
# Health check
curl http://localhost:8000/health

# ดู sources
curl http://localhost:8000/sources

# ดู API docs
# เปิดเบราว์เซอร์: http://your-server-ip:8000/docs
```

---

## 🆘 Troubleshooting

### ❌ ถ้ายัง error "ModuleNotFoundError":

1. เช็คว่าไฟล์ `sources.py` มีจริงบน server:
   ```bash
   ls -la /opt/thai-news-scraper/thai-news-scraper/app/api/sources.py
   ```

2. เช็ค permissions:
   ```bash
   chmod 644 /opt/thai-news-scraper/thai-news-scraper/app/api/sources.py
   ```

3. Restart แบบ force:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### ❌ ถ้า container ไม่ขึ้น:

```bash
# ดู logs แบบเต็ม
docker logs thai-news-api

# เข้าไปใน container
docker exec -it thai-news-api bash
ls -la /app/app/api/
```

---

## 📝 หมายเหตุ

- ถ้าใช้ Docker image จาก registry ต้อง **rebuild และ push image ใหม่**
- ถ้า mount volume อยู่ การแก้ไขไฟล์จะมีผลทันที (ไม่ต้อง rebuild)
- ระบบจะโหลด sources จาก `sources.yaml` ตอน startup เท่านั้น
