import requests
import streamlit as st
import json
from typing import Optional, Dict, Any
import time

# API Configuration
API_BASE_URL = "https://api.corpus.swecha.org"
API_VERSION = "v1"

class CorpusAPIAuth:
    """Authentication handler for Indic Corpus Collections API"""
    
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
        self.access_token = None
        self.user_info = None
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        if include_auth and self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     include_auth: bool = True) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_auth)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {str(e)}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON response: {str(e)}")
            return {"error": "Invalid response format"}
    
    def send_login_otp(self, phone_number: str) -> Dict[str, Any]:
        """Send OTP for login"""
        data = {"phone_number": phone_number}
        return self._make_request("POST", "/auth/login/send-otp", data, include_auth=False)
    
    def verify_login_otp(self, phone_number: str, otp_code: str, has_given_consent: bool = True) -> Dict[str, Any]:
        """Verify OTP for login"""
        data = {
            "phone_number": phone_number,
            "otp_code": otp_code,
            "has_given_consent": has_given_consent
        }
        result = self._make_request("POST", "/auth/login/verify-otp", data, include_auth=False)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self.user_info = {
                "user_id": result.get("user_id"),
                "phone_number": result.get("phone_number"),
                "roles": result.get("roles", [])
            }
        
        return result
    
    def resend_login_otp(self, phone_number: str) -> Dict[str, Any]:
        """Resend OTP for login"""
        data = {"phone_number": phone_number}
        return self._make_request("POST", "/auth/login/resend-otp", data, include_auth=False)
    
    def login_with_password(self, phone: str, password: str) -> Dict[str, Any]:
        """Login with phone and password"""
        data = {"phone": phone, "password": password}
        result = self._make_request("POST", "/auth/login", data, include_auth=False)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
        
        return result
    
    def send_signup_otp(self, phone_number: str) -> Dict[str, Any]:
        """Send OTP for signup"""
        data = {"phone_number": phone_number}
        return self._make_request("POST", "/auth/signup/send-otp", data, include_auth=False)
    
    def verify_signup_otp(self, phone_number: str, otp_code: str, name: str, 
                         email: str, password: str, has_given_consent: bool = True) -> Dict[str, Any]:
        """Verify OTP and create new user account"""
        data = {
            "phone_number": phone_number,
            "otp_code": otp_code,
            "name": name,
            "email": email,
            "password": password,
            "has_given_consent": has_given_consent
        }
        result = self._make_request("POST", "/auth/signup/verify-otp", data, include_auth=False)
        
        if "access_token" in result:
            self.access_token = result["access_token"]
            self.user_info = {
                "user_id": result.get("user_id"),
                "phone_number": result.get("phone_number"),
                "roles": result.get("roles", [])
            }
        
        return result
    
    def resend_signup_otp(self, phone_number: str) -> Dict[str, Any]:
        """Resend OTP for signup"""
        data = {"phone_number": phone_number}
        return self._make_request("POST", "/auth/signup/resend-otp", data, include_auth=False)
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user information"""
        return self._make_request("GET", "/auth/me")
    
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change current user's password"""
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        return self._make_request("POST", "/auth/change-password", data)
    
    def refresh_token(self) -> Dict[str, Any]:
        """Refresh access token"""
        result = self._make_request("POST", "/auth/refresh")
        if "access_token" in result:
            self.access_token = result["access_token"]
        return result
    
    def forgot_password_init(self, phone_number: str) -> Dict[str, Any]:
        """Initiate password reset"""
        data = {"phone_number": phone_number}
        return self._make_request("POST", "/auth/forgot-password/init", data, include_auth=False)
    
    def forgot_password_confirm(self, phone_number: str, otp_code: str, 
                               new_password: str, confirm_password: str) -> Dict[str, Any]:
        """Confirm password reset"""
        data = {
            "phone_number": phone_number,
            "otp_code": otp_code,
            "new_password": new_password,
            "confirm_password": confirm_password
        }
        return self._make_request("POST", "/auth/forgot-password/confirm", data, include_auth=False)
    
    def reset_password(self, phone: str, new_password: str) -> Dict[str, Any]:
        """Reset user password (admin functionality)"""
        data = {"phone": phone, "new_password": new_password}
        return self._make_request("POST", "/auth/reset-password", data)
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None
    
    def logout(self):
        """Logout user"""
        self.access_token = None
        self.user_info = None
        self.session = requests.Session()
    
    def get_user_info(self) -> Optional[Dict[str, Any]]:
        """Get cached user information"""
        return self.user_info


# Global API auth instance
api_auth = CorpusAPIAuth()


def init_session_state():
    """Initialize session state for authentication"""
    if "api_auth_token" not in st.session_state:
        st.session_state.api_auth_token = None
    if "api_user_info" not in st.session_state:
        st.session_state.api_user_info = None
    if "api_auth_phone" not in st.session_state:
        st.session_state.api_auth_phone = None
    if "api_auth_otp_sent" not in st.session_state:
        st.session_state.api_auth_otp_sent = False
    if "api_auth_signup_data" not in st.session_state:
        st.session_state.api_auth_signup_data = {}


def save_auth_to_session():
    """Save authentication data to session state"""
    if api_auth.access_token:
        st.session_state.api_auth_token = api_auth.access_token
    if api_auth.user_info:
        st.session_state.api_user_info = api_auth.user_info


def load_auth_from_session():
    """Load authentication data from session state"""
    if st.session_state.api_auth_token:
        api_auth.access_token = st.session_state.api_auth_token
    if st.session_state.api_user_info:
        api_auth.user_info = st.session_state.api_user_info


def clear_auth_session():
    """Clear authentication data from session state"""
    st.session_state.api_auth_token = None
    st.session_state.api_user_info = None
    st.session_state.api_auth_phone = None
    st.session_state.api_auth_otp_sent = False
    st.session_state.api_auth_signup_data = {}
    api_auth.logout()
