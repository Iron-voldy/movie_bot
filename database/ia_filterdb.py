import logging
from struct import pack
import re
import base64
from hydrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError, OperationFailure
from pymongo import MongoClient, ASCENDING
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME, FILE_DB_URL, FILE_DB_NAME

logger = logging.getLogger(__name__)

# Primary database connection (your new database)
primary_client = MongoClient(DATABASE_URL)
primary_db = primary_client[DATABASE_NAME]
primary_col = primary_db[COLLECTION_NAME]

# Secondary database connection (same as primary for now)
secondary_client = MongoClient(FILE_DB_URL)
secondary_db = secondary_client[FILE_DB_NAME]
secondary_col = secondary_db[COLLECTION_NAME]



def get_database_size():
    """Get total size of data in both databases"""
    primary_size = primary_db.command("dbstats")['dataSize']
    secondary_size = secondary_db.command("dbstats")['dataSize']
    return primary_size, secondary_size

def get_database_count():
    """Get total count of files in both databases"""
    primary_count = primary_col.count_documents({})
    secondary_count = secondary_col.count_documents({})
    return primary_count, secondary_count

async def save_file(media):
    """Save file to available database"""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))

    document = {
        '_id': file_id,
        'file_name': file_name,
        'file_size': media.file_size
    }

    try:
        primary_col.insert_one(document)
        logger.info(f'{file_name} saved to primary database')
        return True, 1
    except DuplicateKeyError:
        logger.warning(f'{file_name} already exists in primary database')
        return False, 0
    except OperationFailure as e:
        if 'quota' in str(e).lower():
            logger.warning("Primary database over quota")
            return await save_to_secondary(document, file_name)
        else:
            logger.error(f"Primary database error: {e}")
            return False, 2


async def save_to_secondary(document, file_name):
    """Helper function to save to secondary database"""
    try:
        if primary_col.find_one({'_id': document['_id']}):
            logger.warning(f'{file_name} already exists in primary database')
            return False, 0
        secondary_col.insert_one(document)
        logger.info(f'{file_name} saved to secondary database')
        return True, 1
    except DuplicateKeyError:
        logger.warning(f'{file_name} already exists in secondary database')
        return False, 0
    except Exception as e:
        logger.error(f"Secondary database error: {e}")
        return False, 2

async def get_search_results(query, file_type=None):
    """Search in both databases and return combined results"""
    query = query.strip()
    if not query:
        return []

    # Split query into individual terms
    terms = query.split()

    # Create a list of regex patterns for each term
    regex_patterns = []
    for term in terms:
        raw_pattern = r'(\b|[\.\+\-_])' + re.escape(term) + r'(\b|[\.\+\-_])'
        try:
            regex_patterns.append(re.compile(raw_pattern, flags=re.IGNORECASE))
        except:
            continue

    if not regex_patterns:
        return []

    # Create filter that requires all terms to match
    filter = {'file_name': {'$all': regex_patterns}}

    # Get results from primary database if available
    primary_results = list(primary_col.find(filter))

    # Get results from secondary database if available
    secondary_results = list(secondary_col.find(filter))

    # Combine results (remove duplicates by file_id)
    combined_results = primary_results
    existing_ids = {r['_id'] for r in primary_results}

    for result in secondary_results:
        if result['_id'] not in existing_ids:
            combined_results.append(result)

    combined_results.reverse()

    return combined_results

async def get_delete_results(query):
    """Get files to delete from both databases"""
    query = query.strip()
    raw_pattern = r'(\b|[\.\+\-_])' + query + r'(\b|[\.\+\-_])' if query else '.'
    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except:
        return [], 0

    filter = {'file_name': regex}

    # Get results from both databases
    primary_files = list(primary_col.find(filter))

    secondary_files = list(secondary_col.find(filter))

    total_count = len(primary_files) + len(secondary_files)
    return primary_files + secondary_files, total_count

async def delete_func(file):
    """Delete a file from the database(s)"""
    file_id = file.get('_id')

    result = primary_col.delete_one({'_id': file_id})

    result = secondary_col.delete_one({'_id': file_id})


async def get_file_details(query):
    """Get file details from both databases"""
    # Check primary first
    file = primary_col.find_one({'_id': query})
    if file:
        return file

    file = secondary_col.find_one({'_id': query})
    if file:
        return file

    return None

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
