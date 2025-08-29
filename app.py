import streamlit as st
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
import io
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
import base64
import random
import api_auth_ui
import api_records
import api_categories


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


def get_image_format(image_data):
    """Determine the image format from its raw data."""
    try:
        if not image_data:
            return "png"
        image = Image.open(io.BytesIO(image_data))
        if image.format:
            return image.format.lower()
        else:
            return "png"  # Default to png if format is not identifiable
    except (IOError, TypeError, AttributeError):
        return "png"  # Default to png if format is not identifiable


def main():
    st.set_page_config(
        page_title="Desi Dialect Map",
        page_icon="🗺️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Initialize API authentication
    api_auth_ui.init_session_state()
    api_auth_ui.load_auth_from_session()

    st.title("Desi Dialect Map 🗺️📍")
    st.markdown("A collaborative project by **Team ahjin Guild**")
    st.markdown("*Sreenidhi Institute of Science and Technology*")
    
    # API Integration Notice
    st.info("🚀 **Indic Corpus Collections API Integration** - Connect to contribute to the official corpus database.")
    
    # Show demo mode indicator if API is not working
    if api_auth_ui.api_auth.is_authenticated():
        try:
            test_records = api_records.api_records.get_records(limit=1)
            if test_records is None:
                st.warning("⚠️ **Demo Mode Active** - API connection issues detected. Showing demo data.")
        except Exception:
            st.warning("⚠️ **Demo Mode Active** - API connection failed. Showing demo data.")

    # --- Sidebar ---
    with st.sidebar:
        # Show API Authentication
        api_auth_ui.show_api_auth_sidebar()
        
        st.markdown("---")
        st.header("Contribute Your Dialect!")
        st.markdown("Help us build a living map of India's languages.")

        uploaded_image = st.file_uploader(
            "Upload an image...", type=["jpg", "jpeg", "png"]
        )
        dialect_word = st.text_input(
            "What is this called in your dialect?", placeholder="e.g., Cycle, Baingan"
        )
        location_text = st.text_input(
            "Enter your city/town:", placeholder="e.g., Hyderabad"
        )
        
        # Category selection
        selected_category = None
        if api_auth_ui.api_auth.is_authenticated():
            categories = api_categories.get_category_options()
            category_names = [cat[0] for cat in categories]
            category_ids = [cat[1] for cat in categories]
            
            selected_category_name = st.selectbox(
                "Choose a category:",
                category_names,
                index=0
            )
            
            if selected_category_name != "Select a category":
                selected_category = category_ids[category_names.index(selected_category_name)]
        else:
            st.info("Please login to select categories")

        if st.button("Put my word on the map!", use_container_width=True):
            if uploaded_image and dialect_word and location_text:
                if not api_auth_ui.api_auth.is_authenticated():
                    st.error("Please login to submit records to the API")
                    return
                
                image_data = uploaded_image.getvalue()
                lat, lon = geocode_location(location_text)

                if lat and lon:
                    submission_id = api_records.add_record_to_api(
                        dialect_word, location_text, image_data, lat, lon, selected_category
                    )
                    
                    if submission_id:
                        st.success("Thank you for your contribution!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to submit record. Please try again.")
                else:
                    st.error("Could not geocode location. Please check the location name.")
            else:
                st.warning("Please upload an image and fill in all fields.")

        st.markdown("---")
        st.header("Project Stats")
        
        if api_auth_ui.api_auth.is_authenticated():
            records = api_records.get_records_for_map()
            st.metric("Total Contributions", f"{len(records)}")
            
            if records:
                unique_locations = len(set(record.get('location_text', '') for record in records))
                st.metric("Unique Locations Mapped", f"{unique_locations}")
            else:
                st.metric("Unique Locations Mapped", "0")
        else:
            st.metric("Total Contributions", "Login to view")
            st.metric("Unique Locations Mapped", "Login to view")

        st.markdown("---")
        st.header("Export Data")

        if api_auth_ui.api_auth.is_authenticated():
            records = api_records.get_records_for_map()
            if records:
                # Convert records to DataFrame for CSV export
                df = pd.DataFrame(records)
                csv = df.to_csv(index=False).encode("utf-8")
                
                st.download_button(
                    label="Download data as CSV",
                    data=csv,
                    file_name="dialect_map_submissions.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
            else:
                st.info("No records available for download")
        else:
            st.info("Login to download data")

        st.markdown("---")
        st.header("Submission of the Day")
        
        if api_auth_ui.api_auth.is_authenticated():
            random_record = api_records.get_random_record()
            if random_record:
                sub_id = random_record.get('id')
                sub_word = random_record.get('dialect_word')
                sub_loc = random_record.get('location_text')
                
                image_data = api_records.get_image_from_api(sub_id)
                if image_data:
                    try:
                        st.image(
                            image_data,
                            caption=f"'{sub_word}' from {sub_loc}",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.info(f"'{sub_word}' from {sub_loc} (image unavailable)")
                else:
                    st.info(f"'{sub_word}' from {sub_loc} (image unavailable)")
            else:
                st.info("No submissions yet. Be the first to contribute!")
        else:
            st.info("Login to view submissions")

    # --- Main Page ---

    # --- Filtering ---
    states = [
        "All States",
        "Andaman and Nicobar Islands",
        "Andhra Pradesh",
        "Arunachal Pradesh",
        "Assam",
        "Bihar",
        "Chandigarh",
        "Chhattisgarh",
        "Dadra and Nagar Haveli and Daman and Diu",
        "Delhi",
        "Goa",
        "Gujarat",
        "Haryana",
        "Himachal Pradesh",
        "Jammu and Kashmir",
        "Jharkhand",
        "Karnataka",
        "Kerala",
        "Ladakh",
        "Lakshadweep",
        "Madhya Pradesh",
        "Maharashtra",
        "Manipur",
        "Meghalaya",
        "Mizoram",
        "Nagaland",
        "Odisha",
        "Puducherry",
        "Punjab",
        "Rajasthan",
        "Sikkim",
        "Tamil Nadu",
        "Telangana",
        "Tripura",
        "Uttar Pradesh",
        "Uttarakhand",
        "West Bengal",
    ]

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        search_query = st.text_input("Search by dialect word:", placeholder="Search...")
    with col2:
        state_filter = st.selectbox("Filter by State:", states)
    with col3:
        selected_category_filter = None
        if api_auth_ui.api_auth.is_authenticated():
            categories = api_categories.get_category_options()
            category_names = [cat[0] for cat in categories]
            category_ids = [cat[1] for cat in categories]
            
            selected_category_filter_name = st.selectbox(
                "Filter by Category:",
                ["All Categories"] + category_names[1:],  # Skip "Select a category"
                index=0
            )
            
            if selected_category_filter_name != "All Categories":
                selected_category_filter = category_ids[category_names.index(selected_category_filter_name)]

    # Get records from API
    if api_auth_ui.api_auth.is_authenticated():
        try:
            records = api_records.get_records_for_map()
            filtered_records = records
        except Exception as e:
            st.warning("⚠️ API temporarily unavailable. Showing demo data.")
            # Fallback to demo data when API is down
            records = [
                {
                    "id": "demo_1",
                    "dialect_word": "Baingan",
                    "location_text": "Hyderabad, Telangana",
                    "latitude": 17.3850,
                    "longitude": 78.4867,
                    "image_path": None,
                    "is_verified": True,
                    "user_id": "demo_user",
                    "created_at": "2025-01-01T00:00:00Z"
                },
                {
                    "id": "demo_2", 
                    "dialect_word": "Cycle",
                    "location_text": "Mumbai, Maharashtra",
                    "latitude": 19.0760,
                    "longitude": 72.8777,
                    "image_path": None,
                    "is_verified": True,
                    "user_id": "demo_user",
                    "created_at": "2025-01-01T00:00:00Z"
                }
            ]
            filtered_records = records
        
        # Apply search filter
        if search_query:
            filtered_records = [
                record for record in filtered_records
                if search_query.lower() in record.get('dialect_word', '').lower()
            ]
        
        # Apply state filter
        if state_filter != "All States":
            filtered_records = [
                record for record in filtered_records
                if state_filter.lower() in record.get('location_text', '').lower()
            ]
        
        # Apply category filter
        if selected_category_filter:
            # Note: Category filtering would need to be implemented based on API response structure
            st.info(f"Category filtering: {selected_category_filter}")
    else:
        filtered_records = []

    tab1, tab2, tab3 = st.tabs(["🗺️ Interactive Map", "🖼️ Community Gallery", "🚀 API Mode"])

    with tab1:
        st.subheader("A Living Map of India's Languages")
        
        if api_auth_ui.api_auth.is_authenticated():
            # Filter records with valid coordinates
            map_data = [
                record for record in filtered_records
                if record.get('latitude') and record.get('longitude')
            ]

            m = folium.Map(
                location=[20.5937, 78.9629], zoom_start=5, tiles="CartoDB positron"
            )

            if map_data:
                heat_data = [
                    [record["latitude"], record["longitude"]] for record in map_data
                ]
                HeatMap(heat_data, radius=15).add_to(
                    folium.FeatureGroup(name="Heatmap").add_to(m)
                )

                marker_cluster = MarkerCluster(name="Submissions").add_to(m)
                for record in map_data:
                    image_data = api_records.get_image_from_api(record["id"])
                    if image_data:
                        try:
                            image_format = get_image_format(image_data)
                            encoded = base64.b64encode(image_data).decode()
                            html = f'<img src="data:image/{image_format};base64,{encoded}" width="150"><br><b>{record["dialect_word"]}</b>'
                        except Exception:
                            html = f'<b>{record["dialect_word"]}</b><br><i>Image unavailable</i>'
                    else:
                        html = f'<b>{record["dialect_word"]}</b><br><i>Image unavailable</i>'

                    popup = folium.Popup(html, max_width=200)

                    icon = folium.DivIcon(
                        html=f'<div style="font-size: 24px;">📍</div>',
                        icon_size=(30, 30),
                        icon_anchor=(15, 30),
                    )
                    
                    location_text = record.get("location_text", "Unknown Location")
                    folium.Marker(
                        location=[record["latitude"], record["longitude"]],
                        popup=popup,
                        tooltip=f"{record['dialect_word']} ({location_text})",
                        icon=icon,
                    ).add_to(marker_cluster)

                folium.LayerControl().add_to(m)
                st_folium(m, width="100%", height=700, returned_objects=[])
            else:
                st.info(
                    "No submissions match your criteria. Try a different filter or be the first to contribute!"
                )
        else:
            st.info("Please login to view the map")

    with tab2:
        st.subheader("Community Gallery")
        
        if api_auth_ui.api_auth.is_authenticated():
            if filtered_records:
                items_per_page = 12
                total_items = len(filtered_records)
                total_pages = (total_items // items_per_page) + (
                    1 if total_items % items_per_page > 0 else 0
                )

                page_number = st.number_input(
                    "Page",
                    min_value=1,
                    max_value=max(1, total_pages),
                    value=1,
                    step=1,
                    key="gallery_page",
                )

                start_index = (page_number - 1) * items_per_page
                end_index = start_index + items_per_page

                paginated_records = filtered_records[start_index:end_index]

                cols = st.columns(4)
                for i, record in enumerate(paginated_records):
                    with cols[i % 4]:
                        image_data = api_records.get_image_from_api(record["id"])
                        if image_data:
                            try:
                                image = Image.open(io.BytesIO(image_data))
                                st.image(
                                    image,
                                    caption=f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')}",
                                    use_container_width=True,
                                )
                            except (IOError, TypeError, AttributeError):
                                st.info(f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')} (image unavailable)")
                        else:
                            st.info(f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')} (image unavailable)")
            else:
                st.info("The gallery is empty or no submissions match your criteria.")
        else:
            st.info("Please login to view the gallery")

    with tab3:
        st.subheader("🚀 Indic Corpus Collections API")
        
        # API Status Check
        api_status = "🟢 Connected" if api_auth_ui.api_auth.is_authenticated() else "🔴 Disconnected"
        st.info(f"**API Status:** {api_status}")
        
        if api_auth_ui.api_auth.is_authenticated():
            try:
                # Test API connection
                test_records = api_records.api_records.get_records(limit=1)
                if test_records is not None:
                    st.success("✅ API connection successful")
                else:
                    st.warning("⚠️ API connection issues detected")
            except Exception as e:
                st.error(f"❌ API connection failed: {str(e)}")
                st.info("The app will continue with demo data until the API is restored.")
        
        st.markdown("Connect to the official Indic Corpus Collections API to:")
        st.markdown("• 📤 Submit dialect records to the centralized database")
        st.markdown("• 🗺️ Browse records from across India")
        st.markdown("• 📊 View analytics and user contributions")
        st.markdown("• 🔍 Search nearby records and filter by categories")
        
        api_auth_ui.main_api_interface()
        
        # Show API statistics
        if api_auth_ui.api_auth.is_authenticated():
            st.markdown("---")
            st.subheader("📊 API Statistics")
            
            # Get user's records
            user_id = None
            if api_auth_ui.api_auth.user_info:
                user_id = api_auth_ui.api_auth.user_info.get("user_id")
            
            user_records = []
            if user_id:
                user_records = api_records.api_records.get_records(
                    user_id=user_id,
                    limit=1000
                )
            
            # Get category statistics
            category_stats = api_categories.get_category_statistics()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Your Contributions", len(user_records))
            with col2:
                verified_count = len([r for r in user_records if r.get("reviewed", False)])
                st.metric("Verified Records", verified_count)
            with col3:
                pending_count = len([r for r in user_records if not r.get("reviewed", False)])
                st.metric("Pending Review", pending_count)
            with col4:
                st.metric("Categories", category_stats.get("published_categories", 0))
            
            # Show recent contributions
            if user_records:
                st.markdown("---")
                st.subheader("Your Recent Contributions")
                recent_records = user_records[:5]  # Show last 5
                
                for record in recent_records:
                    with st.expander(f"'{record.get('title', 'Untitled')}' - {record.get('created_at', 'Unknown date')[:10]}"):
                        st.write(f"**Status:** {'✅ Verified' if record.get('reviewed') else '⏳ Pending Review'}")
                        st.write(f"**Language:** {record.get('language', 'Unknown')}")
                        st.write(f"**Media Type:** {record.get('media_type', 'Unknown')}")
                        if record.get('location'):
                            st.write(f"**Location:** {record['location'].get('latitude', 'N/A')}, {record['location'].get('longitude', 'N/A')}")
            
            # Category Information
            st.markdown("---")
            st.subheader("🏷️ Available Categories")
            
            categories = api_categories.get_published_categories()
            if categories:
                for category in categories:
                    with st.expander(f"{category.get('title', 'Unknown')} - {category.get('description', 'No description')}"):
                        st.write(f"**ID:** {category.get('id', 'N/A')}")
                        st.write(f"**Name:** {category.get('name', 'N/A')}")
                        st.write(f"**Published:** {'✅ Yes' if category.get('published') else '❌ No'}")
                        st.write(f"**Rank:** {category.get('rank', 0)}")
            else:
                st.info("No categories available")


if __name__ == "__main__":
    main()
