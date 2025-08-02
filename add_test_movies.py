"""
Script to add test movies to the database for testing
"""
import asyncio
import logging
from pymongo import MongoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "mongodb+srv://tharu:20020224Ha@cluster0.tn75wcw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
DATABASE_NAME = "Cluster0"
COLLECTION_NAME = "Telegram_files"

client = MongoClient(DATABASE_URL)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def add_test_movies():
    """Add some test movies to the database"""
    test_movies = [
        {
            '_id': 'test_movie_1',
            'file_name': 'Avengers Endgame 2019 1080p BluRay x264',
            'file_size': 2147483648  # 2GB
        },
        {
            '_id': 'test_movie_2', 
            'file_name': 'Spider-Man No Way Home 2021 720p HDCAM',
            'file_size': 1073741824  # 1GB
        },
        {
            '_id': 'test_movie_3',
            'file_name': 'The Batman 2022 1080p WEBRip x264',
            'file_size': 3221225472  # 3GB
        },
        {
            '_id': 'test_movie_4',
            'file_name': 'Top Gun Maverick 2022 4K UHD BluRay x265',
            'file_size': 5368709120  # 5GB
        },
        {
            '_id': 'test_movie_5',
            'file_name': 'John Wick Chapter 4 2023 1080p BluRay',
            'file_size': 2684354560  # 2.5GB
        },
        {
            '_id': 'test_movie_6',
            'file_name': 'Fast X 2023 720p HDRip Hindi Dubbed',
            'file_size': 1610612736  # 1.5GB
        },
        {
            '_id': 'test_movie_7',
            'file_name': 'Oppenheimer 2023 1080p IMAX BluRay x264',
            'file_size': 4294967296  # 4GB
        },
        {
            '_id': 'test_movie_8',
            'file_name': 'Barbie 2023 1080p WEBRip Tamil Dubbed',
            'file_size': 2147483648  # 2GB
        },
        {
            '_id': 'test_movie_9',
            'file_name': 'Mission Impossible Dead Reckoning 2023 720p',
            'file_size': 1879048192  # 1.75GB
        },
        {
            '_id': 'test_movie_10',
            'file_name': 'Guardians of the Galaxy Vol 3 2023 1080p',
            'file_size': 3758096384  # 3.5GB
        }
    ]
    
    added = 0
    already_exists = 0
    
    try:
        for movie in test_movies:
            try:
                # Check if already exists
                existing = collection.find_one({'_id': movie['_id']})
                if existing:
                    logger.info(f"Movie already exists: {movie['file_name']}")
                    already_exists += 1
                    continue
                
                # Insert movie
                collection.insert_one(movie)
                logger.info(f"Added: {movie['file_name']}")
                added += 1
                
            except Exception as e:
                logger.error(f"Error adding {movie['file_name']}: {e}")
        
        logger.info(f"\n✅ Database Update Complete!")
        logger.info(f"📁 Added: {added} new movies")
        logger.info(f"⚠️ Already existed: {already_exists} movies")
        logger.info(f"📊 Total test movies: {len(test_movies)}")
        
        # Verify database content
        total_count = collection.count_documents({})
        logger.info(f"🎬 Total movies in database: {total_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error adding test movies: {e}")
        return False

if __name__ == "__main__":
    add_test_movies()