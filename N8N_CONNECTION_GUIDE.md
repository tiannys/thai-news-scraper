# การตั้งค่า n8n Webhook (แบบ Push Model)

## ทำไมต้องใช้ Webhook?

แทนที่ n8n จะต้อง**ดึงข้อมูล** (pull) จาก API ทุกๆ ชั่วโมง ให้ API **ส่งข้อมูล** (push) ไปหา n8n ทันทีที่มีข่าวใหม่

### ข้อดี:
- ✅ **Real-time**: ได้ข่าวทันทีที่ scrape เสร็จ
- ✅ **ประหยัด**: ไม่ต้องเรียก API ซ้ำๆ
- ✅ **ง่ายกว่า**: n8n แค่รอรับข้อมูล ไม่ต้อง filter
- ✅ **Reliable**: ไม่พลาดข่าว

## ขั้นตอนการตั้งค่า

### 1. สร้าง Webhook ใน n8n

1. เปิด n8n workflow
2. เพิ่ม node **"Webhook"**
3. ตั้งค่า:
   - **HTTP Method**: POST
   - **Path**: `thai-news` (หรือชื่ออื่นที่ต้องการ)
   - **Authentication**: None (หรือ Header Auth ถ้าต้องการความปลอดภัย)

4. คัดลอก **Webhook URL** ที่ได้ เช่น:
   ```
   https://your-n8n-server.com/webhook/thai-news
   ```

### 2. ตั้งค่า API เพื่อส่งข้อมูลไป n8n

แก้ไขไฟล์ `.env`:

```bash
# เปิดใช้งาน webhook
WEBHOOK_ENABLED=true

# ใส่ URL ที่ได้จาก n8n
WEBHOOK_URL=https://your-n8n-server.com/webhook/thai-news

# (Optional) ใส่ secret สำหรับความปลอดภัย
WEBHOOK_SECRET=your-secret-key-123
```

### 3. Restart API

```powershell
docker compose restart api
```

## วิธีทำงาน

### เมื่อ Scraper ดึงข่าวใหม่:

```
┌─────────────────┐
│  Scraper API    │
│  (ทุก 30 นาที)  │
└────────┬────────┘
         │
         │ 1. ดึงข่าวจาก RSS
         │ 2. บันทึกลง Database
         │
         ▼
┌─────────────────┐
│  มีข่าวใหม่?    │
└────────┬────────┘
         │ Yes
         ▼
┌─────────────────────────────┐
│  ส่ง POST request ไป n8n   │
│  Webhook URL                │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  n8n Webhook รับข้อมูล      │
│  ▼                          │
│  OpenAI สร้างคอนเทนต์       │
│  ▼                          │
│  ส่งไป Line/Notion/Sheets   │
└─────────────────────────────┘
```

## ข้อมูลที่ API ส่งไป n8n

### Payload Format:

```json
{
  "event": "new_articles",
  "timestamp": "2024-11-30T10:00:00",
  "count": 5,
  "articles": [
    {
      "id": 123,
      "title": "หัวข้อข่าว",
      "summary": "สรุปข่าว...",
      "url": "https://example.com/news/123",
      "category": "news",
      "published_at": "2024-11-30T09:30:00",
      "tags": ["การเมือง", "เศรษฐกิจ"],
      "source_id": 1
    }
  ]
}
```

## n8n Workflow (แบบใหม่ - รับ Webhook)

### Node 1: Webhook Trigger

**Type**: Webhook
**Method**: POST
**Path**: `thai-news`

**Output**: จะได้ข้อมูลตาม payload ด้านบน

### Node 2: Filter Articles (Optional)

ถ้าต้องการ filter เพิ่ม:

```javascript
// Function node
const articles = $input.item.json.articles || [];

// Filter เฉพาะ news และ lifestyle
return articles
  .filter(article => ['news', 'lifestyle'].includes(article.category))
  .map(article => ({json: article}));
```

### Node 3: OpenAI - Generate Content

**Input**: `{{$json}}` (แต่ละ article)

**System Message**:
```
คุณเป็นนักเขียนคอนเทนต์โซเชียลมีเดียมืออาชีพ...
(เหมือนเดิม)
```

**User Message**:
```
วิเคราะห์ข่าวนี้:

หัวข้อ: {{$json.title}}
สรุป: {{$json.summary}}
หมวดหมู่: {{$json.category}}

ตอบกลับเป็น JSON...
```

### Node 4: Output

ส่งไป Line/Notion/Google Sheets

## ตัวอย่าง Workflow JSON (Import ได้เลย)

```json
{
  "name": "Thai News Webhook Handler",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "thai-news",
        "responseMode": "onReceived",
        "options": {}
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "webhookId": "your-webhook-id",
      "typeVersion": 1
    },
    {
      "parameters": {
        "functionCode": "const articles = $input.item.json.articles || [];\n\nreturn articles.map(article => ({json: article}));"
      },
      "name": "Split Articles",
      "type": "n8n-nodes-base.function",
      "position": [450, 300],
      "typeVersion": 1
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{$json.category}}",
              "operation": "equals",
              "value2": "news"
            },
            {
              "value1": "={{$json.category}}",
              "operation": "equals",
              "value2": "lifestyle"
            }
          ]
        },
        "combineOperation": "any"
      },
      "name": "Filter Category",
      "type": "n8n-nodes-base.if",
      "position": [650, 300],
      "typeVersion": 1
    },
    {
      "parameters": {
        "model": "gpt-4",
        "messages": {
          "values": [
            {
              "role": "system",
              "content": "คุณเป็นนักเขียนคอนเทนต์โซเชียลมีเดีย..."
            },
            {
              "role": "user",
              "content": "วิเคราะห์ข่าว:\n\nหัวข้อ: {{$json.title}}\nสรุป: {{$json.summary}}\n\nตอบกลับเป็น JSON..."
            }
          ]
        },
        "options": {
          "temperature": 0.7,
          "maxTokens": 500
        }
      },
      "name": "OpenAI",
      "type": "n8n-nodes-base.openAi",
      "position": [850, 300],
      "typeVersion": 1
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Split Articles", "type": "main", "index": 0}]]
    },
    "Split Articles": {
      "main": [[{"node": "Filter Category", "type": "main", "index": 0}]]
    },
    "Filter Category": {
      "main": [[{"node": "OpenAI", "type": "main", "index": 0}]]
    }
  }
}
```

## การทดสอบ

### 1. ทดสอบ Webhook ใน n8n

1. เปิด workflow ใน n8n
2. คลิก "Listen for Test Event" ที่ Webhook node
3. ส่ง test request:

```powershell
# PowerShell
$body = @{
    event = "new_articles"
    count = 1
    articles = @(
        @{
            id = 1
            title = "ทดสอบข่าว"
            summary = "สรุปข่าวทดสอบ"
            url = "https://example.com"
            category = "news"
            tags = @("ทดสอบ")
        }
    )
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "YOUR_WEBHOOK_URL" -Method Post -Body $body -ContentType "application/json"
```

### 2. ทดสอบจาก API

```powershell
# Trigger manual fetch
curl -X POST http://localhost:8000/articles/fetch
```

ถ้าตั้งค่า webhook ถูกต้อง n8n จะได้รับข้อมูลทันที!

### 3. ดู Logs

```powershell
# ดู API logs
docker compose logs -f api

# ควรเห็น:
# "Sent 5 articles to webhook: https://..."
```

## การป้องกันความปลอดภัย

### ใช้ Webhook Secret

1. ตั้งค่าใน `.env`:
```bash
WEBHOOK_SECRET=my-super-secret-key-123
```

2. ใน n8n Webhook node:
   - เปิด **Header Auth**
   - Header Name: `X-Webhook-Secret`
   - Header Value: `my-super-secret-key-123`

3. n8n จะตรวจสอบ header ก่อนรับข้อมูล

### ใช้ HTTPS

ถ้า n8n อยู่บน internet ให้ใช้ HTTPS:
```bash
WEBHOOK_URL=https://your-n8n-server.com/webhook/thai-news
```

## เปรียบเทียบ Pull vs Push

### Pull Model (เดิม):
```
n8n (Cron 09:00) → GET /articles → API → ส่งข้อมูลกลับ
n8n (Cron 13:00) → GET /articles → API → ส่งข้อมูลกลับ
n8n (Cron 19:00) → GET /articles → API → ส่งข้อมูลกลับ
```
- ❌ ได้ข้อมูลช้า (รอถึงเวลา cron)
- ❌ อาจพลาดข่าว (ถ้ามีข่าวระหว่างเวลา)
- ❌ ต้อง filter ใน n8n

### Push Model (ใหม่):
```
API (Scrape เสร็จ) → POST webhook → n8n → ได้ข้อมูลทันที
```
- ✅ Real-time
- ✅ ไม่พลาดข่าว
- ✅ ง่ายกว่า

## Troubleshooting

### ปัญหา: n8n ไม่ได้รับข้อมูล

**ตรวจสอบ**:
1. Webhook URL ถูกต้องไหม?
2. `WEBHOOK_ENABLED=true` ใน `.env` หรือยัง?
3. API restart แล้วหรือยัง?
4. ดู logs: `docker compose logs -f api`

### ปัญหา: Webhook error 401/403

**วิธีแก้**:
- ตรวจสอบ `WEBHOOK_SECRET` ตรงกันใน `.env` และ n8n
- หรือปิด authentication ใน n8n webhook node

### ปัญหา: ได้ข้อมูลซ้ำ

**วิธีแก้**:
- API จะส่งเฉพาะข่าวใหม่เท่านั้น (ที่สร้างใน 1 นาทีที่แล้ว)
- ถ้ายังซ้ำ ให้เพิ่ม deduplication ใน n8n

## สรุป

### ขั้นตอนสั้นๆ:

1. **สร้าง Webhook ใน n8n** → คัดลอก URL
2. **ตั้งค่า `.env`**:
   ```bash
   WEBHOOK_ENABLED=true
   WEBHOOK_URL=https://your-n8n.com/webhook/thai-news
   ```
3. **Restart API**: `docker compose restart api`
4. **ทดสอบ**: `curl -X POST http://localhost:8000/articles/fetch`
5. **เช็ค n8n** → ควรได้รับข้อมูล!

---

**แบบนี้ดีกว่าไหมครับ?** API จะส่งข้อมูลไปหา n8n เอง ไม่ต้องให้ n8n มาดึง! 🚀
