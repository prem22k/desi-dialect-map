import streamlit as st
import pandas as pd
import numpy as np
import database as db
from geopy.geocoders import Nominatim
import io
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import base64

# Initialize geolocator
geolocator = Nominatim(user_agent="dialect_map_app")

def geocode_location(location_name):
    """Geocode a location name to get latitude and longitude."""
    try:
        location = geolocator.geocode(location_name, country_codes="IN")
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        st.error(f"Geocoding error: {e}")
    return None, None

def main():
    st.set_page_config(
        page_title="Desi Dialect Map",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize the database
    db.initialize_database()
    conn = db.create_connection()

    st.title("Desi Dialect Map 🗺️📍")
    st.markdown("### A Summer of AI 2025 Project by Team 'ahjin Guild'")

    with st.sidebar:
        st.header("Contribute Your Dialect!")
        st.markdown("---")
        
        # 1. User Input
        st.subheader("Upload an image and describe it:")
        uploaded_image = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
        dialect_word = st.text_input("What is this called in your dialect?", placeholder="e.g., Cycle, Baingan, Jalebi")
        location_text = st.text_input("Enter your city/town:", placeholder="e.g., Hyderabad")
        
        # 2. Submit Button
        if st.button("Put my word on the map!"):
            if uploaded_image and dialect_word and location_text:
                image_data = uploaded_image.getvalue()
                
                # Geocode the location
                lat, lon = geocode_location(location_text)
                
                submission_id = db.add_submission(conn, dialect_word, location_text, image_data)
                
                # Update the submission with coordinates if found
                if lat and lon:
                    c = conn.cursor()
                    c.execute("UPDATE submissions SET latitude=?, longitude=? WHERE id=?", (lat, lon, submission_id))
                    conn.commit()

                st.success(f"Thank you! Your contribution has been added.")
                st.rerun()
            else:
                st.warning("Please upload an image and fill in all fields.")

    # Main page content
    st.markdown("""
    Welcome to the **Desi Dialect Map**! This project is a fun, interactive application 
    designed to create a crowdsourced, living map of India's incredible linguistic diversity. 
    Explore the map and see what words others have shared!
    """)

    # 3. Interactive Map
    st.markdown("---")
    st.subheader("A Living Map of India's Languages")
    
    submissions_df = db.get_all_submissions(conn)
    map_data = submissions_df.dropna(subset=['latitude', 'longitude'])

    # Create a Folium map centered on India
    m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)

    if not map_data.empty:
        # Heatmap Layer
        heat_data = [[row['latitude'], row['longitude']] for index, row in map_data.iterrows()]
        HeatMap(heat_data).add_to(m)

        # Marker Layer
        for index, row in map_data.iterrows():
            # Prepare the image for the popup
            image = db.get_image(conn, row['id'])
            encoded = base64.b64encode(image).decode()
            html = f'<img src="data:image/png;base64,{encoded}" width="150"><br><b>{row["dialect_word"]}</b>'
            
            iframe = folium.IFrame(html, width=200, height=200)
            popup = folium.Popup(iframe, max_width=2650)
            
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=popup,
                tooltip=f"{row['dialect_word']} ({row['location_text']})"
            ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Render the map
        st_folium(m, width='100%', height=500)
    else:
        st.info("No submissions with location data yet. Be the first to contribute!")

    # 4. Community Gallery
    st.markdown("---")
    st.subheader("Community Gallery")

    if not submissions_df.empty:
        # Create columns for the gallery
        cols = st.columns(4)
        for i, row in submissions_df.iterrows():
            with cols[i % 4]:
                try:
                    image = Image.open(io.BytesIO(db.get_image(conn, row['id'])))
                    st.image(image, caption=f"'{row['dialect_word']}' from {row['location_text']}", use_container_width=True)
                except (IOError, TypeError):
                    st.error("Could not display image.")
    else:
        st.info("The gallery is empty. Upload an image to get started!")

    conn.close()

if __name__ == "__main__":
    main()
