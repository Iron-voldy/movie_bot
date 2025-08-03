"""
Advanced Auto-Filter Database System - Enhanced like PROFESSOR-BOT
Combines your existing functionality with PROFESSOR-BOT's advanced features
"""
import logging
import re
import asyncio
from struct import pack
import base64
from hydrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError, OperationFailure
from pymongo import MongoClient, ASCENDING, TEXT
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, FILE_DB_URL, FILE_DB_NAME
import aiohttp
import json
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Database connections
primary_client = MongoClient(DATABASE_URL)
primary_db = primary_client[DATABASE_NAME]
primary_col = primary_db[COLLECTION_NAME]

secondary_client = MongoClient(FILE_DB_URL)
secondary_db = secondary_client[FILE_DB_NAME]
secondary_col = secondary_db[COLLECTION_NAME]

# Create indexes for better search performance
try:
    primary_col.create_index([("file_name", TEXT)])
    primary_col.create_index("file_size")
    primary_col.create_index("file_type")
    secondary_col.create_index([("file_name", TEXT)])
    logger.info("Database indexes created successfully")
except Exception as e:
    logger.error(f"Error creating indexes: {e}")

def get_database_size():
    """Get total size of data in both databases"""
    try:
        primary_size = primary_db.command("dbstats")['dataSize']
        secondary_size = secondary_db.command("dbstats")['dataSize']
        return primary_size, secondary_size
    except Exception as e:
        logger.error(f"Error getting database size: {e}")
        return 0, 0

def get_database_count():
    """Get total count of files in both databases"""
    try:
        primary_count = primary_col.count_documents({})
        secondary_count = secondary_col.count_documents({})
        return primary_count, secondary_count
    except Exception as e:
        logger.error(f"Error getting database count: {e}")
        return 0, 0

async def save_file(media):
    """Enhanced file saving with PROFESSOR-BOT style features"""
    try:
        logger.info(f"Processing file for advanced database save...")
        
        # Enhanced file ID processing
        if not hasattr(media, 'file_id') or not media.file_id:
            logger.error("Media object missing file_id")
            return False, 3
            
        # Process file ID with fallback
        try:
            file_id, file_ref = unpack_new_file_id(media.file_id)
        except Exception as e:
            logger.error(f"Error processing file_id: {e}")
            file_id = media.file_id
            file_ref = ""
        
        # Enhanced file name processing (PROFESSOR-BOT style)
        if hasattr(media, 'file_name') and media.file_name:
            # Clean but preserve structure better than simple regex
            file_name = str(media.file_name)
        else:
            file_name = f"Movie_{getattr(media, 'file_unique_id', 'unknown')}"
            if hasattr(media, 'file_type'):
                file_name += f".{media.file_type}"
        
        # Enhanced document structure (PROFESSOR-BOT compatible)
        document = {
            '_id': file_id,
            'file_ref': file_ref,
            'file_name': file_name,
            'file_size': getattr(media, 'file_size', 0),
            'file_type': getattr(media, 'file_type', 'unknown'),
            'file_unique_id': getattr(media, 'file_unique_id', None),
            'mime_type': getattr(media, 'mime_type', None),
            'caption': getattr(media, 'caption', ''),
            'added_time': asyncio.get_event_loop().time()  # For trending analysis
        }
        
        # Try saving with enhanced error handling
        try:
            result = primary_col.insert_one(document)
            logger.info(f'✅ {file_name} saved to primary database')
            return True, 1
        except DuplicateKeyError:
            logger.warning(f'⚠️ {file_name} already exists in primary database')
            return False, 0
        except OperationFailure as e:
            if 'quota' in str(e).lower():
                logger.warning("Primary database over quota, trying secondary")
                return await save_to_secondary(document, file_name)
            else:
                logger.error(f"Primary database operation error: {e}")
                return False, 2
        except Exception as e:
            logger.error(f"Unexpected error saving to primary database: {e}")
            return False, 2
            
    except Exception as e:
        logger.error(f"Critical error in enhanced save_file: {e}")
        return False, 4

async def save_to_secondary(document, file_name):
    """Enhanced secondary database save"""
    try:
        if primary_col.find_one({'_id': document['_id']}):
            logger.warning(f'{file_name} already exists in primary database')
            return False, 0
        secondary_col.insert_one(document)
        logger.info(f'✅ {file_name} saved to secondary database')
        return True, 1
    except DuplicateKeyError:
        logger.warning(f'{file_name} already exists in secondary database')
        return False, 0
    except Exception as e:
        logger.error(f"Secondary database error: {e}")
        return False, 2

async def get_search_results(query: str, file_type: str = None, max_results: int = 10, offset: int = 0) -> Tuple[List[Dict], int, int]:
    """
    Advanced search system inspired by PROFESSOR-BOT
    Supports intelligent pattern matching and multiple search strategies
    """
    try:
        query = query.strip()
        if not query:
            logger.info("Empty query, returning recent files")
            return await get_recent_files(max_results, offset)
        
        logger.info(f"Searching for: '{query}' (type: {file_type}, max: {max_results}, offset: {offset})")
        
        # PROFESSOR-BOT style search patterns
        search_patterns = []
        
        if len(query) <= 2:
            # Very short query - exact match
            pattern = f"^{re.escape(query)}"
        elif ' ' not in query:
            # Single word - word boundary matching
            pattern = r'(\b|[\.\+\-_])' + re.escape(query) + r'(\b|[\.\+\-_])'
        else:
            # Multiple words - flexible matching
            words = query.split()
            pattern = r'.*'.join([re.escape(word) for word in words])
        
        # Create regex with case insensitive flag
        try:
            regex = re.compile(pattern, flags=re.IGNORECASE)
        except re.error:
            # Fallback to simple contains search
            regex = re.compile(re.escape(query), flags=re.IGNORECASE)
        
        # Build MongoDB query
        search_filter = {'file_name': regex}
        
        # Add file type filter if specified
        if file_type:
            search_filter['file_type'] = file_type
        
        # Search in primary database
        primary_cursor = primary_col.find(search_filter).sort([("file_size", -1)])
        primary_results = list(primary_cursor.skip(offset).limit(max_results))
        
        # If not enough results, search secondary database
        if len(primary_results) < max_results:
            remaining = max_results - len(primary_results)
            secondary_cursor = secondary_col.find(search_filter).sort([("file_size", -1)])
            secondary_results = list(secondary_cursor.skip(max(0, offset - primary_cursor.count())).limit(remaining))
            
            # Combine results, avoiding duplicates
            existing_ids = {r['_id'] for r in primary_results}
            for result in secondary_results:
                if result['_id'] not in existing_ids:
                    primary_results.append(result)
        
        # Get total count for pagination
        total_primary = primary_col.count_documents(search_filter)
        total_secondary = secondary_col.count_documents(search_filter)
        total_results = total_primary + total_secondary
        
        # Calculate next offset
        next_offset = offset + len(primary_results)
        if next_offset >= total_results:
            next_offset = ""
        
        logger.info(f"Found {len(primary_results)} results (total: {total_results})")
        return primary_results, next_offset, total_results
        
    except Exception as e:
        logger.error(f"Error in get_search_results: {e}")
        return [], "", 0

async def get_recent_files(max_results: int = 10, offset: int = 0) -> Tuple[List[Dict], int, int]:
    """Get recently added files"""
    try:
        # Get recent files from primary database
        cursor = primary_col.find().sort([("added_time", -1)])
        results = list(cursor.skip(offset).limit(max_results))
        
        total_count = primary_col.count_documents({})
        next_offset = offset + len(results)
        if next_offset >= total_count:
            next_offset = ""
            
        return results, next_offset, total_count
        
    except Exception as e:
        logger.error(f"Error getting recent files: {e}")
        return [], "", 0

async def get_popular_movies(max_results: int = 10) -> List[Dict]:
    """Get popular/trending movies based on file size and recent additions"""
    try:
        # Simple popularity algorithm: larger files added recently
        pipeline = [
            {"$match": {"file_size": {"$gt": 100000000}}},  # Files > 100MB
            {"$sort": {"file_size": -1, "added_time": -1}},
            {"$limit": max_results}
        ]
        
        popular_movies = list(primary_col.aggregate(pipeline))
        return popular_movies
        
    except Exception as e:
        logger.error(f"Error getting popular movies: {e}")
        return []

async def get_file_details(query):
    """Enhanced file details retrieval"""
    try:
        # Check primary database first
        file = primary_col.find_one({'_id': query})
        if file:
            return file
        
        # Check secondary database
        file = secondary_col.find_one({'_id': query})
        if file:
            return file
        
        logger.warning(f"File not found: {query}")
        return None
        
    except Exception as e:
        logger.error(f"Error getting file details: {e}")
        return None

async def delete_file(file_id):
    """Delete file from both databases"""
    try:
        primary_result = primary_col.delete_one({'_id': file_id})
        secondary_result = secondary_col.delete_one({'_id': file_id})
        
        deleted = primary_result.deleted_count + secondary_result.deleted_count
        return deleted > 0
        
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return False

async def get_search_suggestions(query: str) -> List[str]:
    """Get search suggestions based on existing files"""
    try:
        # Use MongoDB text search for suggestions
        suggestions = []
        
        # Get partial matches
        regex = re.compile(f".*{re.escape(query)}.*", re.IGNORECASE)
        cursor = primary_col.find(
            {"file_name": regex}, 
            {"file_name": 1}
        ).limit(5)
        
        for doc in cursor:
            filename = doc['file_name']
            # Extract movie name (remove extension and common patterns)
            clean_name = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v)$', '', filename, flags=re.IGNORECASE)
            clean_name = re.sub(r'\s*[\(\[].*?[\)\]]', '', clean_name)  # Remove brackets content
            clean_name = clean_name.strip()
            
            if clean_name not in suggestions and len(clean_name) > 2:
                suggestions.append(clean_name)
        
        return suggestions[:5]
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        return []

# File ID processing functions (from original)
def encode_file_id(s: bytes) -> str:
    r, n = b"", 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

# Legacy compatibility functions
async def get_delete_results(query):
    """Legacy function for delete operations"""
    return await get_search_results(query, max_results=1000)

async def delete_func(file):
    """Legacy delete function"""
    return await delete_file(file.get('_id'))