# 🚀 Movie Bot Setup Guide

## 📋 Prerequisites

1. **Python 3.7+** installed on your system
2. **Telegram Bot Token** from @BotFather
3. **Your Telegram User ID** (get from @userinfobot)

## 🔧 Step-by-Step Setup

### Step 1: Install Required Packages

Run the installation script:
```bash
python install_requirements.py
```

Or install manually:
```bash
pip install hydrogram==0.1.4 pymongo aiohttp requests beautifulsoup4 dnspython
```

### Step 2: Get Your Bot Token

1. Message @BotFather on Telegram
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Get Your User ID

1. Message @userinfobot on Telegram
2. Copy your user ID (a number like: `123456789`)

### Step 4: Configure the Bot

Edit `start_bot.py` and replace:
```python
os.environ['BOT_TOKEN'] = 'YOUR_BOT_TOKEN_HERE'  # Replace with your actual token
os.environ['ADMINS'] = '1234523543'              # Replace with your user ID
```

Example:
```python
os.environ['BOT_TOKEN'] = '6123456789:ABCdefGHIjklMNOpqrsTUVwxyz'
os.environ['ADMINS'] = '987654321'
```

### Step 5: Start the Bot

```bash
python start_bot.py
```

## 🎯 Quick Start Commands

After the bot starts successfully:

### For Admins:
- `/adminhelp` - See all admin commands
- `/testdb` - Test database connectivity
- Forward movie files from channels to add them to database

### For Users:
- Send movie names to search
- Select subtitle language
- Download movies with subtitles

## 🔍 Troubleshooting

### Bot Won't Start?

1. **Check Python Version**:
   ```bash
   python --version
   ```
   Should be 3.7 or higher.

2. **Install Missing Packages**:
   ```bash
   python install_requirements.py
   ```

3. **Check Token Format**:
   Bot tokens should look like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

4. **Verify Environment Variables**:
   Make sure you edited `start_bot.py` with your actual values.

### Common Errors:

#### Error: `ModuleNotFoundError: No module named 'hydrogram'`
**Solution**: Run `python install_requirements.py`

#### Error: `BOT_TOKEN environment variable is required!`
**Solution**: Edit `start_bot.py` and add your actual bot token

#### Error: `Invalid BOT_TOKEN format!`
**Solution**: Make sure your token contains a colon (:) and is from @BotFather

### Database Issues:

The bot uses MongoDB. If you see database errors:
1. The default MongoDB URL should work for testing
2. For production, get your own MongoDB connection string
3. Update the `DATABASE_URL` in `start_bot.py`

## 🎬 Using the Bot

### Adding Movies (Admin):
1. Forward movie files from any channel to your bot
2. Bot will automatically detect and save them
3. Users can then search and download

### Searching Movies (Users):
1. Send a movie name to the bot
2. Bot shows search results
3. Click on a movie
4. Select subtitle language
5. Receive movie file + subtitles

### Popular Movies:
- Type `/popular` to see trending movies
- Click on any movie to search and download

## 🛠 Advanced Configuration

### Channel Management:
- Use `/addchannel <channel_id>` to add movie channels
- Use `/channels` to list all channels
- Use `/removechannel <channel_id>` to remove channels

### Database Management:
- Use `/testdb` to check database status
- Bot automatically saves movies with duplicate detection
- Supports primary and secondary databases

## 🚀 Production Deployment

For production use:
1. Get your own MongoDB database
2. Update `DATABASE_URL` in `start_bot.py`
3. Add your server admin user IDs to `ADMINS`
4. Consider using environment variables instead of hardcoded values

## ✅ Success Indicators

Your bot is working correctly when:
- ✅ Bot starts without errors
- ✅ `/adminhelp` shows your admin status
- ✅ `/testdb` shows database connectivity
- ✅ Forwarding movies works (saves to database)
- ✅ Users can search and receive movies
- ✅ Subtitle generation works

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Ensure all requirements are installed
3. Verify your bot token and user ID are correct
4. Check the console output for specific error messages

Your movie bot is now ready to serve movies with subtitles! 🎉