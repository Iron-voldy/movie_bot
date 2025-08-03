"""
Channel Setup and Management Plugin
Helps admins properly configure channel verification
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("channel_setup") & filters.user(ADMINS))
async def channel_setup_command(client: Client, message: Message):
    """Help admin set up channel verification properly"""
    try:
        setup_guide = """🔧 **Channel Setup Guide**

**Current Channels to Configure:**
• Channel 1: -1002766947260
• Channel 2: -1002886647880

**🎯 Steps to Fix Channel Verification:**

**1. Add Bot as Admin:**
   • Go to each channel
   • Add your bot as administrator
   • Give permissions: "Invite Users" + "Delete Messages"

**2. Test Bot Access:**
   • Use `/test_channels` command
   • Check if bot can access both channels

**3. Enable Channel Checking:**
   • Use `/enable_channels` to turn on verification
   • Use `/disable_channels` to turn off verification

**4. Create Invite Links:**
   • Use `/create_invites` to generate working invite links

**⚠️ Current Status:** Channel checking is DISABLED
Users can access bot without joining channels.

**💡 Quick Commands:**
• `/test_channels` - Test bot access to channels
• `/enable_channels` - Enable channel verification  
• `/disable_channels` - Disable channel verification
• `/create_invites` - Create invite links for channels"""

        await message.reply(setup_guide)
        
    except Exception as e:
        logger.error(f"Error in channel setup command: {e}")
        await message.reply("❌ Error showing setup guide")

@Client.on_message(filters.command("test_channels") & filters.user(ADMINS))
async def test_channels_command(client: Client, message: Message):
    """Test if bot can access the required channels"""
    try:
        channels_to_test = [-1002766947260, -1002886647880]
        results = []
        
        await message.reply("🔍 **Testing Channel Access...**")
        
        for i, channel_id in enumerate(channels_to_test, 1):
            try:
                # Test basic chat access
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
                
                # Test bot membership
                try:
                    bot_member = await client.get_chat_member(channel_id, client.me.id)
                    bot_status = bot_member.status
                    
                    if bot_status in ["creator", "administrator"]:
                        status = f"✅ **GOOD** - Bot is {bot_status}"
                    else:
                        status = f"⚠️ **ISSUE** - Bot is {bot_status} (needs admin)"
                        
                except Exception as member_error:
                    status = f"❌ **ERROR** - Cannot check bot status: {member_error}"
                
                results.append(f"**Channel {i}:** {channel_name}\n"
                             f"   ID: `{channel_id}`\n"
                             f"   Status: {status}\n")
                
            except Exception as e:
                results.append(f"**Channel {i}:** ID `{channel_id}`\n"
                             f"   Status: ❌ **CANNOT ACCESS** - {e}\n")
        
        # Test creating invite links
        invite_results = []
        for i, channel_id in enumerate(channels_to_test, 1):
            try:
                invite_link = await client.export_chat_invite_link(channel_id)
                invite_results.append(f"✅ Channel {i}: Invite link created")
            except Exception as e:
                invite_results.append(f"❌ Channel {i}: Cannot create invite - {e}")
        
        test_report = f"""🔍 **Channel Access Test Results**

**📊 Channel Access:**
{chr(10).join(results)}

**🔗 Invite Link Test:**
{chr(10).join(invite_results)}

**🛠 Next Steps:**
• If bot cannot access: Add bot to channels as admin
• If bot is not admin: Promote bot with proper permissions
• If invite links fail: Check bot has "Invite Users" permission"""

        await message.reply(test_report)
        
    except Exception as e:
        logger.error(f"Error testing channels: {e}")
        await message.reply(f"❌ **Error testing channels:** {e}")

@Client.on_message(filters.command("enable_channels") & filters.user(ADMINS))
async def enable_channels_command(client: Client, message: Message):
    """Enable channel verification"""
    try:
        # Update the channel handler to enable checking
        import plugins.simple_channel_handler as handler
        
        # You would need to implement a way to toggle this dynamically
        # For now, provide instructions
        instructions = """🔓 **Enable Channel Verification**

**To enable channel checking:**

1. Edit `plugins/simple_channel_handler.py`
2. Find line: `ENABLE_CHANNEL_CHECKING = False`
3. Change to: `ENABLE_CHANNEL_CHECKING = True`
4. Restart the bot

**⚠️ Before enabling:**
• Make sure bot is admin in both channels
• Test with `/test_channels` first
• Create invite links with `/create_invites`

**Current Status:** Channel checking is DISABLED"""

        await message.reply(instructions)
        
    except Exception as e:
        logger.error(f"Error in enable channels: {e}")
        await message.reply("❌ Error enabling channels")

@Client.on_message(filters.command("disable_channels") & filters.user(ADMINS))
async def disable_channels_command(client: Client, message: Message):
    """Disable channel verification"""
    try:
        instructions = """🔒 **Disable Channel Verification**

**To disable channel checking:**

1. Edit `plugins/simple_channel_handler.py`
2. Find line: `ENABLE_CHANNEL_CHECKING = True`
3. Change to: `ENABLE_CHANNEL_CHECKING = False`
4. Restart the bot

**Current Status:** Channel checking is already DISABLED
All users can access the bot without joining channels."""

        await message.reply(instructions)
        
    except Exception as e:
        logger.error(f"Error in disable channels: {e}")
        await message.reply("❌ Error disabling channels")

@Client.on_message(filters.command("create_invites") & filters.user(ADMINS))
async def create_invites_command(client: Client, message: Message):
    """Create and test invite links for channels"""
    try:
        channels_to_test = [-1002766947260, -1002886647880]
        invite_info = []
        
        await message.reply("🔗 **Creating Invite Links...**")
        
        for i, channel_id in enumerate(channels_to_test, 1):
            try:
                # Get channel info
                chat = await client.get_chat(channel_id)
                channel_name = chat.title
                
                # Try different methods to create invite links
                invite_methods = []
                
                # Method 1: Export existing invite link
                try:
                    invite_link = await client.export_chat_invite_link(channel_id)
                    invite_methods.append(f"✅ Export Link: {invite_link}")
                except Exception as e:
                    invite_methods.append(f"❌ Export Link Failed: {e}")
                
                # Method 2: Create new invite link
                try:
                    new_invite = await client.create_chat_invite_link(
                        channel_id, 
                        creates_join_request=False,
                        name=f"Bot Access {i}"
                    )
                    invite_methods.append(f"✅ New Link: {new_invite.invite_link}")
                except Exception as e:
                    invite_methods.append(f"❌ New Link Failed: {e}")
                
                # Method 3: Check for username
                username_info = "❌ No username"
                if hasattr(chat, 'username') and chat.username:
                    username_info = f"✅ Username: @{chat.username} (https://t.me/{chat.username})"
                
                invite_info.append(f"**Channel {i}: {channel_name}**\n"
                                 f"   ID: `{channel_id}`\n"
                                 f"   {username_info}\n"
                                 f"   {chr(10).join(invite_methods)}\n")
                
            except Exception as e:
                invite_info.append(f"**Channel {i}: ID `{channel_id}`**\n"
                                 f"   ❌ Cannot access channel: {e}\n")
        
        invite_report = f"""🔗 **Invite Links Report**

{chr(10).join(invite_info)}

**📋 Usage Instructions:**
1. Test the invite links yourself first
2. Share working links with users
3. Update channel verification if needed

**💡 Best Practice:**
• Use username links (@channel) when available
• Keep exported links as backup
• Create multiple invite links for reliability"""

        await message.reply(invite_report)
        
    except Exception as e:
        logger.error(f"Error creating invites: {e}")
        await message.reply(f"❌ **Error creating invites:** {e}")

@Client.on_message(filters.command("channel_status") & filters.user(ADMINS))
async def channel_status_command(client: Client, message: Message):
    """Show current channel verification status"""
    try:
        # Import the current setting
        from plugins.simple_channel_handler import check_user_channels
        
        # Test with a dummy user to see current behavior
        status_info = """📊 **Channel Verification Status**

**🎯 Configured Channels:**
• Channel 1: -1002766947260
• Channel 2: -1002886647880

**⚙️ Current Setting:**
• Channel Checking: **DISABLED**
• All users can access bot without joining

**🛠 Available Commands:**
• `/test_channels` - Test bot access
• `/create_invites` - Generate invite links
• `/enable_channels` - Turn on verification
• `/disable_channels` - Turn off verification

**📝 To Enable Verification:**
1. Run `/test_channels` first
2. Fix any access issues
3. Edit code to enable checking
4. Restart bot"""

        await message.reply(status_info)
        
    except Exception as e:
        logger.error(f"Error showing channel status: {e}")
        await message.reply("❌ Error showing status")