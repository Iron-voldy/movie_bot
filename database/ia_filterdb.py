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
    """Save file to available database with enhanced error handling and duplicate management"""
    try:
        # Enhanced file ID processing with error handling
        logger.info(f"Processing file for database save...")
        logger.info(f"Media type: {type(media)}")
        logger.info(f"File ID: {getattr(media, 'file_id', 'Missing')}")
        logger.info(f"File name: {getattr(media, 'file_name', 'Missing')}")
        logger.info(f"File size: {getattr(media, 'file_size', 'Missing')}")
        
        # Get file ID
        if not hasattr(media, 'file_id') or not media.file_id:
            logger.error("Media object missing file_id")
            return False, 3
            
        # Process file ID
        try:
            file_id, file_ref = unpack_new_file_id(media.file_id)
            logger.info(f"Processed file_id: {file_id}")
        except Exception as e:
            logger.error(f"Error processing file_id: {e}")
            # Fallback: use the original file_id if processing fails
            file_id = media.file_id
            logger.info(f"Using original file_id as fallback: {file_id}")
        
        # Process file name
        if hasattr(media, 'file_name') and media.file_name:
            file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        else:
            # Generate a filename if missing
            file_name = f"Movie_{getattr(media, 'file_unique_id', 'unknown')}"
            if hasattr(media, 'file_type'):
                file_name += f".{media.file_type}"
            logger.info(f"Generated filename: {file_name}")

        file_size = getattr(media, 'file_size', 0)
        
        # Check for existing file by name and size
        existing_file, database_location = await find_duplicate_by_name_and_size(file_name, file_size)
        
        if existing_file:
            old_file_id = existing_file['_id']
            logger.info(f"Found existing file: {file_name} with old ID: {old_file_id}")
            
            # If it's the same file ID, no update needed
            if old_file_id == file_id:
                logger.info(f"File {file_name} already has current ID")
                return False, 0
            
            # Update the existing file with new ID (refresh expired ID)
            logger.info(f"Updating file ID from {old_file_id} to {file_id}")
            
            try:
                if database_location == 'primary':
                    # Remove old entry and insert new one
                    primary_col.delete_one({'_id': old_file_id})
                    document = {
                        '_id': file_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'file_type': getattr(media, 'file_type', 'unknown'),
                        'file_unique_id': getattr(media, 'file_unique_id', None)
                    }
                    primary_col.insert_one(document)
                    logger.info(f"✅ Updated {file_name} with fresh file ID in primary database")
                    return True, 5  # Return code 5 for "updated existing file"
                    
                else:  # secondary
                    # Remove old entry and insert new one
                    secondary_col.delete_one({'_id': old_file_id})
                    document = {
                        '_id': file_id,
                        'file_name': file_name,
                        'file_size': file_size,
                        'file_type': getattr(media, 'file_type', 'unknown'),
                        'file_unique_id': getattr(media, 'file_unique_id', None)
                    }
                    secondary_col.insert_one(document)
                    logger.info(f"✅ Updated {file_name} with fresh file ID in secondary database")
                    return True, 5  # Return code 5 for "updated existing file"
                    
            except Exception as update_error:
                logger.error(f"Error updating existing file: {update_error}")
                # Continue with normal save process if update fails

        # Create document for database
        document = {
            '_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_type': getattr(media, 'file_type', 'unknown'),
            'file_unique_id': getattr(media, 'file_unique_id', None)
        }
        
        logger.info(f"Document to save: {document}")

        # Try to save to primary database
        try:
            result = primary_col.insert_one(document)
            logger.info(f'{file_name} saved to primary database with ID: {result.inserted_id}')
            return True, 1
        except DuplicateKeyError:
            logger.warning(f'{file_name} already exists in primary database with same file ID')
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
        logger.error(f"Critical error in save_file: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False, 4


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

async def validate_file_id(client, file_id):
    """Test if a file ID is valid by attempting to get file info"""
    try:
        # Try to send to a dummy chat to test validity
        await client.get_file(file_id)
        return True
    except Exception as e:
        logger.error(f"File ID validation failed: {e}")
        return False

async def update_file_id(old_file_id, new_file_id, file_name):
    """Update an existing file's ID in the database"""
    try:
        # Update in primary database
        result = primary_col.update_one(
            {'_id': old_file_id},
            {'$set': {'_id': new_file_id}}
        )
        
        if result.matched_count == 0:
            # Try secondary database
            result = secondary_col.update_one(
                {'_id': old_file_id},
                {'$set': {'_id': new_file_id}}
            )
        
        if result.matched_count > 0:
            logger.info(f"Updated file ID for {file_name}")
            return True
        else:
            logger.warning(f"Could not find file to update: {file_name}")
            return False
            
    except Exception as e:
        logger.error(f"Error updating file ID: {e}")
        return False

async def find_duplicate_by_name_and_size(file_name, file_size):
    """Find existing file by name and size to handle duplicates"""
    try:
        # Search in primary database first
        existing = primary_col.find_one({
            'file_name': file_name,
            'file_size': file_size
        })
        
        if existing:
            return existing, 'primary'
            
        # Search in secondary database
        existing = secondary_col.find_one({
            'file_name': file_name,
            'file_size': file_size
        })
        
        if existing:
            return existing, 'secondary'
            
        return None, None
        
    except Exception as e:
        logger.error(f"Error finding duplicate: {e}")
        return None, None
