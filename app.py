import streamlit as st
import main
import os

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Smart AI Audio Player",
    page_icon="🎵",
    layout="centered"
)


# ================= UI HEADER =================
st.title("🎵 Smart AI Audio Player")
st.markdown("Generates music playlist based on **Weather**, **Mood**, and **Location**.")

# ================= INITIALIZE STATE =================
if "playlist" not in st.session_state:
    st.session_state.playlist = []
if "current_song_index" not in st.session_state:
    st.session_state.current_song_index = 0

# ================= INPUTS =================
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        city = st.text_input("Enter City Name", placeholder="e.g., Hyderabad")
        language = st.selectbox("Select Language", ["Any", "Telugu", "Tamil", "Hindi", "English", "Kannada", "Malayalam"])
        mood = st.selectbox("Select Mood", ["Any", "Happy", "Sad", "Relax", "Study", "Devotional", "Motivational", "Sleep", "Focus"])

    with col2:
        weather_mode = st.radio("Weather Mode", ["Include Weather", "Ignore Weather"])
        content_type = st.selectbox("Content Type", ["Any", "Songs", "Motivational", "Stories", "Pravachanam", "Meditation", "Bhajans", "Podcast"])

# ================= LOGIC =================
if st.button("Generate Playlist 🎵", type="primary"):
    if not city.strip():
        st.warning("Please enter a city name.")
    else:
        status_text = st.empty()
        status_text.info("Fetching city data...")

        # 1. Get City Coords
        coords = main.get_city_coordinates(city)
        if not coords:
            status_text.error("City not found. Please try again.")
        else:
            lat, lon, city_name, country = coords
            
            # 2. Get Weather
            status_text.info(f"Fetching weather for {city_name}...")
            weather = main.get_weather(lat, lon, city_name)
            
            weather_desc = "Unknown"
            weather_temp = ""
            
            if weather:
                weather_desc = weather["description"].capitalize()
                weather_temp = f"{weather['temperature']}°C"
                st.success(f"📍 **{city_name}, {country}** | 🌤 {weather_desc} | 🌡 {weather_temp}")
            else:
                st.warning(f"📍 **{city_name}** | Weather data unavailable.")

            # 3. Get AI Recommendations
            st.divider()
            st.markdown("### 🤖 **AI DJ is thinking...**")
            
            # Check for API Key
            if not os.getenv("GOOGLE_API_KEY"):
                st.warning("⚠️ **Google API Key not found!** Please set `GOOGLE_API_KEY` in your `.env` file.")
                st.info("Falling back to basic search...")
                
                # FALLBACK logic (old way)
                query_parts = []
                if language != "Any": query_parts.append(language)
                if content_type != "Any": query_parts.append(content_type)
                else: query_parts.append("Songs")
                if mood != "Any": query_parts.append(mood)
                if weather_mode == "Include Weather" and weather:
                     w_query = main.get_weather_query(weather)
                     if w_query: query_parts.append(w_query)
                final_query = " ".join(query_parts)
                videos = main.search_youtube(final_query, limit=10)

            else:
                # 3. AI Suggestions
                with st.spinner("Asking Gemini for the best tracks..."):
                    suggested_songs = main.get_ai_song_recommendations(weather, mood, language, content_type, city_name)
                
                if suggested_songs:
                    st.success("✨ **AI Suggested Playlist:**")
                    for s in suggested_songs:
                        st.write(f"- 🎵 {s}")
                    
                    st.divider()
                    status_text.info("Finding these songs on YouTube...")
                    
                    # 4. Search via YouTube (One by one)
                    videos = []
                    progress_bar = st.progress(0)
                    
                    for idx, song in enumerate(suggested_songs):
                        # Search specific song, limit 1
                        results = main.search_youtube(song, limit=1)
                        if results:
                            videos.extend(results)
                        progress_bar.progress((idx + 1) / len(suggested_songs))
                        
                else:
                    st.error("AI couldn't generate suggestions. Trying fallback...")
                    videos = [] # Or define fallback here
            
            
            # 5. Store in Session State
            if videos:
                st.session_state.playlist = videos
                st.session_state.current_song_index = 0 # Reset
                status_text.success(f"🎉 Ready to play {len(videos)} tracks!")
            else:
                status_text.error("No videos found.")

# ================= PLAYER UI =================
if st.session_state.playlist:
    videos = st.session_state.playlist
    
    # --- AUTOPLAY PLAYLIST UI ---
    # 1. Extract Video IDs
    video_ids = [v['id'] for v in videos if v.get('id')]
    
    if video_ids:
        # Get Current Index
        current_index = st.session_state.current_song_index
        
        # Ensure index is within bounds (safety check)
        if current_index >= len(video_ids):
             current_index = 0
             st.session_state.current_song_index = 0

        # Current main video
        current_video_id = video_ids[current_index]
        
        # Playlist: All other videos (to keep them in queue)
        # Note: YouTube 'playlist' param takes comma separated IDs. 
        # We can pass ALL IDs. The 'autoplay=1' combined with path '/embed/ID' usually plays that ID first.
        playlist_str = ",".join(video_ids) 
        
        # 2. Construct Embed URL with Autoplay & Playlist
        embed_url = f"https://www.youtube.com/embed/{current_video_id}?playlist={playlist_str}&autoplay=1&loop=1"
        
        st.markdown(f"""
        <iframe width="100%" height="400" 
                src="{embed_url}" 
                title="YouTube video player" 
                frameborder="0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                allowfullscreen>
        </iframe>
        """, unsafe_allow_html=True)
        
        st.divider()

    # --- INDIVIDUAL SELECTION ---
    st.write("### 🎧 Now Playing Control")
    
    # Controls
    col_prev, col_curr, col_next = st.columns([1, 4, 1])
    
    with col_prev:
        if st.button("⬅️ Prev"):
            st.session_state.current_song_index = (st.session_state.current_song_index - 1) % len(videos)
            st.rerun()
    
    with col_next:
        if st.button("Next ➡️"):
            st.session_state.current_song_index = (st.session_state.current_song_index + 1) % len(videos)
            st.rerun()

    # Get Current Video
    current_video = videos[st.session_state.current_song_index]
    
    with col_curr:
         st.write(f"**Playing:** {current_video['title']}")
         st.video(current_video['link'])
    
    # Optional: Dropbox to jump
    video_options = [v['title'] for v in videos]
    selected_idx = st.selectbox("Jump to track:", range(len(video_options)), 
                                format_func=lambda x: video_options[x],
                                index=st.session_state.current_song_index)
    
    if selected_idx != st.session_state.current_song_index:
        st.session_state.current_song_index = selected_idx
        st.rerun()
