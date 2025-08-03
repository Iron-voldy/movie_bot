"""
Advanced Auto-Filter System - PROFESSOR-BOT Style
Enhanced with spell check, Google search, and intelligent search patterns
"""
import asyncio
import re
import math
import logging
import aiohttp
import json
from urllib.parse import quote_plus
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from hydrogram.errors import FloodWait, UserIsBlocked, MessageNotModified

from database.advanced_filterdb import get_search_results, get_search_suggestions, get_popular_movies
from utils import format_size, remove_username_from_filename, get_size, temp
from info import ADMINS, PICS, CUSTOM_FILE_CAPTION, SINGLE_BUTTON, IMDB, SPELL_CHECK_REPLY
from real_subtitle_handler import real_subtitle_handler as subtitle_handler
import random

logger = logging.getLogger(__name__)

# Storage for button states and pagination
BUTTONS = {}
SPELL_CHECK = {}
ORIGINAL_FILES = {}
SELECTIONS = {}
FILES = {}

# PROFESSOR-BOT style search patterns
STOP_WORDS = [
    'pl', 'pls', 'please', 'plz', 'plss', 'send', 'snd', 'give', 'giv', 'gib', 'movie', 'movies',
    'new', 'latest', 'br', 'bro', 'bruh', 'hello', 'hi', 'hey', 'helo', 'hii', 'mal', 'malayalam',
    'tamil', 'file', 'that', 'find', 'und', 'kit', 'kitto', 'thar', 'tharu', 'tharumo', 'kittum',
    'aya', 'ayak', 'ayakum', 'full', 'any', 'anyone', 'with', 'subtitle', 'subtitles'
]

async def clean_search_query(query: str) -> str:
    """Clean search query by removing common words and patterns"""
    try:
        # Remove common patterns (PROFESSOR-BOT style)
        query = re.sub(
            r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
            "", query, flags=re.IGNORECASE
        )
        
        # Remove extra spaces and common symbols
        query = re.sub(r'[^\w\s]', ' ', query)
        query = ' '.join(query.split())
        
        return query.strip()
        
    except Exception as e:
        logger.error(f"Error cleaning search query: {e}")
        return query

async def search_google_suggestions(query: str) -> list:
    """Get Google search suggestions for spell check"""
    try:
        if len(query) < 3:
            return []
            
        # Simple Google search API call (you can enhance this)
        suggestions = []
        
        # For now, return some common movie-related suggestions
        # You can implement actual Google API integration here
        common_suggestions = [
            f"{query} movie",
            f"{query} film",
            f"{query} download",
            f"{query} 2023",
            f"{query} 2024"
        ]
        
        return common_suggestions[:3]
        
    except Exception as e:
        logger.error(f"Error getting Google suggestions: {e}")
        return []

async def handle_spell_check(client: Client, message, original_query: str):
    """Handle spell check and suggestions when no results found"""
    try:
        # Get database suggestions
        db_suggestions = await get_search_suggestions(original_query)
        
        # Get Google suggestions
        google_suggestions = await search_google_suggestions(original_query)
        
        # Combine suggestions
        all_suggestions = db_suggestions + google_suggestions
        
        if not all_suggestions:
            # No suggestions found
            await message.reply(
                f"🔍 **No Results Found**\n\n"
                f"**Searched for:** `{original_query}`\n\n"
                f"**Suggestions:**\n"
                f"• Check spelling\n"
                f"• Try different keywords\n"
                f"• Search with movie year\n"
                f"• Use English movie name\n\n"
                f"💡 **Popular Movies** available - type `/popular`",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔍 Search Google", url=f"https://www.google.com/search?q={quote_plus(original_query + ' movie')}")
                ]])
            )
            return
        
        # Create suggestion buttons
        buttons = []
        for suggestion in all_suggestions[:8]:  # Limit to 8 suggestions
            buttons.append([
                InlineKeyboardButton(
                    f"🎬 {suggestion}",
                    callback_data=f"suggestion#{suggestion}"
                )
            ])
        
        # Add Google search option
        buttons.append([
            InlineKeyboardButton(
                "🔍 Search Google",
                url=f"https://www.google.com/search?q={quote_plus(original_query + ' movie')}"
            )
        ])
        
        await message.reply(
            f"🔍 **No Exact Match Found**\n\n"
            f"**You searched:** `{original_query}`\n\n"
            f"**Did you mean:**",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        logger.error(f"Error in spell check: {e}")
        await message.reply("🔍 No results found. Please try different keywords.")

@Client.on_callback_query(filters.regex(r"^suggestion"))
async def handle_suggestion_click(client: Client, query):
    """Handle clicks on suggestion buttons"""
    try:
        _, suggested_query = query.data.split("#", 1)
        
        # Update the message to show search is happening
        await query.message.edit_text(f"🔍 Searching for: **{suggested_query}**...")
        
        # Perform search with suggested query
        await perform_auto_filter(client, query.message, suggested_query, from_suggestion=True)
        
    except Exception as e:
        logger.error(f"Error handling suggestion click: {e}")
        await query.answer("❌ Error processing suggestion", show_alert=True)

async def perform_auto_filter(client: Client, message, search_query: str = None, from_suggestion: bool = False):
    """Enhanced auto-filter with PROFESSOR-BOT features"""
    try:
        # Use provided query or extract from message
        if search_query:
            search = search_query
        else:
            search = message.text.strip()
        
        # Skip commands
        if search.startswith('/'):
            return
        
        # Clean the search query
        cleaned_search = await clean_search_query(search)
        
        if len(cleaned_search) < 2:
            await message.reply("🔍 Please provide a longer search term (at least 2 characters)")
            return
        
        logger.info(f"Auto-filter search: '{search}' -> '{cleaned_search}'")
        
        # Search for files
        files, next_offset, total_results = await get_search_results(
            cleaned_search, 
            max_results=10,
            offset=0
        )
        
        if not files:
            # No results - trigger spell check
            await handle_spell_check(client, message, search)
            return
        
        # Files found - display results
        await display_search_results(
            client, message, files, next_offset, total_results, cleaned_search, from_suggestion
        )
        
    except Exception as e:
        logger.error(f"Error in perform_auto_filter: {e}")
        await message.reply("❌ An error occurred while searching. Please try again.")

async def display_search_results(client: Client, message, files: list, next_offset, total_results: int, search_query: str, from_suggestion: bool = False):
    """Display search results with PROFESSOR-BOT style formatting"""
    try:
        # Create file buttons
        btn = []
        for file in files:
            file_name = remove_username_from_filename(file['file_name'])
            file_size = format_size(get_size(file['file_size']))
            
            btn.append([
                InlineKeyboardButton(
                    text=f"{file_size} - {file_name}",
                    callback_data=f'files#{file["_id"]}'
                )
            ])
        
        # Add pagination if needed
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search_query
        ORIGINAL_FILES[key] = files
        FILES[key] = files
        SELECTIONS[key] = {'language': 'any', 'resolution': 'any', 'category': 'any'}
        req = message.from_user.id if message.from_user else 0
        
        # Add filter buttons (PROFESSOR-BOT style)
        btn.insert(0, [
            InlineKeyboardButton('🗣 Language', callback_data=f"language#{req}#{key}"),
            InlineKeyboardButton('▶️ Resolution', callback_data=f"resolution#{req}#{key}")
        ])
        btn.insert(1, [
            InlineKeyboardButton('🎦 Category', callback_data=f"category#{req}#{key}")
        ])
        
        # Add pagination buttons
        if next_offset:
            btn.append([
                InlineKeyboardButton(f"📃 1/{math.ceil(total_results / 10)}", callback_data="pages"),
                InlineKeyboardButton("Next ⏩", callback_data=f"next_{req}_{key}_{next_offset}")
            ])
        else:
            btn.append([
                InlineKeyboardButton("📃 No More Pages", callback_data="pages")
            ])
        
        # Create caption
        caption = f"""<b>"{search_query}"</b>
<b>Found {total_results} result{'s' if total_results > 1 else ''}!</b> ✨

<b>Choose your preferred options below to find the best match</b> 🔻

🗣 Language | ▶️ Resolution | 🎦 Category"""
        
        # Send or edit message
        if from_suggestion:
            await message.edit_text(
                caption, 
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.HTML
            )
        else:
            # Send new message with photo
            photo = random.choice(PICS) if PICS else None
            if photo:
                m = await message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.HTML
                )
            else:
                m = await message.reply_text(
                    caption,
                    reply_markup=InlineKeyboardMarkup(btn),
                    parse_mode=enums.ParseMode.HTML
                )
            
            # Auto-delete after 10 minutes
            asyncio.create_task(delete_message_after_delay(m, 600))
        
    except Exception as e:
        logger.error(f"Error displaying search results: {e}")
        await message.reply("❌ Error displaying results. Please try again.")

async def delete_message_after_delay(message, delay: int):
    """Delete message after specified delay"""
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except Exception as e:
        logger.debug(f"Could not delete message: {e}")

@Client.on_message(filters.group & filters.text & filters.incoming)
async def group_auto_filter(client: Client, message):
    """Group auto-filter handler"""
    try:
        # Check if auto-filter is enabled for this group
        # You can add group-specific settings here
        
        if len(message.text) < 2 or len(message.text) > 100:
            return
        
        await perform_auto_filter(client, message)
        
    except Exception as e:
        logger.error(f"Error in group auto-filter: {e}")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def private_auto_filter(client: Client, message):
    """Private auto-filter handler"""
    try:
        if message.text.startswith('/'):
            return
        
        # Check channel subscriptions first
        from database.users_chats_db import db
        from .simple_channel_handler import check_user_channels, create_join_buttons
        
        if message.from_user:
            is_subscribed_all, missing_channels = await check_user_channels(
                client, message.from_user.id
            )
            
            if not is_subscribed_all:
                subscription_buttons = await create_join_buttons(client, missing_channels)
                await message.reply(
                    "🚫 **Channel Membership Required**\n"
                    "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    "🎭 **Welcome to our Movie Bot!**\n\n"
                    "To search and download movies, join our official channels first.\n\n"
                    "🎯 **Easy Steps:**\n"
                    "1️⃣ Click the numbered buttons below\n"
                    "2️⃣ Join each channel\n"
                    "3️⃣ Come back and click '🔄 Check Again'\n\n"
                    "🎬 **Unlimited Access Awaits!**\n\n"
                    "👇 **Join Now:**",
                    reply_markup=subscription_buttons,
                    parse_mode="markdown"
                )
                return
        
        if len(message.text) < 2 or len(message.text) > 100:
            return
        
        await perform_auto_filter(client, message)
        
    except Exception as e:
        logger.error(f"Error in private auto-filter: {e}")

# Command handlers
@Client.on_message(filters.command("popular") & filters.incoming)
async def popular_movies_command(client: Client, message):
    """Show popular/trending movies"""
    try:
        popular_movies = await get_popular_movies(max_results=20)
        
        if not popular_movies:
            await message.reply("📊 **No popular movies data available yet.**\n\nAdd some movies to see trending content!")
            return
        
        # Create buttons for popular movies
        buttons = []
        for i, movie in enumerate(popular_movies[:10], 1):
            movie_name = movie['file_name']
            # Clean movie name for display
            clean_name = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v)$', '', movie_name, flags=re.IGNORECASE)
            clean_name = re.sub(r'\s*[\(\[].*?[\)\]]', '', clean_name)[:30]
            
            buttons.append([
                InlineKeyboardButton(
                    f"{i}. {clean_name}",
                    callback_data=f"popular_search#{movie_name}"
                )
            ])
        
        caption = """🔥 **Popular & Trending Movies**

📊 **Most Downloaded:**
Click on any movie below to search and download

💡 **Tip:** These are the most popular movies based on file size and recent additions"""
        
        await message.reply_text(
            caption,
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        logger.error(f"Error in popular movies command: {e}")
        await message.reply("❌ Error fetching popular movies.")

@Client.on_callback_query(filters.regex(r"^popular_search"))
async def handle_popular_search(client: Client, query):
    """Handle popular movie search"""
    try:
        _, movie_name = query.data.split("#", 1)
        
        # Clean the movie name for search
        search_query = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v)$', '', movie_name, flags=re.IGNORECASE)
        search_query = re.sub(r'\s*[\(\[].*?[\)\]]', '', search_query)
        
        await query.message.edit_text(f"🔍 Searching for: **{search_query}**...")
        
        # Perform search
        await perform_auto_filter(client, query.message, search_query, from_suggestion=True)
        
    except Exception as e:
        logger.error(f"Error handling popular search: {e}")
        await query.answer("❌ Error processing search", show_alert=True)

# Keep your existing subtitle functionality by importing from pm_filter.py
from plugins.pm_filter import (
    send_subtitle_file, next_page, language, lang_select, 
    resolution, resltn_select, category, catgry_select, cb_handler
)