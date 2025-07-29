"""
Admin command to test channel access and setup
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message
from language_config import get_required_channels
from info import ADMINS

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("testchannels") & filters.user(ADMINS))
async def test_channels(client: Client, message: Message):
    """Test if bot can access required channels"""
    try:
        required_channels = get_required_channels()
        result_text = "🔍 **Channel Access Test**\n━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        for i, channel_id in enumerate(required_channels, 1):
            result_text += f"**Channel {i}:** `{channel_id}`\n"
            
            # Test bot access to channel
            try:
                chat = await client.get_chat(int(channel_id))
                result_text += f"✅ **Access:** OK\n"
                result_text += f"📢 **Title:** {chat.title}\n"
                result_text += f"👤 **Type:** {chat.type}\n"
                
                # Test if bot can get member count
                try:
                    member_count = await client.get_chat_members_count(int(channel_id))
                    result_text += f"👥 **Members:** {member_count:,}\n"
                except:
                    result_text += f"👥 **Members:** Unknown\n"
                
                # Test if bot has admin rights
                try:
                    bot_member = await client.get_chat_member(int(channel_id), "me")
                    result_text += f"🤖 **Bot Status:** {bot_member.status}\n"
                except:
                    result_text += f"🤖 **Bot Status:** Unknown\n"
                
                # Test invite link creation
                try:
                    invite = await client.create_chat_invite_link(int(channel_id), creates_join_request=False)
                    result_text += f"🔗 **Invite Link:** ✅ Can create\n"
                except Exception as e:
                    result_text += f"🔗 **Invite Link:** ❌ Cannot create ({str(e)[:50]}...)\n"
                
            except Exception as e:
                result_text += f"❌ **Access:** FAILED\n"
                result_text += f"🚫 **Error:** {str(e)}\n"
                result_text += f"💡 **Fix:** Add bot to channel with admin rights\n"
            
            result_text += "\n" + "─" * 30 + "\n\n"
        
        # Test user membership for the admin
        result_text += f"**Testing Admin Membership:**\n"
        user_id = message.from_user.id
        
        for i, channel_id in enumerate(required_channels, 1):
            try:
                member = await client.get_chat_member(int(channel_id), user_id)
                if member.status in ["creator", "administrator", "member"]:
                    result_text += f"✅ Channel {i}: Member ({member.status})\n"
                else:
                    result_text += f"❌ Channel {i}: Not member ({member.status})\n"
            except Exception as e:
                result_text += f"❌ Channel {i}: Error checking membership\n"
        
        await message.reply(result_text, parse_mode="markdown")
        
    except Exception as e:
        logger.error(f"Error in channel test: {e}")
        await message.reply(f"❌ **Test Failed:** {str(e)}")

@Client.on_message(filters.command("fixchannels") & filters.user(ADMINS))
async def fix_channels_help(client: Client, message: Message):
    """Show instructions to fix channel setup"""
    help_text = """
🔧 **How to Fix Channel Setup**
━━━━━━━━━━━━━━━━━━━━━━━━

**Steps to fix "Peer id invalid" errors:**

1️⃣ **Add bot to channels:**
   • Go to each channel
   • Add your bot as administrator
   • Give these permissions:
     - Delete messages
     - Ban users
     - Invite users via link
     - Manage video chats

2️⃣ **Verify channel IDs:**
   • Forward any message from channel to @userinfobot
   • Check if the ID matches your config

3️⃣ **Channel settings:**
   • Make sure channels are public OR
   • Bot has proper admin rights in private channels

4️⃣ **Test again:**
   • Use `/testchannels` to verify

**Current channels in config:**
"""
    
    try:
        required_channels = get_required_channels()
        for i, channel_id in enumerate(required_channels, 1):
            help_text += f"• Channel {i}: `{channel_id}`\n"
    except Exception as e:
        help_text += f"❌ Error reading config: {e}\n"
    
    help_text += "\n💡 **Need help?** Contact the developer!"
    
    await message.reply(help_text, parse_mode="markdown")