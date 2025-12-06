# 🚀 YiriAi v2.0 - Quick Start Guide

Get YiriAi running in **5 minutes** with real GSU data integration!

## Prerequisites Check

```bash
# Check Python version (need 3.9+)
python3 --version

# Check if Docker is available (recommended)
docker --version
docker-compose --version
```

## Installation Steps

### Step 1: Clone and Setup (1 min)

```bash
# Clone repository
git clone <your-repo-url>
cd StudentHelper1

# Run automated setup
./setup.sh
```

This installs all Python dependencies and creates configuration files.

### Step 2: Start Databases (1 min)

**Option A: Using Docker (Recommended)**
```bash
# Start PostgreSQL and Redis
docker-compose up -d

# Verify they're running
docker-compose ps
```

**Option B: Manual Installation**
- Install PostgreSQL 13+ and create database `yiriai_db`
- Install Redis 6+ and start service
- Update DATABASE_URL and REDIS_URL in `.env`

### Step 3: Initialize Database (30 sec)

```bash
# Create database tables
python init_db.py
```

Expected output:
```
✓ Database tables created successfully
✓ Created tables: course_cache, professor_cache, scraper_logs
Database initialization complete!
```

### Step 4: Test Installation (1 min)

```bash
# Run production test suite
python test_production.py
```

This tests:
- ✓ Redis cache connection
- ✓ PostgreSQL database
- ✓ PAWS scraper (real GSU data)
- ✓ RateMyProfessors API
- ✓ Full integration

### Step 5: Start Application (30 sec)

```bash
# Start the API server
python main.py
```

Or for development with auto-reload:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**API is now running!**
- Main API: http://localhost:8000
- Health check: http://localhost:8000/health
- Documentation: http://localhost:8000/docs

## First API Request

### Upload Course Preferences

```bash
curl -X POST "http://localhost:8000/api/upload-preferences?term=202508" \
  -F "prefs_file=@examples/preferences_example.json" \
  -F "eval_file=@examples/transcript_example.json"
```

This will:
1. Parse your preferences
2. Scrape real GSU PAWS data for Spring 2025
3. Fetch professor ratings from RateMyProfessors
4. Match courses based on your criteria
5. Return CRNs ready for registration

### Response Example

```json
{
  "matched_courses": [
    {
      "crn": "12345",
      "subject": "CSC",
      "course_number": "2510",
      "title": "Theoretical Foundations of CS",
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

## Verify Everything Works

### 1. Check Health
```bash
curl http://localhost:8000/health
```

Should return `"status": "healthy"`

### 2. Check Cache
```bash
curl http://localhost:8000/api/stats
```

Should show Redis and database connected

### 3. Search Courses
```bash
curl "http://localhost:8000/api/search-courses?term=202508&subject=CSC"
```

Should return real CSC courses

### 4. Get Professor Rating
```bash
curl "http://localhost:8000/api/professor-rating/John%20Smith"
```

May return 404 if professor not found (expected)

## Common Issues & Fixes

### "Cannot connect to database"

**Fix:**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Or if manual install:
sudo systemctl status postgresql

# Restart if needed:
docker-compose restart postgres
```

### "Redis connection error"

**Fix:**
```bash
# Check if Redis is running
docker-compose ps

# Or if manual install:
redis-cli ping

# Should respond with: PONG

# Restart if needed:
docker-compose restart redis
```

### "PAWS scraping failed"

**Possible causes:**
1. GSU PAWS is under maintenance (check time)
2. Network connectivity issue
3. Term code is invalid

**Fix:**
- Try different term (e.g., 202508 for Spring 2025)
- Check if https://www.gosolar.gsu.edu is accessible
- Increase timeout in `.env`: `SCRAPER_TIMEOUT=60`

### "Module not found"

**Fix:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

## Configuration Tips

### Adjust Cache Duration

Edit `.env`:
```bash
# More caching (less scraping, faster responses)
CACHE_TTL_COURSES=7200      # 2 hours
CACHE_TTL_PROFESSOR=604800  # 7 days

# Less caching (fresher data, more scraping)
CACHE_TTL_COURSES=900       # 15 minutes
CACHE_TTL_PROFESSOR=3600    # 1 hour
```

### Change Port

Edit `.env`:
```bash
PORT=3000  # Change from default 8000
```

Then restart:
```bash
python main.py
```

## File Format Examples

### Preferences File (JSON)

`preferences.json`:
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
  "avoid_time_conflicts": true
}
```

### Transcript File (JSON)

`transcript.json`:
```json
[
  {"subject": "CSC", "course_number": "1301", "grade": "A", "term": "202308"},
  {"subject": "MATH", "course_number": "1111", "grade": "B", "term": "202308"}
]
```

More examples in `examples/` directory!

## Next Steps

1. **Read the docs**: Check out [README.md](README.md) for full features
2. **Production setup**: See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. **Customize**: Edit `.env` to tune performance
4. **Monitor**: Use `/api/stats` to track cache performance
5. **Scale**: Add more instances behind nginx load balancer

## GSU Term Codes

Remember to use correct term codes:
- **Spring 2025**: `202508`
- **Summer 2025**: `202514`
- **Fall 2025**: `202518`

Format: `YYYYSS` where SS is semester (08=Spring, 14=Summer, 18=Fall)

## Getting Help

- **Setup issues**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **API usage**: Visit http://localhost:8000/docs
- **Examples**: Check `examples/` directory
- **Logs**: Check database `scraper_logs` table

## Summary Checklist

- [ ] Dependencies installed (`./setup.sh`)
- [ ] Databases running (`docker-compose up -d`)
- [ ] Database initialized (`python init_db.py`)
- [ ] Tests passing (`python test_production.py`)
- [ ] API running (`python main.py`)
- [ ] Health check works (`curl /health`)
- [ ] Can search courses (`curl /api/search-courses`)

**All checked?** You're ready to use YiriAi! 🎉

## Pro Tips

1. **Cache warmup**: First request is slow (scraping), subsequent requests are fast (cached)
2. **Peak times**: Scrape during off-peak hours (not during GSU registration)
3. **Monitoring**: Check `/api/stats` regularly to monitor cache performance
4. **Clear cache**: Use `/api/cache/clear` if data seems stale
5. **Logs**: Enable debug mode for troubleshooting: `DEBUG=true`

---

**Time to completion: ~5 minutes**

**Ready to find your perfect courses! 🎓**
