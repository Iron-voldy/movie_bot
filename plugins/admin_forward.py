"""
Admin channel forwarding handler - Automatically add movies to database when admin forwards from channels
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from database.ia_filterdb import save_file
from info import ADMINS, CHANNELS
from utils import temp

logger = logging.getLogger(__name__)

@Client.on_message(filters.private & filters.forwarded & filters.user(ADMINS))
async def admin_forward_handler(client: Client, message: Message):
    """Handle admin forwarded messages to add movies to database"""
    try:
        user_id = message.from_user.id
        
        logger.info(f"Admin {user_id} forwarded a message - checking for media...")
        
        # Enhanced media detection
        media = None
        file_type = None
        
        # Check for different types of media
        if hasattr(message, 'document') and message.document:
            media = message.document
            file_type = "document"
            logger.info(f"Found document: {media.file_name} ({media.file_size} bytes)")
        elif hasattr(message, 'video') and message.video:
            media = message.video
            file_type = "video"
            logger.info(f"Found video: {getattr(media, 'file_name', 'video')} ({media.file_size} bytes)")
        elif hasattr(message, 'audio') and message.audio:
            media = message.audio
            file_type = "audio"
            logger.info(f"Found audio: {getattr(media, 'file_name', 'audio')} ({media.file_size} bytes)")
        
        # Debug information
        logger.info(f"Message type check - Document: {hasattr(message, 'document')}, Video: {hasattr(message, 'video')}, Audio: {hasattr(message, 'audio')}")
        if hasattr(message, 'document'):
            logger.info(f"Document object: {message.document}")
        if hasattr(message, 'video'):
            logger.info(f"Video object: {message.video}")
        
        if not media:
            # More detailed error message
            debug_info = f"**Debug Info:**\n"
            debug_info += f"• Has document: {hasattr(message, 'document')}\n"
            debug_info += f"• Has video: {hasattr(message, 'video')}\n"
            debug_info += f"• Has audio: {hasattr(message, 'audio')}\n"
            debug_info += f"• Message type: {type(message)}\n"
            debug_info += f"• Forward from chat: {message.forward_from_chat is not None}\n"
            
            await message.reply(f"❌ **No media file found in forwarded message.**\n\n{debug_info}")
            return
        
        # Check if it's forwarded from a valid channel
        if not message.forward_from_chat:
            await message.reply("❌ This message is not forwarded from a channel.")
            return
        
        forward_from_id = message.forward_from_chat.id
        forward_from_title = message.forward_from_chat.title or "Unknown Channel"
        
        logger.info(f"Admin {user_id} forwarded {file_type} from channel {forward_from_id} ({forward_from_title})")
        
        # Set media properties for saving
        media.file_type = file_type
        media.caption = message.caption or ""
        
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
        
        logger.info(f"Processing file: {media.file_name} (Type: {file_type}, Size: {media.file_size})")
        
        # Check for duplicates before saving
        from database.ia_filterdb import primary_col, secondary_col
        
        # Check if file already exists by unique_id or file_name
        existing_file = None
        try:
            # Check by unique_id first (most reliable)
            existing_file = primary_col.find_one({'_id': media.file_unique_id})
            if not existing_file:
                existing_file = secondary_col.find_one({'_id': media.file_unique_id})
            
            # If not found by unique_id, check by file_name (less reliable but catches similar files)
            if not existing_file:
                existing_file = primary_col.find_one({'file_name': media.file_name})
                if not existing_file:
                    existing_file = secondary_col.find_one({'file_name': media.file_name})
                    
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
        
        if existing_file:
            await message.reply(
                f"⚠️ **Duplicate File Detected**\n\n"
                f"📁 **File:** {media.file_name}\n"
                f"📺 **Channel:** {forward_from_title}\n"
                f"🔍 **Match:** Found existing file with same {'unique ID' if existing_file.get('_id') == media.file_unique_id else 'filename'}\n\n"
                f"🚫 **Not added** - This movie is already in the database."
            )
            return
        
        # Save to database
        success, status = await save_file(media)
        
        if success:
            # Add to channels list if not already there
            if forward_from_id not in CHANNELS:
                CHANNELS.append(forward_from_id)
                logger.info(f"Added new channel {forward_from_id} to CHANNELS list")
            
            await message.reply(
                f"✅ **Movie Added Successfully!**\n\n"
                f"📁 **File:** {media.file_name}\n"
                f"📏 **Size:** {media.file_size} bytes\n"
                f"📺 **Channel:** {forward_from_title}\n"
                f"🆔 **Channel ID:** `{forward_from_id}`\n\n"
                f"Users can now search for this movie!"
            )
        else:
            if status == 0:  # Already exists
                await message.reply(
                    f"⚠️ **File Already Exists**\n\n"
                    f"📁 **File:** {media.file_name}\n"
                    f"📺 **Channel:** {forward_from_title}\n\n"
                    f"This movie is already in the database."
                )
            else:  # Error occurred
                await message.reply(
                    f"❌ **Error Adding File**\n\n"
                    f"📁 **File:** {media.file_name}\n"
                    f"📺 **Channel:** {forward_from_title}\n\n"
                    f"There was an error adding this movie to the database."
                )
        
    except Exception as e:
        logger.error(f"Error in admin forward handler: {e}")
        await message.reply("❌ An error occurred while processing the forwarded message.")

@Client.on_message(filters.command("addchannel") & filters.user(ADMINS))
async def add_channel_command(client: Client, message: Message):
    """Manually add a channel to the CHANNELS list"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "**Add Channel Command**\n\n"
                "Usage: `/addchannel <channel_id>`\n\n"
                "Example: `/addchannel -1001234567890`\n\n"
                "You can get channel ID by forwarding any message from the channel to @userinfobot"
            )
            return
        
        channel_id = message.command[1]
        
        # Try to convert to int
        try:
            channel_id = int(channel_id)
        except ValueError:
            await message.reply("❌ Invalid channel ID. Must be a number.")
            return
        
        # Check if bot can access the channel
        try:
            chat = await client.get_chat(channel_id)
            channel_title = chat.title
            
            # Add to channels if not already there
            if channel_id not in CHANNELS:
                CHANNELS.append(channel_id)
                
                await message.reply(
                    f"✅ **Channel Added Successfully!**\n\n"
                    f"📺 **Channel:** {channel_title}\n"
                    f"🆔 **ID:** `{channel_id}`\n\n"
                    f"The bot will now automatically save media files from this channel.\n"
                    f"Current channels: {len(CHANNELS)}"
                )
            else:
                await message.reply(
                    f"⚠️ **Channel Already Added**\n\n"
                    f"📺 **Channel:** {channel_title}\n"
                    f"🆔 **ID:** `{channel_id}`\n\n"
                    f"This channel is already in the list."
                )
                
        except Exception as e:
            await message.reply(
                f"❌ **Cannot Access Channel**\n\n"
                f"🆔 **ID:** `{channel_id}`\n"
                f"❌ **Error:** {str(e)}\n\n"
                f"Make sure:\n"
                f"1. The channel ID is correct\n"
                f"2. The bot is added to the channel as admin\n"
                f"3. The channel exists and is accessible"
            )
        
    except Exception as e:
        logger.error(f"Error in add channel command: {e}")
        await message.reply("❌ An error occurred while adding the channel.")

@Client.on_message(filters.command("channels") & filters.user(ADMINS))
async def list_channels_command(client: Client, message: Message):
    """List all configured channels"""
    try:
        if not CHANNELS:
            await message.reply(
                "📋 **No Channels Configured**\n\n"
                "Use `/addchannel <channel_id>` to add channels or forward movies from channels to add them automatically."
            )
            return
        
        channel_list = "📋 **Configured Channels:**\n\n"
        
        for i, channel_id in enumerate(CHANNELS, 1):
            try:
                chat = await client.get_chat(channel_id)
                channel_title = chat.title
                member_count = ""
                try:
                    count = await client.get_chat_members_count(channel_id)
                    member_count = f" • {count:,} members"
                except:
                    pass
                
                channel_list += f"{i}. **{channel_title}**{member_count}\n"
                channel_list += f"   🆔 `{channel_id}`\n\n"
            except Exception as e:
                channel_list += f"{i}. **Channel {channel_id}** (Inaccessible)\n"
                channel_list += f"   🆔 `{channel_id}`\n"
                channel_list += f"   ❌ Error: {str(e)[:50]}...\n\n"
        
        channel_list += f"**Total:** {len(CHANNELS)} channels"
        
        await message.reply(channel_list)
        
    except Exception as e:
        logger.error(f"Error in list channels command: {e}")
        await message.reply("❌ An error occurred while listing channels.")

@Client.on_message(filters.command("removechannel") & filters.user(ADMINS))
async def remove_channel_command(client: Client, message: Message):
    """Remove a channel from the CHANNELS list"""
    try:
        if len(message.command) < 2:
            await message.reply(
                "**Remove Channel Command**\n\n"
                "Usage: `/removechannel <channel_id>`\n\n"
                "Example: `/removechannel -1001234567890`"
            )
            return
        
        channel_id = message.command[1]
        
        # Try to convert to int
        try:
            channel_id = int(channel_id)
        except ValueError:
            await message.reply("❌ Invalid channel ID. Must be a number.")
            return
        
        if channel_id in CHANNELS:
            CHANNELS.remove(channel_id)
            
            # Try to get channel name
            try:
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
            except:
                channel_name = f"Channel {channel_id}"
            
            await message.reply(
                f"✅ **Channel Removed Successfully!**\n\n"
                f"📺 **Channel:** {channel_name}\n"
                f"🆔 **ID:** `{channel_id}`\n\n"
                f"Remaining channels: {len(CHANNELS)}"
            )
        else:
            await message.reply(
                f"❌ **Channel Not Found**\n\n"
                f"🆔 **ID:** `{channel_id}`\n\n"
                f"This channel is not in the configured channels list."
            )
        
    except Exception as e:
        logger.error(f"Error in remove channel command: {e}")
        await message.reply("❌ An error occurred while removing the channel.")