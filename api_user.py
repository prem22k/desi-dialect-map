"""
Separate user profile API handler to avoid conflicts with auth module
"""
import requests
import streamlit as st
from typing import Dict, Any, Optional
from config.settings import API_BASE_URL


class UserAPI:
    def __init__(self):
        self.base_url = API_BASE_URL
        
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """Get user profile from /auth/me endpoint using Bearer token"""
        if not access_token:
            return {"error": "No access token provided"}
            
        url = f"{self.base_url}/api/v1/auth/me"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        
        try:
            response = requests.get(url, headers=headers)
                
            if response.status_code == 200:
                user_data = response.json()
                return user_data
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                st.error(f"Failed to get user profile: {error_msg}")
                return {"error": error_msg}
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Request failed: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            st.error(error_msg)
            return {"error": error_msg}
    
    def get_user_id(self, access_token: str) -> Optional[str]:
        """Extract user ID from user profile"""
        profile = self.get_user_profile(access_token)
        
        if "error" in profile:
            return None
            
        # Try different possible keys for user ID
        user_id = profile.get("id") or profile.get("user_id") or profile.get("sub")
        
        if user_id:
            return user_id
        else:
            st.error(f"No user ID found in profile: {profile}")
            return None
    
    def is_admin(self, access_token: str) -> bool:
        """Check if user has admin role"""
        profile = self.get_user_profile(access_token)
        
        if "error" in profile:
            return False
            
        # Check for admin role in various possible fields
        roles = profile.get("roles", [])
        if isinstance(roles, list):
            return "admin" in [role.lower() if isinstance(role, str) else str(role).lower() for role in roles]
        
        # Check other possible admin indicators
        is_admin = profile.get("is_admin", False) or profile.get("admin", False)
        return bool(is_admin)


# Global instance
user_api = UserAPI()
