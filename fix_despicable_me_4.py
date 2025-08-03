#!/usr/bin/env python3
"""
Quick fix script for Despicable Me 4 expired file ID
Run this script to manually update the expired file ID
"""

import asyncio
import logging
from pymongo import MongoClient
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_despicable_me_4():
    """Fix the expired file ID for Despicable Me 4"""
    try:
        # Connect to database
        client = MongoClient(DATABASE_URL)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        
        # Find the expired file
        expired_file_id = "BQADBQADIREAAo3P8VUghYq4pZK_LRYE"
        file_info = col.find_one({'_id': expired_file_id})
        
        if file_info:
            print(f"✅ Found expired file: {file_info['file_name']}")
            print(f"📄 File size: {file_info['file_size']:,} bytes")
            print(f"🆔 Current ID: {expired_file_id}")
            print()
            print("🔧 TO FIX THIS ISSUE:")
            print("1. Go to your source channel where you have 'Despicable Me 4 (2024)' movie")
            print("2. Forward the movie file to your bot again")
            print("3. The bot will automatically detect it's the same movie and update the ID")
            print()
            print("✨ The enhanced duplicate detection system will handle the rest!")
            print()
            
            # Show current database stats
            total_files = col.count_documents({})
            print(f"📊 Current database: {total_files:,} total files")
            
            return True
        else:
            print(f"❌ File not found in database: {expired_file_id}")
            
            # Search for similar files
            similar_files = list(col.find({
                'file_name': {'$regex': 'Despicable Me 4', '$options': 'i'}
            }))
            
            if similar_files:
                print(f"🔍 Found {len(similar_files)} similar files:")
                for i, file in enumerate(similar_files, 1):
                    print(f"  {i}. {file['file_name']}")
                    print(f"     ID: {file['_id']}")
                    print(f"     Size: {file['file_size']:,} bytes")
                    print()
            
            return False
            
    except Exception as e:
        logger.error(f"Error fixing file: {e}")
        return False

async def check_database_health():
    """Check overall database health"""
    try:
        client = MongoClient(DATABASE_URL)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        
        # Get basic stats
        total_files = col.count_documents({})
        
        # Check for files with short IDs (likely invalid)
        invalid_files = []
        all_files = col.find().limit(50)  # Check first 50 files
        
        for file_info in all_files:
            file_id = str(file_info.get('_id', ''))
            if len(file_id) < 10:
                invalid_files.append(file_info)
        
        print("📊 DATABASE HEALTH CHECK")
        print("=" * 40)
        print(f"📁 Total files: {total_files:,}")
        print(f"⚠️ Potentially invalid IDs: {len(invalid_files)}")
        
        if invalid_files:
            print("\n🚨 Files with suspicious IDs:")
            for file in invalid_files[:5]:  # Show first 5
                print(f"  • {file.get('file_name', 'Unknown')[:50]}...")
                print(f"    ID: {file.get('_id')}")
        
        # Get recent files
        recent_files = list(col.find().sort([("_id", -1)]).limit(5))
        print(f"\n📋 Recent files ({len(recent_files)}):")
        for file in recent_files:
            print(f"  • {file.get('file_name', 'Unknown')[:50]}...")
        
        print("\n💡 RECOMMENDATIONS:")
        if len(invalid_files) > 0:
            print("  1. Run `/auto_fix_database` command in bot")
            print("  2. Use `/fix_expired_files` to identify expired IDs")
        print("  3. Forward fresh copies of frequently requested movies")
        print("  4. Use the new admin commands for maintenance")
        
    except Exception as e:
        logger.error(f"Error checking database health: {e}")

if __name__ == "__main__":
    print("🎬 DESPICABLE ME 4 - FILE ID FIX TOOL")
    print("=" * 50)
    print()
    
    # Run the fix
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Fix the specific file
        success = loop.run_until_complete(fix_despicable_me_4())
        
        print()
        print("-" * 50)
        
        # Check database health
        loop.run_until_complete(check_database_health())
        
        print()
        print("🚀 NEXT STEPS:")
        print("1. Forward 'Despicable Me 4' movie from your source channel to the bot")
        print("2. Test the bot with a user request")
        print("3. Use `/database_stats` command for monitoring")
        print("4. Use `/fix_expired_files` for regular maintenance")
        
    finally:
        loop.close()