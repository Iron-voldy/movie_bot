"""
Simple test script to check if basic imports work
"""
import sys
import os

print("=== Bot Startup Test ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test basic imports
try:
    print("Testing info.py import...")
    from info import BOT_TOKEN, API_ID, API_HASH, ADMINS
    print(f"[OK] info.py imported successfully")
    print(f"BOT_TOKEN present: {bool(BOT_TOKEN)}")
    print(f"API_ID: {API_ID}")
    print(f"ADMINS: {ADMINS}")
except Exception as e:
    print(f"[ERROR] Error importing info.py: {e}")
    sys.exit(1)

# Test database import
try:
    print("Testing database import...")
    from database.ia_filterdb import get_database_count
    print("[OK] Database import successful")
except Exception as e:
    print(f"[ERROR] Error importing database: {e}")

# Test hydrogram import
try:
    print("Testing hydrogram import...")
    import hydrogram
    print(f"[OK] Hydrogram imported successfully: {hydrogram.__version__}")
except ImportError as e:
    print(f"[ERROR] Hydrogram not installed: {e}")
    print("Please install hydrogram with: pip install hydrogram==0.1.4")
except Exception as e:
    print(f"[ERROR] Error importing hydrogram: {e}")

# Test other critical imports
critical_modules = [
    'pymongo',
    'aiohttp',
    'requests',
    'beautifulsoup4'
]

for module in critical_modules:
    try:
        __import__(module)
        print(f"[OK] {module} available")
    except ImportError:
        print(f"[ERROR] {module} not installed")

print("\n=== Test Complete ===")
print("If hydrogram is missing, install it with:")
print("pip install hydrogram==0.1.4 pymongo aiohttp requests beautifulsoup4")