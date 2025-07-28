"""
Simplified channel configuration - Only 2 required channels
"""

# Required channels that all users must join before using the bot
REQUIRED_CHANNELS = [
    {
        'channel': '-1002766947260',
        'name': 'Movies Channel 1',
        'type': 'main'
    },
    {
        'channel': '-1002886647880', 
        'name': 'Movies Channel 2',
        'type': 'main'
    }
]

# Legacy compatibility - keeping old structure but simplified
COMMON_CHANNEL = '-1002766947260'  # First required channel

LANGUAGE_CHANNELS = {
    'english': {
        'channel': '-1002766947260',
        'display_name': 'English Movies',
        'flag': '🇺🇸'
    },
    
    'all': {
        'channel': '-1002886647880',
        'display_name': 'All Movies',
        'flag': '🌐'
    }
}

def get_required_channels():
    """Get list of all required channels"""
    return [ch['channel'] for ch in REQUIRED_CHANNELS]

def get_channel_info(channel_id):
    """Get channel information by ID"""
    for ch in REQUIRED_CHANNELS:
        if ch['channel'] == channel_id:
            return ch
    return None

def get_all_languages():
    """Get all available languages"""
    return list(LANGUAGE_CHANNELS.keys())

def get_language_display_name(language):
    """Get display name for a language"""
    return LANGUAGE_CHANNELS.get(language, {}).get('display_name', language.title())

def get_language_channel(language):
    """Get channel ID for a language"""
    return LANGUAGE_CHANNELS.get(language, {}).get('channel', COMMON_CHANNEL)

def get_language_channels():
    """Get all language channels"""
    return LANGUAGE_CHANNELS