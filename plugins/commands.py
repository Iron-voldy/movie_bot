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
    from .channel_handler import check_user_subscriptions, create_subscription_buttons, show_language_selection
    
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
    if len(message.command) != 2:
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
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    # Check user's language preference
    
    user_language = await db.get_user_language(message.from_user.id)
    
    if not user_language:
        # User hasn't selected a language yet
        language_buttons = await show_language_selection(client, message.from_user.id)
        await client.send_message(
            chat_id=message.from_user.id,
            text="🌐 **Welcome!** Please select your language to continue:\n\n"
                 "You'll need to join 2 channels:\n"
                 "1. Common Updates Channel (for all users)\n"
                 "2. Language-specific Channel (for your chosen language)",
            reply_markup=language_buttons,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    
    # Check if user is subscribed to required channels
    is_subscribed_all, missing_channels, _ = await check_user_subscriptions(client, message.from_user.id, user_language)
    
    if not is_subscribed_all:
        # User needs to join channels
        subscription_buttons = await create_subscription_buttons(
            client, message.from_user.id, user_language, f"check_subscription_{user_language}"
        )
        
        from language_config import get_language_display_name
        await client.send_message(
            chat_id=message.from_user.id,
            text=f"🎯 **Your Language**: {get_language_display_name(user_language)}\n\n"
                 "📋 **Required Channels:**\n"
                 "1. Common Updates Channel (for all users)\n"
                 f"2. {get_language_display_name(user_language)} Channel (for your language)\n\n"
                 "Please join both channels to continue:",
            reply_markup=subscription_buttons,
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
        
        # Get subtitle preferences
        subtitle_prefs = getattr(temp, 'SUBTITLE_PREFS', {}).get(message.from_user.id, {})
        
        if subtitle_prefs and subtitle_prefs.get('language') == subtitle_language:
            # Use language-specific channels for authorization
            language_channels = subtitle_prefs.get('channels', [])
            auth_channels = [int(ch) for ch in language_channels]
        else:
            # Fallback to default channels
            auth_channels = temp.AUTH_CHANNEL
            
        # Check subscription to language-specific channels
        btn = []
        for channel in auth_channels:
            if not await is_subscribed(client, message, channel):
                try:
                    invite_link = await client.create_chat_invite_link(channel, creates_join_request=True)
                    chat = await client.get_chat(channel)
                    btn.append(
                        [InlineKeyboardButton(f"✇ Join {chat.title} ✇", url=invite_link.invite_link)]
                    )
                except Exception as e:
                    logger.error(f"Error creating invite link for channel {channel}: {e}")
                    continue

        if btn:
            btn.append([InlineKeyboardButton("🔄 Try Again", url=f"https://t.me/{temp.U_NAME}?start={file_id}")])
            await client.send_message(
                chat_id=message.from_user.id,
                text=f"**Please Join {subtitle_language.title()} Movie Channels to get subtitles!**\n\n"
                     f"🗣 **Language:** {subtitle_language.title()}\n"
                     f"🎬 **Includes:** Movie + Subtitles",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
            )
            return
            
        # User is subscribed to language channels, send movie with subtitles
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

@Client.on_message(filters.command("subtitle_stats") & filters.private & filters.user(ADMINS))
async def subtitle_stats(client, message):
    """Show subtitle statistics for admins"""
    try:
        from subtitle_channel_manager import subtitle_channel_manager
        
        stats = await subtitle_channel_manager.get_subtitle_stats(client)
        
        if stats:
            stats_text = f"""📊 **Subtitle Statistics**

📁 Total Subtitles: {stats.get('total_subtitles', 0)}
🎬 Unique Movies: {stats.get('unique_movies', 0)}

🗣️ **Languages:**
"""
            for lang, count in stats.get('languages', {}).items():
                stats_text += f"• {lang.title()}: {count}\n"
            
            await message.reply(stats_text)
        else:
            await message.reply("❌ No subtitle statistics available")
            
    except Exception as e:
        await message.reply(f"❌ Error getting statistics: {e}")

@Client.on_message(filters.command("test_subtitle") & filters.private & filters.user(ADMINS))
async def test_subtitle_download(client, message):
    """Test subtitle download for admins"""
    try:
        # Parse command: /test_subtitle movie_name language
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            await message.reply("Usage: /test_subtitle <movie_name> <language>\nExample: /test_subtitle KGF english")
            return
        
        movie_name = parts[1]
        language = parts[2]
        
        await message.reply(f"🔍 Testing subtitle download for:\n📽️ Movie: {movie_name}\n🗣️ Language: {language}")
        
        from subtitle_channel_manager import subtitle_channel_manager
        
        # Test subtitle download
        subtitle_content = await subtitle_channel_manager.get_subtitle(client, movie_name, language)
        
        if subtitle_content:
            # Create and send subtitle file
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            subtitle_filename = f"{movie_name.replace(' ', '_')}_{language}_test.srt"
            temp_file = os.path.join(temp_dir, subtitle_filename)
            
            with open(temp_file, 'wb') as f:
                f.write(subtitle_content)
            
            await client.send_document(
                chat_id=message.chat.id,
                document=temp_file,
                file_name=subtitle_filename,
                caption=f"✅ Test subtitle for {movie_name} ({language})\nSize: {len(subtitle_content)} bytes"
            )
            
            os.remove(temp_file)
        else:
            await message.reply("❌ Failed to get subtitle")
            
    except Exception as e:
        await message.reply(f"❌ Error testing subtitle: {e}")

@Client.on_message(filters.command("api_limits") & filters.private & filters.user(ADMINS))
async def check_api_limits(client, message):
    """Check OpenSubtitles API usage and limits"""
    try:
        import aiohttp
        from subtitle_config import OPENSUBTITLES_API_KEY
        
        if not OPENSUBTITLES_API_KEY:
            await message.reply("❌ No OpenSubtitles API key configured")
            return
        
        async with aiohttp.ClientSession() as session:
            url = "https://api.opensubtitles.com/api/v1/infos/user"
            headers = {
                'Api-Key': OPENSUBTITLES_API_KEY,
                'Content-Type': 'application/json',
                'User-Agent': 'SubtitleBot v1.0'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    user_info = data.get('data', {})
                    
                    username = user_info.get('username', 'N/A')
                    downloads_today = user_info.get('downloads_count', 0)
                    downloads_limit = user_info.get('downloads_limit', 0)
                    remaining = downloads_limit - downloads_today
                    
                    # Calculate percentage used
                    if downloads_limit > 0:
                        percentage = (downloads_today / downloads_limit) * 100
                    else:
                        percentage = 0
                    
                    status_text = f"""📊 **OpenSubtitles API Status**

👤 **User**: {username}
🔑 **API Key**: {OPENSUBTITLES_API_KEY[:8]}...

📈 **Daily Limits**:
• Downloaded today: {downloads_today}
• Daily limit: {downloads_limit}
• Remaining: {remaining}
• Usage: {percentage:.1f}%

{'🟢 Good' if percentage < 50 else '🟡 Moderate' if percentage < 80 else '🔴 High'} usage level

💡 **Tips**:
• Cached subtitles don't count toward limits
• Limits reset daily at midnight UTC
• Free accounts get 200 downloads/day"""
                    
                    await message.reply(status_text)
                    
                elif response.status == 401:
                    await message.reply("❌ Invalid API key")
                elif response.status == 403:
                    await message.reply("❌ Access forbidden - check API key permissions")
                else:
                    await message.reply(f"❌ API error: Status {response.status}")
                    
    except Exception as e:
        await message.reply(f"❌ Error checking API limits: {e}")

@Client.on_message(filters.command("optimization_stats") & filters.private & filters.user(ADMINS))
async def optimization_stats(client, message):
    """Show optimization statistics"""
    try:
        from advanced_subtitle_optimizer import subtitle_optimizer
        
        stats = await subtitle_optimizer.get_optimization_stats()
        
        if stats:
            stats_text = f"""🚀 **Subtitle Optimization Stats**

📊 **Performance Metrics**:
• Total requests: {stats.get('total_requests', 0)}
• Cached subtitles: {stats.get('cached_subtitles', 0)}
• Unique movies: {stats.get('unique_movies', 0)}
• Cache hit ratio: {stats.get('cache_hit_ratio', 0):.1f}%

🔑 **API Usage**:
• Used today: {stats.get('api_usage_today', 0)}
• Remaining: {stats.get('api_remaining', 0)}
• Efficiency score: {stats.get('efficiency_score', 0):.1f}%

💡 **Optimization Impact**:
• API calls saved: ~{int(stats.get('total_requests', 0) - stats.get('api_usage_today', 0))}
• User capacity multiplier: {stats.get('total_requests', 0) // max(stats.get('api_usage_today', 1), 1)}x

🎯 **Performance Level**:
{get_performance_emoji(stats.get('cache_hit_ratio', 0))} {get_performance_level(stats.get('cache_hit_ratio', 0))}"""
            
            await message.reply(stats_text)
        else:
            await message.reply("❌ No optimization statistics available")
            
    except Exception as e:
        await message.reply(f"❌ Error getting optimization stats: {e}")

@Client.on_message(filters.command("popular_movies") & filters.private & filters.user(ADMINS))
async def show_popular_movies(client, message):
    """Show most popular movies"""
    try:
        from advanced_subtitle_optimizer import subtitle_optimizer
        
        popular = await subtitle_optimizer.get_popular_movies(10)
        
        if popular:
            movie_list = "🎬 **Most Popular Movies**\n\n"
            for i, movie in enumerate(popular, 1):
                movie_list += f"{i}. **{movie['movie_name']}**\n"
                movie_list += f"   📊 Requests: {movie['request_count']}\n"
                movie_list += f"   🗣️ Languages: {', '.join(movie.get('languages', []))}\n\n"
            
            await message.reply(movie_list)
        else:
            await message.reply("❌ No popular movies data available")
            
    except Exception as e:
        await message.reply(f"❌ Error getting popular movies: {e}")

@Client.on_message(filters.command("preload_suggestions") & filters.private & filters.user(ADMINS))
async def preload_suggestions(client, message):
    """Show suggestions for preloading subtitles"""
    try:
        from advanced_subtitle_optimizer import subtitle_optimizer
        
        suggestions = await subtitle_optimizer.suggest_preload_subtitles()
        
        if suggestions:
            suggestion_text = "💡 **Preload Suggestions**\n\n"
            suggestion_text += "These popular movies should be preloaded:\n\n"
            
            for i, suggestion in enumerate(suggestions[:10], 1):
                suggestion_text += f"{i}. **{suggestion['movie_name']}** ({suggestion['language']})\n"
                suggestion_text += f"   📊 Priority: {suggestion['priority']} requests\n\n"
            
            suggestion_text += "💭 Use `/test_subtitle MovieName language` to preload"
            
            await message.reply(suggestion_text)
        else:
            await message.reply("✅ No preload suggestions - cache is optimal!")
            
    except Exception as e:
        await message.reply(f"❌ Error getting preload suggestions: {e}")

def get_performance_emoji(ratio):
    """Get emoji based on performance ratio"""
    if ratio >= 80:
        return "🚀"
    elif ratio >= 60:
        return "🔥"
    elif ratio >= 40:
        return "📈"
    elif ratio >= 20:
        return "⚡"
    else:
        return "🎯"

def get_performance_level(ratio):
    """Get performance level description"""
    if ratio >= 80:
        return "Excellent - Maximum efficiency!"
    elif ratio >= 60:
        return "Great - High efficiency"
    elif ratio >= 40:
        return "Good - Moderate efficiency"
    elif ratio >= 20:
        return "Fair - Building cache"
    else:
        return "Starting - Cache warming up"
