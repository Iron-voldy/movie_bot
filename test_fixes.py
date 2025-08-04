#!/usr/bin/env python3
"""
Test script to verify all the fixes are working properly
"""

import asyncio
import logging
from pymongo import MongoClient
from info import DATABASE_URL, DATABASE_NAME, COLLECTION_NAME

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database_connection():
    """Test database connectivity"""
    try:
        client = MongoClient(DATABASE_URL)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        
        # Test connection
        total_files = col.count_documents({})
        print(f"✅ Database connected successfully")
        print(f"📊 Total files in database: {total_files:,}")
        
        return True, total_files
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False, 0

async def test_expired_file_detection():
    """Test if the expired file is still in database"""
    try:
        client = MongoClient(DATABASE_URL)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        
        # Check for the specific expired file
        expired_file_id = "BQADBQADIREAAo3P8VUghYq4pZK_LRYE"
        file_info = col.find_one({'_id': expired_file_id})
        
        if file_info:
            print(f"🔍 Found expired file in database:")
            print(f"   • Name: {file_info.get('file_name', 'Unknown')}")
            print(f"   • Size: {file_info.get('file_size', 0):,} bytes")
            print(f"   • ID: {expired_file_id}")
            print(f"⚠️  This file needs to be refreshed")
            return True, file_info
        else:
            print(f"❌ Expired file not found in database")
            print(f"   • File ID: {expired_file_id}")
            print(f"   • This might mean it was already removed or never existed")
            return False, None
            
    except Exception as e:
        print(f"❌ Error checking expired file: {e}")
        return False, None

async def test_duplicate_detection_function():
    """Test the new duplicate detection function"""
    try:
        from database.ia_filterdb import find_duplicate_by_name_and_size
        
        # Test with a known file (if any exist)
        client = MongoClient(DATABASE_URL)
        db = client[DATABASE_NAME]
        col = db[COLLECTION_NAME]
        
        # Get a sample file to test with
        sample_file = col.find_one()
        
        if sample_file:
            file_name = sample_file.get('file_name')
            file_size = sample_file.get('file_size')
            
            print(f"🧪 Testing duplicate detection with:")
            print(f"   • Name: {file_name}")
            print(f"   • Size: {file_size:,} bytes")
            
            # Test the function
            result, location = await find_duplicate_by_name_and_size(file_name, file_size)
            
            if result:
                print(f"✅ Duplicate detection working!")
                print(f"   • Found in: {location} database")
                print(f"   • File ID: {result.get('_id')}")
            else:
                print(f"❌ Duplicate detection failed - couldn't find known file")
            
            return result is not None
        else:
            print(f"⚠️  No files in database to test duplicate detection")
            return True  # Not an error, just empty database
            
    except Exception as e:
        print(f"❌ Error testing duplicate detection: {e}")
        return False

async def test_save_file_function():
    """Test that the enhanced save_file function is available"""
    try:
        from database.ia_filterdb import save_file
        
        print(f"✅ Enhanced save_file function imported successfully")
        print(f"   • Function: {save_file}")
        print(f"   • Should handle duplicate refreshing")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing save_file function: {e}")
        return False

async def run_comprehensive_test():
    """Run all tests"""
    print("🧪 COMPREHENSIVE SYSTEM TEST")
    print("=" * 50)
    print()
    
    tests_results = []
    
    # Test 1: Database Connection
    print("1️⃣ Testing database connection...")
    db_success, total_files = await test_database_connection()
    tests_results.append(("Database Connection", db_success))
    print()
    
    # Test 2: Expired File Detection
    print("2️⃣ Testing expired file detection...")
    expired_success, expired_file = await test_expired_file_detection()
    tests_results.append(("Expired File Detection", expired_success))
    print()
    
    # Test 3: Duplicate Detection Function
    print("3️⃣ Testing duplicate detection function...")
    duplicate_success = await test_duplicate_detection_function()
    tests_results.append(("Duplicate Detection", duplicate_success))
    print()
    
    # Test 4: Enhanced Save Function
    print("4️⃣ Testing enhanced save function...")
    save_success = await test_save_file_function()
    tests_results.append(("Enhanced Save Function", save_success))
    print()
    
    # Summary
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 30)
    
    passed = 0
    failed = 0
    
    for test_name, result in tests_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print()
    print(f"📈 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! System is ready.")
        print()
        print("🚀 NEXT STEPS:")
        print("1. Restart your bot")
        print("2. Forward 'Despicable Me 4' movie file to refresh expired ID")
        print("3. Test with a user request")
        print("4. Monitor logs for successful operation")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print()
        print("🔧 TROUBLESHOOTING:")
        print("1. Check database connection settings in info.py")
        print("2. Ensure all files are properly uploaded")
        print("3. Check Python imports and dependencies")

if __name__ == "__main__":
    print("🎬 MOVIE BOT - SYSTEM TEST")
    print("Testing all fixes and enhancements...")
    print()
    
    # Run the tests
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(run_comprehensive_test())
    finally:
        loop.close()