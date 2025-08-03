#!/usr/bin/env python3
"""
Simple database test - check files without loading full bot
"""
import os
os.environ['BOT_TOKEN'] = 'dummy_token_for_test'
os.environ['API_ID'] = '123456'
os.environ['API_HASH'] = 'dummy_hash'

import pymongo

# Direct database connection
try:
    # Use the actual database configuration from info.py
    DATABASE_URL = "mongodb+srv://tharu:20020224Ha@cluster0.tn75wcw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME = "Cluster0"
    COLLECTION_NAME = "Telegram_files"
    
    # Connect to MongoDB
    myclient = pymongo.MongoClient(DATABASE_URL)
    mydb = myclient[DATABASE_NAME]
    collection = mydb[COLLECTION_NAME]
    
    print("Connected to database successfully!")
    
    # Check total files
    total_files = collection.count_documents({})
    print(f"Total files in database: {total_files}")
    
    if total_files > 0:
        # Find Despicable Me 4
        despicable_file = collection.find_one({'file_name': {'$regex': 'Despicable Me 4', '$options': 'i'}})
        
        if despicable_file:
            print(f"\nFound Despicable Me 4:")
            print(f"   File name: {despicable_file['file_name']}")
            print(f"   File ID: {despicable_file['_id']}")
            print(f"   File size: {despicable_file.get('file_size', 'Unknown')}")
            print(f"   File ID length: {len(str(despicable_file['_id']))}")
            
            # Check if this looks like a valid Telegram file ID
            file_id = str(despicable_file['_id'])
            if len(file_id) < 10:
                print(f"   [ERROR] File ID too short - likely invalid")
            elif len(file_id) > 200:
                print(f"   [ERROR] File ID too long - likely invalid")
            else:
                print(f"   [OK] File ID length looks reasonable")
        else:
            print(f"\n[NOT FOUND] Despicable Me 4 not found in database")
        
        # Show recent files
        print(f"\nRecent 5 files:")
        recent_files = list(collection.find().sort([("_id", -1)]).limit(5))
        for i, file_info in enumerate(recent_files, 1):
            file_name = file_info.get('file_name', 'Unknown')[:40]
            file_id_length = len(str(file_info.get('_id', '')))
            print(f"   {i}. {file_name}... (ID length: {file_id_length})")
    
except Exception as e:
    print(f"[ERROR] Database connection error: {e}")
    print(f"\nThis might mean:")
    print(f"   - MongoDB is not running locally")
    print(f"   - Database is hosted remotely (check info.py for DATABASE_URL)")
    print(f"   - Different database configuration needed")