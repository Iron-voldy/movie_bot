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

@Client.on_message(filters.private & filters.user(ADMINS))
async def admin_forward_handler(client: Client, message: Message):
    """Handle admin forwarded messages to add movies to database - Enhanced Debug Version"""
    try:
        user_id = message.from_user.id
        
        # Check if user is admin first
        if user_id not in ADMINS:
            logger.info(f"Non-admin user {user_id} tried to use admin forwarding")
            return
        
        logger.info(f"Admin {user_id} sent a message - analyzing...")
        logger.info(f"Message has forward info: {hasattr(message, 'forward_from_chat') and message.forward_from_chat is not None}")
        logger.info(f"Message content type: Document={hasattr(message, 'document') and message.document is not None}, Video={hasattr(message, 'video') and message.video is not None}, Audio={hasattr(message, 'audio') and message.audio is not None}")
        
        # Enhanced media detection - check forwarded OR direct media
        media = None
        file_type = None
        
        # Check for different types of media
        if hasattr(message, 'document') and message.document:
            media = message.document
            file_type = "document"
            logger.info(f"Found document: {getattr(media, 'file_name', 'Unknown')} ({media.file_size} bytes)")
        elif hasattr(message, 'video') and message.video:
            media = message.video
            file_type = "video"
            logger.info(f"Found video: {getattr(media, 'file_name', 'Unknown')} ({media.file_size} bytes)")
        elif hasattr(message, 'audio') and message.audio:
            media = message.audio
            file_type = "audio"
            logger.info(f"Found audio: {getattr(media, 'file_name', 'Unknown')} ({media.file_size} bytes)")
        
        # If no media found, provide detailed feedback
        if not media:
            debug_info = f"**🔍 Debug Analysis:**\n"
            debug_info += f"• User ID: {user_id}\n"
            debug_info += f"• Is Admin: {user_id in ADMINS}\n"
            debug_info += f"• Has Document: {hasattr(message, 'document') and message.document is not None}\n"
            debug_info += f"• Has Video: {hasattr(message, 'video') and message.video is not None}\n"
            debug_info += f"• Has Audio: {hasattr(message, 'audio') and message.audio is not None}\n"
            debug_info += f"• Has Text: {hasattr(message, 'text') and message.text is not None}\n"
            debug_info += f"• Is Forwarded: {hasattr(message, 'forward_from_chat') and message.forward_from_chat is not None}\n"
            debug_info += f"• Message Type: {type(message).__name__}\n"
            
            if hasattr(message, 'text') and message.text:
                debug_info += f"• Text Content: {message.text[:100]}...\n"
            
            await message.reply(
                f"❌ **No Media File Detected**\n\n"
                f"Please forward or send a movie file (video/document/audio).\n\n"
                f"{debug_info}\n"
                f"💡 **Tips:**\n"
                f"• Forward a movie file from a channel\n"
                f"• Send a movie file directly\n"
                f"• Make sure the file is a video/document/audio\n"
            )
            return
        
        # Determine source information
        if message.forward_from_chat:
            forward_from_id = message.forward_from_chat.id
            forward_from_title = message.forward_from_chat.title or "Unknown Channel"
            source_info = f"Forwarded from: {forward_from_title} ({forward_from_id})"
            logger.info(f"Admin {user_id} forwarded {file_type} from channel {forward_from_id} ({forward_from_title})")
        else:
            forward_from_id = "direct_upload"
            forward_from_title = "Direct Upload"
            source_info = "Direct upload by admin"
            logger.info(f"Admin {user_id} directly uploaded {file_type}")
        
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
        
        # Enhanced duplicate detection with file ID refresh capability
        from database.ia_filterdb import primary_col, secondary_col, find_duplicate_by_name_and_size
        
        existing_file = None
        update_mode = False
        
        try:
            # First check by file_name and size (more reliable for expired ID updates)
            existing_file, database_location = await find_duplicate_by_name_and_size(
                media.file_name, media.file_size
            )
            
            if existing_file:
                old_file_id = existing_file['_id']
                new_file_id = media.file_id
                
                logger.info(f"Found existing file: {media.file_name}")
                logger.info(f"Old file ID: {old_file_id}")
                logger.info(f"New file ID: {new_file_id}")
                
                # Check if this is the same file ID or a potential refresh
                if old_file_id == new_file_id:
                    await message.reply(
                        f"⚠️ **Identical File Already Exists**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📺 **Channel:** {forward_from_title}\n"
                        f"🔍 **Match:** Same file ID\n\n"
                        f"🚫 **Not added** - This exact movie is already in the database."
                    )
                    return
                else:
                    # This could be a refresh with new file ID
                    update_mode = True
                    logger.info(f"Potential file ID refresh detected - proceeding with update")
                    
                    await message.reply(
                        f"🔄 **File Refresh Detected**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📺 **Channel:** {forward_from_title}\n"
                        f"🔄 **Action:** Updating expired file ID\n\n"
                        f"⏳ Processing update..."
                    )
            
        except Exception as e:
            logger.error(f"Error checking for duplicates: {e}")
            existing_file = None
        
        # Enhanced database saving with detailed logging
        logger.info(f"Attempting to save file: {media.file_name}")
        logger.info(f"File ID: {getattr(media, 'file_id', 'Not found')}")
        logger.info(f"File unique ID: {getattr(media, 'file_unique_id', 'Not found')}")
        logger.info(f"File size: {media.file_size}")
        logger.info(f"File type: {file_type}")
        
        try:
            success, status = await save_file(media)
            logger.info(f"Save result - Success: {success}, Status: {status}")
            
            if success:
                # Add to channels list if it's a forwarded message and not already there
                if message.forward_from_chat and forward_from_id not in CHANNELS and isinstance(forward_from_id, int):
                    CHANNELS.append(forward_from_id)
                    logger.info(f"Added new channel {forward_from_id} to CHANNELS list")
                
                # Different message based on whether this was an update or new file
                if update_mode and status == 5:  # Status 5 = updated existing file
                    await message.reply(
                        f"✅ **Movie File ID Refreshed Successfully!**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📏 **Size:** {media.file_size:,} bytes\n"
                        f"🎬 **Type:** {file_type.title()}\n"
                        f"📺 **Source:** {forward_from_title}\n"
                        f"🔄 **Action:** Updated expired file ID\n"
                        f"🆔 **New File ID:** `{getattr(media, 'file_id', 'Unknown')[:20]}...`\n\n"
                        f"🎉 **FIXED!** Users can now get this movie again!\n"
                        f"🔍 Try searching: `{media.file_name.split('.')[0]}`"
                    )
                    logger.info(f"✅ Successfully refreshed file ID for: {media.file_name}")
                else:
                    await message.reply(
                        f"✅ **Movie Added Successfully!**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📏 **Size:** {media.file_size:,} bytes\n"
                        f"🎬 **Type:** {file_type.title()}\n"
                        f"📺 **Source:** {forward_from_title}\n"
                        f"🆔 **File ID:** `{getattr(media, 'file_id', 'Unknown')[:20]}...`\n\n"
                        f"✨ Users can now search for this movie!\n"
                        f"🔍 Try searching: `{media.file_name.split('.')[0]}`"
                    )
                    logger.info(f"✅ Successfully processed and saved: {media.file_name}")
                
            else:
                if status == 0:  # Already exists
                    await message.reply(
                        f"⚠️ **File Already Exists**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📺 **Source:** {forward_from_title}\n\n"
                        f"🔍 This movie is already in the database.\n"
                        f"Users can search: `{media.file_name.split('.')[0]}`"
                    )
                    logger.info(f"⚠️ File already exists: {media.file_name}")
                else:  # Error occurred
                    await message.reply(
                        f"❌ **Database Error**\n\n"
                        f"📁 **File:** {media.file_name}\n"
                        f"📺 **Source:** {forward_from_title}\n"
                        f"⚠️ **Status Code:** {status}\n\n"
                        f"Please check logs and try again."
                    )
                    logger.error(f"❌ Database error for file: {media.file_name}, Status: {status}")
                    
        except Exception as save_error:
            logger.error(f"Exception during save_file: {save_error}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            await message.reply(
                f"❌ **Unexpected Error**\n\n"
                f"📁 **File:** {media.file_name}\n"
                f"📺 **Source:** {forward_from_title}\n"
                f"❌ **Error:** {str(save_error)}\n\n"
                f"Please check the bot logs for details."
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

@Client.on_message(filters.command("testdb") & filters.user(ADMINS))
async def test_database_command(client: Client, message: Message):
    """Test database connectivity and functionality"""
    try:
        await message.reply("🔍 **Testing Database...**")
        
        # Test database connection
        from database.ia_filterdb import primary_col, secondary_col, get_database_count
        
        try:
            primary_count, secondary_count = get_database_count()
            total_movies = primary_count + secondary_count
            
            test_result = f"✅ **Database Test Results**\n\n"
            test_result += f"🎬 **Total Movies:** {total_movies}\n"
            test_result += f"📊 **Primary DB:** {primary_count} movies\n"
            test_result += f"📊 **Secondary DB:** {secondary_count} movies\n\n"
            
            if total_movies > 0:
                # Get sample movie
                sample = primary_col.find_one()
                if sample:
                    test_result += f"📁 **Sample Movie:**\n"
                    test_result += f"   • Name: {sample.get('file_name', 'Unknown')}\n"
                    test_result += f"   • Size: {sample.get('file_size', 0):,} bytes\n"
                    test_result += f"   • ID: {str(sample.get('_id', 'Unknown'))[:30]}...\n\n"
                
                test_result += f"✅ **Database Status:** Ready for use!\n"
                test_result += f"🚀 **System Status:** Operational"
            else:
                test_result += f"⚠️ **Database is empty**\n"
                test_result += f"💡 Forward some movie files to populate it!"
            
        except Exception as db_error:
            test_result = f"❌ **Database Error:**\n{str(db_error)}"
        
        await message.reply(test_result)
        
    except Exception as e:
        await message.reply(f"❌ **Test failed:** {str(e)}")

@Client.on_message(filters.command("adminhelp") & filters.user(ADMINS))
async def admin_help_command(client: Client, message: Message):
    """Show admin help and debugging commands"""
    help_text = f"""🛠 **Admin Commands & Debug Guide**

📋 **Available Commands:**
• `/testdb` - Test database connectivity
• `/addchannel <id>` - Add channel manually
• `/channels` - List all channels
• `/removechannel <id>` - Remove channel
• `/adminhelp` - Show this help

🎬 **Adding Movies:**
1. Forward movie files from channels
2. Send movie files directly to the bot
3. Bot will detect and save automatically

🔍 **Debugging Steps:**
If movies aren't being added:
1. Check you're an admin: Your ID should be in ADMINS list
2. Use `/testdb` to check database
3. Forward a movie file and check the response
4. Check bot logs for detailed error info

📊 **Current Admin Status:**
• Your ID: `{message.from_user.id}`
• Admin List: `{ADMINS}`
• Is Admin: {'✅ Yes' if message.from_user.id in ADMINS else '❌ No'}

💡 **Tips:**
• Movie files must be videos, documents, or audio
• Bot supports forwarded and direct uploads
• Check logs for detailed error information
• Use `/testdb` regularly to monitor system health"""

    await message.reply(help_text)