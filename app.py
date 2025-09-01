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
from config.settings import SUPPORTED_IMAGE_FORMATS, MAX_FILE_SIZE


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


def validate_image_upload(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded image file"""
    if not uploaded_file:
        return False, "No file uploaded"
    
    # Check file size
    if uploaded_file.size > MAX_FILE_SIZE:
        return False, f"File too large. Maximum: {MAX_FILE_SIZE/(1024*1024):.0f}MB"
    
    # Check file extension
    file_ext = uploaded_file.name.split('.')[-1].lower() if '.' in uploaded_file.name else ''
    if file_ext not in SUPPORTED_IMAGE_FORMATS:
        return False, f"Unsupported format. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}"
    
    # Try to open as image
    try:
        image_data = uploaded_file.getvalue()
        Image.open(io.BytesIO(image_data))
        return True, "Valid image"
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"
    
    return True, "Valid"


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
        
        # Show upload guidelines
        with st.expander("📋 Upload Guidelines", expanded=False):
            st.markdown(f"""
            **Image Requirements:**
            - **Formats**: {', '.join(SUPPORTED_IMAGE_FORMATS)}
            - **Max Size**: {MAX_FILE_SIZE/(1024*1024):.0f}MB
            - **Content**: Clear images related to your dialect word
            
            **Tips for better uploads:**
            - Use descriptive titles for your dialect words
            - Provide accurate location information
            - Choose appropriate language and release rights
            """)

        uploaded_image = st.file_uploader(
            "Upload an image...", 
            type=SUPPORTED_IMAGE_FORMATS,
            help=f"Supported formats: {', '.join(SUPPORTED_IMAGE_FORMATS)}. Max size: {MAX_FILE_SIZE/(1024*1024):.0f}MB"
        )
        dialect_word = st.text_input(
            "What is this called in your dialect?", placeholder="e.g., Cycle, Baingan"
        )
        location_text = st.text_input(
            "Enter your city/town:", placeholder="e.g., Hyderabad"
        )
        
        # Language selection
        languages = [
            "hindi", "bengali", "telugu", "marathi", "tamil", "gujarati", "urdu",
            "kannada", "odia", "punjabi", "malayalam", "assamese", "maithili",
            "santali", "kashmiri", "nepali", "konkani", "sindhi", "dogri", "manipuri",
            "bodo", "sanskrit", "english"
        ]
        selected_language = st.selectbox("Language", languages, index=0)
        
        # Show image validation status
        if uploaded_image:
            is_valid, message = validate_image_upload(uploaded_image)
            if is_valid:
                st.success(f"✅ {message}")
                # Show image preview
                image = Image.open(uploaded_image)
                st.image(image, caption=f"Preview: {uploaded_image.name}", width=300)
            else:
                st.error(f"❌ {message}")

        # Release rights selection with help
        release_options = {
            "family_or_friend": "Family or Friend",
            "creator": "Creator", 
            "public_domain": "Public Domain",
            "creative_commons": "Creative Commons"
        }
        release_rights = st.selectbox(
            "Release Rights", 
            options=list(release_options.keys()),
            format_func=lambda x: release_options[x],
            index=0,
            help="Choose how others can use your contribution"
        )

        # Categories section
        st.subheader("📂 Categories")
        if api_auth_ui.api_auth.is_authenticated():
            categories = api_categories.get_categories_cached()
            if categories:
                category_options = {cat.get("id", cat.get("category_id")): cat.get("name", "Unnamed Category") for cat in categories}
                selected_category = st.selectbox(
                    "Select Category",
                    options=list(category_options.keys()),
                    format_func=lambda x: category_options.get(x, "Unknown"),
                    index=0 if category_options else None,
                    help="Choose the most appropriate category for your dialect word"
                st.info(f"Selected: {category_options.get(selected_category, 'None')}")
            else:
                st.warning("⚠️ No categories available. A default category will be used.")
                selected_category = None
        else:
            st.info("🔐 Please login to view categories")
            selected_category = None

        if st.button("Put my word on the map!", use_container_width=True):
            if uploaded_image and dialect_word and location_text:
                if not api_auth_ui.api_auth.is_authenticated():
                    st.error("Please login to submit records to the API")
                    return
                
                # Validate image size
                image_data = uploaded_image.getvalue()
                if len(image_data) > MAX_FILE_SIZE:
                    st.error(f"Image too large! Maximum size: {MAX_FILE_SIZE/(1024*1024):.0f}MB")
                    return
                
                # Validate image format
                file_ext = uploaded_image.name.split('.')[-1].lower() if '.' in uploaded_image.name else 'jpg'
                if file_ext not in SUPPORTED_IMAGE_FORMATS:
                    st.error(f"Unsupported format '{file_ext}'. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}")
                    return
                
                lat, lon = geocode_location(location_text)

                if lat and lon:
                    with st.spinner("Adding your word to the map..."):
                        record_id = api_records.add_record_to_api(
                            dialect_word=dialect_word,
                            location_text=location_text,
                            image_data=image_data,
                            latitude=lat,
                            longitude=lon,
                            language=selected_language,
                            release_rights=release_rights
                        )
                        
                        if record_id:
                            st.success(f"✅ Your word '{dialect_word}' has been added to your map!")
                            st.info(f"Record ID: {record_id}")
                            st.balloons()  # Celebration animation
                            # Clear the form by rerunning
                            st.rerun()
                        else:
                            st.error("❌ Failed to add record. Please check the error messages above.")
                            st.info("💡 Try checking your internet connection and login status.")
                else:
                    st.error("Could not geocode location. Please check the location name.")
            else:
                missing_fields = []
                if not uploaded_image:
                    missing_fields.append("image")
                if not dialect_word:
                    missing_fields.append("dialect word")
                if not location_text:
                    missing_fields.append("location")
                
                st.warning(f"⚠️ Please provide: {', '.join(missing_fields)}")

                # Show helpful tips for missing fields
                if "image" in missing_fields:
                    st.info("💡 Upload a clear image that represents your dialect word")
                if "dialect word" in missing_fields:
                    st.info("💡 Enter the word or phrase in your local dialect")
                if "location" in missing_fields:
                    st.info("💡 Enter your city, village, or region name")
                    
        st.markdown("---")
        st.info("🔒 **Privacy Note:** Your uploaded records are private to your account and can only be viewed by you when logged in.")

        st.markdown("---")
        st.header("📊 Project Stats")
        
        if api_auth_ui.api_auth.is_authenticated():
            with st.spinner("Loading your statistics..."):
                records = api_records.get_user_records_cached()
                total_records = len(records)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📝 Total Records", total_records)
                with col2:
                    image_records = len([r for r in records if r.get("media_type") == "image"])
                    st.metric("🖼️ Images", image_records)
                with col3:
                    languages = set(r.get("language", "unknown") for r in records)
                    st.metric("🗣️ Languages", len(languages))
                with col4:
                    verified_records = len([r for r in records if r.get("reviewed")])
                    st.metric("✅ Verified", verified_records)
                    
                # Show recent activity if available
                if records:
                    st.subheader("🕒 Your Recent Activity")
                    recent_records = sorted(records, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
                    for record in recent_records:
                        status_icon = "✅" if record.get("reviewed") else "⏳"
                        st.write(f"• {status_icon} {record.get('title', 'Untitled')} - {record.get('language', 'Unknown')}")
                else:
                    st.info("No records yet. Upload your first dialect word to get started!")

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
            if categories and len(categories) > 1:  # More than just "Select a category"
                category_names = [cat[0] for cat in categories]
                category_ids = [cat[1] for cat in categories]
                
                selected_category_filter_name = st.selectbox(
                    "Filter by Category:",
                    ["All Categories"] + category_names[1:],  # Skip "Select a category"
                    index=0
                )
                
                if selected_category_filter_name != "All Categories":
                    selected_category_filter = category_ids[category_names.index(selected_category_filter_name)]
        else:
            st.selectbox(
                "Filter by Category:",
                ["Login to view categories"],
                index=0,
                disabled=True
            )

    # Get user's records from API
    if api_auth_ui.api_auth.is_authenticated():
        try:
            records = api_records.get_user_records_for_map()
            filtered_records = records
        except Exception as e:
            st.warning("⚠️ API temporarily unavailable.")
            records = []
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

    tab1, tab2, tab3 = st.tabs(["🗺️ Your Dialect Map", "🖼️ Your Gallery", "🚀 API Mode"])

    with tab1:
        st.subheader("Your Dialect Contributions Map")
        
        if api_auth_ui.api_auth.is_authenticated():
            # Filter records with valid coordinates
            map_data = [
                record for record in filtered_records
                if record.get('latitude') and record.get('longitude')
            ]

            if map_data:
                # Center map on user's records
                avg_lat = sum(r['latitude'] for r in map_data) / len(map_data)
                avg_lng = sum(r['longitude'] for r in map_data) / len(map_data)
                
                m = folium.Map(
                    location=[avg_lat, avg_lng], zoom_start=6, tiles="CartoDB positron"
                )

                heat_data = [
                    [record["latitude"], record["longitude"]] for record in map_data
                ]
                HeatMap(heat_data, radius=15).add_to(
                    folium.FeatureGroup(name="Your Contributions Heatmap").add_to(m)
                )

                marker_cluster = MarkerCluster(name="Your Dialect Words").add_to(m)
                for record in map_data:
                    image_data = api_records.get_image_from_api(record["id"])
                    if image_data:
                        try:
                            image_format = get_image_format(image_data)
                            encoded = base64.b64encode(image_data).decode()
                            status_icon = "✅" if record.get("is_verified") else "⏳"
                            html = f'<img src="data:image/{image_format};base64,{encoded}" width="150"><br><b>{record["dialect_word"]}</b><br>{status_icon} {"Verified" if record.get("is_verified") else "Pending Review"}'
                        except Exception:
                            html = f'<b>{record["dialect_word"]}</b><br><i>Image unavailable</i>'
                    else:
                        status_icon = "✅" if record.get("is_verified") else "⏳"
                        html = f'<b>{record["dialect_word"]}</b><br>{status_icon} {"Verified" if record.get("is_verified") else "Pending Review"}<br><i>Image unavailable</i>'

                    popup = folium.Popup(html, max_width=200)

                    # Different icons for verified vs pending
                    icon_color = "🟢" if record.get("is_verified") else "🟡"
                    icon = folium.DivIcon(
                        html=f'<div style="font-size: 24px;">{icon_color}</div>',
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
                
                # Show summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📍 Your Locations", len(map_data))
                with col2:
                    verified_count = len([r for r in map_data if r.get("is_verified")])
                    st.metric("✅ Verified", verified_count)
                with col3:
                    pending_count = len(map_data) - verified_count
                    st.metric("⏳ Pending", pending_count)
            else:
                st.info(
                    "🗺️ Your map is empty! Upload your first dialect word to see it appear here."
                )
                st.markdown("**Get started:**")
                st.markdown("1. 📸 Upload an image in the sidebar")
                st.markdown("2. 📝 Enter your dialect word")
                st.markdown("3. 📍 Add your location")
                st.markdown("4. 🚀 Click 'Put my word on the map!'")
        else:
            st.info("🔐 Please login to view your dialect map")

    with tab2:
        st.subheader("Your Dialect Gallery")
        
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

                cols = st.columns(3)  # Changed to 3 columns for better display
                for i, record in enumerate(paginated_records):
                    with cols[i % 3]:
                        # Show verification status
                        status_badge = "✅ Verified" if record.get("is_verified") else "⏳ Pending Review"
                        
                        image_data = api_records.get_image_from_api(record["id"])
                        if image_data:
                            try:
                                image = Image.open(io.BytesIO(image_data))
                                st.image(
                                    image,
                                    caption=f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')}",
                                    use_container_width=True,
                                )
                                st.caption(f"{status_badge} • {record.get('language', 'Unknown')}")
                            except (IOError, TypeError, AttributeError):
                                st.info(f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')} (image unavailable)")
                                st.caption(status_badge)
                        else:
                            st.info(f"'{record['dialect_word']}' from {record.get('location_text', 'Unknown Location')} (image unavailable)")
                            st.caption(status_badge)
                            
                        # Show additional details in expander
                        with st.expander("Details"):
                            st.write(f"**Created:** {record.get('created_at', 'Unknown')[:10]}")
                            st.write(f"**Language:** {record.get('language', 'Unknown')}")
                            st.write(f"**Status:** {record.get('status', 'Unknown')}")
                            if record.get('file_size'):
                                st.write(f"**File Size:** {record.get('file_size')} bytes")
            else:
                st.info("🖼️ Your gallery is empty! Upload some dialect words to see them here.")
                st.markdown("**Your contributions will appear here once uploaded:**")
                st.markdown("• 📸 Images with dialect words")
                st.markdown("• ✅ Verification status")
                st.markdown("• 📍 Location information")
                st.markdown("• 🗣️ Language details")
        else:
            st.info("🔐 Please login to view your gallery")

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
        st.markdown("• 📤 Submit your dialect records to the centralized database")
        st.markdown("• 🗺️ View your contributions on the map")
        st.markdown("• 📊 Track your upload statistics and verification status")
        st.markdown("• 🔍 Manage your records and categories")
        
        st.info("ℹ️ **Note:** With Bearer token authentication, you can only view and manage your own records for privacy and security.")
        
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
                recent_records = sorted(user_records, key=lambda x: x.get('created_at', ''), reverse=True)[:5]
                
                for record in recent_records:
                    status_icon = "✅" if record.get('reviewed') else "⏳"
                    with st.expander(f"{status_icon} '{record.get('title', 'Untitled')}' - {record.get('created_at', 'Unknown date')[:10]}"):
                        st.write(f"**Status:** {'✅ Verified' if record.get('reviewed') else '⏳ Pending Review'}")
                        st.write(f"**Language:** {record.get('language', 'Unknown')}")
                        st.write(f"**Media Type:** {record.get('media_type', 'Unknown')}")
                        if record.get('location'):
                            st.write(f"**Location:** {record['location'].get('latitude', 'N/A')}, {record['location'].get('longitude', 'N/A')}")
                        st.write(f"**Record ID:** {record.get('uid', 'N/A')}")
            else:
                st.info("No contributions yet. Upload your first dialect word!")
            
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
