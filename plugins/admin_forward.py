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
        
        # Check if message has media
        media = None
        file_type = None
        
        if message.document:
            media = message.document
            file_type = "document"
        elif message.video:
            media = message.video
            file_type = "video"
        elif message.audio:
            media = message.audio
            file_type = "audio"
        
        if not media:
            await message.reply("❌ No media file found in forwarded message.")
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