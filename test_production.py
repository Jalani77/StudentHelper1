"""
Production testing script for YiriAi v2.0
Tests real data integration with caching
"""
import asyncio
import sys
from pathlib import Path
import time

sys.path.insert(0, str(Path(__file__).parent))

from scrapers.paws_scraper import PAWSScraper
from scrapers.rmp_scraper import RateMyProfessorsScraper
from cache import cache_manager
from database import init_db
from config import settings
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_cache():
    """Test Redis cache connectivity"""
    logger.info("Testing cache connection...")
    
    try:
        await cache_manager.initialize()
        
        # Test set/get
        test_key = "test:key"
        test_value = {"message": "hello", "timestamp": time.time()}
        
        await cache_manager.set(test_key, test_value, ttl=60)
        retrieved = await cache_manager.get(test_key)
        
        assert retrieved == test_value, "Cache value mismatch"
        
        # Test stats
        stats = await cache_manager.get_stats()
        logger.info(f"✓ Cache connected: {stats}")
        
        # Cleanup
        await cache_manager.delete(test_key)
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Cache test failed: {e}")
        return False


async def test_database():
    """Test PostgreSQL connectivity"""
    logger.info("Testing database connection...")
    
    try:
        await init_db()
        logger.info("✓ Database connected and tables created")
        return True
        
    except Exception as e:
        logger.error(f"✗ Database test failed: {e}")
        return False


async def test_paws_scraper():
    """Test PAWS scraper with real data"""
    logger.info("Testing PAWS scraper...")
    
    scraper = PAWSScraper()
    
    try:
        # Test with a small subject list
        term = "202508"  # Spring 2025
        subjects = ["CSC"]  # Just Computer Science for testing
        
        logger.info(f"Scraping {subjects} for term {term}...")
        start_time = time.time()
        
        courses = await scraper.get_available_courses(
            term=term,
            subjects=subjects,
            open_only=False,
            use_cache=True
        )
        
        duration = time.time() - start_time
        
        logger.info(f"✓ Found {len(courses)} courses in {duration:.2f}s")
        
        if courses:
            course = courses[0]
            logger.info(f"  Sample: {course.subject} {course.course_number} - {course.title}")
            logger.info(f"  CRN: {course.crn}, Seats: {course.seats_available}/{course.total_seats}")
            if course.professor:
                logger.info(f"  Professor: {course.professor}")
        
        # Test cache hit
        logger.info("Testing cache hit...")
        start_time = time.time()
        
        cached_courses = await scraper.get_available_courses(
            term=term,
            subjects=subjects,
            use_cache=True
        )
        
        cache_duration = time.time() - start_time
        logger.info(f"✓ Cache hit: {len(cached_courses)} courses in {cache_duration:.2f}s")
        logger.info(f"  Speedup: {duration/cache_duration:.1f}x faster")
        
        await scraper.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ PAWS scraper test failed: {e}", exc_info=True)
        await scraper.close()
        return False


async def test_rmp_scraper():
    """Test RateMyProfessors scraper"""
    logger.info("Testing RateMyProfessors scraper...")
    
    scraper = RateMyProfessorsScraper()
    
    try:
        # Test with a common professor name (you may need to adjust)
        professor = "John Smith"
        
        logger.info(f"Looking up professor: {professor}")
        start_time = time.time()
        
        rating = await scraper.get_professor_rating(
            professor_name=professor,
            use_cache=True
        )
        
        duration = time.time() - start_time
        
        if rating:
            logger.info(f"✓ Found rating in {duration:.2f}s")
            logger.info(f"  Rating: {rating.get('rating')}/5.0")
            logger.info(f"  Difficulty: {rating.get('difficulty')}/5.0")
            logger.info(f"  Would take again: {rating.get('would_take_again')}%")
            logger.info(f"  Number of ratings: {rating.get('num_ratings')}")
        else:
            logger.info(f"✓ Professor not found (expected for generic name)")
        
        # Test cache hit
        logger.info("Testing cache hit...")
        start_time = time.time()
        
        cached_rating = await scraper.get_professor_rating(
            professor_name=professor,
            use_cache=True
        )
        
        cache_duration = time.time() - start_time
        logger.info(f"✓ Cache hit in {cache_duration:.2f}s")
        
        await scraper.close()
        return True
        
    except Exception as e:
        logger.error(f"✗ RMP scraper test failed: {e}", exc_info=True)
        await scraper.close()
        return False


async def test_integration():
    """Test full integration"""
    logger.info("Testing full integration...")
    
    try:
        paws = PAWSScraper()
        rmp = RateMyProfessorsScraper()
        
        # Get courses
        courses = await paws.get_available_courses(
            term="202508",
            subjects=["MATH"],
            open_only=True,
            use_cache=True
        )
        
        if not courses:
            logger.warning("No courses found for integration test")
            return True
        
        # Get ratings for professors
        professors = list(set(c.professor for c in courses[:5] if c.professor))
        
        logger.info(f"Getting ratings for {len(professors)} professors...")
        
        ratings = await rmp.batch_get_ratings(professors)
        
        logger.info(f"✓ Retrieved {len([r for r in ratings.values() if r])} ratings")
        
        await paws.close()
        await rmp.close()
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        return False


async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("YiriAi v2.0 Production Test Suite")
    logger.info("=" * 60)
    logger.info(f"Database: {settings.database_url}")
    logger.info(f"Redis: {settings.redis_url}")
    logger.info(f"PAWS: {settings.gsu_paws_base_url}")
    logger.info("=" * 60)
    
    results = {}
    
    # Run tests
    tests = [
        ("Cache", test_cache),
        ("Database", test_database),
        ("PAWS Scraper", test_paws_scraper),
        ("RMP Scraper", test_rmp_scraper),
        ("Integration", test_integration),
    ]
    
    for name, test_func in tests:
        logger.info("")
        logger.info(f"Running: {name}")
        logger.info("-" * 60)
        
        try:
            result = await test_func()
            results[name] = result
        except Exception as e:
            logger.error(f"Test {name} raised exception: {e}")
            results[name] = False
        
        await asyncio.sleep(1)  # Brief pause between tests
    
    # Cleanup
    await cache_manager.close()
    
    # Summary
    logger.info("")
    logger.info("=" * 60)
    logger.info("Test Summary")
    logger.info("=" * 60)
    
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{name:20s}: {status}")
    
    all_passed = all(results.values())
    
    logger.info("=" * 60)
    if all_passed:
        logger.info("✓ All tests passed!")
        logger.info("YiriAi v2.0 is ready for production")
    else:
        logger.error("✗ Some tests failed")
        logger.error("Please fix issues before deploying")
    
    logger.info("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
