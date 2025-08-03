"""
Install required packages for the movie bot
"""
import subprocess
import sys

packages = [
    'hydrogram==0.1.4',
    'pymongo==4.6.1',
    'aiohttp==3.9.1',
    'requests==2.31.0',
    'beautifulsoup4==4.12.2',
    'dnspython==2.4.2',
    'python-dotenv==1.0.0'
]

print("=== Installing Movie Bot Requirements ===")

for package in packages:
    print(f"Installing {package}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"[OK] {package} installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to install {package}: {e}")
    except Exception as e:
        print(f"[ERROR] Error installing {package}: {e}")

print("\n=== Installation Complete ===")
print("Now you can:")
print("1. Edit start_bot.py and add your BOT_TOKEN")
print("2. Run: python start_bot.py")