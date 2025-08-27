import requests
import streamlit as st
import json
from typing import Optional, Dict, List, Any
from datetime import datetime
import os


class IndicCorpusAPI:
    """Client for the Indic Corpus Collections API"""
    
    def __init__(self, base_url: str = None, api_key: str = None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL for the API (defaults to environment variable)
            api_key: API key for authentication (defaults to environment variable)
        """
        self.base_url = base_url or os.getenv("INDIC_CORPUS_API_URL", "https://api.example.com")
        self.api_key = api_key or os.getenv("INDIC_CORPUS_API_KEY")
        self.session = requests.Session()
        self.access_token = None
        
        # Set default headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make a request to the API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            st.error(f"API request failed: {e}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse API response: {e}")
            return {"error": "Invalid JSON response"}
    
    # Authentication Methods
    def login(self, username: str, password: str) -> Dict:
        """Login and get access token"""
        data = {
            "username": username,
            "password": password
        }
        response = self._make_request("POST", "/api/v1/auth/login", data=data)
        
        if "access_token" in response:
            self.access_token = response["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
        return response
    
    def login_with_otp(self, phone: str) -> Dict:
        """Send OTP for login"""
        data = {"phone": phone}
        return self._make_request("POST", "/api/v1/auth/login/send-otp", data=data)
    
    def verify_login_otp(self, phone: str, otp: str) -> Dict:
        """Verify OTP and login"""
        data = {
            "phone": phone,
            "otp": otp
        }
        response = self._make_request("POST", "/api/v1/auth/login/verify-otp", data=data)
        
        if "access_token" in response:
            self.access_token = response["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
        return response
    
    def signup_send_otp(self, phone: str) -> Dict:
        """Send OTP for signup"""
        data = {"phone": phone}
        return self._make_request("POST", "/api/v1/auth/signup/send-otp", data=data)
    
    def signup_verify_otp(self, phone: str, otp: str, username: str, password: str) -> Dict:
        """Verify OTP and create account"""
        data = {
            "phone": phone,
            "otp": otp,
            "username": username,
            "password": password
        }
        response = self._make_request("POST", "/api/v1/auth/signup/verify-otp", data=data)
        
        if "access_token" in response:
            self.access_token = response["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
        return response
    
    def get_current_user(self) -> Dict:
        """Get current user information"""
        return self._make_request("GET", "/api/v1/auth/me")
    
    def change_password(self, current_password: str, new_password: str) -> Dict:
        """Change user password"""
        data = {
            "current_password": current_password,
            "new_password": new_password
        }
        return self._make_request("POST", "/api/v1/auth/change-password", data=data)
    
    def refresh_token(self) -> Dict:
        """Refresh access token"""
        response = self._make_request("POST", "/api/v1/auth/refresh")
        
        if "access_token" in response:
            self.access_token = response["access_token"]
            self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
            
        return response
    
    # User Management
    def get_users(self, skip: int = 0, limit: int = 100) -> Dict:
        """Get list of users"""
        params = {"skip": skip, "limit": limit}
        return self._make_request("GET", "/api/v1/users/", params=params)
    
    def get_user(self, user_id: str) -> Dict:
        """Get specific user by ID"""
        return self._make_request("GET", f"/api/v1/users/{user_id}")
    
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user"""
        return self._make_request("POST", "/api/v1/users/", data=user_data)
    
    def update_user(self, user_id: str, user_data: Dict) -> Dict:
        """Update user information"""
        return self._make_request("PUT", f"/api/v1/users/{user_id}", data=user_data)
    
    def delete_user(self, user_id: str) -> Dict:
        """Delete a user"""
        return self._make_request("DELETE", f"/api/v1/users/{user_id}")
    
    def get_user_contributions(self, user_id: str, media_type: str = None) -> Dict:
        """Get user contributions"""
        endpoint = f"/api/v1/users/{user_id}/contributions"
        if media_type:
            endpoint += f"/{media_type}"
        return self._make_request("GET", endpoint)
    
    # Records Management
    def get_records(self, skip: int = 0, limit: int = 100, category_id: str = None) -> Dict:
        """Get list of records"""
        params = {"skip": skip, "limit": limit}
        if category_id:
            params["category_id"] = category_id
        return self._make_request("GET", "/api/v1/records/", params=params)
    
    def get_record(self, record_id: str) -> Dict:
        """Get specific record by ID"""
        return self._make_request("GET", f"/api/v1/records/{record_id}")
    
    def create_record(self, record_data: Dict) -> Dict:
        """Create a new record"""
        return self._make_request("POST", "/api/v1/records/", data=record_data)
    
    def update_record(self, record_id: str, record_data: Dict) -> Dict:
        """Update record information"""
        return self._make_request("PUT", f"/api/v1/records/{record_id}", data=record_data)
    
    def patch_record(self, record_id: str, record_data: Dict) -> Dict:
        """Patch record information"""
        return self._make_request("PATCH", f"/api/v1/records/{record_id}", data=record_data)
    
    def delete_record(self, record_id: str) -> Dict:
        """Delete a record"""
        return self._make_request("DELETE", f"/api/v1/records/{record_id}")
    
    def upload_record(self, file_path: str, metadata: Dict) -> Dict:
        """Upload a record with file"""
        url = f"{self.base_url}/api/v1/records/upload"
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = metadata
                response = self.session.post(url, files=files, data=data)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            st.error(f"File upload failed: {e}")
            return {"error": str(e)}
    
    def search_records_nearby(self, latitude: float, longitude: float, radius: float = 10.0) -> Dict:
        """Search records near a location"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius
        }
        return self._make_request("GET", "/api/v1/records/search/nearby", params=params)
    
    def search_records_bbox(self, min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> Dict:
        """Search records within a bounding box"""
        params = {
            "min_lat": min_lat,
            "min_lon": min_lon,
            "max_lat": max_lat,
            "max_lon": max_lon
        }
        return self._make_request("GET", "/api/v1/records/search/bbox", params=params)
    
    # Categories Management
    def get_categories(self) -> Dict:
        """Get list of categories"""
        return self._make_request("GET", "/api/v1/categories/")
    
    def get_category(self, category_id: str) -> Dict:
        """Get specific category by ID"""
        return self._make_request("GET", f"/api/v1/categories/{category_id}")
    
    def create_category(self, category_data: Dict) -> Dict:
        """Create a new category"""
        return self._make_request("POST", "/api/v1/categories/", data=category_data)
    
    def update_category(self, category_id: str, category_data: Dict) -> Dict:
        """Update category information"""
        return self._make_request("PUT", f"/api/v1/categories/{category_id}", data=category_data)
    
    def delete_category(self, category_id: str) -> Dict:
        """Delete a category"""
        return self._make_request("DELETE", f"/api/v1/categories/{category_id}")
    
    # Tasks Management
    def start_audio_processing(self, record_id: str) -> Dict:
        """Start audio processing for a record"""
        return self._make_request("POST", f"/api/v1/tasks/process-audio/{record_id}")
    
    def start_content_analysis(self, record_id: str) -> Dict:
        """Start content analysis for a record"""
        return self._make_request("POST", f"/api/v1/tasks/analyze-content/{record_id}")
    
    def generate_statistics(self) -> Dict:
        """Generate system statistics"""
        return self._make_request("POST", "/api/v1/tasks/generate-statistics")
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get task status"""
        return self._make_request("GET", f"/api/v1/tasks/status/{task_id}")
    
    def cancel_task(self, task_id: str) -> Dict:
        """Cancel a task"""
        return self._make_request("DELETE", f"/api/v1/tasks/cancel/{task_id}")
    
    # Health Check
    def health_check(self) -> Dict:
        """Check API health"""
        return self._make_request("GET", "/health")
    
    # Utility Methods
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None
    
    def logout(self):
        """Logout and clear session"""
        self.access_token = None
        self.session.headers.pop("Authorization", None)
    
    def sync_local_data(self, local_submissions: List[Dict]) -> Dict:
        """Sync local submissions with the API"""
        synced_count = 0
        errors = []
        
        for submission in local_submissions:
            try:
                # Convert local submission to API format
                record_data = {
                    "dialect_word": submission.get("dialect_word"),
                    "location_text": submission.get("location_text"),
                    "latitude": submission.get("latitude"),
                    "longitude": submission.get("longitude"),
                    "category_id": "dialect_word",  # Default category
                    "media_type": "image",
                    "is_public": submission.get("is_public", True),
                    "metadata": {
                        "local_id": submission.get("id"),
                        "user_id": submission.get("user_id"),
                        "timestamp": submission.get("timestamp")
                    }
                }
                
                # Create record in API
                response = self.create_record(record_data)
                if "id" in response:
                    synced_count += 1
                else:
                    errors.append(f"Failed to sync submission {submission.get('id')}: {response.get('error', 'Unknown error')}")
                    
            except Exception as e:
                errors.append(f"Error syncing submission {submission.get('id')}: {str(e)}")
        
        return {
            "synced_count": synced_count,
            "total_count": len(local_submissions),
            "errors": errors
        }


# Convenience functions for Streamlit integration
def get_api_client() -> IndicCorpusAPI:
    """Get API client instance"""
    return IndicCorpusAPI()


def api_login_ui():
    """Show API login UI in Streamlit"""
    st.subheader("🔐 API Authentication")
    
    api_client = get_api_client()
    
    tab1, tab2, tab3 = st.tabs(["Login", "OTP Login", "Signup"])
    
    with tab1:
        st.write("Login with username and password")
        username = st.text_input("Username", key="api_username")
        password = st.text_input("Password", type="password", key="api_password")
        
        if st.button("Login"):
            if username and password:
                response = api_client.login(username, password)
                if "access_token" in response:
                    st.session_state["api_authenticated"] = True
                    st.session_state["api_user"] = response
                    st.success("Successfully logged in to API!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {response.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter username and password")
    
    with tab2:
        st.write("Login with phone number and OTP")
        phone = st.text_input("Phone Number", key="api_phone")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send OTP"):
                if phone:
                    response = api_client.login_with_otp(phone)
                    if "message" in response:
                        st.success("OTP sent successfully!")
                    else:
                        st.error(f"Failed to send OTP: {response.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter phone number")
        
        with col2:
            otp = st.text_input("OTP", key="api_otp")
            if st.button("Verify OTP"):
                if phone and otp:
                    response = api_client.verify_login_otp(phone, otp)
                    if "access_token" in response:
                        st.session_state["api_authenticated"] = True
                        st.session_state["api_user"] = response
                        st.success("Successfully logged in with OTP!")
                        st.rerun()
                    else:
                        st.error(f"OTP verification failed: {response.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter phone number and OTP")
    
    with tab3:
        st.write("Create new account")
        signup_phone = st.text_input("Phone Number", key="signup_phone")
        signup_username = st.text_input("Username", key="signup_username")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Send Signup OTP"):
                if signup_phone:
                    response = api_client.signup_send_otp(signup_phone)
                    if "message" in response:
                        st.success("Signup OTP sent successfully!")
                    else:
                        st.error(f"Failed to send signup OTP: {response.get('error', 'Unknown error')}")
                else:
                    st.warning("Please enter phone number")
        
        with col2:
            signup_otp = st.text_input("Signup OTP", key="signup_otp")
            if st.button("Create Account"):
                if signup_phone and signup_otp and signup_username and signup_password:
                    response = api_client.signup_verify_otp(signup_phone, signup_otp, signup_username, signup_password)
                    if "access_token" in response:
                        st.session_state["api_authenticated"] = True
                        st.session_state["api_user"] = response
                        st.success("Account created and logged in successfully!")
                        st.rerun()
                    else:
                        st.error(f"Account creation failed: {response.get('error', 'Unknown error')}")
                else:
                    st.warning("Please fill all fields")


def api_user_info():
    """Show API user information"""
    if st.session_state.get("api_authenticated"):
        st.subheader("👤 API User")
        
        api_client = get_api_client()
        user_info = api_client.get_current_user()
        
        if "username" in user_info:
            st.write(f"**Username:** {user_info.get('username')}")
            st.write(f"**Email:** {user_info.get('email', 'Not provided')}")
            st.write(f"**Phone:** {user_info.get('phone', 'Not provided')}")
            
            if st.button("Logout from API"):
                api_client.logout()
                for key in ["api_authenticated", "api_user"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.success("Logged out from API!")
                st.rerun()
        else:
            st.error("Failed to get user information")
            st.session_state["api_authenticated"] = False


def sync_data_ui():
    """Show data synchronization UI"""
    if not st.session_state.get("api_authenticated"):
        st.warning("Please login to API first to sync data")
        return
    
    st.subheader("🔄 Data Synchronization")
    
    api_client = get_api_client()
    
    if st.button("Sync Local Data to API"):
        with st.spinner("Syncing data..."):
            # Get local submissions from database
            import database as db
            conn = db.create_connection()
            local_submissions = db.get_all_submissions(conn, public_only=False)
            
            if not local_submissions.empty:
                # Convert DataFrame to list of dictionaries
                submissions_list = local_submissions.to_dict('records')
                
                # Sync with API
                result = api_client.sync_local_data(submissions_list)
                
                st.write(f"**Sync Results:**")
                st.write(f"- Synced: {result['synced_count']}/{result['total_count']} submissions")
                
                if result['errors']:
                    st.write("**Errors:**")
                    for error in result['errors'][:5]:  # Show first 5 errors
                        st.write(f"- {error}")
                    if len(result['errors']) > 5:
                        st.write(f"- ... and {len(result['errors']) - 5} more errors")
            else:
                st.info("No local data to sync")


def api_status_check():
    """Check API status and show information"""
    st.subheader("📊 API Status")
    
    api_client = get_api_client()
    
    # Health check
    health = api_client.health_check()
    if "status" in health:
        st.success(f"API Status: {health['status']}")
    else:
        st.error("API is not accessible")
        return
    
    # Get categories
    categories = api_client.get_categories()
    if "items" in categories:
        st.write(f"**Available Categories:** {len(categories['items'])}")
        for category in categories['items'][:5]:  # Show first 5
            st.write(f"- {category.get('name', 'Unknown')}")
    
    # Get statistics if authenticated
    if st.session_state.get("api_authenticated"):
        if st.button("Generate Statistics"):
            with st.spinner("Generating statistics..."):
                stats = api_client.generate_statistics()
                if "statistics" in stats:
                    st.write("**System Statistics:**")
                    for key, value in stats['statistics'].items():
                        st.write(f"- {key}: {value}")
                else:
                    st.error("Failed to generate statistics")
