# วิธีแก้ปัญหา Docker บน Windows

## ปัญหา: "unable to get image" และ "The system cannot find the file specified"

ปัญหานี้เกิดจาก **Docker Desktop ยังไม่ได้เปิด** หรือ **Docker service ไม่ทำงาน**

## วิธีแก้ (เลือกอย่างใดอย่างหนึ่ง)

### วิธีที่ 1: เปิด Docker Desktop (แนะนำ)

1. กด Windows key และพิมพ์ "Docker Desktop"
2. คลิกเปิดโปรแกรม Docker Desktop
3. รอจนกว่า Docker Desktop จะแสดงสถานะ "Running" (สีเขียว)
4. ลองรัน docker compose อีกครั้ง:

```powershell
docker compose up -d
```

### วิธีที่ 2: Start Docker Service ผ่าน PowerShell

```powershell
# เปิด PowerShell แบบ Administrator
Start-Service docker

# หรือ
Start-Service com.docker.service
```

### วิธีที่ 3: Restart Docker Desktop

1. เปิด Docker Desktop
2. คลิกที่ไอคอน Docker ใน System Tray (ข้างนาฬิกา)
3. เลือก "Restart"
4. รอจนกว่าจะเริ่มใหม่เสร็จ

## ตรวจสอบว่า Docker ทำงานหรือไม่

```powershell
# ตรวจสอบ Docker version
docker --version

# ตรวจสอบ Docker Compose version
docker compose version

# ดู Docker containers ที่กำลังทำงาน
docker ps

# ทดสอบรัน container ง่ายๆ
docker run hello-world
```

## หลังจาก Docker ทำงานแล้ว

```powershell
# ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# Start services
docker compose up -d

# ดูสถานะ
docker compose ps

# ดู logs
docker compose logs -f
```

## ถ้ายังไม่ได้

### ตรวจสอบ Docker Desktop Settings

1. เปิด Docker Desktop
2. ไปที่ Settings (เฟืองด้านบนขวา)
3. ตรวจสอบว่า:
   - ✅ "Start Docker Desktop when you log in" เปิดอยู่
   - ✅ "Use WSL 2 based engine" เปิดอยู่ (ถ้ามี)
   - ✅ Resources → Memory อย่างน้อย 2GB

### ติดตั้ง Docker Desktop ใหม่

ถ้ายังไม่ได้ลอง:

1. ดาวน์โหลด Docker Desktop: https://www.docker.com/products/docker-desktop
2. ติดตั้งและ restart เครื่อง
3. เปิด Docker Desktop
4. ลองรัน docker compose อีกครั้ง

## Alternative: รันแบบไม่ใช้ Docker (สำหรับ Development)

ถ้าไม่อยากใช้ Docker ตอนนี้ สามารถรันแบบ local ได้:

### 1. ติดตั้ง PostgreSQL

ดาวน์โหลดและติดตั้ง PostgreSQL:
https://www.postgresql.org/download/windows/

### 2. สร้าง Database

```sql
CREATE DATABASE thai_news;
CREATE USER newsuser WITH PASSWORD 'newspassword';
GRANT ALL PRIVILEGES ON DATABASE thai_news TO newsuser;
```

### 3. ติดตั้ง Python Dependencies

```powershell
# สร้าง virtual environment
python -m venv venv

# Activate
.\venv\Scripts\Activate.ps1

# ติดตั้ง dependencies
pip install -r requirements.txt
```

### 4. แก้ไข .env

```bash
DATABASE_URL=postgresql+asyncpg://newsuser:newspassword@localhost:5432/thai_news
DATABASE_URL_SYNC=postgresql://newsuser:newspassword@localhost:5432/thai_news
```

### 5. รัน API

```powershell
# ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# รัน
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## สรุป

**แนะนำ**: เปิด Docker Desktop แล้วรัน `docker compose up -d` อีกครั้ง

ถ้ามีปัญหาอื่นๆ ให้ส่ง error message มาดูครับ!
