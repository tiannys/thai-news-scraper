# n8n Workflow Setup Guide

This guide provides detailed instructions for setting up the n8n automation workflow to generate AI-powered Thai content ideas from scraped news.

## Overview

The n8n workflow will:
1. Run on a schedule (09:00, 13:00, 19:00 Thai time)
2. Fetch new articles from the scraper API
3. Filter for news/lifestyle content
4. Generate Thai content ideas using OpenAI
5. Send results to Line/Notion/Google Sheets

## Prerequisites

- n8n instance running (included in docker-compose.yml)
- OpenAI API key
- Line Notify token OR Notion integration OR Google Sheets access

## Step 1: Access n8n

1. Open browser: `http://your-server-ip:5678`
2. Login with credentials from docker-compose.yml
3. Click "Add workflow" to create a new workflow

## Step 2: Workflow Structure

Here's the complete node-by-node breakdown:

### Node 1: Cron Trigger

**Purpose**: Schedule workflow execution at specific times

**Configuration**:
- **Node Type**: Schedule Trigger
- **Trigger Times**: Custom
- **Mode**: Every Day
- **Hour**: 9, 13, 19
- **Minute**: 0
- **Timezone**: Asia/Bangkok

**Settings**:
```json
{
  "mode": "everyDay",
  "hour": 9,
  "minute": 0,
  "timezone": "Asia/Bangkok"
}
```

**Note**: Add three separate cron nodes or use a single cron with multiple executions.

---

### Node 2: HTTP Request - Fetch Articles

**Purpose**: Get new articles from the scraper API

**Configuration**:
- **Node Type**: HTTP Request
- **Method**: GET
- **URL**: `http://api:8000/articles?limit=50&since={{$now.minus({hours: 6}).toISO()}}`
- **Authentication**: None (or API Key if configured)
- **Response Format**: JSON

**Expression for 'since' parameter**:
```javascript
{{$now.minus({hours: 6}).toISO()}}
```

This fetches articles from the last 6 hours.

**Headers**:
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

---

### Node 3: Filter - News/Lifestyle Only

**Purpose**: Filter articles to only news and lifestyle categories

**Configuration**:
- **Node Type**: Filter
- **Conditions**: Keep items if

**Condition 1**:
- **Field**: `{{$json.category}}`
- **Operation**: equals
- **Value**: `news`

**Condition 2** (OR):
- **Field**: `{{$json.category}}`
- **Operation**: equals
- **Value**: `lifestyle`

**Condition 3** (OR):
- **Field**: `{{$json.category}}`
- **Operation**: equals
- **Value**: `entertainment`

**Combine**: Any condition matches (OR)

---

### Node 4: Code - Prepare Article Data

**Purpose**: Format article data for OpenAI

**Configuration**:
- **Node Type**: Code
- **Mode**: Run Once for All Items

**JavaScript Code**:
```javascript
// Extract articles from response
const articles = items[0].json.articles || [];

// Prepare data for OpenAI
const preparedArticles = articles.slice(0, 10).map(article => ({
  id: article.id,
  title: article.title,
  summary: article.summary || '',
  category: article.category,
  url: article.url,
  published_at: article.published_at
}));

return preparedArticles.map(article => ({json: article}));
```

---

### Node 5: OpenAI - Generate Content Ideas

**Purpose**: Generate Thai social media content ideas

**Configuration**:
- **Node Type**: OpenAI
- **Resource**: Chat
- **Model**: gpt-4 (or gpt-3.5-turbo for lower cost)
- **Messages**: System + User

**System Message**:
```
คุณเป็นนักเขียนคอนเทนต์โซเชียลมีเดียมืออาชีพสำหรับเพจข่าวและไลฟ์สไตล์ไทย 
งานของคุณคือวิเคราะห์ข่าวและสร้างไอเดียคอนเทนต์ที่น่าสนใจ ดึงดูดความสนใจ และเหมาะกับโซเชียลมีเดีย

คุณต้องคิดเชิงกลยุทธ์:
- มุมมองที่ไม่เหมือนใคร (unique angle)
- ประโยคเปิดที่ดึงดูดความสนใจ (hook)
- แคปชันที่กระชับและน่าสนใจ
- แฮชแท็กที่เกี่ยวข้อง
- รูปแบบคอนเทนต์ที่เหมาะสม

ตอบกลับเป็น JSON เท่านั้น ไม่ต้องมีคำอธิบายเพิ่มเติม
```

**User Message**:
```
วิเคราะห์ข่าวนี้และสร้างไอเดียคอนเทนต์โซเชียลมีเดีย:

หัวข้อ: {{$json.title}}
สรุป: {{$json.summary}}
หมวดหมู่: {{$json.category}}

ตอบกลับในรูปแบบ JSON:
{
  "angle": "มุมการเล่าที่ไม่เหมือนใคร",
  "hook": "ประโยคเปิดที่ดึงดูดความสนใจ (ไม่เกิน 100 ตัวอักษร)",
  "caption": "แคปชันโพสต์โซเชียล (ไม่เกิน 300 ตัวอักษร)",
  "hashtags": ["#แท็ก1", "#แท็ก2", "#แท็ก3"],
  "format": "รูปภาพ/Carousel/Reel/Story"
}
```

**Options**:
- **Temperature**: 0.7 (creative but controlled)
- **Max Tokens**: 500
- **Response Format**: JSON Object

**Important**: Enable "JSON Mode" in OpenAI settings

---

### Node 6: Code - Parse OpenAI Response

**Purpose**: Parse and validate JSON response from OpenAI

**Configuration**:
- **Node Type**: Code
- **Mode**: Run Once for Each Item

**JavaScript Code**:
```javascript
const article = items[0].json;
const openaiResponse = $input.item.json;

// Parse OpenAI response
let contentIdea;
try {
  // OpenAI returns JSON in message.content
  const content = openaiResponse.choices[0].message.content;
  contentIdea = JSON.parse(content);
} catch (error) {
  // Fallback if parsing fails
  contentIdea = {
    angle: "ไม่สามารถสร้างได้",
    hook: article.title,
    caption: article.summary,
    hashtags: ["#ข่าว", "#ไทย"],
    format: "รูปภาพ"
  };
}

// Combine with original article data
return {
  json: {
    article_id: article.id,
    article_title: article.title,
    article_url: article.url,
    article_category: article.category,
    ...contentIdea,
    generated_at: new Date().toISOString()
  }
};
```

---

### Node 7a: Line Notify (Option 1)

**Purpose**: Send content ideas to Line

**Configuration**:
- **Node Type**: HTTP Request
- **Method**: POST
- **URL**: `https://notify-api.line.me/api/notify`
- **Authentication**: Header Auth
  - **Name**: Authorization
  - **Value**: `Bearer YOUR_LINE_NOTIFY_TOKEN`

**Body**:
```
🎯 ไอเดียคอนเทนต์ใหม่!

📰 ข่าว: {{$json.article_title}}

💡 มุมการเล่า: {{$json.angle}}

🎣 Hook: {{$json.hook}}

✍️ Caption:
{{$json.caption}}

🏷️ Hashtags: {{$json.hashtags.join(' ')}}

📱 Format: {{$json.format}}

🔗 {{$json.article_url}}
```

**How to get Line Notify Token**:
1. Go to https://notify-bot.line.me/
2. Login with Line account
3. Click "Generate token"
4. Select chat room
5. Copy token

---

### Node 7b: Notion (Option 2)

**Purpose**: Add content ideas to Notion database

**Configuration**:
- **Node Type**: Notion
- **Resource**: Database Page
- **Operation**: Create
- **Database ID**: Your Notion database ID

**Properties**:
- **Title**: `{{$json.article_title}}`
- **Angle** (Text): `{{$json.angle}}`
- **Hook** (Text): `{{$json.hook}}`
- **Caption** (Text): `{{$json.caption}}`
- **Hashtags** (Multi-select): `{{$json.hashtags}}`
- **Format** (Select): `{{$json.format}}`
- **URL** (URL): `{{$json.article_url}}`
- **Category** (Select): `{{$json.article_category}}`
- **Generated** (Date): `{{$json.generated_at}}`

**Setup Notion Integration**:
1. Go to https://www.notion.so/my-integrations
2. Create new integration
3. Copy integration token
4. Share database with integration
5. Get database ID from URL

---

### Node 7c: Google Sheets (Option 3)

**Purpose**: Append content ideas to Google Sheets

**Configuration**:
- **Node Type**: Google Sheets
- **Resource**: Sheet
- **Operation**: Append
- **Document**: Your spreadsheet
- **Sheet**: Sheet1

**Columns**:
- A: `{{$json.generated_at}}`
- B: `{{$json.article_category}}`
- C: `{{$json.article_title}}`
- D: `{{$json.angle}}`
- E: `{{$json.hook}}`
- F: `{{$json.caption}}`
- G: `{{$json.hashtags.join(', ')}}`
- H: `{{$json.format}}`
- I: `{{$json.article_url}}`

**Setup Google Sheets**:
1. Create Google Cloud project
2. Enable Google Sheets API
3. Create OAuth credentials
4. Connect in n8n

---

## Complete Workflow JSON

You can import this workflow directly into n8n:

```json
{
  "name": "Thai News Content Generator",
  "nodes": [
    {
      "parameters": {
        "rule": {
          "interval": [
            {
              "field": "hours",
              "hoursInterval": 1
            }
          ]
        }
      },
      "name": "Schedule Trigger",
      "type": "n8n-nodes-base.scheduleTrigger",
      "position": [250, 300]
    },
    {
      "parameters": {
        "method": "GET",
        "url": "http://api:8000/articles",
        "queryParameters": {
          "parameters": [
            {
              "name": "limit",
              "value": "50"
            },
            {
              "name": "since",
              "value": "={{$now.minus({hours: 6}).toISO()}}"
            }
          ]
        }
      },
      "name": "Fetch Articles",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300]
    }
  ],
  "connections": {
    "Schedule Trigger": {
      "main": [[{"node": "Fetch Articles", "type": "main", "index": 0}]]
    }
  }
}
```

## Testing the Workflow

1. **Test Individual Nodes**:
   - Click on each node
   - Click "Execute Node"
   - Verify output

2. **Test Full Workflow**:
   - Click "Execute Workflow"
   - Check each node's output
   - Verify final delivery (Line/Notion/Sheets)

3. **Check OpenAI Usage**:
   - Monitor OpenAI dashboard
   - Each execution = 10 articles × API calls
   - Estimate: ~$0.05-0.10 per execution with GPT-4

## Troubleshooting

### OpenAI returns invalid JSON

- Increase temperature to 0.5
- Add more specific instructions
- Use GPT-4 instead of GPT-3.5

### No articles fetched

- Check API is running: `curl http://api:8000/health`
- Verify time range in 'since' parameter
- Check article categories match filter

### Line Notify fails

- Verify token is correct
- Check token hasn't expired
- Ensure Line app is installed

### Workflow doesn't run on schedule

- Check timezone setting
- Verify n8n is running
- Check n8n logs: `docker compose logs n8n`

## Optimization Tips

1. **Reduce OpenAI Costs**:
   - Use GPT-3.5-turbo instead of GPT-4
   - Reduce max_tokens to 300
   - Process fewer articles (top 5 instead of 10)

2. **Improve Content Quality**:
   - Add more context in system message
   - Include trending topics
   - Provide examples in prompt

3. **Better Filtering**:
   - Add keyword filters
   - Check article engagement metrics
   - Filter by source quality

## Next Steps

1. Monitor workflow executions
2. Collect feedback on generated content
3. Refine OpenAI prompts
4. Add more output channels
5. Implement content scoring
