"""
Simple collection handler for debugging
"""

import logging
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

logger = logging.getLogger(__name__)

# Simple test data
TEST_MOVIES = [
    {
        "name": "Avatar: The Way of Water",
        "rating": "7.6/10",
        "description": "Jake Sully lives with his newfound family formed on the planet of Pandora."
    },
    {
        "name": "Top Gun: Maverick", 
        "rating": "8.3/10",
        "description": "After thirty years, Maverick is still pushing the envelope as a top naval aviator."
    }
]

@Client.on_callback_query(filters.regex(r"^test_collection$"))
async def test_collection(client: Client, query: CallbackQuery):
    """Test collection handler"""
    try:
        logger.info("Test collection called")
        
        text = "🔥 **Test Popular Movies**\n\n"
        
        for i, movie in enumerate(TEST_MOVIES, 1):
            text += f"**{i}. {movie['name']}**\n"
            text += f"⭐ Rating: {movie['rating']}\n"
            text += f"📝 Description: {movie['description']}\n\n"
        
        buttons = [[
            InlineKeyboardButton("🔙 Back", callback_data="collection")
        ]]
        
        await query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        
        logger.info("Test collection completed successfully")
        
    except Exception as e:
        logger.error(f"Error in test collection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await query.answer("❌ Test failed. Check logs.")