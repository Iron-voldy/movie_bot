"""
Simplified configuration - Only 2 required channels for joining, all languages for subtitles
"""

# Required channels that all users must join before using the bot  
# TEMPORARY: Empty list to disable channel checking for testing
REQUIRED_CHANNELS = [
    # Uncomment and replace with your actual channel IDs when ready:
    # {
    #     'channel': 'YOUR_CHANNEL_ID_1',
    #     'name': 'Movies Channel 1',
    #     'type': 'main'
    # },
    # {
    #     'channel': 'YOUR_CHANNEL_ID_2',
    #     'name': 'Movies Channel 2', 
    #     'type': 'main'
    # }
]

# Legacy compatibility - keeping old structure but simplified
COMMON_CHANNEL = 'YOUR_CHANNEL_ID_1'  # First required channel - REPLACE THIS

# All available languages for subtitle selection (not for channels)
SUBTITLE_LANGUAGES = {
    'english': {
        'display_name': 'English',
        'flag': '🇺🇸'
    },
    'tamil': {
        'display_name': 'Tamil',
        'flag': '🇮🇳'
    },
    'hindi': {
        'display_name': 'Hindi',
        'flag': '🇮🇳'
    },
    'malayalam': {
        'display_name': 'Malayalam',
        'flag': '🇮🇳'
    },
    'telugu': {
        'display_name': 'Telugu',
        'flag': '🇮🇳'
    },
    'korean': {
        'display_name': 'Korean',
        'flag': '🇰🇷'
    },
    'sinhala': {
        'display_name': 'Sinhala',
        'flag': '🇱🇰'
    },
    'chinese': {
        'display_name': 'Chinese',
        'flag': '🇨🇳'
    },
    'japanese': {
        'display_name': 'Japanese',
        'flag': '🇯🇵'
    },
    'spanish': {
        'display_name': 'Spanish',
        'flag': '🇪🇸'
    },
    'french': {
        'display_name': 'French',
        'flag': '🇫🇷'
    },
    'arabic': {
        'display_name': 'Arabic',
        'flag': '🇸🇦'
    }
}

# Legacy compatibility for old language channels (now just for backward compatibility)
LANGUAGE_CHANNELS = SUBTITLE_LANGUAGES

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
    """Get all available languages for subtitles"""
    return list(SUBTITLE_LANGUAGES.keys())

def get_subtitle_languages():
    """Get all subtitle languages"""
    return SUBTITLE_LANGUAGES

def get_language_display_name(language):
    """Get display name for a language"""
    return SUBTITLE_LANGUAGES.get(language, {}).get('display_name', language.title())

def get_language_flag(language):
    """Get flag emoji for a language"""
    return SUBTITLE_LANGUAGES.get(language, {}).get('flag', '🌐')

# Legacy compatibility functions (for backward compatibility only)
def get_language_channel(language):
    """Legacy function - now returns common channel for all languages"""
    return COMMON_CHANNEL

def get_language_channels(*args):
    """Legacy function - now returns subtitle languages for compatibility"""
    # Accept any arguments for backward compatibility but ignore them
    return SUBTITLE_LANGUAGES