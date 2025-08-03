"""
Enhanced File Management System
Handles file validation, duplicate detection, and expired file ID management
"""
import logging
from hydrogram import Client, filters
from hydrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from info import ADMINS
from database.ia_filterdb import primary_col, secondary_col, find_duplicate_by_name_and_size
import asyncio

logger = logging.getLogger(__name__)

@Client.on_message(filters.command("fix_expired_files") & filters.user(ADMINS))
async def fix_expired_files_command(client: Client, message: Message):
    """Help admin identify and fix files with expired IDs"""
    try:
        status_msg = await message.reply("🔄 **Checking for expired file IDs...**\n\nThis may take a few minutes...")
        
        # Get sample of files to test
        test_files = list(primary_col.find().limit(20))  # Test first 20 files
        
        if not test_files:
            await status_msg.edit("📭 **No files found in database**")
            return
        
        expired_files = []
        valid_files = []
        test_count = 0
        
        for file_info in test_files:
            test_count += 1
            file_name = file_info.get('file_name', 'Unknown')
            file_id = file_info.get('_id')
            
            # Update progress every 5 files
            if test_count % 5 == 0:
                await status_msg.edit(f"🔄 **Testing file IDs... ({test_count}/{len(test_files)})**\n\n"
                                    f"⏳ Current: {file_name[:30]}...")
            
            try:
                # Try to send file to admin (this tests if ID is valid)
                test_message = await client.send_document(
                    chat_id=message.from_user.id,
                    document=file_id,
                    caption="🧪 File ID Test - Please ignore"
                )
                
                # If successful, delete the test message and mark as valid
                await test_message.delete()
                valid_files.append({
                    'name': file_name,
                    'id': file_id,
                    'size': file_info.get('file_size', 0)
                })
                
            except Exception as e:
                error_msg = str(e).lower()
                if 'media_empty' in error_msg or 'invalid' in error_msg:
                    expired_files.append({
                        'name': file_name,
                        'id': file_id,
                        'size': file_info.get('file_size', 0),
                        'error': str(e)[:50]
                    })
                
            # Small delay to avoid rate limiting
            await asyncio.sleep(0.5)
        
        # Prepare results
        expired_list = []
        for i, file_info in enumerate(expired_files[:10], 1):  # Show first 10
            expired_list.append(f"**{i}.** {file_info['name'][:40]}...\n"
                              f"    Size: {file_info['size']:,} bytes\n"
                              f"    Error: {file_info['error']}\n")
        
        if len(expired_files) > 10:
            expired_list.append(f"... and {len(expired_files) - 10} more expired files")
        
        results_text = f"""🔍 **File ID Check Complete**

📊 **Results:**
• ✅ Valid IDs: {len(valid_files)}
• ❌ Expired IDs: {len(expired_files)}
• 📁 Total tested: {test_count}

🚨 **Expired Files:**
{chr(10).join(expired_list) if expired_files else "None found! 🎉"}

💡 **To fix expired files:**
1. Forward fresh copies of the movies listed above
2. The bot will automatically update expired IDs
3. Use `/database_stats` to monitor progress

🔧 **Quick Actions:**"""
        
        buttons = []
        if expired_files:
            buttons.append([InlineKeyboardButton("📋 Get Full Expired List", callback_data="get_expired_list")])
        
        buttons.extend([
            [InlineKeyboardButton("📊 Database Stats", callback_data="admin_db_stats")],
            [InlineKeyboardButton("🔄 Test More Files", callback_data="test_more_files")]
        ])
        
        await status_msg.edit(results_text, reply_markup=InlineKeyboardMarkup(buttons))
        
        # Store results for later use
        global last_expired_check
        last_expired_check = {
            'expired': expired_files,
            'valid': valid_files,
            'timestamp': message.date
        }
        
    except Exception as e:
        logger.error(f"Error checking expired files: {e}")
        await message.reply(f"❌ **Error checking expired files:** {e}")

# Global variable to store last check results
last_expired_check = {}

@Client.on_message(filters.command("refresh_movie") & filters.user(ADMINS))
async def refresh_movie_command(client: Client, message: Message):
    """Help admin refresh a specific movie by name"""
    try:
        if len(message.command) < 2:
            await message.reply("""🔄 **Refresh Movie Command**

**Usage:** `/refresh_movie <movie_name>`

**Example:** `/refresh_movie Despicable Me 4`

This command will:
1. Search for the movie in database
2. Show current file ID status
3. Guide you on how to refresh it

**For bulk operations, use:** `/fix_expired_files`""")
            return
        
        movie_name = " ".join(message.command[1:])
        await message.reply(f"🔍 **Searching for:** {movie_name}")
        
        # Search for movie in database
        search_results = list(primary_col.find({
            'file_name': {'$regex': movie_name, '$options': 'i'}
        }).limit(5))
        
        if not search_results:
            # Try secondary database
            search_results = list(secondary_col.find({
                'file_name': {'$regex': movie_name, '$options': 'i'}
            }).limit(5))
        
        if not search_results:
            await message.reply(f"❌ **Movie not found:** {movie_name}\n\n"
                              f"💡 Make sure to use the exact movie name as stored in database.\n"
                              f"Use `/database_stats` to see available movies.")
            return
        
        # Show results and test file IDs
        results_text = f"🎬 **Found {len(search_results)} matching movies:**\n\n"
        
        for i, movie in enumerate(search_results, 1):
            file_name = movie.get('file_name', 'Unknown')
            file_id = movie.get('_id')
            file_size = movie.get('file_size', 0)
            
            # Test file ID
            try:
                test_message = await client.send_document(
                    chat_id=message.from_user.id,
                    document=file_id,
                    caption=f"🧪 Testing: {file_name}"
                )
                await test_message.delete()
                status = "✅ Working"
            except Exception as e:
                if 'media_empty' in str(e).lower():
                    status = "❌ Expired"
                else:
                    status = f"⚠️ Error: {str(e)[:20]}..."
            
            results_text += f"**{i}.** {file_name[:50]}...\n"
            results_text += f"    📏 Size: {file_size:,} bytes\n"
            results_text += f"    🔗 Status: {status}\n"
            results_text += f"    🆔 ID: `{file_id}`\n\n"
        
        results_text += f"""🔧 **To refresh expired movies:**
1. Forward the movie file again from source channel
2. Bot will automatically detect and update the expired ID
3. Use `/test_file_id <file_id>` to verify the fix

💡 **Note:** Files marked as "Working" don't need refresh."""
        
        await message.reply(results_text)
        
    except Exception as e:
        logger.error(f"Error in refresh movie command: {e}")
        await message.reply(f"❌ **Error searching movie:** {e}")

@Client.on_message(filters.command("auto_fix_database") & filters.user(ADMINS))
async def auto_fix_database_command(client: Client, message: Message):
    """Automatically attempt to fix common database issues"""
    try:
        await message.reply("🔧 **Starting automatic database fixes...**")
        
        fixes_applied = []
        
        # Fix 1: Remove files with obviously invalid IDs
        logger.info("Removing files with invalid ID formats...")
        invalid_files = list(primary_col.find({}))
        removed_invalid = 0
        
        for file_info in invalid_files:
            file_id = str(file_info.get('_id', ''))
            if len(file_id) < 5 or len(file_id) > 300 or not file_id.strip():
                primary_col.delete_one({'_id': file_info['_id']})
                removed_invalid += 1
        
        if removed_invalid > 0:
            fixes_applied.append(f"✅ Removed {removed_invalid} files with invalid ID formats")
        
        # Fix 2: Remove duplicate entries (same name and size)
        logger.info("Checking for duplicate entries...")
        all_files = list(primary_col.find({}))
        duplicates_removed = 0
        seen_files = {}
        
        for file_info in all_files:
            file_name = file_info.get('file_name', '')
            file_size = file_info.get('file_size', 0)
            file_key = f"{file_name}_{file_size}"
            
            if file_key in seen_files:
                # This is a duplicate, keep the one with longer/better file ID
                existing_id = seen_files[file_key]['_id']
                current_id = file_info['_id']
                
                # Keep the one with longer ID (usually more recent/valid)
                if len(str(current_id)) > len(str(existing_id)):
                    # Remove the old one
                    primary_col.delete_one({'_id': existing_id})
                    seen_files[file_key] = file_info
                else:
                    # Remove the current one
                    primary_col.delete_one({'_id': current_id})
                
                duplicates_removed += 1
            else:
                seen_files[file_key] = file_info
        
        if duplicates_removed > 0:
            fixes_applied.append(f"✅ Removed {duplicates_removed} duplicate entries")
        
        # Fix 3: Update database statistics
        primary_count = primary_col.count_documents({})
        secondary_count = secondary_col.count_documents({})
        
        fixes_applied.append(f"📊 Database now has {primary_count + secondary_count:,} total files")
        
        # Create results message
        if len(fixes_applied) > 1:
            results = f"""🔧 **Database Auto-Fix Complete!**

🛠️ **Fixes Applied:**
{chr(10).join(f"• {fix}" for fix in fixes_applied)}

💡 **Recommendations:**
• Use `/fix_expired_files` to check for expired file IDs  
• Forward fresh copies of important movies regularly
• Use `/database_stats` to monitor database health

✨ **Your database is now optimized!**"""
        else:
            results = f"""✅ **Database Check Complete!**

🎉 **Good news:** No major issues found in your database.

📊 **Current Status:**
• Total files: {primary_count + secondary_count:,}
• Database appears healthy

💡 **Keep it healthy:**
• Regular use of `/fix_expired_files`
• Forward fresh movie copies when users report issues"""
        
        await message.reply(results)
        
    except Exception as e:
        logger.error(f"Error in auto fix database: {e}")
        await message.reply(f"❌ **Error during auto-fix:** {e}")

@Client.on_callback_query(filters.regex(r"^admin_db_stats$"))
async def admin_db_stats_callback(client: Client, query):
    """Show database statistics in callback"""
    try:
        if query.from_user.id not in ADMINS:
            await query.answer("❌ Admin only", show_alert=True)
            return
        
        # Get database stats
        primary_count = primary_col.count_documents({})
        secondary_count = secondary_col.count_documents({})
        total_files = primary_count + secondary_count
        
        # Get recent files
        recent_files = list(primary_col.find().sort([("_id", -1)]).limit(3))
        recent_info = []
        for file_info in recent_files:
            file_name = file_info.get('file_name', 'Unknown')[:25]
            recent_info.append(f"• {file_name}...")
        
        stats_text = f"""📊 **Database Statistics**

📁 **File Count:**
• Primary: {primary_count:,} files
• Secondary: {secondary_count:,} files  
• **Total: {total_files:,} files**

📋 **Recent Files:**
{chr(10).join(recent_info) if recent_info else "No recent files"}

🔧 **Maintenance Tools:**
• `/fix_expired_files` - Find expired IDs
• `/auto_fix_database` - Auto cleanup
• `/refresh_movie <name>` - Fix specific movie"""
        
        await query.message.edit(stats_text, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Refresh Stats", callback_data="admin_db_stats")],
            [InlineKeyboardButton("🔍 Check Expired Files", callback_data="check_expired_callback")]
        ]))
        
    except Exception as e:
        logger.error(f"Error in admin db stats callback: {e}")
        await query.answer("❌ Error loading stats", show_alert=True)

@Client.on_callback_query(filters.regex(r"^check_expired_callback$"))
async def check_expired_callback(client: Client, query):
    """Run expired file check from callback"""
    try:
        if query.from_user.id not in ADMINS:
            await query.answer("❌ Admin only", show_alert=True)
            return
        
        await query.message.edit("🔄 **Starting expired file check...**\n\nThis will test file IDs to find expired ones.")
        
        # Simulate the expired file check process
        test_files = list(primary_col.find().limit(10))
        expired_count = 0
        valid_count = 0
        
        for file_info in test_files:
            file_id = file_info.get('_id')
            try:
                test_msg = await client.send_document(
                    chat_id=query.from_user.id,
                    document=file_id,
                    caption="Test"
                )
                await test_msg.delete()
                valid_count += 1
            except:
                expired_count += 1
        
        results = f"""🔍 **Quick File Check Results**

📊 **Sample of {len(test_files)} files:**
• ✅ Valid: {valid_count}
• ❌ Expired: {expired_count}

💡 **For complete analysis, use:**
`/fix_expired_files` command

🔧 **Quick Actions:**"""
        
        await query.message.edit(results, reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 Full Database Stats", callback_data="admin_db_stats")],
            [InlineKeyboardButton("🛠️ Auto Fix Database", callback_data="auto_fix_callback")]
        ]))
        
    except Exception as e:
        logger.error(f"Error in check expired callback: {e}")
        await query.answer("❌ Error checking files", show_alert=True)