# 🎵 Smart AI Audio Player

A smart music player that generates personalized playlists based on your **Location**, **Weather**, and **Mood** using **Google Gemini AI**. The app identifies the vibe and fetches specific songs from YouTube to create a seamless listening experience.

## ✨ Features
- **AI-Powered Recommendations**: Uses Google Gemini Pro to suggest specific songs tailored to your context.
- **Weather Integration**: Automatically detects weather (via OpenWeatherMap) to match the music vibe (e.g., "Rainy Day" -> "Cozy Acoustic").
- **Smart Search**: Searches for the exact recommended songs on YouTube.
- **Interactive Player**: 
    - Auto-generated YouTube Playlist.
    - Individual track controls (Next/Previous).
    - Direct track selection.

## 🛠️ Installation

1.  **Clone/Download** the repository.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## ⚙️ Configuration

Create a `.env` file in the project root directory and add your API keys:

```env
# Get from https://openweathermap.org/api
OPENWEATHER_API_KEY=your_openweather_key_here

# Get from https://aistudio.google.com/
GOOGLE_API_KEY=your_gemini_key_here
```

> **Note**: If you don't provide a valid OpenWeather key, the app will use "Mock Weather" (Clear Sky) so you can still use the music features.

## 🚀 How to Run

Run the Streamlit application:

```bash
streamlit run app.py
```

## 📂 Project Structure
- `app.py`: Frontend interface (Streamlit).
- `main.py`: Backend logic for Weather API, Gemini AI, and YouTube Search.
- `requirements.txt`: Python dependencies.

### 🧪 Testing Files (Optional)
The following files were created for debugging purposes and **can be safely deleted** if you don't need them:
- `test_backend.py`: Verifies API connections without running the UI.
- `test_langchain.py`: Tests specific AI model connectivity.
- `debug_apis.py`: Low-level API connection test.
