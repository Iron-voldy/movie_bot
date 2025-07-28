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
    from info import ADMINS
    
    # Always allow admins
    if user_id in ADMINS:
        logger.info(f"User {user_id} is admin - granting access")
        return True, []
    
    missing_channels = []
    required_channel_ids = get_required_channels()
    
    logger.info(f"Checking channels for user {user_id}: {required_channel_ids}")
    
    for channel_id in required_channel_ids:
        try:
            # Direct channel member check
            member = await client.get_chat_member(int(channel_id), user_id)
            logger.info(f"User {user_id} status in {channel_id}: {member.status}")
            
            # Check if user is actually a member (not just in db)
            if member.status in ["creator", "administrator", "member"]:
                logger.info(f"✅ User {user_id} IS member of {channel_id}")
            else:
                logger.info(f"❌ User {user_id} NOT member of {channel_id} (status: {member.status})")
                missing_channels.append(int(channel_id))
                
        except Exception as e:
            logger.error(f"❌ Error checking {channel_id} for user {user_id}: {e}")
            missing_channels.append(int(channel_id))
    
    is_all_subscribed = len(missing_channels) == 0
    logger.info(f"Final result for user {user_id}: subscribed={is_all_subscribed}, missing={missing_channels}")
    
    return is_all_subscribed, missing_channels

async def create_join_buttons(client: Client, missing_channels: list) -> InlineKeyboardMarkup:
    """Create numbered buttons for joining missing channels with direct links"""
    buttons = []
    channel_counter = 1
    
    for channel_id in missing_channels:
        try:
            chat = await client.get_chat(channel_id)
            
            # Try to create invite link first
            try:
                invite_link = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                button_text = f"[{channel_counter}] Join {chat.title}"
                buttons.append([
                    InlineKeyboardButton(button_text, url=invite_link.invite_link)
                ])
                logger.info(f"Created invite link for {channel_id}: {invite_link.invite_link}")
                channel_counter += 1
            except Exception as e:
                logger.error(f"Could not create invite link for {channel_id}: {e}")
                # Fallback - use channel username if available
                if hasattr(chat, 'username') and chat.username:
                    button_text = f"[{channel_counter}] Join {chat.title}"
                    buttons.append([
                        InlineKeyboardButton(button_text, url=f"https://t.me/{chat.username}")
                    ])
                    logger.info(f"Using username link for {channel_id}: @{chat.username}")
                    channel_counter += 1
                else:
                    # Try to get chat invite link from chat info
                    try:
                        if hasattr(chat, 'invite_link') and chat.invite_link:
                            button_text = f"[{channel_counter}] Join {chat.title}"
                            buttons.append([
                                InlineKeyboardButton(button_text, url=chat.invite_link)
                            ])
                            logger.info(f"Using chat invite link for {channel_id}")
                            channel_counter += 1
                        else:
                            # Manual join instruction as last resort
                            button_text = f"[{channel_counter}] {chat.title} (Manual Join Required)"
                            buttons.append([
                                InlineKeyboardButton(button_text, callback_data=f"manual_join_{channel_id}")
                            ])
                            logger.warning(f"No direct link available for {channel_id}")
                            channel_counter += 1
                    except Exception as e2:
                        logger.error(f"Error getting chat invite link for {channel_id}: {e2}")
                        button_text = f"[{channel_counter}] {chat.title} (Manual Join Required)"
                        buttons.append([
                            InlineKeyboardButton(button_text, callback_data=f"manual_join_{channel_id}")
                        ])
                        channel_counter += 1
                        
        except Exception as e:
            logger.error(f"Error creating button for channel {channel_id}: {e}")
            # Add fallback button even if chat info fails
            buttons.append([
                InlineKeyboardButton(f"[{channel_counter}] Join Channel (ID: {channel_id})", callback_data=f"manual_join_{channel_id}")
            ])
            channel_counter += 1
    
    # Add check again button with improved styling
    buttons.append([
        InlineKeyboardButton("🔄 Check Again", callback_data="check_channels_again")
    ])
    
    return InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex(r"^check_channels_again$"))
async def check_channels_again(client: Client, query: CallbackQuery):
    """Check channels again after user joins"""
    try:
        user_id = query.from_user.id
        
        # Answer callback query first to show loading
        await query.answer("🔄 Checking channel memberships...")
        
        # Add a small delay to ensure membership status is updated
        import asyncio
        await asyncio.sleep(1)
        
        # Check if user is now subscribed to all channels
        is_subscribed, missing_channels = await check_user_channels(client, user_id)
        
        if is_subscribed:
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
            # Show improved error message with channel details
            join_buttons = await create_join_buttons(client, missing_channels)
            
            # Get channel names for better UI
            channel_names = []
            for i, channel_id in enumerate(missing_channels, 1):
                try:
                    chat = await client.get_chat(channel_id)
                    channel_names.append(f"{i}. {chat.title}")
                except:
                    channel_names.append(f"{i}. Channel {channel_id}")
            
            channels_text = "\n".join(channel_names)
            
            await query.message.edit_text(
                "❌ **Access Denied**\n\n"
                "You must join **all required channels** below to use this bot:\n\n"
                "📋 **Missing Channels:**\n"
                f"{channels_text}\n\n"
                "Please join the channels using the numbered buttons below and click 'Check Again':",
                reply_markup=join_buttons,
                parse_mode="markdown"
            )
            
    except Exception as e:
        logger.error(f"Error checking channels again: {e}")
        await query.answer("❌ An error occurred. Please try again.", show_alert=True)

@Client.on_callback_query(filters.regex(r"^manual_join_"))
async def manual_join_info(client: Client, query: CallbackQuery):
    """Show manual join instructions"""
    try:
        channel_id = int(query.data.split("_")[2])
        
        # Try to get channel info
        try:
            chat = await client.get_chat(channel_id)
            channel_name = chat.title
            
            # Check if channel has username for direct link
            if hasattr(chat, 'username') and chat.username:
                instructions = (
                    f"**Manual Join Required**\n\n"
                    f"📢 **Channel:** {channel_name}\n"
                    f"🔗 **Link:** @{chat.username}\n\n"
                    f"Please visit https://t.me/{chat.username} to join manually, "
                    f"then click 'Check Again' button."
                )
            else:
                instructions = (
                    f"**Manual Join Required**\n\n"
                    f"📢 **Channel:** {channel_name}\n\n"
                    f"This channel requires manual joining. Please contact the "
                    f"admin for the channel link, then click 'Check Again' button."
                )
        except:
            instructions = (
                f"**Manual Join Required**\n\n"
                f"📢 **Channel ID:** {channel_id}\n\n"
                f"Please contact the admin for the channel link, "
                f"then click 'Check Again' button."
            )
        
        await query.answer(instructions, show_alert=True)
        
    except Exception as e:
        logger.error(f"Error in manual join info: {e}")
        await query.answer("❌ Please join the channel manually and click 'Check Again'.", show_alert=True)