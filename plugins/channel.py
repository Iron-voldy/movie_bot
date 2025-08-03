from hydrogram import Client, filters
from info import CHANNELS
from database.advanced_filterdb import save_file
import logging

logger = logging.getLogger(__name__)

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    """Enhanced Media Handler - Automatically index movies from channels"""
    try:
        logger.info(f"New media detected in channel {message.chat.id} ({message.chat.title})")
        
        # Find the media object
        media = None
        file_type = None
        
        for media_type in ("document", "video", "audio"):
            media_obj = getattr(message, media_type, None)
            if media_obj is not None:
                media = media_obj
                file_type = media_type
                break
        
        if not media:
            logger.warning("No media found in message")
            return

        # Enhanced file name handling
        if not hasattr(media, 'file_name') or not media.file_name:
            # Generate filename from caption or use default
            if message.caption:
                # Extract potential filename from caption
                import re
                filename_match = re.search(r'([^\n]+\.(?:mkv|mp4|avi|mov|wmv|flv|webm|m4v))', message.caption, re.IGNORECASE)
                if filename_match:
                    media.file_name = filename_match.group(1).strip()
                else:
                    # Use first line of caption as filename
                    first_line = message.caption.split('\n')[0].strip()
                    media.file_name = f"{first_line}.mp4" if first_line else f"Movie_{media.file_unique_id}.mp4"
            else:
                media.file_name = f"Movie_{media.file_unique_id}.mp4"

        logger.info(f"Processing {file_type}: {media.file_name} ({media.file_size} bytes)")

        # Check for duplicates before saving
        from database.advanced_filterdb import primary_col, secondary_col
        
        existing_file = None
        try:
            # Check by unique_id first
            existing_file = primary_col.find_one({'_id': media.file_unique_id})
            if not existing_file:
                existing_file = secondary_col.find_one({'_id': media.file_unique_id})
            
            # Also check by file_name as secondary check
            if not existing_file:
                existing_file = primary_col.find_one({'file_name': media.file_name})
                if not existing_file:
                    existing_file = secondary_col.find_one({'file_name': media.file_name})
                    
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
        
        if existing_file:
            logger.info(f"Duplicate detected: {media.file_name} already exists in database")
            return

        # Set media properties for saving
        media.file_type = file_type
        media.caption = message.caption or ""
        
        # Save to database
        success, status = await save_file(media)
        
        if success:
            logger.info(f"✅ Successfully saved {media.file_name} to database")
        else:
            if status == 0:
                logger.info(f"⚠️ {media.file_name} already exists in database")
            else:
                logger.error(f"❌ Failed to save {media.file_name} to database")
                
    except Exception as e:
        logger.error(f"Error in media handler: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")