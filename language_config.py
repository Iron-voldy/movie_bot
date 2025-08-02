"""
Simplified configuration - Only 2 required channels for joining, all languages for subtitles
"""

# Required channels that all users must join before using the bot  
# Using the channels from info.py CHANNELS config
REQUIRED_CHANNELS = []

def _get_channels_from_info():
    """Get channels from info.py configuration"""
    try:
        from info import CHANNELS
        if CHANNELS:
            return [
                {
                    'channel': ch,
                    'name': f'Movie Channel {i+1}',
                    'type': 'main'
                }
                for i, ch in enumerate(CHANNELS)
            ]
    except:
        pass
    return []

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
    # First try to get from dynamic config
    dynamic_channels = _get_channels_from_info() 
    if dynamic_channels:
        return [ch['channel'] for ch in dynamic_channels]
    
    # Fallback to static config
    return [ch['channel'] for ch in REQUIRED_CHANNELS]

def get_channel_info(channel_id):
    """Get channel information by ID"""
    # Try dynamic channels first
    dynamic_channels = _get_channels_from_info()
    if dynamic_channels:
        for ch in dynamic_channels:
            if str(ch['channel']) == str(channel_id):
                return ch
    
    # Fallback to static config
    for ch in REQUIRED_CHANNELS:
        if str(ch['channel']) == str(channel_id):
            return ch
    
    # If not found, return a default
    return {
        'channel': channel_id,
        'name': f'Channel {channel_id}',
        'type': 'main'
    }

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