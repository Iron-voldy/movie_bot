"""
Emergency Fix Commands for Critical Issues
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.ia_filterdb import primary_col, secondary_col

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("emergency_fix") & filters.user(ADMINS))
async def emergency_fix_command(client: Client, message: Message):
    """Emergency fix for the current file sending issues"""
    try:
        status_msg = await message.reply("🚨 **EMERGENCY FIX - Analyzing Issues...**")
        
        # Check the specific problematic file
        expired_file_id = "BQADBQADIREAAo3P8VUghYq4pZK_LRYE"
        file_info = primary_col.find_one({'_id': expired_file_id})
        
        if not file_info:
            file_info = secondary_col.find_one({'_id': expired_file_id})
        
        if file_info:
            file_name = file_info.get('file_name', 'Unknown')
            file_size = file_info.get('file_size', 0)
            
            # Test if the file ID works
            try:
                test_msg = await client.send_document(
                    chat_id=message.from_user.id,
                    document=expired_file_id,
                    caption="🧪 Testing expired file ID"
                )
                await test_msg.delete()
                file_status = "✅ Working (Unexpected!)"
            except Exception as e:
                if 'media_empty' in str(e).lower():
                    file_status = "❌ EXPIRED (MEDIA_EMPTY)"
                else:
                    file_status = f"⚠️ Error: {str(e)[:30]}..."
            
            emergency_report = f"""🚨 **EMERGENCY ANALYSIS COMPLETE**

🎬 **Problematic File:**
• **Name:** {file_name}
• **Size:** {file_size:,} bytes  
• **File ID:** `{expired_file_id}`
• **Status:** {file_status}

🔧 **IMMEDIATE SOLUTIONS:**

**Option 1: Quick Fix (Recommended)**
1. Go to your source channel
2. Find "Despicable Me 4 (2024)" movie file
3. Forward it to this bot again
4. Bot will auto-update the expired ID

**Option 2: Manual Database Fix**
1. Use `/test_file_id {expired_file_id}` to confirm it's broken
2. Delete the expired entry: `/delete_file {expired_file_id}`
3. Re-add the movie file

**Option 3: Bulk Fix**
Use `/fix_expired_files` to find and fix all expired files

📊 **Current Database Status:**"""
            
            # Get database stats
            primary_count = primary_col.count_documents({})
            secondary_count = secondary_col.count_documents({})
            total_files = primary_count + secondary_count
            
            emergency_report += f"""
• Primary DB: {primary_count:,} files
• Secondary DB: {secondary_count:,} files  
• **Total: {total_files:,} files**

⚡ **URGENT ACTION NEEDED:** Forward the movie file now to fix the issue!"""
            
            await status_msg.edit(emergency_report, reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🧪 Test This File ID", callback_data=f"test_file#{expired_file_id}")],
                [InlineKeyboardButton("📊 Full Database Check", callback_data="emergency_db_check")],
                [InlineKeyboardButton("🔄 Refresh All Stats", callback_data="refresh_emergency")]
            ]))
            
        else:
            await status_msg.edit(f"❌ **File not found in database:** `{expired_file_id}`\n\n"
                                f"This might mean:\n"
                                f"• File was already deleted\n"
                                f"• Database connection issue\n"
                                f"• File ID was never stored\n\n"
                                f"**Solution:** Add the movie file fresh to the database.")
        
    except Exception as e:
        logger.error(f"Error in emergency fix: {e}")
        await message.reply(f"❌ **Emergency fix error:** {e}")

@Client.on_message(filters.command("quick_test") & filters.user(ADMINS))
async def quick_test_command(client: Client, message: Message):
    """Quick test of the problematic file"""
    try:
        if len(message.command) < 2:
            # Test the known problematic file
            test_file_id = "BQADBQADIREAAo3P8VUghYq4pZK_LRYE"
        else:
            test_file_id = message.command[1]
        
        await message.reply(f"🧪 **Testing file ID:** `{test_file_id}`")
        
        try:
            # Try to send the file
            test_message = await client.send_document(
                chat_id=message.from_user.id,
                document=test_file_id,
                caption="🧪 **File ID Test** - This file works!"
            )
            
            await message.reply(f"✅ **SUCCESS!** File ID is working.\n\n"
                              f"File ID: `{test_file_id}`\n"
                              f"Message ID: {test_message.id}\n\n"
                              f"The issue might be resolved!")
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'media_empty' in error_msg:
                await message.reply(f"❌ **CONFIRMED: File ID is EXPIRED**\n\n"
                                  f"File ID: `{test_file_id}`\n"
                                  f"Error: {e}\n\n"
                                  f"**🔧 SOLUTION:**\n"
                                  f"Forward the movie file again from your source channel.\n"
                                  f"The bot will automatically update the expired ID.")
            else:
                await message.reply(f"⚠️ **File ID test failed**\n\n"
                                  f"File ID: `{test_file_id}`\n"
                                  f"Error: {e}\n\n"
                                  f"This might be a different issue.")
        
    except Exception as e:
        logger.error(f"Error in quick test: {e}")
        await message.reply(f"❌ **Quick test error:** {e}")

@Client.on_message(filters.command("force_refresh") & filters.user(ADMINS))
async def force_refresh_command(client: Client, message: Message):
    """Force refresh a specific movie by removing expired entry"""
    try:
        if len(message.command) < 2:
            await message.reply("""🔄 **Force Refresh Command**

**Usage:** `/force_refresh <movie_name>`
**Example:** `/force_refresh Despicable Me 4`

This will:
1. Find the movie in database
2. Remove expired entries
3. Prepare for fresh file addition

**For the current issue, use:**
`/force_refresh Despicable Me 4`""")
            return
        
        movie_name = " ".join(message.command[1:])
        await message.reply(f"🔄 **Force refreshing:** {movie_name}")
        
        # Find and remove expired entries
        search_pattern = {'file_name': {'$regex': movie_name, '$options': 'i'}}
        
        # Check primary database
        found_files = list(primary_col.find(search_pattern))
        removed_count = 0
        
        for file_info in found_files:
            file_id = file_info['_id']
            file_name = file_info['file_name']
            
            # Test if file ID is expired
            try:
                test_msg = await client.send_document(
                    chat_id=message.from_user.id,
                    document=file_id,
                    caption="Test"
                )
                await test_msg.delete()
                # File works, keep it
            except:
                # File is expired, remove it
                primary_col.delete_one({'_id': file_id})
                removed_count += 1
                logger.info(f"Removed expired file: {file_name}")
        
        # Check secondary database too
        secondary_files = list(secondary_col.find(search_pattern))
        for file_info in secondary_files:
            file_id = file_info['_id']
            file_name = file_info['file_name']
            
            try:
                test_msg = await client.send_document(
                    chat_id=message.from_user.id,
                    document=file_id,
                    caption="Test"
                )
                await test_msg.delete()
            except:
                secondary_col.delete_one({'_id': file_id})
                removed_count += 1
                logger.info(f"Removed expired file from secondary: {file_name}")
        
        if removed_count > 0:
            await message.reply(f"✅ **Force refresh complete!**\n\n"
                              f"🗑️ Removed {removed_count} expired entries for: {movie_name}\n\n"
                              f"🎬 **Next step:** Forward the movie file again to add fresh copy.")
        else:
            await message.reply(f"ℹ️ **No expired entries found for:** {movie_name}\n\n"
                              f"All existing entries appear to be working.\n\n"
                              f"If users still report issues, the problem might be elsewhere.")
        
    except Exception as e:
        logger.error(f"Error in force refresh: {e}")
        await message.reply(f"❌ **Force refresh error:** {e}")

@Client.on_callback_query(filters.regex(r"^test_file#"))
async def test_file_callback(client: Client, query):
    """Test file ID from callback"""
    try:
        if query.from_user.id not in ADMINS:
            await query.answer("❌ Admin only", show_alert=True)
            return
        
        file_id = query.data.split("#")[1]
        await query.message.edit(f"🧪 **Testing file ID...**\n\n`{file_id}`")
        
        try:
            test_msg = await client.send_document(
                chat_id=query.from_user.id,
                document=file_id,
                caption="🧪 File ID Test"
            )
            await test_msg.delete()
            
            await query.message.edit(f"✅ **File ID Works!**\n\n"
                                   f"File ID: `{file_id}`\n\n"
                                   f"The file ID is valid and can be sent to users.")
        except Exception as e:
            await query.message.edit(f"❌ **File ID Failed!**\n\n"
                                   f"File ID: `{file_id}`\n"
                                   f"Error: {e}\n\n"
                                   f"**Solution:** Forward fresh copy of this movie.")
        
    except Exception as e:
        logger.error(f"Error in test file callback: {e}")
        await query.answer("❌ Test failed", show_alert=True)

@Client.on_callback_query(filters.regex(r"^emergency_db_check$"))
async def emergency_db_check_callback(client: Client, query):
    """Emergency database check callback"""
    try:
        if query.from_user.id not in ADMINS:
            await query.answer("❌ Admin only", show_alert=True)
            return
        
        await query.message.edit("🔍 **Emergency Database Check...**")
        
        # Quick database health check
        primary_count = primary_col.count_documents({})
        secondary_count = secondary_col.count_documents({})
        
        # Check for the specific problematic file
        expired_file = primary_col.find_one({'_id': 'BQADBQADIREAAo3P8VUghYq4pZK_LRYE'})
        if not expired_file:
            expired_file = secondary_col.find_one({'_id': 'BQADBQADIREAAo3P8VUghYq4pZK_LRYE'})
        
        db_status = f"""🔍 **Emergency Database Status**

📊 **File Counts:**
• Primary: {primary_count:,} files
• Secondary: {secondary_count:,} files
• **Total: {primary_count + secondary_count:,} files**

🎬 **Despicable Me 4 Status:**
{'✅ Found in database' if expired_file else '❌ Not found in database'}

💡 **Immediate Actions:**
1. Forward movie file to refresh expired ID
2. Use `/quick_test` to verify fixes
3. Monitor with `/database_stats`

🚨 **If issues persist:**
Contact support with error logs"""
        
        await query.message.edit(db_status, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🧪 Quick Test", callback_data="quick_test_callback")],
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="emergency_db_check")]
        ]))
        
    except Exception as e:
        logger.error(f"Error in emergency db check: {e}")
        await query.answer("❌ Check failed", show_alert=True)