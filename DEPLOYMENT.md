# YiriAi v2.0 - Production Deployment Guide

## 🚀 Overview

YiriAi v2.0 is a production-ready FastAPI application that automates course selection for Georgia State University students. This version features:

- **Real data integration** with GSU PAWS/Banner system
- **RateMyProfessors GraphQL API** for professor ratings
- **Multi-layer caching** (Redis + PostgreSQL) with TTL management
- **Retry logic** with exponential backoff
- **Structured logging** for monitoring and debugging
- **Database persistence** for historical data
- **No credential handling** - students log into PAWS themselves

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose (recommended) or manual installation

## 🛠️ Installation

### Option 1: Quick Start with Docker (Recommended)

```bash
# Clone repository
git clone <your-repo-url>
cd StudentHelper1

# Run setup script
./setup.sh

# Start database services
docker-compose up -d

# Initialize database
python init_db.py

# Start application
python main.py
```

### Option 2: Manual Installation

#### 1. Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE yiriai_db;
CREATE USER yiriai WITH PASSWORD 'yiriai_pass';
GRANT ALL PRIVILEGES ON DATABASE yiriai_db TO yiriai;
\q
```

**macOS (Homebrew):**
```bash
brew install postgresql@15
brew services start postgresql@15
createdb yiriai_db
```

#### 2. Install Redis

**Ubuntu/Debian:**
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**macOS (Homebrew):**
```bash
brew install redis
brew services start redis
```

#### 3. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

#### 4. Configure Environment

```bash
# Copy and edit configuration
cp .env.example .env
nano .env  # Edit with your settings
```

#### 5. Initialize Database

```bash
python init_db.py
```

#### 6. Start Application

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
python main.py
```

## ⚙️ Configuration

### Environment Variables

Edit `.env` file:

```bash
# Database - Update for your PostgreSQL instance
DATABASE_URL=postgresql+asyncpg://yiriai:yiriai_pass@localhost:5432/yiriai_db

# Redis - Update for your Redis instance
REDIS_URL=redis://localhost:6379/0
REDIS_PASSWORD=your_password_if_any

# Cache TTL (tune based on your needs)
CACHE_TTL_COURSES=3600      # 1 hour - courses change frequently
CACHE_TTL_PROFESSOR=86400   # 24 hours - ratings are stable
CACHE_TTL_SCHEDULE=1800     # 30 min - for search results

# Scraping behavior
SCRAPER_TIMEOUT=30          # Increase if PAWS is slow
SCRAPER_MAX_RETRIES=3       # Retries on failure
SCRAPER_RETRY_DELAY=2       # Seconds between retries
```

### Database Connection Strings

**Local PostgreSQL:**
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname
```

**Docker PostgreSQL:**
```
DATABASE_URL=postgresql+asyncpg://yiriai:yiriai_pass@postgres:5432/yiriai_db
```

**Cloud PostgreSQL (e.g., AWS RDS):**
```
DATABASE_URL=postgresql+asyncpg://user:password@rds-endpoint.region.rds.amazonaws.com:5432/dbname
```

## 🏗️ Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
    ┌────┴────┐
    │  Cache  │
    │  Layer  │
    └────┬────┘
         │
    ┌────┴────────┬──────────┐
    │             │          │
┌───▼───┐  ┌─────▼─────┐ ┌──▼────┐
│ Redis │  │PostgreSQL │ │Memory │
└───┬───┘  └─────┬─────┘ └──┬────┘
    │            │           │
    └────────┬───┴───────────┘
             │
    ┌────────┴────────┐
    │    Scrapers     │
    ├─────────────────┤
    │ PAWS  │   RMP   │
    └───┬───┴────┬────┘
        │        │
    ┌───▼───┐ ┌──▼──────┐
    │ GSU   │ │ RateMyP │
    │ PAWS  │ │ rofessor│
    └───────┘ └─────────┘
```

### Caching Strategy

1. **Memory Cache**: Fast, session-scoped, cleared on restart
2. **Redis Cache**: Shared across instances, fast access, TTL-based
3. **PostgreSQL Cache**: Persistent storage, backup for Redis misses
4. **Cache Hierarchy**: Memory → Redis → Database → Scrape

### Data Flow

1. **Request arrives** → Check memory cache
2. **Cache miss** → Check Redis cache
3. **Redis miss** → Check PostgreSQL cache
4. **DB miss** → Scrape PAWS/RMP
5. **Store results** → All cache layers + database
6. **Return response** → Client receives data

## 📊 Monitoring

### Health Check Endpoints

```bash
# Basic health check
curl http://localhost:8000/

# Detailed health check
curl http://localhost:8000/health

# Application statistics
curl http://localhost:8000/api/stats
```

### Cache Management

```bash
# Clear specific pattern
curl -X POST "http://localhost:8000/api/cache/clear?pattern=courses:202508:*"

# Clear all cache (use with caution)
curl -X POST "http://localhost:8000/api/cache/clear"
```

### Database Monitoring

```bash
# Connect to PostgreSQL
psql postgresql://yiriai:yiriai_pass@localhost:5432/yiriai_db

# Check cache entries
SELECT subject, COUNT(*) FROM course_cache 
WHERE expires_at > NOW() 
GROUP BY subject;

# Check scraper logs
SELECT source, status, COUNT(*) FROM scraper_logs 
WHERE created_at > NOW() - INTERVAL '1 day' 
GROUP BY source, status;

# Check professor cache
SELECT COUNT(*) FROM professor_cache 
WHERE expires_at > NOW();
```

### Redis Monitoring

```bash
# Connect to Redis
redis-cli

# Check cache size
DBSIZE

# Monitor commands in real-time
MONITOR

# Get cache hit rate
INFO stats
```

## 🔧 Production Tuning

### Performance Optimization

1. **Increase cache TTL** for stable data:
   ```bash
   CACHE_TTL_PROFESSOR=604800  # 7 days
   ```

2. **Tune database pool**:
   ```bash
   DATABASE_POOL_SIZE=50
   DATABASE_MAX_OVERFLOW=20
   ```

3. **Increase concurrent requests**:
   ```bash
   SCRAPER_CONCURRENT_REQUESTS=10
   ```

### Memory Management

**Redis maxmemory policy** (add to redis.conf):
```
maxmemory 2gb
maxmemory-policy allkeys-lru
```

**PostgreSQL connection limits** (postgresql.conf):
```
max_connections = 200
shared_buffers = 256MB
```

### Scaling

**Horizontal scaling with multiple instances:**

1. Use same Redis and PostgreSQL instances
2. Load balance with nginx/HAProxy
3. Session affinity not required (stateless)

**Example nginx config:**
```nginx
upstream yiriai {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name yiriai.example.com;
    
    location / {
        proxy_pass http://yiriai;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**1. Database connection errors**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql postgresql://yiriai:yiriai_pass@localhost:5432/yiriai_db -c "SELECT 1"

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

**2. Redis connection errors**
```bash
# Check Redis is running
sudo systemctl status redis

# Test connection
redis-cli ping

# Check logs
sudo tail -f /var/log/redis/redis-server.log
```

**3. PAWS scraping failures**
- Check if GSU PAWS is accessible: `curl https://www.gosolar.gsu.edu`
- Increase timeout: `SCRAPER_TIMEOUT=60`
- Check scraper logs in database

**4. RMP API errors**
- RMP may rate limit: check `scraper_logs` table
- Increase retry delay: `SCRAPER_RETRY_DELAY=5`
- RMP GraphQL schema may change - check for updates

**5. Cache not working**
```bash
# Test Redis connection
python -c "import redis; r = redis.Redis(); print(r.ping())"

# Check cache in application
curl http://localhost:8000/api/stats
```

### Debug Mode

Enable debug logging:
```bash
DEBUG=true
uvicorn main:app --reload --log-level debug
```

### Logs

Application logs are structured JSON:
```bash
tail -f logs/yiriai.log | jq '.'
```

## 🔒 Security

### Best Practices

1. **Change default passwords** in `.env`
2. **Use environment variables** for secrets (never commit .env)
3. **Enable firewall** for database ports
4. **Use HTTPS** in production (reverse proxy)
5. **Rate limit** API endpoints
6. **Regular updates** for dependencies

### No Credential Risk

YiriAi **never** handles student credentials:
- ✅ Scrapes public PAWS schedule data
- ✅ Provides CRNs and registration link
- ✅ Student logs into PAWS themselves
- ❌ Never stores or transmits passwords
- ❌ Never performs actual registration

## 📈 Performance Benchmarks

Expected performance (with warm cache):

- Course search: 50-200ms
- Professor rating: 100-300ms
- Full preference upload: 2-10s (depending on subjects)
- Cache hit rate: 80-95% after warmup

## 🚢 Deployment

### Docker Production Deployment

```bash
# Build image
docker build -t yiriai:latest .

# Run with docker-compose
docker-compose -f docker-compose.prod.yml up -d

# Scale instances
docker-compose -f docker-compose.prod.yml up -d --scale api=3
```

### Systemd Service

Create `/etc/systemd/system/yiriai.service`:
```ini
[Unit]
Description=YiriAi Course Assistant
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=yiriai
WorkingDirectory=/opt/yiriai
Environment="PATH=/opt/yiriai/venv/bin"
ExecStart=/opt/yiriai/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable yiriai
sudo systemctl start yiriai
sudo systemctl status yiriai
```

## 📝 Maintenance

### Regular Tasks

**Daily:**
- Monitor error logs
- Check cache hit rates
- Verify scraper success rates

**Weekly:**
- Review database growth
- Optimize slow queries
- Update professor cache

**Monthly:**
- Update dependencies
- Review scraper logs
- Clean old cache entries

### Backup Strategy

**PostgreSQL backup:**
```bash
# Automated daily backup
pg_dump yiriai_db > backup_$(date +%Y%m%d).sql

# Restore
psql yiriai_db < backup_20250101.sql
```

**Redis persistence:**
Redis automatically saves to disk with AOF enabled.

## 🎯 GSU-Specific Notes

### Term Codes
- Spring 2025: `202508`
- Summer 2025: `202514`
- Fall 2025: `202518`

### Common Subjects
- CSC: Computer Science
- MATH: Mathematics
- ENGL: English
- BIOL: Biology
- CHEM: Chemistry

### PAWS Maintenance Windows
GSU typically performs PAWS maintenance:
- Sundays 12am-6am
- During registration peaks, may be slower

Plan scraping around these times.

## 📞 Support

For production issues:
1. Check logs: `/var/log/yiriai/` or Docker logs
2. Review scraper_logs table in database
3. Check cache statistics endpoint
4. Review this documentation

---

**Built with ❤️ for GSU students | Production-ready v2.0**
