"""
File Refresh System - Help fix invalid file IDs
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.ia_filterdb import primary_col, secondary_col

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("refresh_files") & filters.user(ADMINS))
async def refresh_files_command(client: Client, message: Message):
    """Help admin refresh old/invalid file IDs"""
    try:
        help_text = """🔄 **File Refresh System**

**Problem:** File IDs become invalid over time, causing "MEDIA_EMPTY" errors.

**Solutions:**

**1. Add Fresh Files:**
   • Forward the same movies from channels again
   • Bot will update database with new file IDs
   • Use different file names to avoid duplicates

**2. Check Invalid Files:**
   • Use `/check_invalid_files` to find problematic files
   • Use `/test_file_id <file_id>` to test specific file

**3. Clean Database:**
   • Use `/clean_invalid_files` to remove broken entries
   • Use `/database_stats` to see database health

**💡 Quick Fix:**
Forward "Despicable Me 4" movie file again to update its file ID.

**🔧 Available Commands:**
• `/check_invalid_files` - Find files with invalid IDs
• `/test_file_id <id>` - Test if a file ID works
• `/database_stats` - Show database statistics
• `/clean_invalid_files` - Remove broken entries"""

        await message.reply(help_text)
        
    except Exception as e:
        logger.error(f"Error in refresh files command: {e}")
        await message.reply("❌ Error showing refresh guide")

@Client.on_message(filters.command("check_invalid_files") & filters.user(ADMINS))
async def check_invalid_files_command(client: Client, message: Message):
    """Check for files with potentially invalid IDs"""
    try:
        await message.reply("🔍 **Checking for invalid file IDs...**")
        
        # Get sample of recent files
        recent_files = list(primary_col.find().sort([("_id", -1)]).limit(10))
        
        if not recent_files:
            await message.reply("📭 **No files found in database**")
            return
        
        results = []
        valid_count = 0
        invalid_count = 0
        
        for i, file_info in enumerate(recent_files, 1):
            file_name = file_info.get('file_name', 'Unknown')
            file_id = file_info.get('_id')
            file_size = file_info.get('file_size', 0)
            
            # Test if file ID works
            try:
                # Try to get file info (doesn't download, just checks validity)
                await client.get_messages(chat_id="me", message_ids=1)  # Dummy call to test bot
                
                # Simple validation checks
                id_length = len(str(file_id))
                if id_length < 10:
                    status = "❌ Too short"
                    invalid_count += 1
                elif id_length > 200:
                    status = "❌ Too long"
                    invalid_count += 1
                else:
                    status = "✅ Format OK"
                    valid_count += 1
                    
            except Exception as e:
                status = f"❌ Error: {str(e)[:20]}..."
                invalid_count += 1
            
            results.append(f"**{i}.** {file_name[:30]}...\n"
                         f"   Size: {file_size:,} bytes\n"
                         f"   ID Length: {len(str(file_id))}\n"
                         f"   Status: {status}\n")
        
        report = f"""🔍 **File ID Check Results**

**📊 Summary:**
• ✅ Valid format: {valid_count}
• ❌ Invalid format: {invalid_count}
• 📁 Total checked: {len(recent_files)}

**📋 Recent Files:**
{chr(10).join(results)}

**💡 Note:** This is a basic format check. 
Files may still fail due to expired IDs even if format is correct.

**🔧 To fix invalid files:**
• Forward fresh copies of movies
• Use `/clean_invalid_files` to remove broken entries"""

        await message.reply(report)
        
    except Exception as e:
        logger.error(f"Error checking invalid files: {e}")
        await message.reply(f"❌ **Error checking files:** {e}")

@Client.on_message(filters.command("test_file_id") & filters.user(ADMINS))
async def test_file_id_command(client: Client, message: Message):
    """Test if a specific file ID works"""
    try:
        if len(message.command) < 2:
            await message.reply("""🧪 **Test File ID**

**Usage:** `/test_file_id <file_id>`

**Example:** `/test_file_id BQADBQADIREAAo3P8VUghYq4pZK_LRYE`

This will test if the file ID can be sent to users.""")
            return
        
        file_id = message.command[1]
        await message.reply(f"🧪 **Testing File ID:** `{file_id}`")
        
        try:
            # Try to send the file to admin
            test_message = await client.send_document(
                chat_id=message.from_user.id,
                document=file_id,
                caption="🧪 **Test File** - This is a file ID test"
            )
            
            await message.reply(f"✅ **File ID Works!**\n\n"
                              f"File ID `{file_id}` is valid and can be sent to users.\n"
                              f"Test message ID: {test_message.id}")
            
        except Exception as send_error:
            await message.reply(f"❌ **File ID Failed!**\n\n"
                              f"File ID `{file_id}` cannot be sent.\n"
                              f"Error: {send_error}\n\n"
                              f"**Solution:** Forward a fresh copy of this file to update the database.")
        
    except Exception as e:
        logger.error(f"Error testing file ID: {e}")
        await message.reply(f"❌ **Error testing file ID:** {e}")

@Client.on_message(filters.command("database_stats") & filters.user(ADMINS))
async def database_stats_command(client: Client, message: Message):
    """Show database statistics"""
    try:
        # Get database stats
        primary_count = primary_col.count_documents({})
        secondary_count = secondary_col.count_documents({})
        total_files = primary_count + secondary_count
        
        # Get recent files info
        recent_files = list(primary_col.find().sort([("_id", -1)]).limit(5))
        
        recent_info = []
        for file_info in recent_files:
            file_name = file_info.get('file_name', 'Unknown')[:30]
            file_size = file_info.get('file_size', 0)
            recent_info.append(f"• {file_name}... ({file_size:,} bytes)")
        
        stats_report = f"""📊 **Database Statistics**

**📁 File Count:**
• Primary Database: {primary_count:,} files
• Secondary Database: {secondary_count:,} files
• **Total Files: {total_files:,}**

**📋 Recent Files:**
{chr(10).join(recent_info) if recent_info else "No recent files"}

**💡 File ID Issues:**
If users report "MEDIA_EMPTY" errors:
1. Forward fresh copies of those movies
2. Use `/test_file_id` to test specific files
3. Use `/refresh_files` for more help

**🔧 Maintenance Commands:**
• `/check_invalid_files` - Find problematic files
• `/clean_invalid_files` - Remove broken entries
• `/refresh_files` - Get help with file refresh"""

        await message.reply(stats_report)
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        await message.reply(f"❌ **Error getting database stats:** {e}")

@Client.on_message(filters.command("clean_invalid_files") & filters.user(ADMINS))
async def clean_invalid_files_command(client: Client, message: Message):
    """Clean obviously invalid files from database"""
    try:
        await message.reply("🧹 **Cleaning Invalid Files...**")
        
        # Find files with obviously invalid IDs
        all_files = list(primary_col.find())
        
        to_remove = []
        for file_info in all_files:
            file_id = str(file_info.get('_id', ''))
            file_name = file_info.get('file_name', 'Unknown')
            
            # Check for obviously invalid IDs
            if (len(file_id) < 10 or 
                len(file_id) > 200 or 
                not file_id.strip() or
                file_id == 'None'):
                
                to_remove.append({
                    'id': file_info['_id'],
                    'name': file_name,
                    'reason': 'Invalid ID format'
                })
        
        if not to_remove:
            await message.reply("✅ **No Obviously Invalid Files Found**\n\n"
                              "All files have reasonable ID formats. "
                              "File delivery issues may be due to expired IDs, "
                              "which require fresh file uploads to fix.")
            return
        
        # Show what will be removed
        removal_list = []
        for item in to_remove[:10]:  # Limit display
            removal_list.append(f"• {item['name'][:40]}... ({item['reason']})")
        
        if len(to_remove) > 10:
            removal_list.append(f"... and {len(to_remove) - 10} more files")
        
        confirmation = f"""🧹 **Files to Remove:**

{chr(10).join(removal_list)}

**Total to remove:** {len(to_remove)} files

⚠️ **Warning:** This will permanently delete these entries from the database.

**To confirm removal, use:** `/confirm_clean_files`
**To cancel, just ignore this message.**"""

        await message.reply(confirmation)
        
        # Store removal list in a simple way (you'd want to use proper storage in production)
        global pending_removal
        pending_removal = to_remove
        
    except Exception as e:
        logger.error(f"Error cleaning invalid files: {e}")
        await message.reply(f"❌ **Error cleaning files:** {e}")

# Global variable for pending removals (simple approach)
pending_removal = []

@Client.on_message(filters.command("confirm_clean_files") & filters.user(ADMINS))
async def confirm_clean_files_command(client: Client, message: Message):
    """Confirm removal of invalid files"""
    try:
        global pending_removal
        
        if not pending_removal:
            await message.reply("❌ **No files pending removal**\n\nUse `/clean_invalid_files` first.")
            return
        
        await message.reply(f"🧹 **Removing {len(pending_removal)} invalid files...**")
        
        removed_count = 0
        for item in pending_removal:
            try:
                result = primary_col.delete_one({'_id': item['id']})
                if result.deleted_count > 0:
                    removed_count += 1
            except Exception as e:
                logger.error(f"Error removing file {item['id']}: {e}")
        
        # Clear pending removal list
        pending_removal = []
        
        await message.reply(f"✅ **Cleanup Complete!**\n\n"
                          f"Removed {removed_count} invalid files from database.\n\n"
                          f"🔄 **Next Steps:**\n"
                          f"• Forward fresh copies of important movies\n"
                          f"• Use `/database_stats` to check database health")
        
    except Exception as e:
        logger.error(f"Error confirming file cleanup: {e}")
        await message.reply(f"❌ **Error during cleanup:** {e}")