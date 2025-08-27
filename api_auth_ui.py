import streamlit as st
import api_client
from typing import Optional, Dict


def init_auth_session():
    """Initialize authentication session state"""
    if 'api_authenticated' not in st.session_state:
        st.session_state.api_authenticated = False
    if 'api_user_profile' not in st.session_state:
        st.session_state.api_user_profile = None
    if 'api_access_token' not in st.session_state:
        st.session_state.api_access_token = None


def api_login_form() -> bool:
    """Display API login form and handle authentication"""
    st.subheader("🔐 Login to Indic Corpus API")
    
    with st.form("api_login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_login = st.form_submit_button("Login", use_container_width=True)
        with col2:
            show_register = st.form_submit_button("New User? Register", use_container_width=True)
    
    if submit_login and username and password:
        with st.spinner("Logging in..."):
            if api_client.login(username, password):
                st.session_state.api_authenticated = True
                st.session_state.api_access_token = api_client.access_token
                
                # Get user profile
                profile = api_client.get_user_profile()
                if profile:
                    st.session_state.api_user_profile = profile
                
                st.success("✅ Successfully logged in to Indic Corpus API!")
                st.rerun()
            else:
                st.error("❌ Login failed. Please check your credentials.")
    
    if show_register:
        st.session_state.show_api_register = True
        st.rerun()
    
    return st.session_state.api_authenticated


def api_register_form() -> bool:
    """Display API registration form"""
    st.subheader("📝 Register for Indic Corpus API")
    
    with st.form("api_register_form"):
        username = st.text_input("Username", placeholder="Choose a username")
        email = st.text_input("Email", placeholder="Enter your email")
        phone = st.text_input("Phone (optional)", placeholder="Enter your phone number")
        password = st.text_input("Password", type="password", placeholder="Choose a password")
        confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submit_register = st.form_submit_button("Register", use_container_width=True)
        with col2:
            show_login = st.form_submit_button("Already have account? Login", use_container_width=True)
    
    if submit_register:
        if not all([username, email, password]):
            st.error("Please fill in all required fields.")
        elif password != confirm_password:
            st.error("Passwords do not match.")
        else:
            with st.spinner("Registering..."):
                if api_client.register_user(username, email, password, phone):
                    st.success("✅ Registration initiated! Please check your email/phone for OTP verification.")
                    st.info("After verifying OTP, you can login with your credentials.")
                    st.session_state.show_api_register = False
                    st.rerun()
                else:
                    st.error("❌ Registration failed. Please try again.")
    
    if show_login:
        st.session_state.show_api_register = False
        st.rerun()
    
    return False


def api_user_profile() -> Optional[Dict]:
    """Display user profile and logout option"""
    if not st.session_state.api_authenticated:
        return None
    
    profile = st.session_state.api_user_profile
    
    st.subheader("👤 API User Profile")
    
    if profile:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**Username:** {profile.get('username', 'N/A')}")
            st.write(f"**Email:** {profile.get('email', 'N/A')}")
            st.write(f"**User ID:** {profile.get('id', 'N/A')}")
            
            # Get user contributions
            contributions = api_client.get_user_contributions()
            if contributions:
                st.write(f"**Total Contributions:** {len(contributions)}")
                
                # Show recent contributions
                if len(contributions) > 0:
                    st.write("**Recent Contributions:**")
                    for i, contrib in enumerate(contributions[:3]):
                        st.write(f"  • {contrib.get('dialect_word', 'N/A')} from {contrib.get('location_text', 'N/A')}")
        
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.api_authenticated = False
                st.session_state.api_user_profile = None
                st.session_state.api_access_token = None
                api_client.access_token = None
                st.success("Logged out successfully!")
                st.rerun()
    
    return profile


def api_contribution_form() -> bool:
    """Enhanced contribution form with API integration"""
    if not st.session_state.api_authenticated:
        st.warning("Please login to the Indic Corpus API to contribute.")
        return False
    
    st.subheader("📤 Submit to Indic Corpus API")
    
    with st.form("api_contribution_form"):
        dialect_word = st.text_input("Dialect Word", placeholder="e.g., Cycle, Baingan")
        location_text = st.text_input("Location", placeholder="e.g., Hyderabad, Telangana")
        
        # Category selection
        categories = api_client.get_categories()
        category_options = ["None"] + [cat.get('name', 'Unknown') for cat in categories]
        selected_category = st.selectbox("Category (optional)", category_options)
        
        # Media upload
        uploaded_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        uploaded_audio = st.file_uploader("Upload Audio (optional)", type=["wav", "mp3"])
        
        # Coordinates (can be auto-filled from location)
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude", value=20.5937, format="%.4f")
        with col2:
            longitude = st.number_input("Longitude", value=78.9629, format="%.4f")
        
        submit_api = st.form_submit_button("Submit to API", use_container_width=True)
    
    if submit_api and dialect_word and location_text:
        with st.spinner("Submitting to Indic Corpus API..."):
            # Prepare media data
            image_data = uploaded_image.getvalue() if uploaded_image else None
            audio_data = uploaded_audio.getvalue() if uploaded_audio else None
            
            # Get category ID if selected
            category_id = None
            if selected_category != "None":
                for cat in categories:
                    if cat.get('name') == selected_category:
                        category_id = cat.get('id')
                        break
            
            # Create record
            record_id = api_client.create_record(
                dialect_word=dialect_word,
                location_text=location_text,
                latitude=latitude,
                longitude=longitude,
                image_data=image_data,
                audio_data=audio_data,
                category_id=category_id
            )
            
            if record_id:
                st.success(f"✅ Successfully submitted to Indic Corpus API! Record ID: {record_id}")
                return True
            else:
                st.error("❌ Failed to submit to API. Please try again.")
    
    return False


def api_records_display():
    """Display records from the API"""
    if not st.session_state.api_authenticated:
        st.warning("Please login to view API records.")
        return
    
    st.subheader("🗺️ Records from Indic Corpus API")
    
    # Search and filter options
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        search_query = st.text_input("Search records", placeholder="Enter dialect word...")
    with col2:
        categories = api_client.get_categories()
        category_options = ["All"] + [cat.get('name', 'Unknown') for cat in categories]
        selected_category = st.selectbox("Filter by category", category_options)
    with col3:
        if st.button("🔍 Search", use_container_width=True):
            st.session_state.api_search_results = True
    
    # Get records
    if st.session_state.get('api_search_results', False):
        with st.spinner("Fetching records..."):
            category_id = None
            if selected_category != "All":
                for cat in categories:
                    if cat.get('name') == selected_category:
                        category_id = cat.get('id')
                        break
            
            records = api_client.search_records(
                query=search_query if search_query else None,
                category_id=category_id,
                limit=50
            )
            
            if records:
                st.write(f"Found {len(records)} records:")
                
                # Display records in a table
                import pandas as pd
                records_data = []
                for record in records:
                    records_data.append({
                        'Dialect Word': record.get('dialect_word', 'N/A'),
                        'Location': record.get('location_text', 'N/A'),
                        'Category': record.get('category_name', 'N/A'),
                        'Media Type': record.get('media_type', 'N/A'),
                        'Created': record.get('created_at', 'N/A')[:10] if record.get('created_at') else 'N/A'
                    })
                
                df = pd.DataFrame(records_data)
                st.dataframe(df, use_container_width=True)
                
                # Show map of records
                if records:
                    st.subheader("📍 Records Map")
                    try:
                        import folium
                        from streamlit_folium import st_folium
                        
                        m = folium.Map(location=[20.5937, 78.9629], zoom_start=5)
                        
                        for record in records:
                            lat = record.get('latitude')
                            lon = record.get('longitude')
                            if lat and lon:
                                folium.Marker(
                                    [lat, lon],
                                    popup=f"<b>{record.get('dialect_word', 'N/A')}</b><br>{record.get('location_text', 'N/A')}",
                                    tooltip=record.get('dialect_word', 'N/A')
                                ).add_to(m)
                        
                        st_folium(m, width="100%", height=400)
                    except Exception as e:
                        st.warning(f"Could not display map: {e}")
            else:
                st.info("No records found matching your criteria.")
    
    # Nearby records feature
    st.subheader("📍 Find Records Near You")
    col1, col2, col3 = st.columns(3)
    with col1:
        near_lat = st.number_input("Your Latitude", value=20.5937, format="%.4f")
    with col2:
        near_lon = st.number_input("Your Longitude", value=78.9629, format="%.4f")
    with col3:
        radius = st.number_input("Radius (km)", value=50, min_value=1, max_value=500)
    
    if st.button("🔍 Find Nearby Records"):
        with st.spinner("Searching nearby records..."):
            nearby_records = api_client.get_records_nearby(near_lat, near_lon, radius)
            
            if nearby_records:
                st.write(f"Found {len(nearby_records)} records within {radius}km:")
                
                for record in nearby_records[:10]:  # Show first 10
                    st.write(f"• **{record.get('dialect_word', 'N/A')}** from {record.get('location_text', 'N/A')}")
            else:
                st.info(f"No records found within {radius}km of your location.")


def api_analytics():
    """Display analytics from the API"""
    if not st.session_state.api_authenticated:
        st.warning("Please login to view analytics.")
        return
    
    st.subheader("📊 API Analytics")
    
    # Get user contributions
    contributions = api_client.get_user_contributions()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Your Contributions", len(contributions))
    with col2:
        # Count by media type
        image_count = len([c for c in contributions if c.get('media_type') == 'image'])
        st.metric("Image Submissions", image_count)
    with col3:
        audio_count = len([c for c in contributions if c.get('media_type') == 'audio'])
        st.metric("Audio Submissions", audio_count)
    
    # Recent activity
    if contributions:
        st.write("**Recent Activity:**")
        for contrib in contributions[:5]:
            st.write(f"• {contrib.get('dialect_word', 'N/A')} - {contrib.get('created_at', 'N/A')[:10]}")
    
    # Categories breakdown
    categories = api_client.get_categories()
    if categories:
        st.write("**Available Categories:**")
        for cat in categories:
            st.write(f"• {cat.get('name', 'N/A')} - {cat.get('description', 'No description')}")


def main_api_interface():
    """Main API interface with tabs"""
    init_auth_session()
    
    if not st.session_state.api_authenticated:
        if st.session_state.get('show_api_register', False):
            api_register_form()
        else:
            api_login_form()
        return
    
    # User is authenticated
    api_user_profile()
    
    # Main interface tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Submit", "🗺️ Browse", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        api_contribution_form()
    
    with tab2:
        api_records_display()
    
    with tab3:
        api_analytics()
    
    with tab4:
        st.subheader("⚙️ API Settings")
        st.write("**API Base URL:**", api_client.base_url)
        st.write("**Authentication Status:**", "✅ Connected" if st.session_state.api_authenticated else "❌ Disconnected")
        
        if st.button("🔄 Refresh Connection"):
            st.rerun()
