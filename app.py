import streamlit as st
import pandas as pd
import numpy as np
import database as db
from geopy.geocoders import Nominatim
import io
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
import base64
import random

# --- Caching ---
@st.cache_resource
def get_geolocator():
    """Get a cached geolocator object."""
    return Nominatim(user_agent="dialect_map_app")

@st.cache_data
def geocode_location(location_name):
    """Geocode a location name to get latitude and longitude."""
    geolocator = get_geolocator()
    try:
        location = geolocator.geocode(location_name, country_codes="IN")
        if location:
            return location.latitude, location.longitude
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None, None

@st.cache_resource
def get_db_connection():
    """Get a cached database connection."""
    return db.create_connection()

@st.cache_data(ttl=300)
def get_all_submissions_cached():
    """Get all submissions from the database (cached)."""
    conn = get_db_connection()
    return db.get_all_submissions(conn)

@st.cache_data(ttl=300)
def get_image_cached(submission_id):
    """Get an image from the database by ID (cached)."""
    conn = get_db_connection()
    return db.get_image(conn, submission_id)

@st.cache_data(ttl=300)
def get_random_submission_cached():
    """Get a random submission from the database (cached)."""
    conn = get_db_connection()
    return db.get_random_submission(conn)

def get_image_format(image_data):
    """Determine the image format from its raw data."""
    try:
        image = Image.open(io.BytesIO(image_data))
        return image.format.lower()
    except (IOError, TypeError):
        return "png" # Default to png if format is not identifiable

def main():
    st.set_page_config(
        page_title="Desi Dialect Map",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    db.initialize_database()
    conn = get_db_connection()

    st.title("Desi Dialect Map 🗺️📍")
    st.markdown("A Summer of AI 2025 Project by Team **'ahjin Guild'**")

    # --- Sidebar ---
    with st.sidebar:
        st.header("Contribute Your Dialect!")
        st.markdown("Help us build a living map of India's languages.")
        
        uploaded_image = st.file_uploader("Upload an image...", type=["jpg", "jpeg", "png"])
        dialect_word = st.text_input("What is this called in your dialect?", placeholder="e.g., Cycle, Baingan")
        location_text = st.text_input("Enter your city/town:", placeholder="e.g., Hyderabad")
        
        if st.button("Put my word on the map!", use_container_width=True):
            if uploaded_image and dialect_word and location_text:
                image_data = uploaded_image.getvalue()
                lat, lon = geocode_location(location_text)
                
                submission_id = db.add_submission(conn, dialect_word, location_text, image_data)
                
                if lat and lon:
                    c = conn.cursor()
                    c.execute("UPDATE submissions SET latitude=?, longitude=? WHERE id=?", (lat, lon, submission_id))
                    conn.commit()

                st.success("Thank you for your contribution!")
                st.cache_data.clear()
                st.rerun()
            else:
                st.warning("Please upload an image and fill in all fields.")
        
        st.markdown("---")
        st.header("Project Stats")
        submissions_df = get_all_submissions_cached()
        st.metric("Total Contributions", f"{len(submissions_df)}")
        st.metric("Unique Locations Mapped", f"{submissions_df['location_text'].nunique()}")

        st.markdown("---")
        st.header("Submission of the Day")
        random_submission = get_random_submission_cached()
        if random_submission:
            sub_id, sub_word, sub_loc = random_submission
            st.image(get_image_cached(sub_id), caption=f"'{sub_word}' from {sub_loc}", use_container_width=True)

    # --- Main Page ---
    tab1, tab2 = st.tabs(["🗺️ Interactive Map", "🖼️ Community Gallery"])

    with tab1:
        st.subheader("A Living Map of India's Languages")
        map_data = submissions_df.dropna(subset=['latitude', 'longitude'])

        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron")

        if not map_data.empty:
            heat_data = [[row['latitude'], row['longitude']] for _, row in map_data.iterrows()]
            HeatMap(heat_data, radius=15).add_to(folium.FeatureGroup(name="Heatmap").add_to(m))

            marker_cluster = MarkerCluster(name="Submissions").add_to(m)
            for _, row in map_data.iterrows():
                image_data = get_image_cached(row['id'])
                image_format = get_image_format(image_data)
                encoded = base64.b64encode(image_data).decode()
                html = f'<img src="data:image/{image_format};base64,{encoded}" width="150"><br><b>{row["dialect_word"]}</b>'
                
                iframe = folium.IFrame(html, width=200, height=200)
                popup = folium.Popup(iframe, max_width=2650)
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup,
                    tooltip=f"{row['dialect_word']} ({row['location_text']})"
                ).add_to(marker_cluster)
            
            folium.LayerControl().add_to(m)
            st_folium(m, width='100%', height=600, returned_objects=[])
        else:
            st.info("No submissions with location data yet. Be the first to contribute!")

    with tab2:
        st.subheader("Community Gallery")
        if not submissions_df.empty:
            search_query = st.text_input("Search by dialect word:")
            filtered_df = submissions_df[submissions_df['dialect_word'].str.contains(search_query, case=False)]

            items_per_page = 12
            total_items = len(filtered_df)
            total_pages = (total_items // items_per_page) + (1 if total_items % items_per_page > 0 else 0)
            
            page_number = st.number_input('Page', min_value=1, max_value=max(1, total_pages), value=1, step=1)
            
            start_index = (page_number - 1) * items_per_page
            end_index = start_index + items_per_page
            
            paginated_df = filtered_df.iloc[start_index:end_index]

            cols = st.columns(4)
            for i, row in paginated_df.iterrows():
                with cols[i % 4]:
                    try:
                        image = Image.open(io.BytesIO(get_image_cached(row['id'])))
                        st.image(image, caption=f"'{row['dialect_word']}' from {row['location_text']}", use_container_width=True)
                    except (IOError, TypeError):
                        st.error("Could not display image.")
        else:
            st.info("The gallery is empty. Upload an image to get started!")

if __name__ == "__main__":
    main()
