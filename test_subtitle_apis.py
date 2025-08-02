"""
Test script for subtitle API integration
"""
import asyncio
import logging
from real_subtitle_handler import real_subtitle_handler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_subtitle_apis():
    """Test subtitle API functionality"""
    test_movies = [
        'Avengers Endgame 2019',
        'Spider-Man No Way Home 2021',
        'The Batman 2022',
        'Top Gun Maverick 2022'
    ]
    
    test_languages = ['english', 'korean', 'spanish', 'hindi', 'tamil', 'sinhala']
    
    print("Testing Subtitle API Integration")
    print("=" * 50)
    
    for movie in test_movies:
        print(f"\nTesting: {movie}")
        print("-" * 30)
        
        for language in test_languages[:3]:  # Test first 3 languages for each movie
            try:
                print(f"  Language: {language}")
                
                # Search for subtitles
                subtitles = await real_subtitle_handler.search_subtitles(movie, language)
                
                if subtitles:
                    print(f"    Found {len(subtitles)} subtitle(s)")
                    subtitle = subtitles[0]
                    print(f"    Source: {subtitle['source']}")
                    print(f"    Has download URL: {'Yes' if subtitle.get('download_url') else 'No'}")
                    
                    # Test download
                    content = await real_subtitle_handler.download_subtitle(subtitle)
                    if content:
                        size_kb = len(content) / 1024
                        print(f"    Downloaded: {size_kb:.1f} KB")
                        
                        # Check if it's valid SRT format
                        text = content.decode('utf-8', errors='ignore')
                        if '00:00:' in text and '-->' in text:
                            print(f"    Valid SRT format")
                        else:
                            print(f"    Generated content (not API)")
                    else:
                        print(f"    Download failed")
                else:
                    print(f"    No subtitles found")
                    
            except Exception as e:
                print(f"    Error: {e}")
    
    print("\n" + "=" * 50)
    print("API Test Summary:")
    print("OpenSubtitles: Web scraping approach")
    print("Subscene: HTML parsing approach")  
    print("YifySubtitles: JSON API approach")
    print("SubDB: Hash-based approach")
    print("Quality fallback: Multi-language templates")
    
    # Close session
    await real_subtitle_handler.close_session()
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_subtitle_apis())