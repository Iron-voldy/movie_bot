"""
IMDB Integration Module - PROFESSOR-BOT Style
Provides movie information, posters, and enhanced search results
"""
import aiohttp
import asyncio
import re
import logging
from typing import Dict, Optional, List
from hydrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)

# IMDB/TMDB API configuration
IMDB_TEMPLATE = """
🎬 **{title}**

📅 **Year:** {year}
⭐ **Rating:** {rating}/10
🎭 **Genres:** {genres}
⏰ **Runtime:** {runtime}
🌍 **Language:** {languages}
🎭 **Director:** {director}
👥 **Cast:** {cast}

📖 **Plot:**
{plot}

🔗 **IMDB:** {imdb_url}
"""

async def get_movie_info(title: str) -> Optional[Dict]:
    """
    Get movie information from TMDB/IMDB
    Enhanced version of PROFESSOR-BOT's IMDB integration
    """
    try:
        # Clean the title for API search
        clean_title = clean_movie_title(title)
        
        if len(clean_title) < 2:
            return None
        
        logger.info(f"Getting movie info for: {clean_title}")
        
        # Try TMDB API first (free and reliable)
        movie_data = await search_tmdb(clean_title)
        
        if movie_data:
            return format_movie_data(movie_data)
        
        # Fallback to OMDB API
        movie_data = await search_omdb(clean_title)
        
        if movie_data:
            return format_omdb_data(movie_data)
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting movie info: {e}")
        return None

def clean_movie_title(title: str) -> str:
    """Clean movie title for API search"""
    try:
        # Remove file extensions
        title = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm|m4v)$', '', title, flags=re.IGNORECASE)
        
        # Remove quality indicators
        title = re.sub(r'\b(720p|1080p|2160p|4k|hd|bluray|webrip|hdcam|cam|ts|dvdrip)\b', '', title, flags=re.IGNORECASE)
        
        # Remove brackets and their content
        title = re.sub(r'\s*[\(\[].*?[\)\]]', '', title)
        
        # Remove extra whitespace
        title = ' '.join(title.split())
        
        return title.strip()
        
    except Exception as e:
        logger.error(f"Error cleaning title: {e}")
        return title

async def search_tmdb(title: str) -> Optional[Dict]:
    """Search TMDB for movie information"""
    try:
        # TMDB API (you can get a free API key from themoviedb.org)
        api_key = "YOUR_TMDB_API_KEY"  # Add your TMDB API key here
        
        if api_key == "YOUR_TMDB_API_KEY":
            # Fallback without API key
            return None
        
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': api_key,
            'query': title,
            'language': 'en-US'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('results'):
                        # Get detailed info for the first result
                        movie_id = data['results'][0]['id']
                        return await get_tmdb_details(movie_id, api_key)
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching TMDB: {e}")
        return None

async def get_tmdb_details(movie_id: int, api_key: str) -> Optional[Dict]:
    """Get detailed movie information from TMDB"""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            'api_key': api_key,
            'append_to_response': 'credits'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
        
        return None
        
    except Exception as e:
        logger.error(f"Error getting TMDB details: {e}")
        return None

async def search_omdb(title: str) -> Optional[Dict]:
    """Search OMDB for movie information (fallback)"""
    try:
        # OMDB API (you can get a free API key from omdbapi.com)
        api_key = "YOUR_OMDB_API_KEY"  # Add your OMDB API key here
        
        if api_key == "YOUR_OMDB_API_KEY":
            # Return mock data for demonstration
            return create_mock_movie_data(title)
        
        url = "http://www.omdbapi.com/"
        params = {
            'apikey': api_key,
            't': title,
            'type': 'movie',
            'plot': 'full'
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('Response') == 'True':
                        return data
        
        return None
        
    except Exception as e:
        logger.error(f"Error searching OMDB: {e}")
        return None

def create_mock_movie_data(title: str) -> Dict:
    """Create mock movie data when APIs are not available"""
    return {
        'title': title,
        'year': 'Unknown',
        'rating': 'N/A',
        'genres': 'Movie',
        'runtime': 'N/A',
        'languages': 'Unknown',
        'director': 'Unknown',
        'cast': 'Unknown',
        'plot': f'Information for "{title}" is not available. Enjoy the movie!',
        'poster_url': None,
        'imdb_url': f'https://www.imdb.com/find?q={title.replace(" ", "+")}'
    }

def format_movie_data(tmdb_data: Dict) -> Dict:
    """Format TMDB data for display"""
    try:
        # Extract cast and crew
        cast = []
        director = "Unknown"
        
        if 'credits' in tmdb_data:
            # Get top 5 cast members
            cast = [actor['name'] for actor in tmdb_data['credits'].get('cast', [])[:5]]
            
            # Get director
            crew = tmdb_data['credits'].get('crew', [])
            for person in crew:
                if person.get('job') == 'Director':
                    director = person['name']
                    break
        
        # Extract genres
        genres = [genre['name'] for genre in tmdb_data.get('genres', [])]
        
        # Extract languages
        languages = [lang['english_name'] for lang in tmdb_data.get('spoken_languages', [])]
        
        return {
            'title': tmdb_data.get('title', 'Unknown'),
            'year': tmdb_data.get('release_date', 'Unknown')[:4] if tmdb_data.get('release_date') else 'Unknown',
            'rating': f"{tmdb_data.get('vote_average', 0):.1f}",
            'genres': ', '.join(genres) if genres else 'Unknown',
            'runtime': f"{tmdb_data.get('runtime', 0)} min" if tmdb_data.get('runtime') else 'Unknown',
            'languages': ', '.join(languages) if languages else 'Unknown',
            'director': director,
            'cast': ', '.join(cast) if cast else 'Unknown',
            'plot': tmdb_data.get('overview', 'No plot available.'),
            'poster_url': f"https://image.tmdb.org/t/p/w500{tmdb_data['poster_path']}" if tmdb_data.get('poster_path') else None,
            'imdb_url': f"https://www.imdb.com/title/{tmdb_data.get('imdb_id', '')}" if tmdb_data.get('imdb_id') else None
        }
        
    except Exception as e:
        logger.error(f"Error formatting TMDB data: {e}")
        return create_mock_movie_data(tmdb_data.get('title', 'Unknown'))

def format_omdb_data(omdb_data: Dict) -> Dict:
    """Format OMDB data for display"""
    try:
        return {
            'title': omdb_data.get('Title', 'Unknown'),
            'year': omdb_data.get('Year', 'Unknown'),
            'rating': omdb_data.get('imdbRating', 'N/A'),
            'genres': omdb_data.get('Genre', 'Unknown'),
            'runtime': omdb_data.get('Runtime', 'Unknown'),
            'languages': omdb_data.get('Language', 'Unknown'),
            'director': omdb_data.get('Director', 'Unknown'),
            'cast': omdb_data.get('Actors', 'Unknown'),
            'plot': omdb_data.get('Plot', 'No plot available.'),
            'poster_url': omdb_data.get('Poster') if omdb_data.get('Poster') != 'N/A' else None,
            'imdb_url': f"https://www.imdb.com/title/{omdb_data.get('imdbID', '')}" if omdb_data.get('imdbID') else None
        }
        
    except Exception as e:
        logger.error(f"Error formatting OMDB data: {e}")
        return create_mock_movie_data(omdb_data.get('Title', 'Unknown'))

def create_imdb_caption(movie_data: Dict) -> str:
    """Create formatted caption with movie information"""
    try:
        return IMDB_TEMPLATE.format(**movie_data)
        
    except Exception as e:
        logger.error(f"Error creating IMDB caption: {e}")
        return f"🎬 **{movie_data.get('title', 'Movie')}**\n\nEnjoy your movie!"

def create_imdb_buttons(movie_data: Dict) -> InlineKeyboardMarkup:
    """Create buttons for IMDB information"""
    try:
        buttons = []
        
        if movie_data.get('imdb_url'):
            buttons.append([
                InlineKeyboardButton("🔗 View on IMDB", url=movie_data['imdb_url'])
            ])
        
        buttons.append([
            InlineKeyboardButton("🔍 Search More Movies", switch_inline_query_current_chat="")
        ])
        
        return InlineKeyboardMarkup(buttons)
        
    except Exception as e:
        logger.error(f"Error creating IMDB buttons: {e}")
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("🔍 Search More", switch_inline_query_current_chat="")
        ]])

async def send_movie_info(client, chat_id: int, movie_title: str):
    """Send movie information to chat"""
    try:
        movie_data = await get_movie_info(movie_title)
        
        if not movie_data:
            await client.send_message(
                chat_id,
                f"🎬 **{movie_title}**\n\n"
                f"ℹ️ Movie information not available.\n"
                f"But you can still enjoy the movie!"
            )
            return
        
        caption = create_imdb_caption(movie_data)
        buttons = create_imdb_buttons(movie_data)
        
        # Send with poster if available
        if movie_data.get('poster_url'):
            try:
                await client.send_photo(
                    chat_id,
                    photo=movie_data['poster_url'],
                    caption=caption,
                    reply_markup=buttons
                )
                return
            except Exception as e:
                logger.error(f"Error sending poster: {e}")
        
        # Send as text if poster fails
        await client.send_message(
            chat_id,
            caption,
            reply_markup=buttons
        )
        
    except Exception as e:
        logger.error(f"Error sending movie info: {e}")
        await client.send_message(
            chat_id,
            f"🎬 **{movie_title}**\n\n"
            f"❌ Error fetching movie information.\n"
            f"Please enjoy the movie!"
        )