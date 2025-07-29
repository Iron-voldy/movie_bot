"""
Real-time movie data fetcher using Google Gemini API
"""

import os
import json
import logging
import asyncio
from typing import List, Dict
import aiohttp
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MovieFetcher:
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
        self.cache = {}
        self.cache_duration = timedelta(hours=2)  # Cache for 2 hours to reduce API calls
        
    async def _make_request(self, prompt: str, max_retries: int = 3) -> str:
        """Make request to Gemini API with retry logic"""
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not set, using fallback data")
            raise ValueError("GEMINI_API_KEY environment variable not set")
            
        headers = {
            'Content-Type': 'application/json',
        }
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        for attempt in range(max_retries):
            try:
                timeout = aiohttp.ClientTimeout(total=15)  # 15 second timeout
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    async with session.post(url, headers=headers, json=data) as response:
                        if response.status == 200:
                            result = await response.json()
                            return result['candidates'][0]['content']['parts'][0]['text']
                        elif response.status == 503:  # Service unavailable/overloaded
                            error_text = await response.text()
                            logger.warning(f"Gemini API overloaded (attempt {attempt + 1}/{max_retries}): {error_text}")
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 2  # Exponential backoff: 2, 4, 6 seconds
                                logger.info(f"Retrying in {wait_time} seconds...")
                                await asyncio.sleep(wait_time)
                                continue
                            else:
                                raise Exception(f"API overloaded after {max_retries} attempts")
                        else:
                            error_text = await response.text()
                            logger.error(f"Gemini API error: {response.status} - {error_text}")
                            raise Exception(f"API request failed: {response.status}")
            except asyncio.TimeoutError:
                logger.warning(f"API request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)
                    continue
                else:
                    raise Exception("API request timed out after retries")

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key]['timestamp']
        return datetime.now() - cached_time < self.cache_duration

    async def get_popular_movies(self) -> List[Dict]:
        """Get current popular movies"""
        cache_key = "popular_movies"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached popular movies data")
            return self.cache[cache_key]['data']
        
        prompt = """
        Get the current top 15 most popular movies in 2024-2025. 
        Return ONLY a JSON array with this exact format:
        [
          {
            "name": "Movie Title",
            "rating": "8.5/10",
            "description": "Very short description under 60 characters"
          }
        ]
        
        Make sure descriptions are under 60 characters. Include mix of recent releases and popular classics.
        Return only valid JSON, no additional text.
        """
        
        try:
            response = await self._make_request(prompt)
            # Clean the response to ensure it's valid JSON
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            movies = json.loads(response)
            
            # Cache the result
            self.cache[cache_key] = {
                'data': movies,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Fetched {len(movies)} popular movies from Gemini API")
            return movies
            
        except Exception as e:
            logger.error(f"Error fetching popular movies: {e}")
            # Return fallback data
            return self._get_fallback_popular()

    async def get_latest_movies(self) -> List[Dict]:
        """Get latest released movies"""
        cache_key = "latest_movies"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached latest movies data")
            return self.cache[cache_key]['data']
        
        prompt = """
        Get the 12 most recent movie releases from 2024-2025 (last 6 months).
        Return ONLY a JSON array with this exact format:
        [
          {
            "name": "Movie Title",
            "rating": "7.2/10",
            "description": "Very short description under 60 characters"
          }
        ]
        
        Focus on movies released in theaters or streaming in 2024-2025.
        Make sure descriptions are under 60 characters.
        Return only valid JSON, no additional text.
        """
        
        try:
            response = await self._make_request(prompt)
            # Clean the response
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            movies = json.loads(response)
            
            # Cache the result
            self.cache[cache_key] = {
                'data': movies,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Fetched {len(movies)} latest movies from Gemini API")
            return movies
            
        except Exception as e:
            logger.error(f"Error fetching latest movies: {e}")
            return self._get_fallback_latest()

    async def get_random_movies(self) -> List[Dict]:
        """Get random mix of good movies"""
        cache_key = "random_movies"
        
        if self._is_cache_valid(cache_key):
            logger.info("Using cached random movies data")
            return self.cache[cache_key]['data']
        
        prompt = """
        Get 12 random excellent movies from different genres and decades.
        Mix of classics, modern hits, and hidden gems.
        Return ONLY a JSON array with this exact format:
        [
          {
            "name": "Movie Title",
            "rating": "8.1/10",
            "description": "Very short description under 60 characters"
          }
        ]
        
        Include variety: action, comedy, drama, sci-fi, thriller, animation.
        Make sure descriptions are under 60 characters.
        Return only valid JSON, no additional text.
        """
        
        try:
            response = await self._make_request(prompt)
            # Clean the response
            response = response.strip()
            if response.startswith('```json'):
                response = response.replace('```json', '').replace('```', '').strip()
            
            movies = json.loads(response)
            
            # Cache the result
            self.cache[cache_key] = {
                'data': movies,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Fetched {len(movies)} random movies from Gemini API")
            return movies
            
        except Exception as e:
            logger.error(f"Error fetching random movies: {e}")
            return self._get_fallback_random()

    def _get_fallback_popular(self) -> List[Dict]:
        """Fallback popular movies if API fails"""
        return [
            {"name": "The Shawshank Redemption", "rating": "9.3/10", "description": "Two prisoners bond over years, finding redemption."},
            {"name": "The Dark Knight", "rating": "9.0/10", "description": "Batman faces the Joker in battle for Gotham's soul."},
            {"name": "Avatar: The Way of Water", "rating": "7.6/10", "description": "Jake Sully protects family on Pandora from threats."},
            {"name": "Top Gun: Maverick", "rating": "8.3/10", "description": "Maverick trains pilots for dangerous mission."},
            {"name": "Spider-Man: No Way Home", "rating": "8.2/10", "description": "Peter Parker faces villains from other dimensions."}
        ]

    def _get_fallback_latest(self) -> List[Dict]:
        """Fallback latest movies if API fails"""
        return [
            {"name": "Deadpool & Wolverine", "rating": "8.0/10", "description": "Wade Wilson teams up with Wolverine."},
            {"name": "Inside Out 2", "rating": "7.7/10", "description": "Riley's emotions navigate teenage challenges."},
            {"name": "Dune: Part Two", "rating": "8.5/10", "description": "Paul Atreides leads rebellion against enemies."},
            {"name": "Bad Boys: Ride or Die", "rating": "6.8/10", "description": "Miami cops face their biggest threat yet."}
        ]

    def _get_fallback_random(self) -> List[Dict]:
        """Fallback random movies if API fails"""
        return [
            {"name": "Casablanca", "rating": "8.5/10", "description": "Nightclub owner helps lovers escape Nazis."},
            {"name": "Toy Story", "rating": "8.3/10", "description": "Toys come to life when humans leave."},
            {"name": "Jurassic Park", "rating": "8.1/10", "description": "Dinosaurs brought back to life in theme park."},
            {"name": "Star Wars", "rating": "8.6/10", "description": "Farm boy joins rebellion against Empire."}
        ]

# Global instance
movie_fetcher = MovieFetcher()