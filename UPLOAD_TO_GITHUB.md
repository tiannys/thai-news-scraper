# คำสั่งอัพโหลดขึ้น GitHub

## ขั้นตอนที่ 1: ตั้งค่า Git (ครั้งแรกเท่านั้น)

เปิด PowerShell และรันคำสั่งเหล่านี้:

```powershell
# ตั้งค่าชื่อและอีเมล (ใช้ข้อมูลจริงของคุณ)
git config --global user.name "tiannys"
git config --global user.email "your-email@example.com"

# ตรวจสอบการตั้งค่า
git config --global user.name
git config --global user.email
```

## ขั้นตอนที่ 2: เตรียม Repository

```powershell
# ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# Initialize git repository
git init

# เปลี่ยน branch เป็น main (ถ้ายังเป็น master)
git branch -M main
```

## ขั้นตอนที่ 3: Add และ Commit ไฟล์

```powershell
# Add ไฟล์ทั้งหมด
git add .

# ตรวจสอบว่าไฟล์อะไรจะถูก commit
git status

# Commit
git commit -m "Initial commit: Thai News Scraper with n8n webhook integration"
```

## ขั้นตอนที่ 4: เชื่อมต่อกับ GitHub

```powershell
# Add remote repository (ใช้ URL ของคุณ)
git remote add origin https://github.com/tiannys/thai-news-scraper.git

# ตรวจสอบ remote
git remote -v
```

## ขั้นตอนที่ 5: Push ขึ้น GitHub

### วิธีที่ 1: ใช้ HTTPS (แนะนำสำหรับครั้งแรก)

```powershell
# Push ขึ้น GitHub
git push -u origin main
```

**จะขึ้นหน้าต่างให้ login GitHub**:
1. เลือก "Sign in with your browser"
2. Login ด้วย GitHub account
3. Authorize Git Credential Manager
4. กลับมาที่ PowerShell → จะ push เสร็จ

### วิธีที่ 2: ใช้ Personal Access Token (ถ้าวิธีที่ 1 ไม่ได้)

#### 2.1 สร้าง Personal Access Token

1. ไปที่ https://github.com/settings/tokens
2. คลิก **"Generate new token"** → **"Generate new token (classic)"**
3. ตั้งชื่อ: `thai-news-scraper`
4. เลือก scope: ✅ **repo** (ทั้งหมด)
5. คลิก **"Generate token"**
6. **คัดลอก token** (จะแสดงครั้งเดียว!)

#### 2.2 Push ด้วย Token

```powershell
# Push (จะถามรหัสผ่าน)
git push -u origin main

# Username: tiannys
# Password: [วาง token ที่คัดลอกมา]
```

## ขั้นตอนที่ 6: ตรวจสอบบน GitHub

เปิดเว็บ: https://github.com/tiannys/thai-news-scraper

ควรเห็นไฟล์ทั้งหมดอัพโหลดแล้ว! 🎉

## การอัพเดทโค้ดในอนาคต

เมื่อแก้ไขโค้ดแล้วต้องการ push อีกครั้ง:

```powershell
# ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# Add ไฟล์ที่แก้ไข
git add .

# Commit พร้อมข้อความอธิบาย
git commit -m "Update: คำอธิบายการแก้ไข"

# Push
git push
```

## Troubleshooting

### ปัญหา: "fatal: remote origin already exists"

```powershell
# ลบ remote เดิม
git remote remove origin

# Add ใหม่
git remote add origin https://github.com/tiannys/thai-news-scraper.git
```

### ปัญหา: "Updates were rejected"

```powershell
# Pull ก่อน
git pull origin main --allow-unrelated-histories

# แก้ไข conflicts (ถ้ามี)
# จากนั้น push
git push -u origin main
```

### ปัญหา: "Authentication failed"

**วิธีแก้**:
1. ใช้ Personal Access Token แทนรหัสผ่าน
2. หรือติดตั้ง Git Credential Manager:
   ```powershell
   winget install Git.Git
   ```

### ปัญหา: ไฟล์ .env ถูก commit

```powershell
# ลบออกจาก git (แต่ไม่ลบไฟล์จริง)
git rm --cached .env

# Commit
git commit -m "Remove .env from git"

# Push
git push
```

## คำสั่งที่ใช้บ่อย

```powershell
# ดูสถานะ
git status

# ดู history
git log --oneline

# ดู remote
git remote -v

# Pull อัพเดทล่าสุด
git pull

# Push
git push

# ดู branch
git branch

# สร้าง branch ใหม่
git checkout -b feature-name
```

## ตรวจสอบก่อน Push

- [ ] ไฟล์ `.env` **ไม่ถูก** commit (มี `.gitignore` ป้องกันอยู่แล้ว)
- [ ] ไฟล์ `__pycache__` **ไม่ถูก** commit
- [ ] ไฟล์ `*.pyc` **ไม่ถูก** commit
- [ ] README.md มีข้อมูลครบถ้วน
- [ ] LICENSE มีอยู่

ตรวจสอบด้วย:
```powershell
git status
```

## สรุปคำสั่งทั้งหมด (Copy-Paste ได้เลย)

```powershell
# 1. ไปที่ project directory
cd C:\Users\teain\.gemini\antigravity\scratch\thai-news-scraper

# 2. Initialize git
git init
git branch -M main

# 3. Add และ Commit
git add .
git commit -m "Initial commit: Thai News Scraper with n8n webhook integration"

# 4. Add remote
git remote add origin https://github.com/tiannys/thai-news-scraper.git

# 5. Push
git push -u origin main
```

**เสร็จแล้ว!** ไปดูที่ https://github.com/tiannys/thai-news-scraper 🎉

---

## Next Steps

หลังจาก push แล้ว:

1. **ตรวจสอบ README** - ดูว่าแสดงผลถูกต้องไหม
2. **เพิ่ม Description** - ไปที่ repo settings → About → เพิ่มคำอธิบาย
3. **เพิ่ม Topics** - เช่น `python`, `fastapi`, `news-scraper`, `thai`, `n8n`
4. **Clone ลง Linux** - ตามคู่มือใน GITHUB_LINUX_GUIDE.md

ถ้ามีปัญหาตรงไหนบอกได้เลยครับ!
