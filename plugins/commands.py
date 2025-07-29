import os
import logging
import random
import asyncio
from Script import script
from hydrogram import Client, filters, enums
from hydrogram.errors import ChatAdminRequired, FloodWait
from hydrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import get_file_details, unpack_new_file_id, get_delete_results
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, NON_AUTH_GROUPS, PICS, BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT
from utils import get_size, is_subscribed, temp
from real_subtitle_handler import real_subtitle_handler as subtitle_handler
import re
import json
import base64
logger = logging.getLogger(__name__)
from os import environ
import time, psutil


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    # Import required modules at the top
    from database.users_chats_db import db
    from .simple_channel_handler import check_user_channels, create_join_buttons
    
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('Uᴘᴅᴀᴛᴇѕ', url='https://t.me/SECL4U')
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            try:
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            except Exception as e:
                logger.error(f"Failed to send log message: {e}")
            await db.add_chat(message.chat.id, message.chat.title)
        return
    
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        try:
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
        except Exception as e:
            logger.error(f"Failed to send log message: {e}")
    # Check if user is subscribed to required channels (skip language selection)
    is_subscribed_all, missing_channels = await check_user_channels(client, message.from_user.id)
    
    if not is_subscribed_all:
        # User needs to join channels
        join_buttons = await create_join_buttons(client, missing_channels)
        
        await message.reply_text(
            "🎬 **Welcome to Movie Bot!**\n\n"
            "❌ **Access Denied**\n\n"
            "You must join **both channels** below to use this bot:\n\n"
            "📋 **Required Channels:**\n"
            "• Movies Channel 1\n"
            "• Movies Channel 2\n\n"
            "Please join both channels and click 'Check Again':",
            reply_markup=join_buttons,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    if len(message.command) != 2:
        # User is subscribed, show main menu
        buttons = [[
                    InlineKeyboardButton('🎬 Search Movies', switch_inline_query_current_chat=''),
                    InlineKeyboardButton('🎭 Browse Collection', callback_data='collection')
                ],[
                    InlineKeyboardButton('🔔 Updates Channel', url='https://t.me/c/2614174192/1'),
                    InlineKeyboardButton('📱 Add to Group', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('ℹ️ About Bot', callback_data='about'),
                    InlineKeyboardButton('❓ Help & Support', callback_data='help')
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=f"🎉 **Welcome {message.from_user.mention}!**\n\n"
                   f"✅ You have access to **{temp.B_NAME}**\n\n"
                   f"🎬 Search movies using inline mode\n"
                   f"🎭 Browse our movie collection\n"
                   f"🔍 All movies with subtitles available!\n\n"
                   f"Choose an option below:",
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
                    InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],[
                    InlineKeyboardButton('🧩 Updates', url='https://t.me/SECL4U'),
                    InlineKeyboardButton('📚 How To Use', url='https://t.me/SECOfficial_Bot')
                ],[
                    InlineKeyboardButton('🛠 Help', callback_data='help'),
                    InlineKeyboardButton('📞 Contact', callback_data='about')
                ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    
    file_id = message.command[1]
    
    # Check if this is a subtitle request
    if '_sub_' in file_id:
        parts = file_id.split('_sub_')
        actual_file_id = parts[0]
        subtitle_language = parts[1]
        
        # Check subscription to required channels (simplified to 2 channels only)
        is_subscribed_all, missing_channels = await check_user_channels(client, message.from_user.id)
        
        if not is_subscribed_all:
            # User needs to join required channels
            subscription_buttons = await create_join_buttons(client, missing_channels)
            await message.reply_text(
                "🔐 **Premium Movie Access**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🎬 **Subtitle Movie Request**\n\n"
                "To access movies with subtitles, join our official channels first.\n\n"
                "🎯 **Quick Steps:**\n"
                "1️⃣ Click the buttons below to join\n"
                "2️⃣ Return and try your request again\n"
                "3️⃣ Enjoy movies with subtitles!\n\n"
                "👇 **Join Our Channels:**",
                reply_markup=subscription_buttons,
                parse_mode="markdown"
            )
            return
            
        # User is subscribed, send movie with subtitles
        await send_movie_with_subtitles(client, message, actual_file_id, subtitle_language)
        return
        
    # Regular file request without subtitles
    files_ = await get_file_details(file_id)           
    if not files_:
        return await message.reply('No such file exist.')
    files = files_
    title = files['file_name']
    size=get_size(files['file_size'])
    f_caption=""
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption=f_caption
    if f_caption is None:
        f_caption = f"{files['file_name']}"
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption
        )
                    

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)



@Client.on_message(filters.command('setchannel') & filters.user(ADMINS))
async def save_channel(client, message):
    try:
        _ids = message.text.split(" ", 1)[1]
    except:
        return await message.reply("No Input!!")
    txt = 'Saved Channels:\n'
    try:
        ids = _ids.split()
        for id in ids:
            chat = await client.get_chat(int(id))
            txt += '\n' + chat.title
    except Exception as e:
        return await message.reply(f"Error: {e}")

    temp.AUTH_CHANNEL = list(map(int, _ids.split()))
    stg = {'AUTH_CHANNEL': _ids}
    await db.update_sttg(stg)
    await message.reply(txt)
    

@Client.on_message(filters.command('getchannel') & filters.user(ADMINS))
async def get_channel(client, message):
    ids = temp.AUTH_CHANNEL
    txt = 'Channels:\n'
    try:
        for id in ids:
            chat = await client.get_chat(int(id))
            txt += '\n' + chat.title
        await message.reply(txt)
    except Exception as e:
        await message.reply(f"Error: {e}")


@Client.on_message(filters.command("delete_files") & filters.user(ADMINS))
async def delete_files(bot, message):
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text("No Input!!")
    files, total_results = await get_delete_results(keyword)
    btn = [[
        InlineKeyboardButton('YES', callback_data=f'del_files#{keyword}')
    ],[
        InlineKeyboardButton('NO', callback_data='close_data')
    ]]
    await message.reply(f'Total {total_results} files found, Do you want to delete?', reply_markup=InlineKeyboardMarkup(btn))
    
    
@Client.on_message(filters.command('ping'))
async def ping(client, message):
    start_time = time.monotonic()
    msg = await message.reply("👀")
    end_time = time.monotonic()
    await msg.edit(f'{round((end_time - start_time) * 1000)} ms')

@Client.on_message(filters.command('checkme') & filters.user(ADMINS))
async def check_my_channels(client, message):
    """Debug command to check admin's channel membership"""
    try:
        from .simple_channel_handler import check_user_channels
        
        user_id = message.from_user.id
        is_subscribed, missing = await check_user_channels(client, user_id)
        
        response = f"🔍 **Channel Check for User {user_id}**\n\n"
        response += f"✅ **Is Subscribed**: {is_subscribed}\n"
        response += f"❌ **Missing Channels**: {missing}\n\n"
        
        # Check each channel individually
        from language_config import get_required_channels
        for channel_id in get_required_channels():
            try:
                member = await client.get_chat_member(int(channel_id), user_id)
                chat = await client.get_chat(int(channel_id))
                response += f"📢 **{chat.title}** (`{channel_id}`)\n"
                response += f"   Status: `{member.status}`\n\n"
            except Exception as e:
                response += f"📢 **Channel {channel_id}**\n"
                response += f"   Error: `{str(e)}`\n\n"
        
        await message.reply(response, parse_mode="markdown")
        
    except Exception as e:
        await message.reply(f"❌ Error checking channels: {e}")


async def send_movie_with_subtitles(client, message, file_id, subtitle_language):
    """Send movie file with subtitles"""
    try:
        # Get movie file details
        files_ = await get_file_details(file_id)
        if not files_:
            await message.reply('No such file exist.')
            return
            
        files = files_
        title = files['file_name']
        size = get_size(files['file_size'])
        
        # Debug: Print file info
        logger.info(f"Attempting to send file: {title}, file_id: {file_id}")
        logger.info(f"File details: {files}")
        
        # Search for subtitles
        await message.reply("🔍 Searching for subtitles...")
        subtitles = await subtitle_handler.search_subtitles(title, subtitle_language)
        
        # Send the movie file
        f_caption = ""
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        
        if f_caption is None:
            f_caption = f"{files['file_name']}"
        
        # Add subtitle info to caption
        f_caption += f"\n\n🗣 **Language:** {subtitle_language.title()}"
        
        # Step 1: Send movie first (try multiple methods)
        movie_sent = False
        try:
            # Method 1: Try send_cached_media (original method)
            await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption
            )
            await message.reply("✅ Movie sent successfully!")
            movie_sent = True
        except Exception as e1:
            logger.error(f"send_cached_media failed: {e1}")
            
            try:
                # Method 2: Try send_document
                await client.send_document(
                    chat_id=message.from_user.id,
                    document=file_id,
                    caption=f_caption
                )
                await message.reply("✅ Movie sent successfully!")
                movie_sent = True
            except Exception as e2:
                logger.error(f"send_document failed: {e2}")
                
                try:
                    # Method 3: Try send_video
                    await client.send_video(
                        chat_id=message.from_user.id,
                        video=file_id,
                        caption=f_caption
                    )
                    await message.reply("✅ Movie sent successfully!")
                    movie_sent = True
                except Exception as e3:
                    logger.error(f"send_video failed: {e3}")
                    await message.reply(f"❌ Movie file unavailable. Sending subtitles only...\n📁 Movie: {title}")
                    # Continue to send subtitles even if movie fails
        
        # Step 2: Process and send subtitles
        if subtitles:
            await message.reply("📥 Processing subtitles...")
            
            subtitle_sent = False
            for i, subtitle in enumerate(subtitles[:1]):  # Send 1 subtitle file for now
                try:
                    subtitle_data = await subtitle_handler.download_subtitle(subtitle, client)
                    if subtitle_data:
                        # Create subtitle file
                        import tempfile
                        temp_dir = tempfile.gettempdir()
                        subtitle_filename = f"{title.replace(' ', '_')}_{subtitle_language}.srt"
                        temp_file = os.path.join(temp_dir, subtitle_filename)
                        
                        # Write subtitle file
                        with open(temp_file, 'wb') as f:
                            f.write(subtitle_data)
                        
                        # Send subtitle file
                        await client.send_document(
                            chat_id=message.from_user.id,
                            document=temp_file,
                            caption=f"🗣 **{subtitle_language.title()} Subtitle**\n🎬 **Movie:** {title}\n📁 **File:** {subtitle_filename}"
                        )
                        
                        # Clean up
                        try:
                            os.remove(temp_file)
                        except:
                            pass
                        
                        subtitle_sent = True
                        break
                        
                except Exception as e:
                    logger.error(f"Error processing subtitle: {e}")
                    continue
            
            if subtitle_sent:
                if movie_sent:
                    await message.reply(f"✅ Movie and subtitle sent successfully!\n🗣 Language: {subtitle_language.title()}")
                else:
                    await message.reply(f"✅ Subtitle sent successfully!\n🗣 Language: {subtitle_language.title()}\n⚠️ Movie file had issues")
            else:
                if movie_sent:
                    await message.reply(f"✅ Movie sent successfully!\n❌ Could not process subtitles for {subtitle_language.title()}")
                else:
                    await message.reply(f"❌ Both movie and subtitles had issues. Please try again later.")
                
        else:
            if movie_sent:
                await message.reply(f"✅ Movie sent successfully!\n❌ No subtitles found for {subtitle_language.title()}")
            else:
                await message.reply(f"❌ Movie file issues and no subtitles found. Please try again later.")
            
    except Exception as e:
        logger.error(f"Error sending movie with subtitles: {e}")
        await message.reply("❌ Error occurred while processing your request.")
    
    finally:
        # Close subtitle handler session
        await subtitle_handler.close_session()

@Client.on_callback_query(filters.regex(r"^about$"))
async def about_bot(client: Client, query):
    """Show bot information"""
    try:
        from utils import temp
        
        about_text = f"""ℹ️ **About {temp.B_NAME}**

🤖 **Bot Name:** {temp.B_NAME}
👨‍💻 **Developer:** [Hasindu Theekshana](https://t.me/Iron_voldy)
🔗 **GitHub:** [Iron-voldy](https://github.com/Iron-voldy)

📋 **Features:**
• 🎬 Movie Search & Download
• 🗣️ Multi-language Subtitles
• 🎭 Movie Collection Browser
• 🔍 Inline Search Support
• 📱 Group & Channel Support

💡 **How to Use:**
1. Search movies using inline mode
2. Browse collections for popular movies
3. Select your language for subtitles
4. Join required channels to access content

🆘 **Need Help?** Use /help command
🔄 **Updates:** @SECL4U"""

        buttons = [[
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"),
            InlineKeyboardButton("❓ Help", callback_data="help")
        ],[
            InlineKeyboardButton("📢 Updates Channel", url="https://t.me/SECL4U"),
            InlineKeyboardButton("👨‍💻 Developer", url="https://t.me/Iron_voldy")
        ]]
        
        await query.message.edit_text(
            about_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="markdown",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error showing about: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^help$"))
async def help_bot(client: Client, query):
    """Show help information"""
    try:
        from utils import temp
        
        help_text = f"""❓ **Help & Support - {temp.B_NAME}**

🔍 **How to Search Movies:**
• Type movie name in inline mode: `@{temp.U_NAME} movie name`
• Use the 🎬 Search Movies button
• Browse collections with 🎭 Browse Collection

🗣️ **Language Selection:**
• Select your language when you first start
• Join required channels for your language
• Bot will provide movies with subtitles

🎭 **Collection Features:**
• 🔥 Popular Movies - Most watched films
• 🆕 Latest Added - Recently added content  
• 🎲 Random Movies - Discover new films

📱 **Commands:**
• `/start` - Start the bot
• `/ping` - Check bot status
• Use inline search for best results

🔧 **Troubleshooting:**
• Join all required channels (2 channels total)
• Try again after joining channels
• Contact support if issues persist

📞 **Support:**
• Updates: @SECL4U
• Developer: @Iron_voldy
• Issues: Report in support group"""

        buttons = [[
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],[
            InlineKeyboardButton("📢 Support Channel", url="https://t.me/SECL4U"),
            InlineKeyboardButton("🎬 Try Search", switch_inline_query_current_chat="")
        ]]
        
        await query.message.edit_text(
            help_text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="markdown",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error showing help: {e}")
        await query.answer("❌ An error occurred. Please try again.")