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
            
        url = f"{self.base_url}/auth/me"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        st.write(f"🔍 DEBUG: Making GET request to: {url}")
        st.write(f"🔍 DEBUG: Headers: {headers}")
        
        try:
            response = requests.get(url, headers=headers)
            st.write(f"🔍 DEBUG: Response status: {response.status_code}")
            
            if response.status_code == 200:
                user_data = response.json()
                st.write(f"🔍 DEBUG: User profile data: {user_data}")
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
            st.write(f"🔍 DEBUG: Extracted user_id: {user_id}")
            return user_id
        else:
            st.error(f"No user ID found in profile: {profile}")
            return None


# Global instance
user_api = UserAPI()
