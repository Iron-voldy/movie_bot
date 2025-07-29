"""
Channel handler for managing user channel subscriptions
Handles both common channel and language-specific channel joining
"""
import logging
import asyncio
from hydrogram import Client, filters, enums
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from hydrogram.errors import FloodWait, UserIsBlocked, PeerIdInvalid
from database.users_chats_db import db
from language_config import COMMON_CHANNEL, get_language_channels, get_language_channel, get_all_languages, get_language_display_name, LANGUAGE_CHANNELS
from utils import is_subscribed, temp
from info import ADMINS

logger = logging.getLogger(__name__)

async def check_user_subscriptions(client: Client, user_id: int, selected_language: str = None) -> tuple:
    """
    Check if user is subscribed to required channels
    Returns (is_subscribed, missing_channels, language_needed)
    """
    from language_config import get_required_channels
    
    missing_channels = []
    required_channels = get_required_channels()
    
    logger.info(f"Checking channels for user {user_id}: {required_channels}")
    
    # Check all required channels
    for channel_id in required_channels:
        try:
            # First check if bot can access the channel
            try:
                await client.get_chat(int(channel_id))
                logger.info(f"✅ Bot can access channel {channel_id}")
            except Exception as e:
                logger.error(f"❌ Bot cannot access channel {channel_id}: {e}")
                # If bot cannot access channel, add it to missing list
                missing_channels.append(int(channel_id))
                continue
            
            # Check user subscription
            subscribed = await is_subscribed(client, user_id, int(channel_id))
            logger.info(f"User {user_id} channel {channel_id} subscription: {subscribed}")
            
            if not subscribed:
                missing_channels.append(int(channel_id))
                
        except Exception as e:
            logger.error(f"Error checking channel {channel_id}: {e}")
            missing_channels.append(int(channel_id))
    
    logger.info(f"Final result for user {user_id}: subscribed={len(missing_channels) == 0}, missing={missing_channels}")
    return len(missing_channels) == 0, missing_channels, selected_language is None

async def create_subscription_buttons(client: Client, user_id: int, selected_language: str = None, callback_data: str = None) -> InlineKeyboardMarkup:
    """Create buttons for channel subscription with auto-join capability"""
    from language_config import get_required_channels, get_channel_info
    
    buttons = []
    required_channels = get_required_channels()
    
    # Check which channels user needs to join
    for channel_id in required_channels:
        try:
            # Check if user is subscribed
            if await is_subscribed(client, user_id, int(channel_id)):
                continue  # User already subscribed, skip this channel
            
            # Try to get channel info
            try:
                chat = await client.get_chat(int(channel_id))
                logger.info(f"✅ Got chat info for {channel_id}: {chat.title}")
                
                # Try to create invite link
                try:
                    invite = await client.create_chat_invite_link(int(channel_id), creates_join_request=False)
                    logger.info(f"✅ Created invite link for {channel_id}")
                    
                    button_text = f"✇ Join {chat.title} ✇"
                    buttons.append([
                        InlineKeyboardButton(button_text, url=invite.invite_link)
                    ])
                    logger.info(f"✅ Created join button for {channel_id} with URL")
                    
                except Exception as invite_error:
                    logger.error(f"❌ Cannot create invite for {channel_id}: {invite_error}")
                    # Fallback to callback button for auto-join attempt
                    button_text = f"✇ Join {chat.title} ✇"
                    buttons.append([
                        InlineKeyboardButton(button_text, callback_data=f"auto_join_{channel_id}")
                    ])
                    
            except Exception as chat_error:
                logger.error(f"❌ Bot cannot access channel {channel_id}: {chat_error}")
                # Create fallback button
                channel_info = get_channel_info(channel_id)
                channel_name = channel_info['name'] if channel_info else f"Channel {channel_id}"
                
                button_text = f"✇ Join {channel_name} ✇"
                buttons.append([
                    InlineKeyboardButton(button_text, callback_data=f"fallback_join_{channel_id}")
                ])
                logger.warning(f"⚠️ Created fallback button for inaccessible channel {channel_id}")
                
        except Exception as e:
            logger.error(f"Error processing channel {channel_id}: {e}")
    
    # Add try again button
    if callback_data:
        buttons.append([
            InlineKeyboardButton("🔄 Try Again", callback_data=callback_data)
        ])
    elif selected_language:
        buttons.append([
            InlineKeyboardButton("🔄 Try Again", callback_data=f"check_subscription_{selected_language}")
        ])
    
    return InlineKeyboardMarkup(buttons)

async def show_language_selection(client: Client, user_id: int, callback_data: str = None) -> InlineKeyboardMarkup:
    """Show language selection buttons"""
    buttons = []
    languages = get_all_languages()
    
    # Create buttons in rows of 2
    for i in range(0, len(languages), 2):
        row = []
        for j in range(2):
            if i + j < len(languages):
                lang = languages[i + j]
                display_name = get_language_display_name(lang)
                row.append(InlineKeyboardButton(
                    display_name,
                    callback_data=f"select_language_{lang}"
                ))
        buttons.append(row)
    
    return InlineKeyboardMarkup(buttons)

@Client.on_callback_query(filters.regex(r"^select_language_"))
async def handle_language_selection(client: Client, query: CallbackQuery):
    """Handle language selection callback"""
    try:
        from database.users_chats_db import db
        
        language = query.data.split("_", 2)[2]
        user_id = query.from_user.id
        
        logger.info(f"Language selection: {language} by user {user_id}")
        
        # Save user's language preference
        await db.add_user_language(user_id, language)
        
        # Answer the callback query first
        await query.answer(f"✅ {get_language_display_name(language)} selected!")
        
        # Check if user is subscribed to required channels
        is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, language)
        
        if is_subscribed:
            await query.message.edit_text(
                f"✅ **Language Selected**: {get_language_display_name(language)}\n\n"
                "You are subscribed to all required channels. You can now use the bot!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎬 Search Movies", switch_inline_query_current_chat="")
                ]])
            )
        else:
            # Show subscription buttons
            subscription_buttons = await create_subscription_buttons(
                client, user_id, language, f"check_subscription_{language}"
            )
            
            await query.message.edit_text(
                f"🎯 **Language Selected**: {get_language_display_name(language)}\n\n"
                "📋 **Required Channels:**\n"
                "1. Common Updates Channel (for all users)\n"
                f"2. {get_language_display_name(language)} Channel (for your language)\n\n"
                "Please join both channels to continue:",
                reply_markup=subscription_buttons
            )
    except Exception as e:
        logger.error(f"Error handling language selection: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^check_subscription_"))
async def handle_subscription_check(client: Client, query: CallbackQuery):
    """Handle subscription check callback"""
    try:
        language = query.data.split("_", 2)[2]
        user_id = query.from_user.id
        
        # Show loading message
        await query.answer("🔄 Checking your channel subscriptions...")
        
        # Add small delay to allow Telegram to sync
        await asyncio.sleep(2)
        
        # Check if user is subscribed to required channels
        is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, language)
        
        if is_subscribed:
            await query.message.edit_text(
                f"✅ **Language**: {get_language_display_name(language)}\n\n"
                "🎉 **All set!** You are now subscribed to all required channels.\n"
                "You can now use the bot to search for movies and subtitles!",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🎬 Search Movies", switch_inline_query_current_chat="")
                ]])
            )
        else:
            # Show subscription buttons again with missing channels
            subscription_buttons = await create_subscription_buttons(
                client, user_id, language, f"check_subscription_{language}"
            )
            
            from language_config import get_channel_info
            missing_channel_names = []
            for channel_id in missing_channels:
                try:
                    chat = await client.get_chat(channel_id)
                    missing_channel_names.append(chat.title)
                except:
                    channel_info = get_channel_info(str(channel_id))
                    channel_name = channel_info['name'] if channel_info else f"Channel {channel_id}"
                    missing_channel_names.append(channel_name)
            
            await query.message.edit_text(
                f"🎯 **Language**: {get_language_display_name(language)}\n\n"
                "❌ **Still need to join these channels:**\n" +
                "\n".join([f"• {name}" for name in missing_channel_names]) +
                "\n\nPlease join the channels below:",
                reply_markup=subscription_buttons
            )
    except Exception as e:
        logger.error(f"Error checking subscription: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^fallback_join_"))
async def handle_fallback_join(client: Client, query: CallbackQuery):
    """Handle fallback join for inaccessible channels"""
    try:
        channel_id = query.data.split("_", 2)[2]
        user_id = query.from_user.id
        
        from language_config import get_channel_info
        channel_info = get_channel_info(channel_id)
        channel_name = channel_info['name'] if channel_info else f"Channel {channel_id}"
        
        await query.answer(
            f"❌ Cannot access {channel_name}. Please contact admin to add the bot to this channel.",
            show_alert=True
        )
        
    except Exception as e:
        logger.error(f"Error in fallback join handler: {e}")
        await query.answer("❌ An error occurred. Please contact admin.")

@Client.on_callback_query(filters.regex(r"^auto_join_-?\d+$"))
async def handle_generic_auto_join(client: Client, query: CallbackQuery):
    """Handle generic auto-join for channels"""
    try:
        channel_id = int(query.data.split("_", 2)[2])
        user_id = query.from_user.id
        
        # Try to add user to channel
        try:
            await client.add_chat_members(channel_id, user_id)
            await query.answer("✅ Successfully joined the channel!")
            
            # Re-check subscriptions
            from database.users_chats_db import db
            user_language = await db.get_user_language(user_id) or 'english'
            is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, user_language)
            
            if is_subscribed:
                await query.message.edit_text(
                    f"🎉 **All set!** You are now subscribed to all required channels.\n"
                    f"✅ **Language**: {get_language_display_name(user_language)}\n\n"
                    "You can now use the bot to search for movies and subtitles!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎬 Search Movies", switch_inline_query_current_chat="")
                    ]])
                )
            else:
                # Still need to join other channels
                subscription_buttons = await create_subscription_buttons(
                    client, user_id, user_language, f"check_subscription_{user_language}"
                )
                await query.message.edit_text(
                    f"✅ **Channel joined!**\n\n"
                    f"🎯 **Language**: {get_language_display_name(user_language)}\n\n"
                    "📋 **Still need to join remaining channels**\n\n"
                    "Please join the remaining channels to continue:",
                    reply_markup=subscription_buttons
                )
                
        except Exception as e:
            logger.error(f"Error adding user to channel {channel_id}: {e}")
            await query.answer("❌ Unable to join channel automatically. Please use the invite link or contact admin.", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in generic auto-join handler: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^show_language_selection$"))
async def handle_show_language_selection(client: Client, query: CallbackQuery):
    """Handle show language selection callback"""
    try:
        language_buttons = await show_language_selection(client, query.from_user.id)
        await query.message.edit_text(
            "🌐 **Select Your Language**\n\n"
            "Choose your preferred language to get access to language-specific content:",
            reply_markup=language_buttons
        )
    except Exception as e:
        logger.error(f"Error showing language selection: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^auto_join_common_"))
async def handle_auto_join_common(client: Client, query: CallbackQuery):
    """Handle auto-join to common channel"""
    try:
        from database.users_chats_db import db
        
        channel_id = int(query.data.split("_")[3])
        user_id = query.from_user.id
        
        # Try to add user to channel
        try:
            await client.add_chat_members(channel_id, user_id)
            await query.answer("✅ Successfully joined the common channel!")
            
            # Check if user still needs to join other channels
            user_language = await db.get_user_language(user_id)
            if user_language:
                is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, user_language)
                
                if is_subscribed:
                    await query.message.edit_text(
                        f"🎉 **All set!** You are now subscribed to all required channels.\n"
                        f"✅ **Language**: {get_language_display_name(user_language)}\n\n"
                        "You can now use the bot to search for movies and subtitles!",
                        reply_markup=InlineKeyboardMarkup([[
                            InlineKeyboardButton("🎬 Search Movies", switch_inline_query_current_chat="")
                        ]])
                    )
                else:
                    # Still need to join language channel
                    subscription_buttons = await create_subscription_buttons(
                        client, user_id, user_language, f"check_subscription_{user_language}"
                    )
                    await query.message.edit_text(
                        f"✅ **Common channel joined!**\n\n"
                        f"🎯 **Language**: {get_language_display_name(user_language)}\n\n"
                        f"📋 **Still need to join**: {get_language_display_name(user_language)} Channel\n\n"
                        "Please join the language-specific channel to continue:",
                        reply_markup=subscription_buttons
                    )
            else:
                await query.message.edit_text(
                    "✅ **Common channel joined!**\n\n"
                    "Please select your language to continue:",
                    reply_markup=await show_language_selection(client, user_id)
                )
                
        except Exception as e:
            logger.error(f"Error adding user to common channel: {e}")
            # Fallback to invite link
            try:
                chat = await client.get_chat(channel_id)
                invite = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                await query.answer(f"Click the link to join {chat.title}", show_alert=True)
                await query.message.edit_text(
                    f"🔗 **Please join manually:**\n\n"
                    f"Click the button below to join {chat.title}:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(f"✇ Join {chat.title} ✇", url=invite.invite_link)
                    ], [
                        InlineKeyboardButton("🔄 Try Again", callback_data=f"check_subscription_{await db.get_user_language(user_id) or 'english'}")
                    ]])
                )
            except Exception as e2:
                logger.error(f"Error creating fallback invite link: {e2}")
                await query.answer("❌ Unable to join channel. Please contact admin.", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in auto-join common handler: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^auto_join_language_"))
async def handle_auto_join_language(client: Client, query: CallbackQuery):
    """Handle auto-join to language-specific channel"""
    try:
        parts = query.data.split("_")
        channel_id = int(parts[3])
        language = parts[4]
        user_id = query.from_user.id
        
        # Try to add user to channel
        try:
            await client.add_chat_members(channel_id, user_id)
            await query.answer(f"✅ Successfully joined the {get_language_display_name(language)} channel!")
            
            # Check if user is now subscribed to all required channels
            is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, language)
            
            if is_subscribed:
                await query.message.edit_text(
                    f"🎉 **All set!** You are now subscribed to all required channels.\n"
                    f"✅ **Language**: {get_language_display_name(language)}\n\n"
                    "You can now use the bot to search for movies and subtitles!",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("🎬 Search Movies", switch_inline_query_current_chat="")
                    ]])
                )
            else:
                # Still need to join common channel
                subscription_buttons = await create_subscription_buttons(
                    client, user_id, language, f"check_subscription_{language}"
                )
                await query.message.edit_text(
                    f"✅ **{get_language_display_name(language)} channel joined!**\n\n"
                    f"📋 **Still need to join**: Common Channel\n\n"
                    "Please join the common channel to continue:",
                    reply_markup=subscription_buttons
                )
                
        except Exception as e:
            logger.error(f"Error adding user to language channel: {e}")
            # Fallback to invite link
            try:
                chat = await client.get_chat(channel_id)
                invite = await client.create_chat_invite_link(channel_id, creates_join_request=False)
                await query.answer(f"Click the link to join {chat.title}", show_alert=True)
                await query.message.edit_text(
                    f"🔗 **Please join manually:**\n\n"
                    f"Click the button below to join {chat.title}:",
                    reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton(f"✇ Join {chat.title} ✇", url=invite.invite_link)
                    ], [
                        InlineKeyboardButton("🔄 Try Again", callback_data=f"check_subscription_{language}")
                    ]])
                )
            except Exception as e2:
                logger.error(f"Error creating fallback invite link: {e2}")
                await query.answer("❌ Unable to join channel. Please contact admin.", show_alert=True)
                
    except Exception as e:
        logger.error(f"Error in auto-join language handler: {e}")
        await query.answer("❌ An error occurred. Please try again.")

@Client.on_callback_query(filters.regex(r"^check_file_access_"))
async def handle_file_access_check(client: Client, query: CallbackQuery):
    """Handle file access check after channel subscription"""
    try:
        from database.users_chats_db import db
        
        file_id = query.data.split("_", 3)[3]
        user_id = query.from_user.id
        
        # Get user's language preference
        user_language = await db.get_user_language(user_id)
        
        if not user_language:
            await query.answer("❌ Please select your language first!")
            return
        
        # Check if user is subscribed to required channels
        is_subscribed, missing_channels, _ = await check_user_subscriptions(client, user_id, user_language)
        
        if is_subscribed:
            await query.answer("✅ Great! You can now access the file!")
            
            # Create a new callback query object to process the file
            new_query = type('CallbackQuery', (), {
                'data': f"files#{file_id}",
                'from_user': query.from_user,
                'message': query.message,
                'answer': query.answer
            })()
            
            # Directly handle the file access without circular import
            await handle_file_button_after_subscription(client, new_query, file_id)
            
        else:
            await query.answer("❌ Please join all required channels first!")
    except Exception as e:
        logger.error(f"Error checking file access: {e}")
        await query.answer("❌ An error occurred. Please try again.")

async def handle_file_button_after_subscription(client: Client, query, file_id: str):
    """Handle file button click after subscription verification"""
    try:
        from database.ia_filterdb import get_file_details
        # from real_subtitle_handler import real_subtitle_handler as subtitle_handler  # Not needed here
        from language_config import get_language_display_name
        from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        # Get file details
        file_details = await get_file_details(file_id)
        if file_details:
            # Show subtitle language selection
            from language_config import get_all_languages, get_language_display_name, get_language_flag
            subtitle_languages = get_all_languages()  # Gets all languages including Sinhala
            btn = []
            
            # Add subtitle language options - show all languages in rows of 2 with flags
            for i in range(0, len(subtitle_languages), 2):
                row = []
                for j in range(2):
                    if i + j < len(subtitle_languages):
                        lang = subtitle_languages[i + j]
                        display_name = get_language_display_name(lang)
                        flag = get_language_flag(lang)
                        row.append(InlineKeyboardButton(f"{flag} {display_name}", callback_data=f"subtitle#{file_id}#{lang}"))
                if row:  # Only add row if it has buttons
                    btn.append(row)
            
            # Add "No Subtitles" option
            btn.append([InlineKeyboardButton("🚫 No Subtitles Needed", callback_data=f"no_sub#{file_id}")])
            
            await query.message.edit_text(
                f"🎬 **{file_details['file_name']}**\n\n"
                "🗣 **Select Subtitle Language:**\n"
                "Choose your preferred subtitle language or select 'No Subtitles' to proceed without subtitles.",
                reply_markup=InlineKeyboardMarkup(btn)
            )
        else:
            from utils import temp
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={file_id}")
    except Exception as e:
        logger.error(f"Error handling file after subscription: {e}")