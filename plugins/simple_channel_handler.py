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

async def handle_channel_check(client: Client, user_id: int, context: str = "general"):
    """
    Centralized function to check channels and return appropriate response
    Returns: (is_subscribed: bool, response_data: dict or None)
    """
    is_subscribed, missing_channels = await check_user_channels(client, user_id)
    
    if is_subscribed:
        logger.info(f"✅ User {user_id} has access - {context}")
        return True, None
    else:
        logger.info(f"❌ User {user_id} needs to join channels - {context}")
        join_buttons = await create_join_buttons(client, missing_channels)
        return False, {
            'buttons': join_buttons,
            'missing_channels': missing_channels,
            'context': context
        }

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
    """Create attractive numbered buttons for joining missing channels"""
    buttons = []
    
    # Channel emojis for better UI
    channel_emojis = ["🎬", "🍿", "📺", "🎭"]
    
    for idx, channel_id in enumerate(missing_channels):
        try:
            chat = await client.get_chat(channel_id)
            emoji = channel_emojis[idx] if idx < len(channel_emojis) else "📢"
            
            # Try to create invite link first
            try:
                invite_link = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                button_text = f"{emoji} [{idx + 1}] {chat.title}"
                buttons.append([
                    InlineKeyboardButton(button_text, url=invite_link.invite_link)
                ])
                logger.info(f"✅ Created invite link for {channel_id}: {invite_link.invite_link}")
            except Exception as e:
                logger.error(f"❌ Could not create invite link for {channel_id}: {e}")
                # Fallback - try channel username
                if hasattr(chat, 'username') and chat.username:
                    button_text = f"{emoji} [{idx + 1}] {chat.title}"
                    buttons.append([
                        InlineKeyboardButton(button_text, url=f"https://t.me/{chat.username}")
                    ])
                    logger.info(f"✅ Using username link for {channel_id}: @{chat.username}")
                else:
                    # Try export chat invite link method
                    try:
                        invite_link = await client.export_chat_invite_link(channel_id)
                        button_text = f"{emoji} [{idx + 1}] {chat.title}"
                        buttons.append([
                            InlineKeyboardButton(button_text, url=invite_link)
                        ])
                        logger.info(f"✅ Using exported invite link for {channel_id}")
                    except Exception as e2:
                        logger.error(f"❌ Failed to export invite link for {channel_id}: {e2}")
                        # Last resort - manual join button
                        button_text = f"{emoji} [{idx + 1}] {chat.title} (Contact Admin)"
                        buttons.append([
                            InlineKeyboardButton(button_text, callback_data=f"manual_join_{channel_id}")
                        ])
                        
        except Exception as e:
            logger.error(f"❌ Error getting chat info for {channel_id}: {e}")
            # Fallback button even if chat info fails
            emoji = channel_emojis[idx] if idx < len(channel_emojis) else "📢"
            buttons.append([
                InlineKeyboardButton(f"{emoji} [{idx + 1}] Join Channel", callback_data=f"manual_join_{channel_id}")
            ])
    
    # Add some spacing and check again button with attractive styling
    buttons.append([])  # Empty row for spacing
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
        await query.answer("🔄 Checking your channel memberships...", show_alert=False)
        
        # Add a small delay to ensure membership status is updated
        import asyncio
        await asyncio.sleep(2)  # Increased delay for better reliability
        
        # Check if user is now subscribed to all channels
        logger.info(f"🔄 Rechecking channels for user {user_id}")
        is_subscribed, missing_channels = await check_user_channels(client, user_id)
        
        # Log the check result
        if is_subscribed:
            logger.info(f"✅ User {user_id} now has access to all channels")
        else:
            logger.info(f"❌ User {user_id} still missing channels: {missing_channels}")
        
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
                "🎉 **Welcome Aboard!**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"✅ **Successfully joined {temp.B_NAME}!**\n\n"
                "🎊 **Congratulations!** You now have full access to:\n"
                "• 🎬 Latest movies & TV shows\n"
                "• 🎭 Multiple genres & languages\n"
                "• 🍿 High-quality downloads\n"
                "• 📱 Subtitle support\n\n"
                "🚀 **Ready to explore? Choose an option:**",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode="markdown"
            )
        else:
            # Show creative channel join form
            join_buttons = await create_join_buttons(client, missing_channels)
            
            # Get channel names for better UI
            channel_info = []
            for i, channel_id in enumerate(missing_channels, 1):
                try:
                    chat = await client.get_chat(channel_id)
                    member_count = ""
                    try:
                        member_count = f" • {await client.get_chat_members_count(channel_id)} members"
                    except:
                        pass
                    channel_info.append(f"🔹 **{chat.title}**{member_count}")
                except:
                    channel_info.append(f"🔹 **Channel {channel_id}**")
            
            channels_text = "\n".join(channel_info)
            
            await query.message.edit_text(
                "🚫 **Channel Membership Required**\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                "🎭 **Welcome to our Movie Bot!**\n\n"
                "To access our **premium content**, you need to join our official channels:\n\n"
                f"{channels_text}\n\n"
                "🎯 **Quick Steps:**\n"
                "1️⃣ Click the numbered buttons below\n"
                "2️⃣ Join each channel\n" 
                "3️⃣ Come back and click '🔄 Check Again'\n\n"
                "🎬 **What you'll get:**\n"
                "• Latest movies & shows\n"
                "• High-quality downloads\n"
                "• Multiple subtitle languages\n"
                "• Fast streaming links\n\n"
                "👇 **Join Now:**",
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