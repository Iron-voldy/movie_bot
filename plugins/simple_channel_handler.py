"""
Simplified channel handler - Only checks 2 required channels
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from hydrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid
from database.users_chats_db import db
from language_config import REQUIRED_CHANNELS, get_required_channels
from utils import is_subscribed, temp

logger = logging.getLogger(__name__)

async def check_user_channels(client: Client, user_id: int) -> tuple:
    """
    Check if user is subscribed to both required channels
    Returns (is_subscribed, missing_channels)
    """
    missing_channels = []
    required_channel_ids = get_required_channels()
    
    for channel_id in required_channel_ids:
        try:
            subscribed = await is_subscribed(client, user_id, int(channel_id))
            logger.info(f"User {user_id} subscription to {channel_id}: {subscribed}")
            if not subscribed:
                missing_channels.append(int(channel_id))
        except Exception as e:
            logger.error(f"Error checking subscription for {channel_id}: {e}")
            missing_channels.append(int(channel_id))
    
    logger.info(f"User {user_id} missing channels: {missing_channels}")
    return len(missing_channels) == 0, missing_channels

async def create_join_buttons(client: Client, missing_channels: list) -> InlineKeyboardMarkup:
    """Create buttons for joining missing channels"""
    buttons = []
    
    for channel_id in missing_channels:
        try:
            chat = await client.get_chat(channel_id)
            # Try to create invite link
            try:
                invite_link = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                button_text = f"✇ Join {chat.title} ✇"
                buttons.append([
                    InlineKeyboardButton(button_text, url=invite_link.invite_link)
                ])
            except Exception as e:
                logger.error(f"Could not create invite link for {channel_id}: {e}")
                # Fallback - use channel username if available
                if chat.username:
                    buttons.append([
                        InlineKeyboardButton(f"✇ Join {chat.title} ✇", url=f"https://t.me/{chat.username}")
                    ])
                else:
                    buttons.append([
                        InlineKeyboardButton(f"✇ Join {chat.title} ✇", callback_data=f"manual_join_{channel_id}")
                    ])
        except Exception as e:
            logger.error(f"Error creating button for channel {channel_id}: {e}")
            continue
    
    # Add check again button
    buttons.append([
        InlineKeyboardButton("🔄 Check Again", callback_data="check_channels_again")
    ])
    
    return InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex(r"^check_channels_again$"))
async def check_channels_again(client: Client, query: CallbackQuery):
    """Check channels again after user joins"""
    try:
        user_id = query.from_user.id
        
        # Check if user is now subscribed to all channels
        is_subscribed, missing_channels = await check_user_channels(client, user_id)
        
        if is_subscribed:
            await query.answer("✅ Great! You are now subscribed to all required channels!")
            
            # Show main menu
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
                f"🎉 **Welcome to {temp.B_NAME}!**\n\n"
                "✅ You are now subscribed to all required channels.\n"
                "🎬 You can now search and download movies!\n\n"
                "Choose an option below:",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="markdown"
            )
        else:
            await query.answer("❌ Please join all required channels first!")
            
            # Show join buttons again
            join_buttons = await create_join_buttons(client, missing_channels)
            await query.message.edit_text(
                "❌ **Access Denied**\n\n"
                "You must join **both channels** below to use this bot:\n\n"
                "📋 **Required Channels:**\n"
                "• Movies Channel 1\n"
                "• Movies Channel 2\n\n"
                "Please join both channels and click 'Check Again':",
                reply_markup=join_buttons,
                parse_mode="markdown"
            )
            
    except Exception as e:
        logger.error(f"Error checking channels again: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^manual_join_"))
async def manual_join_info(client: Client, query: CallbackQuery):
    """Show manual join instructions"""
    try:
        channel_id = query.data.split("_")[2]
        await query.answer(f"Please manually join the channel {channel_id} and then click 'Check Again'", show_alert=True)
    except Exception as e:
        logger.error(f"Error in manual join info: {e}")
        await query.answer("❌ Please join the channel manually.")