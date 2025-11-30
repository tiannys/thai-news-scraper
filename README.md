# Thai News Scraper & AI Content Generator

[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/fastapi-latest-teal.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

ระบบดึงข่าวจากแหล่งข่าวไทย วิเคราะห์เทรนด์ และสร้างไอเดียคอนเทนต์โซเชียลมีเดียด้วย AI

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 2GB+ RAM
- 20GB+ disk space

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/thai-news-scraper.git
cd thai-news-scraper

# Copy and configure environment
cp .env.example .env
nano .env  # แก้ไข WEBHOOK_URL และ settings อื่นๆ

# Start services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f api
```

### Verify Installation

```bash
# Check API health
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/docs

# Trigger manual fetch
curl -X POST http://localhost:8000/articles/fetch
```

## ✨ Features

- ✅ RSS feed scraping with robots.txt compliance
- ✅ Content deduplication (SHA256)
- ✅ Trend extraction and analysis
- ✅ RESTful API with auto-documentation
- ✅ Automated scheduling (APScheduler)
- ✅ PostgreSQL database
- ✅ Webhook notifications to n8n
- ✅ Docker containerization
- ✅ Production-ready

## 🏗️ Architecture

```
┌─────────────────┐
│  News Sources   │ (RSS Feeds)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Scraper API (FastAPI)     │
│   - RSS Parser              │
│   - Normalizer              │
│   - Deduplicator            │
│   - PostgreSQL              │
│   - Webhook Notifier        │
└────────┬────────────────────┘
         │ POST (webhook)
         ▼
┌─────────────────────────────┐
│   n8n Workflow              │
│   - OpenAI GPT-4            │
│   - Content Generation      │
│   - Line/Notion/Sheets      │
└─────────────────────────────┘
```

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Ubuntu deployment guide
- **[N8N_CONNECTION_GUIDE.md](N8N_CONNECTION_GUIDE.md)** - n8n webhook setup
- **[N8N_WORKFLOW.md](N8N_WORKFLOW.md)** - Complete workflow guide
- **[OPENAI_PROMPT.md](OPENAI_PROMPT.md)** - Prompt engineering
- **[COPYRIGHT_TOS.md](COPYRIGHT_TOS.md)** - Legal compliance
- **[EXPANSION_ROADMAP.md](EXPANSION_ROADMAP.md)** - Future features

## 🔧 Configuration

### Environment Variables

Key settings in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://newsuser:newspassword@db:5432/thai_news

# Scraper
SCRAPER_DELAY_SECONDS=2
SCHEDULER_FETCH_INTERVAL_MINUTES=30

# Webhook (n8n)
WEBHOOK_ENABLED=true
WEBHOOK_URL=https://your-n8n.com/webhook/thai-news
WEBHOOK_SECRET=your-secret-key

# API
API_PORT=8000
```

### News Sources

Edit `sources.yaml` to add/remove sources:

```yaml
sources:
  - name: "ThaiPBS News"
    type: "rss"
    url: "https://news.thaipbs.or.th/rss/news.xml"
    category: "news"
    country: "TH"
    language: "th"
```

## 🔌 API Endpoints

```bash
# Get recent articles
GET /articles?limit=50&since=2024-01-01T00:00:00

# Get single article
GET /articles/{id}

# Trigger manual fetch
POST /articles/fetch

# Get today's trends
GET /trends/today

# Get trends by date
GET /trends/date/2024-01-01

# Health check
GET /health

# API documentation
GET /docs
```

## 🤖 n8n Integration

### Webhook Setup

1. Create webhook in n8n (POST method)
2. Copy webhook URL
3. Configure in `.env`:
   ```bash
   WEBHOOK_ENABLED=true
   WEBHOOK_URL=https://your-n8n.com/webhook/thai-news
   ```
4. Restart API: `docker compose restart api`

### Webhook Payload

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
      "tags": ["การเมือง"]
    }
  ]
}
```

See [N8N_CONNECTION_GUIDE.md](N8N_CONNECTION_GUIDE.md) for details.

## 🐧 Linux Deployment

### Ubuntu/Debian

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Clone and start
git clone https://github.com/YOUR_USERNAME/thai-news-scraper.git
cd thai-news-scraper
cp .env.example .env
nano .env  # Configure settings
docker compose up -d
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete guide.

## 📊 Database Schema

- **sources** - News source configuration
- **articles** - Scraped articles with metadata
- **trends** - Trending keywords and topics
- **content_ideas** - AI-generated content (optional)

## 🛡️ Legal & Compliance

This system:
- ✅ Uses only RSS feeds (legally published)
- ✅ Respects robots.txt
- ✅ Implements rate limiting
- ✅ Provides attribution
- ❌ Never republishes full articles
- ❌ Never claims content as original

See [COPYRIGHT_TOS.md](COPYRIGHT_TOS.md) for guidelines.

## 🔍 Monitoring

```bash
# View logs
docker compose logs -f api

# Check container status
docker compose ps

# Database backup
docker compose exec db pg_dump -U newsuser thai_news > backup.sql

# Container stats
docker stats
```

## 🧪 Testing

```bash
# Test RSS parser
curl -X POST http://localhost:8000/articles/fetch

# Check articles
curl http://localhost:8000/articles?limit=10

# Check trends
curl http://localhost:8000/trends/today
```

## 🚧 Troubleshooting

### API won't start
```bash
docker compose logs api
docker compose restart api
```

### No articles fetched
```bash
# Check sources
cat sources.yaml

# Trigger manual fetch
curl -X POST http://localhost:8000/articles/fetch
```

### Database connection error
```bash
docker compose restart db
docker compose ps
```

## 📈 Performance

- **Scraping**: Every 30 minutes (configurable)
- **Deduplication**: SHA256 hash-based
- **Database**: PostgreSQL with indexes
- **API**: Async FastAPI with uvicorn
- **Scalability**: Docker-ready, horizontal scaling

## 🗺️ Roadmap

- [ ] Additional categories (travel, food, tech)
- [ ] YouTube/TikTok trending integration
- [ ] ML-based content scoring
- [ ] Multi-modal content (images, videos)
- [ ] Advanced analytics dashboard
- [ ] Auto-publishing to social media

See [EXPANSION_ROADMAP.md](EXPANSION_ROADMAP.md) for details.

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- Thai news sources for RSS feeds
- OpenAI for GPT-4 API
- n8n for workflow automation
- FastAPI framework

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/thai-news-scraper/issues)
- **Documentation**: See `/docs` folder
- **API Docs**: http://localhost:8000/docs

## 📊 Project Stats

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15
- **Automation**: APScheduler + n8n
- **AI**: OpenAI GPT-4
- **Deployment**: Docker + Docker Compose

---

**Made with ❤️ for Thai content creators**

⭐ Star this repo if you find it useful!
