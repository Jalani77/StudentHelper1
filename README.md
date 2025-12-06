# YiriAi v2.0 - GSU Course Selection Assistant 🎓

**Production-ready FastAPI agent for Georgia State University course selection automation**

YiriAi helps GSU students find the perfect courses by:
- 📚 **Real-time scraping** of GSU PAWS/Banner with actual seat availability
- ⭐ **Live professor ratings** from RateMyProfessors GraphQL API  
- 🚀 **Multi-layer caching** (Redis + PostgreSQL) for instant responses
- 🎯 **Intelligent matching** based on preferences, times, and ratings
- 🔒 **Zero credential risk** - students log into PAWS themselves

> **New in v2.0**: Real data integration, production-grade caching, retry logic, structured logging, database persistence

## 🚀 Features

### Production-Ready
- ✅ **Real Banner Parsing**: Direct GSU PAWS/Banner system integration
- ✅ **Live Professor Data**: RateMyProfessors GraphQL API with actual ratings
- ✅ **Smart Caching**: 3-tier (Memory → Redis → PostgreSQL) with TTL
- ✅ **Retry Logic**: Exponential backoff for network failures
- ✅ **Structured Logging**: JSON logs for monitoring
- ✅ **Database Persistence**: Historical data and cache fallback
- ✅ **Battle-Tested**: Error handling, timeouts, rate limiting

### Core Features
- 🎯 **Smart Matching**: Preferences, priorities, time slots, ratings
- 📊 **Real-Time Data**: Actual seat counts from PAWS
- 🔍 **Advanced Search**: By subject, course, keyword, professor
- ⚡ **Fast Response**: 80-95% cache hit rate
- 🛡️ **No Credentials**: Selection only, never registration
- 📱 **API-First**: RESTful endpoints for integration

## 📋 Requirements

### Runtime
- Python 3.9+
- PostgreSQL 13+ (data caching)
- Redis 6+ (fast caching)

### Optional
- Docker & Docker Compose (recommended)
- nginx (production reverse proxy)

## 🛠️ Quick Start

### Using Docker (Recommended)

```bash
# Clone and setup
git clone <your-repo-url>
cd StudentHelper1
./setup.sh

# Start databases
docker-compose up -d

# Initialize database
python init_db.py

# Start application
python main.py
```

**API available at:** `http://localhost:8000`  
**Documentation:** `http://localhost:8000/docs`

### Manual Installation

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed setup including:
- PostgreSQL and Redis installation
- Environment configuration
- Production deployment
- Monitoring and maintenance

## 📖 Usage

### 1. Upload Course Preferences

```bash
curl -X POST "http://localhost:8000/api/upload-preferences?term=202508" \
  -F "prefs_file=@examples/preferences_example.json" \
  -F "eval_file=@examples/transcript_example.json"
```

**Response:**
```json
{
  "matched_courses": [
    {
      "crn": "12345",
      "subject": "CSC",
      "course_number": "2510",
      "title": "Theoretical Foundations",
      "professor": "John Smith",
      "professor_rating": 4.5,
      "seats_available": 5,
      "days": ["M", "W", "F"],
      "time": "09:00-09:50"
    }
  ],
  "paws_link": "https://www.gosolar.gsu.edu/...",
  "total_credits": 12,
  "instructions": "Steps to register..."
}
```

### 2. Search Courses

```bash
curl "http://localhost:8000/api/search-courses?term=202508&subject=CSC"
```

### 3. Get Professor Rating

```bash
curl "http://localhost:8000/api/professor-rating/John%20Smith"
```

### 4. Check System Health

```bash
curl "http://localhost:8000/health"
```

## 📁 File Formats

### Preferences File (JSON)

```json
{
  "courses": [
    {
      "subject": "CSC",
      "course_number": "2510",
      "priority": 1,
      "online_only": false
    },
    {
      "subject": "MATH",
      "priority": 2
    }
  ],
  "subjects": ["CSC", "MATH"],
  "max_credits": 15,
  "avoid_time_conflicts": true,
  "min_professor_rating": 3.5
}
```

See `examples/` directory for CSV and Excel formats.

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────────┐
    │ Cache Layer │  (3-tier)
    └────┬────────┘
         │
    ┌────┴────┬─────────┐
    │         │         │
┌───▼───┐ ┌──▼───┐ ┌───▼────┐
│ Redis │ │ PgSQL│ │ Memory │
└───┬───┘ └──┬───┘ └───┬────┘
    │        │         │
    └────────┴─────────┘
             │
    ┌────────▼────────┐
    │    Scrapers     │
    ├─────────────────┤
    │ PAWS  │   RMP   │
    └───┬───┴────┬────┘
        │        │
    ┌───▼───┐ ┌──▼──────┐
    │  GSU  │ │  RateMyP│
    │ PAWS  │ │ rofessor│
    └───────┘ └─────────┘
```

### Caching Strategy

1. **Memory**: Fast, session-scoped
2. **Redis**: Shared, fast, TTL-based
3. **PostgreSQL**: Persistent backup
4. **Flow**: Memory → Redis → DB → Scrape

## ⚙️ Configuration

Edit `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/yiriai_db

# Redis
REDIS_URL=redis://localhost:6379/0

# Cache TTL (seconds)
CACHE_TTL_COURSES=3600      # 1 hour
CACHE_TTL_PROFESSOR=86400   # 24 hours

# Scraping
SCRAPER_TIMEOUT=30
SCRAPER_MAX_RETRIES=3
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full configuration options.

## 📊 Monitoring

### Health Checks

```bash
# Basic
curl http://localhost:8000/

# Detailed
curl http://localhost:8000/health

# Statistics
curl http://localhost:8000/api/stats
```

### Cache Management

```bash
# Clear specific pattern
curl -X POST "http://localhost:8000/api/cache/clear?pattern=courses:*"
```

### Database Monitoring

```sql
-- Active cache entries
SELECT subject, COUNT(*) FROM course_cache 
WHERE expires_at > NOW() GROUP BY subject;

-- Scraper success rate
SELECT source, status, COUNT(*) FROM scraper_logs 
WHERE created_at > NOW() - INTERVAL '1 day' 
GROUP BY source, status;
```

## 🎯 GSU-Specific Information

### Term Codes
- **Spring 2025**: `202508`
- **Summer 2025**: `202514`
- **Fall 2025**: `202518`

Format: `YYYYSS` (YYYY=year, SS=semester)

### Common Subjects
- CSC: Computer Science
- MATH: Mathematics  
- ENGL: English
- BIOL: Biology
- CHEM: Chemistry

### PAWS Maintenance
GSU typically performs maintenance:
- Sundays 12am-6am EST
- Heavy traffic during registration periods

## 🔧 Performance

**Expected metrics** (with warm cache):

| Operation | Response Time | Cache Hit Rate |
|-----------|---------------|----------------|
| Course search | 50-200ms | 85-95% |
| Professor rating | 100-300ms | 90-98% |
| Full preferences | 2-10s | 80-90% |

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check PostgreSQL
sudo systemctl status postgresql
psql postgresql://yiriai:yiriai_pass@localhost:5432/yiriai_db -c "SELECT 1"
```

### Redis Connection Error
```bash
# Check Redis
redis-cli ping
```

### PAWS Scraping Fails
- Check GSU PAWS accessibility
- Increase timeout in `.env`
- Check `scraper_logs` table

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## 🔒 Security

### No Credential Risk

YiriAi **never** handles student credentials:
- ✅ Scrapes public PAWS data
- ✅ Provides CRNs and link
- ✅ Student logs in themselves
- ❌ Never stores passwords
- ❌ Never performs registration

### Best Practices
1. Change default passwords in `.env`
2. Never commit `.env` file
3. Use HTTPS in production
4. Enable rate limiting
5. Regular dependency updates

## 🚀 Deployment

### Production with Systemd

```bash
# Create service
sudo nano /etc/systemd/system/yiriai.service

# Enable and start
sudo systemctl enable yiriai
sudo systemctl start yiriai
```

### Docker Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Scaling

Use nginx for load balancing:
```nginx
upstream yiriai {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

## 📚 Documentation

- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete production setup guide
- **[API Docs](http://localhost:8000/docs)**: Interactive API documentation
- **[Examples](examples/)**: Sample preference and transcript files

## 🤝 Contributing

This is an educational project for GSU students. Contributions welcome!

## 📄 License

MIT License - See LICENSE file

## ⚠️ Disclaimer

**Educational tool for course selection only.** YiriAi automates finding courses but NOT registration. Students must manually log into PAWS to register. Always verify course information through official GSU channels.

## 📞 Support

1. Check [DEPLOYMENT.md](DEPLOYMENT.md) for setup issues
2. Review logs: `scraper_logs` table
3. Check cache statistics endpoint
4. Open an issue in the repository

---

**Built with ❤️ for GSU students | Production v2.0**

**Key Changes from v1.0:**
- ✨ Real GSU PAWS/Banner integration
- ✨ Live RateMyProfessors GraphQL API
- ✨ Multi-layer caching (Redis + PostgreSQL)
- ✨ Production-grade error handling
- ✨ Structured logging and monitoring
- ✨ Database persistence and history
