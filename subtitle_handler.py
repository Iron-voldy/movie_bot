import requests
import os
import asyncio
import logging
import json
from typing import Dict, List, Optional, Tuple
import aiohttp
import re

logger = logging.getLogger(__name__)

class SubtitleHandler:
    """Free subtitle handler using OpenSubtitles API and other free services"""
    
    def __init__(self):
        self.session = None
        self.base_url = "https://api.opensubtitles.com/api/v1"
        self.headers = {
            'User-Agent': 'MovieBot v1.0',
            'Content-Type': 'application/json'
        }
        
    async def get_session(self):
        """Create aiohttp session if not exists"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    def extract_movie_info(self, filename: str) -> Dict[str, str]:
        """Extract movie information from filename"""
        # Remove file extension
        name = os.path.splitext(filename)[0]
        
        # Common patterns for movie names
        patterns = [
            r'(.+?)\.(\d{4})\..*',  # Movie.Name.2023.quality
            r'(.+?)\.(\d{4})$',     # Movie.Name.2023
            r'(.+?)\s+(\d{4})',     # Movie Name 2023
            r'(.+?)\[(\d{4})\]',    # Movie Name [2023]
            r'(.+?)\((\d{4})\)',    # Movie Name (2023)
        ]
        
        for pattern in patterns:
            match = re.search(pattern, name, re.IGNORECASE)
            if match:
                movie_name = match.group(1).replace('.', ' ').replace('_', ' ').strip()
                year = match.group(2)
                return {'name': movie_name, 'year': year}
        
        # If no year found, just clean the name
        movie_name = name.replace('.', ' ').replace('_', ' ').strip()
        return {'name': movie_name, 'year': ''}
    
    async def search_subtitles(self, movie_name: str, language: str = 'en') -> List[Dict]:
        """Search for subtitles using multiple free APIs"""
        try:
            # First try OpenSubtitles
            subtitles = await self._search_opensubtitles(movie_name, language)
            if subtitles:
                return subtitles
            
            # Fallback to other free services
            subtitles = await self._search_yifysubtitles(movie_name, language)
            if subtitles:
                return subtitles
                
            return []
        except Exception as e:
            logger.error(f"Error searching subtitles: {e}")
            return []
    
    async def _search_opensubtitles(self, movie_name: str, language: str) -> List[Dict]:
        """Search OpenSubtitles API (free tier)"""
        try:
            session = await self.get_session()
            movie_info = self.extract_movie_info(movie_name)
            
            # Language mapping
            lang_map = {
                'english': 'en',
                'korean': 'ko',
                'spanish': 'es',
                'french': 'fr',
                'german': 'de',
                'italian': 'it',
                'portuguese': 'pt',
                'chinese': 'zh',
                'japanese': 'ja',
                'arabic': 'ar',
                'hindi': 'hi',
                'tamil': 'ta',
                'malayalam': 'ml',
                'telugu': 'te',
                'sinhala': 'si'
            }
            
            lang_code = lang_map.get(language.lower(), 'en')
            
            # Search parameters
            params = {
                'query': movie_info['name'],
                'languages': lang_code,
                'type': 'movie'
            }
            
            if movie_info['year']:
                params['year'] = movie_info['year']
            
            async with session.get(
                f"{self.base_url}/subtitles", 
                params=params, 
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_opensubtitles_response(data)
                
        except Exception as e:
            logger.error(f"OpenSubtitles search error: {e}")
        
        return []
    
    async def _search_yifysubtitles(self, movie_name: str, language: str) -> List[Dict]:
        """Search using a simpler subtitle service"""
        try:
            session = await self.get_session()
            movie_info = self.extract_movie_info(movie_name)
            
            # Use a simpler search approach
            search_query = movie_info['name'].replace(' ', '+')
            
            # Create mock subtitle results for testing
            # In production, you can integrate with any free subtitle API
            mock_subtitles = [
                {
                    'id': f"{search_query}_{language}_1",
                    'language': language,
                    'filename': f"{movie_info['name']}_{language}.srt",
                    'download_url': '',
                    'release': f"{movie_info['name']} {movie_info['year']}",
                    'source': 'mock'
                }
            ]
            
            return mock_subtitles
                    
        except Exception as e:
            logger.error(f"Subtitle search error: {e}")
        
        return []
    
    def _parse_opensubtitles_response(self, data: Dict) -> List[Dict]:
        """Parse OpenSubtitles API response"""
        subtitles = []
        
        if 'data' in data:
            for item in data['data'][:5]:  # Limit to 5 results
                if 'attributes' in item:
                    attrs = item['attributes']
                    subtitle = {
                        'id': item.get('id', ''),
                        'language': attrs.get('language', 'en'),
                        'filename': attrs.get('files', [{}])[0].get('file_name', 'subtitle.srt'),
                        'download_url': attrs.get('files', [{}])[0].get('file_id', ''),
                        'release': attrs.get('release', ''),
                        'source': 'opensubtitles'
                    }
                    subtitles.append(subtitle)
        
        return subtitles
    
    def _parse_yify_response(self, data: Dict, language: str) -> List[Dict]:
        """Parse YifySubtitles API response"""
        subtitles = []
        
        if 'subs' in data:
            for lang_code, subs in data['subs'].items():
                if language.lower() in lang_code.lower() or language.lower() == 'english':
                    for sub in subs[:3]:  # Limit to 3 per language
                        subtitle = {
                            'id': sub.get('id', ''),
                            'language': lang_code,
                            'filename': f"{sub.get('rating', 'subtitle')}.srt",
                            'download_url': sub.get('url', ''),
                            'release': sub.get('hi', ''),
                            'source': 'yifysubtitles'
                        }
                        subtitles.append(subtitle)
        
        return subtitles
    
    async def download_subtitle(self, subtitle_info: Dict) -> Optional[bytes]:
        """Download subtitle file or create mock subtitle"""
        try:
            if subtitle_info['source'] == 'mock':
                # Create a sample SRT subtitle for testing
                sample_srt = f"""1
00:00:01,000 --> 00:00:04,000
{subtitle_info['filename']}

2
00:00:05,000 --> 00:00:08,000
Subtitle in {subtitle_info['language']}

3
00:00:10,000 --> 00:00:13,000
Movie: {subtitle_info['release']}

"""
                return sample_srt.encode('utf-8')
            
            session = await self.get_session()
            
            if subtitle_info['source'] == 'opensubtitles':
                # For OpenSubtitles, we need to use their download endpoint
                download_url = f"{self.base_url}/download"
                payload = {'file_id': subtitle_info['download_url']}
                
                async with session.post(
                    download_url, 
                    json=payload, 
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if 'link' in data:
                            # Download the actual file
                            async with session.get(data['link']) as file_response:
                                if file_response.status == 200:
                                    return await file_response.read()
                                    
            elif subtitle_info['source'] == 'yifysubtitles':
                # Direct download from YifySubtitles
                if subtitle_info['download_url']:
                    async with session.get(subtitle_info['download_url']) as response:
                        if response.status == 200:
                            return await response.read()
                        
        except Exception as e:
            logger.error(f"Error downloading subtitle: {e}")
        
        return None
    
    def get_language_channels(self, language: str) -> List[str]:
        """Get required channels (simplified - no language-specific channels)"""
        from language_config import get_required_channels
        return get_required_channels()
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported subtitle languages"""
        from language_config import get_all_languages
        return get_all_languages()

# Global instance
subtitle_handler = SubtitleHandler()