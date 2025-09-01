"""
Records display component with role-based access control
"""
import streamlit as st
from typing import List, Dict, Any
from api_user import user_api
import api_auth_ui

def display_contributions_with_access_control(contributions_data: Dict[str, Any], user_is_admin: bool = False):
    """Display user contributions with appropriate access control based on user role"""
    
    if "error" in contributions_data:
        st.error(f"Error loading contributions: {contributions_data['error']}")
        return
    
    total_contributions = contributions_data.get('total_contributions', 0)
    if total_contributions == 0:
        st.info("📝 No contributions found.")
        return
    
    # Display summary
    st.success(f"📊 **Total Contributions**: {total_contributions}")
    
    # Display contributions by media type
    contributions_by_type = contributions_data.get('contributions_by_media_type', {})
    if contributions_by_type:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📝 Text", contributions_by_type.get('text', 0))
        with col2:
            st.metric("🎵 Audio", contributions_by_type.get('audio', 0))
        with col3:
            st.metric("🖼️ Image", contributions_by_type.get('image', 0))
        with col4:
            st.metric("🎥 Video", contributions_by_type.get('video', 0))
        with col5:
            st.metric("📄 Document", contributions_by_type.get('document', 0))
    
    # Display detailed contributions by media type
    media_types = ['audio', 'video', 'text', 'image', 'document']
    for media_type in media_types:
        contributions_key = f"{media_type}_contributions"
        contributions = contributions_data.get(contributions_key, [])
        
        if contributions:
            st.subheader(f"{media_type.title()} Contributions ({len(contributions)})")
            
            for i, record in enumerate(contributions):
                access_icon = "🔓" if user_is_admin else "🔒"
                with st.expander(f"{access_icon} {record.get('title', f'{media_type.title()} {i+1}')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Title:** {record.get('title', 'N/A')}")
                        st.write(f"**Description:** {record.get('description', 'N/A')}")
                        st.write(f"**Language:** {record.get('language', 'N/A')}")
                        st.write(f"**Reviewed:** {'✅ Yes' if record.get('reviewed') else '⏳ Pending'}")
                    
                    with col2:
                        if user_is_admin:
                            st.write(f"**ID:** {record.get('id', 'N/A')}")
                            st.write(f"**User ID:** {record.get('user_id', 'N/A')}")
                        st.write(f"**Size:** {record.get('size', 0)} bytes")
                        st.write(f"**Created:** {record.get('timestamp', 'N/A')}")
                        
                        if record.get('location'):
                            location = record['location']
                            st.write(f"**Location:** {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
                    
                    if media_type in ['audio', 'video'] and record.get('duration'):
                        st.write(f"**Duration:** {record['duration']} seconds")
                    
                    if record.get('file_hash') and user_is_admin:
                        st.write(f"**File Hash:** {record['file_hash']}")

def display_media_contributions(user_id: str, media_type: str, user_is_admin: bool = False, force_refresh: bool = False):
    """Display contributions for a specific media type using the new endpoint"""
    from api_records import api_records
    
    try:
        contributions_data = api_records.get_user_contributions_by_media(user_id, media_type, force_refresh)
        
        if "error" in contributions_data:
            st.error(f"Error loading {media_type} contributions: {contributions_data['error']}")
            return
        
        total_contributions = contributions_data.get('total_contributions', 0)
        contributions = contributions_data.get('contributions', [])
        
        if total_contributions == 0:
            st.info(f"📝 No {media_type} contributions found.")
            return
        
        st.success(f"📊 **{media_type.title()} Contributions**: {total_contributions}")
        
        for i, record in enumerate(contributions):
            access_icon = "🔓" if user_is_admin else "🔒"
            with st.expander(f"{access_icon} {record.get('title', f'{media_type.title()} {i+1}')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {record.get('title', 'N/A')}")
                    st.write(f"**Description:** {record.get('description', 'N/A')}")
                    st.write(f"**Language:** {record.get('language', 'N/A')}")
                    st.write(f"**Reviewed:** {'✅ Yes' if record.get('reviewed') else '⏳ Pending'}")
                
                with col2:
                    if user_is_admin:
                        st.write(f"**ID:** {record.get('id', 'N/A')}")
                        st.write(f"**User ID:** {record.get('user_id', 'N/A')}")
                    st.write(f"**Size:** {record.get('size', 0)} bytes")
                    st.write(f"**Created:** {record.get('timestamp', 'N/A')}")
                    
                    if record.get('location'):
                        location = record['location']
                        st.write(f"**Location:** {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
                
                if media_type in ['audio', 'video'] and record.get('duration'):
                    st.write(f"**Duration:** {record['duration']} seconds")
                
                if record.get('file_hash') and user_is_admin:
                    st.write(f"**File Hash:** {record['file_hash']}")
        
        # Show access level info
        if user_is_admin:
            st.info("🔓 **Admin Access**: You can view detailed information including user IDs and file hashes.")
        else:
            st.info("🔒 **Privacy Note:** You are viewing your own contributions. Admins can see additional details.")
    
    except Exception as e:
        st.error(f"Error fetching {media_type} contributions: {str(e)}")
    
    # Show access level info
    if user_is_admin:
        st.info("🔓 **Admin Access**: You can view detailed information including user IDs and file hashes.")
    else:
        st.info("🔒 **Privacy Note:** You are viewing your own contributions. Admins can see additional details.")

def get_and_display_contributions(force_refresh: bool = False):
    """Get user contributions and display them with proper access control"""
    
    if not api_auth_ui.api_auth.is_authenticated():
        st.warning("🔐 Please login to view your contributions")
        return
    
    # Check if user is admin
    try:
        is_admin = user_api.is_admin(api_auth_ui.api_auth.access_token)
    except Exception as e:
        st.error(f"Error checking admin status: {str(e)}")
        is_admin = False
    
    # Get user ID
    try:
        user_id = user_api.get_user_id(api_auth_ui.api_auth.access_token)
        if not user_id:
            st.error("Could not retrieve user ID")
            return
    except Exception as e:
        st.error(f"Error getting user ID: {str(e)}")
        return
    
    # Get contributions with caching
    from api_records import api_records
    
    try:
        if is_admin:
            # Admins can still view all records if needed
            st.tabs_container = st.tabs(["My Contributions", "All Records (Admin)"])
            
            with st.tabs_container[0]:
                contributions = api_records.get_user_contributions(user_id, force_refresh=force_refresh)
                display_contributions_with_access_control(contributions, is_admin)
            
            with st.tabs_container[1]:
                records = api_records.get_records(limit=1000, force_refresh=force_refresh)
                if records:
                    st.success(f"🔓 **Admin Access**: Viewing all {len(records)} records")
                    for i, record in enumerate(records):
                        with st.expander(f"Record {i+1}: {record.get('title', 'Untitled')}"):
                            st.json(record)
                else:
                    st.info("No records found")
        else:
            # Normal users see only their contributions
            contributions = api_records.get_user_contributions(user_id, force_refresh=force_refresh)
            display_contributions_with_access_control(contributions, is_admin)
        
    except Exception as e:
        st.error(f"Error fetching contributions: {str(e)}")
        st.info("💡 Try refreshing the page or checking your internet connection.")
