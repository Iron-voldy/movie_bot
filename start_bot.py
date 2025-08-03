"""
Bot startup script with environment variable setup
"""
import os
import sys

# Set required environment variables
# IMPORTANT: Replace these with your actual values
os.environ['BOT_TOKEN'] = 'YOUR_BOT_TOKEN_HERE'
os.environ['API_ID'] = '3135143'  # Default value from info.py
os.environ['API_HASH'] = '24f97a7491f6fc888eeff31694c061bf'  # Default value from info.py
os.environ['ADMINS'] = '1234523543'  # Default admin ID, replace with your user ID

# Optional environment variables
os.environ['DATABASE_URL'] = os.environ.get('DATABASE_URL', 'mongodb+srv://tharu:20020224Ha@cluster0.tn75wcw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
os.environ['DATABASE_NAME'] = os.environ.get('DATABASE_NAME', 'Cluster0')
os.environ['COLLECTION_NAME'] = os.environ.get('COLLECTION_NAME', 'Telegram_files')

print("=== Movie Bot Startup ===")
print("Environment variables set:")
print(f"BOT_TOKEN: {'*' * 20}...{os.environ['BOT_TOKEN'][-5:] if len(os.environ['BOT_TOKEN']) > 25 else 'SET'}")
print(f"API_ID: {os.environ['API_ID']}")
print(f"ADMINS: {os.environ['ADMINS']}")

# Check if BOT_TOKEN is set to placeholder
if os.environ['BOT_TOKEN'] == 'YOUR_BOT_TOKEN_HERE':
    print("\n[ERROR] Please set your actual BOT_TOKEN!")
    print("1. Get a bot token from @BotFather on Telegram")
    print("2. Replace 'YOUR_BOT_TOKEN_HERE' in this file with your actual token")
    print("3. Replace the ADMINS value with your Telegram user ID")
    sys.exit(1)

# Try to import and start the bot
try:
    print("\nStarting bot...")
    import bot
    print("Bot module imported successfully")
except ImportError as e:
    print(f"[ERROR] Missing dependency: {e}")
    print("\nTo install missing packages, run:")
    print("pip install hydrogram==0.1.4 pymongo aiohttp requests beautifulsoup4 dnspython")
    sys.exit(1)
except Exception as e:
    print(f"[ERROR] Error starting bot: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)