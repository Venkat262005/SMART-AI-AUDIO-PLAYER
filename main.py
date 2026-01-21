import os
import requests
import yt_dlp
from dotenv import load_dotenv
import random
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ================= CONFIG =================
load_dotenv()
MAX_RETRIES = 3
DEFAULT_API_KEY = "20cd0409349298b3dd45fa02799329de"

# ================= GET CITY COORDS =================
def get_city_coordinates(city_name):
    api_key = os.getenv("OPENWEATHER_API_KEY") or DEFAULT_API_KEY
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={api_key}"

    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        if not data:
            return None
        return data[0]['lat'], data[0]['lon'], data[0]['name'], data[0].get('country', '')
    except:
        # FALLBACK: If API fails (e.g. invalid key), return dummy coords to allow app to proceed
        print("⚠️ Weather API Error. Using Mock Coordinates.")
        return 0, 0, city_name, "Mockland"

# ================= GET WEATHER =================
def get_weather(lat, lon, city_name):
    api_key = os.getenv("OPENWEATHER_API_KEY") or DEFAULT_API_KEY
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "main": data["weather"][0]["main"].lower(),
            "description": data["weather"][0]["description"].lower(),
            "temperature": data["main"]["temp"]
        }
    except:
        # FALLBACK: Return dummy weather
        print("⚠️ Weather API Error. Using Mock Weather.")
        return {
            "main": "clear",
            "description": "clear sky (mock data)",
            "temperature": 25.0
        }

# ================= WEATHER QUERIES =================
def get_weather_query(weather):
    if not weather:
        return ""

    w = weather["main"]

    choices = {
        "rain": ["rainy day", "rain vibes", "monsoon mood"],
        "clouds": ["cloudy day", "moody sky", "chill clouds"],
        "clear": ["sunny day", "bright mood", "happy sunshine"],
        "fog": ["foggy morning", "fog calm"],
        "mist": ["misty morning", "mist calm"],
        "snow": ["snow day", "winter calm"],
        "haze": ["haze calm", "hazy vibes"]
    }

    if w in choices:
        return random.choice(choices[w])
    return ""

# ================= YOUTUBE RANDOM FETCH =================
# ================= AI RECOMMENDATIONS =================
def get_ai_song_recommendations(weather, mood, language, content_type, city_name):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Google API Key missing")
    try:
        # Use a widely available model
        llm = ChatGoogleGenerativeAI(model="gemini-flash-latest", google_api_key=api_key)

        template = """
        You are a smart music DJ. Suggest 5 specific songs based on the following context:
        - Weather: {weather}
        - Mood: {mood}
        - Language: {language}
        - Content Type: {content_type}
        - City/Location: {city}

        Return ONLY a list of 5 song titles with their artist names, separated by commas. 
        Do not number them. Do not add quotes. 
        Example: Song1 by Artist1, Song2 by Artist2, Song3 by Artist3
        """

        prompt = PromptTemplate(
            input_variables=["weather", "mood", "language", "content_type", "city"],
            template=template
        )

        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        
        # Safe defaults if None
        response = chain.invoke({
            "weather": weather.get("description", "unknown") if weather else "unknown",
            "mood": mood,
            "language": language,
            "content_type": content_type,
            "city": city_name
        })

        # Process response
        songs = [s.strip() for s in response.split(',')]
        return songs[:5] # Ensure max 5

    except Exception as e:
        print("❌ AI Error:", e)
        return []

# ================= YOUTUBE SEARCH =================
def search_youtube(query, limit=10):
    if not query:
        print("❌ Empty search query")
        return []

    for attempt in range(MAX_RETRIES):
        try:
            print(f"🔍 Searching YouTube: {query}")

            ydl_opts = {
                'format': 'bestaudio/best',
                'default_search': f'ytsearch{limit}',
                'quiet': True,
                'extract_flat': True,  # MUCH FASTER: Doesn't download video details, just metadata
                'noplaylist': True
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
                if not info.get("entries"):
                    print("❌ No results")
                    return []

                results = []
                for video in info["entries"]:
                    results.append({
                        "title": video.get("title", "Unknown Title"),
                        "link": video.get("url"), # In flat mode, 'url' is the webpage link (e.g. https://www.youtube.com/watch?v=...)
                        "id": video.get("id")
                    })
                return results

        except Exception as e:
            print("❌ Error:", e)
    return []

