"""
Records display component with role-based access control
"""
import streamlit as st
from typing import List, Dict, Any
from api_user import user_api
import api_auth_ui

def display_records_with_access_control(records: List[Dict[str, Any]], user_is_admin: bool = False):
    """Display records with appropriate access control based on user role"""
    
    if not records:
        st.info("📝 No records found.")
        return
    
    if user_is_admin:
        # Admin sees all records with full details
        st.success(f"🔓 **Admin Access**: Viewing all {len(records)} records")
        
        for i, record in enumerate(records):
            with st.expander(f"Record {i+1}: {record.get('title', 'Untitled')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {record.get('id', 'N/A')}")
                    st.write(f"**Title:** {record.get('title', 'N/A')}")
                    st.write(f"**Description:** {record.get('description', 'N/A')}")
                    st.write(f"**Language:** {record.get('language', 'N/A')}")
                    st.write(f"**Media Type:** {record.get('media_type', 'N/A')}")
                
                with col2:
                    st.write(f"**User ID:** {record.get('user_id', 'N/A')}")
                    st.write(f"**Category ID:** {record.get('category_id', 'N/A')}")
                    st.write(f"**Status:** {record.get('status', 'N/A')}")
                    st.write(f"**Created:** {record.get('created_at', 'N/A')}")
                    
                    if record.get('location'):
                        location = record['location']
                        st.write(f"**Location:** {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
                
                if record.get('file_url'):
                    st.write(f"**File URL:** {record['file_url']}")
    else:
        # Normal user sees limited view with lock symbol
        st.warning(f"🔒 **User Access**: Viewing your {len(records)} personal records")
        
        for i, record in enumerate(records):
            with st.expander(f"🔒 Your Record {i+1}: {record.get('title', 'Untitled')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Title:** {record.get('title', 'N/A')}")
                    st.write(f"**Description:** {record.get('description', 'N/A')}")
                    st.write(f"**Language:** {record.get('language', 'N/A')}")
                    st.write(f"**Media Type:** {record.get('media_type', 'N/A')}")
                
                with col2:
                    st.write(f"**Status:** {record.get('status', 'N/A')}")
                    st.write(f"**Created:** {record.get('created_at', 'N/A')}")
                    
                    if record.get('location'):
                        location = record['location']
                        st.write(f"**Location:** {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
                
                if record.get('file_url'):
                    st.write(f"**File URL:** {record['file_url']}")
        
        # Show info about limited access
        st.info("🔒 **Privacy Note:** You can only view your own records. Admins can see all contributions.")

def get_and_display_records(force_refresh: bool = False):
    """Get records and display them with proper access control"""
    
    if not api_auth_ui.api_auth.is_authenticated():
        st.warning("🔐 Please login to view records")
        return
    
    # Check if user is admin
    try:
        is_admin = user_api.is_admin(api_auth_ui.api_auth.access_token)
        st.write(f"🔍 DEBUG: User admin status: {is_admin}")
    except Exception as e:
        st.error(f"Error checking admin status: {str(e)}")
        is_admin = False
    
    # Get records with caching
    from api_records import api_records
    
    try:
        records = api_records.get_records(limit=1000, force_refresh=force_refresh)
        display_records_with_access_control(records, is_admin)
        
    except Exception as e:
        st.error(f"Error fetching records: {str(e)}")
        st.info("💡 Try refreshing the page or checking your internet connection.")
