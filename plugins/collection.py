"""
Movie collection handler for browse collection feature
Handles popular movies, latest movies, and random movies
"""

import random
import logging
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from movie_data import POPULAR_MOVIES, LATEST_MOVIES, RANDOM_MOVIES

logger = logging.getLogger(__name__)

# Pagination settings
MOVIES_PER_PAGE = 5

@Client.on_callback_query(filters.regex(r"^collection$"))
async def show_collection_menu(client: Client, query: CallbackQuery):
    """Show the main collection menu"""
    try:
        buttons = [
            [
                InlineKeyboardButton("🔥 Popular Movies", callback_data="popular_movies#0"),
                InlineKeyboardButton("🧪 Test Collection", callback_data="test_collection")
            ],
            [
                InlineKeyboardButton("🆕 Latest Added", callback_data="latest_movies#0"),
                InlineKeyboardButton("🎲 Random Movies", callback_data="random_movies#0")
            ],
            [
                InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
            ]
        ]
        
        await query.message.edit_text(
            "🎭 **Movie Collection**\n\n"
            "Browse our extensive movie collection:\n\n"
            "🔥 **Popular Movies** - Most watched movies\n"
            "🆕 **Latest Added** - Recently added movies\n"
            "🎲 **Random Movies** - Discover something new\n\n"
            "Choose a category to explore:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        
    except Exception as e:
        logger.error(f"Error showing collection menu: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^popular_movies#(\d+)"))
async def show_popular_movies(client: Client, query: CallbackQuery):
    """Show popular movies with pagination"""
    try:
        logger.info(f"Popular movies callback triggered: {query.data}")
        page = int(query.data.split("#")[1])
        logger.info(f"Page number: {page}")
        await show_movie_list(query, POPULAR_MOVIES, "🔥 Popular Movies", "popular_movies", page)
    except Exception as e:
        logger.error(f"Error showing popular movies: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^latest_movies#(\d+)"))
async def show_latest_movies(client: Client, query: CallbackQuery):
    """Show latest movies with pagination"""
    try:
        page = int(query.data.split("#")[1])
        await show_movie_list(query, LATEST_MOVIES, "🆕 Latest Added Movies", "latest_movies", page)
    except Exception as e:
        logger.error(f"Error showing latest movies: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^random_movies#(\d+)"))
async def show_random_movies(client: Client, query: CallbackQuery):
    """Show random movies with pagination"""
    try:
        page = int(query.data.split("#")[1])
        # Shuffle the movies for true randomness
        shuffled_movies = RANDOM_MOVIES.copy()
        random.shuffle(shuffled_movies)
        await show_movie_list(query, shuffled_movies, "🎲 Random Movies", "random_movies", page)
    except Exception as e:
        logger.error(f"Error showing random movies: {e}")
        await query.answer("❌ An error occurred. Please try again.")

async def show_movie_list(query: CallbackQuery, movies: list, title: str, callback_prefix: str, page: int):
    """Display paginated movie list"""
    try:
        logger.info(f"Showing movie list: {title}, page: {page}")
        start_idx = page * MOVIES_PER_PAGE
        end_idx = start_idx + MOVIES_PER_PAGE
        page_movies = movies[start_idx:end_idx]
        
        if not page_movies:
            await query.answer("No more movies available.", show_alert=True)
            return
        
        # Build movie list text
        text = f"{title}\n\n"
        
        for i, movie in enumerate(page_movies, 1):
            movie_num = start_idx + i
            text += f"**{movie_num}. {movie['name']}**\n"
            text += f"⭐ **Rating:** {movie['rating']}\n"
            
            # Truncate description if too long
            description = movie['description']
            if len(description) > 150:
                description = description[:150] + "..."
            
            text += f"📝 **Description:** {description}\n\n"
            text += "─" * 30 + "\n\n"
        
        # Navigation buttons
        buttons = []
        nav_buttons = []
        
        # Previous page button
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}#{page-1}")
            )
        
        # Page indicator
        total_pages = (len(movies) - 1) // MOVIES_PER_PAGE + 1
        nav_buttons.append(
            InlineKeyboardButton(f"📄 {page + 1}/{total_pages}", callback_data="pages_info")
        )
        
        # Next page button
        if end_idx < len(movies):
            nav_buttons.append(
                InlineKeyboardButton("➡️ Next", callback_data=f"{callback_prefix}#{page+1}")
            )
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # Action buttons
        action_buttons = [
            InlineKeyboardButton("🔄 Refresh List", callback_data=f"{callback_prefix}#{page}"),
            InlineKeyboardButton("🔙 Back to Collection", callback_data="collection")
        ]
        buttons.append(action_buttons)
        
        # Search all button
        buttons.append([
            InlineKeyboardButton("🔍 Search All Movies", switch_inline_query_current_chat="")
        ])
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error in show_movie_list: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        # Send simple error message
        await query.message.edit_text(
            f"❌ Error loading {title}\n\nPlease try again later.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 Back to Collection", callback_data="collection")
            ]])
        )

@Client.on_callback_query(filters.regex(r"^back_to_main$"))
async def back_to_main_menu(client: Client, query: CallbackQuery):
    """Go back to the main bot menu"""
    try:
        from utils import temp
        
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
        
        await query.message.edit_text(
            f"🎬 **Welcome to {temp.B_NAME}!**\n\n"
            "🔍 Search movies using inline mode\n"
            "🎭 Browse our movie collection\n"
            "🗣️ Get subtitles in multiple languages\n\n"
            "Choose an option below:",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error going back to main menu: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^pages_info$"))
async def pages_info(client: Client, query: CallbackQuery):
    """Show page information"""
    await query.answer("📄 Page navigation - Use Previous/Next buttons to browse", show_alert=True)

# Handle movie search from collection
@Client.on_message(filters.command("start") & filters.regex(r"search_"))
async def handle_movie_search(client: Client, message):
    """Handle movie search from collection links"""
    try:
        if len(message.command) > 1:
            search_query = message.command[1]
            if search_query.startswith("search_"):
                movie_name = search_query.replace("search_", "").replace("_", " ")
                
                # Provide search instructions
                await message.reply(
                    f"🔍 **Searching for: {movie_name}**\n\n"
                    f"Use the inline search to find this movie:\n"
                    f"Type: `@{message.via_bot.username if message.via_bot else 'yourbotusername'} {movie_name}`\n\n"
                    f"Or use the search button below:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(f"🔍 Search '{movie_name}'", switch_inline_query_current_chat=movie_name)
                    ]])
                )
                
    except Exception as e:
        logger.error(f"Error handling movie search: {e}")
        await message.reply("❌ Error processing search request.")