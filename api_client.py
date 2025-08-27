import requests
import json
import streamlit as st
from typing import Optional, Dict, List, Any
import os
from datetime import datetime


class IndicCorpusAPI:
    """Client for interacting with the Indic Corpus Collections API"""
    
    def __init__(self, base_url: str = "https://api.indiccorpus.org"):
        self.base_url = base_url
        self.session = requests.Session()
        self.access_token = None
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers
    
    def login(self, username: str, password: str) -> bool:
        """Login to get access token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json={"username": username, "password": password},
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                return True
            else:
                st.error(f"Login failed: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"Login error: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str, phone: str = None) -> bool:
        """Register a new user"""
        try:
            # First send OTP for signup
            otp_response = self.session.post(
                f"{self.base_url}/api/v1/auth/signup/send-otp",
                json={"email": email, "phone": phone},
                headers=self._get_headers()
            )
            
            if otp_response.status_code == 200:
                # For demo purposes, we'll assume OTP is verified
                # In production, you'd need to handle OTP verification
                st.success("OTP sent successfully! Please check your email/phone.")
                return True
            else:
                st.error(f"Registration failed: {otp_response.text}")
                return False
                
        except Exception as e:
            st.error(f"Registration error: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get current user profile"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/auth/me",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to get profile: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Profile error: {e}")
            return None
    
    def create_record(self, dialect_word: str, location_text: str, 
                     latitude: float, longitude: float, 
                     image_data: bytes = None, audio_data: bytes = None,
                     category_id: str = None) -> Optional[str]:
        """Create a new dialect record"""
        try:
            record_data = {
                "dialect_word": dialect_word,
                "location_text": location_text,
                "latitude": latitude,
                "longitude": longitude,
                "category_id": category_id,
                "media_type": "image" if image_data else "audio" if audio_data else "text",
                "is_public": True,
                "metadata": {
                    "source": "desi_dialect_map",
                    "submitted_at": datetime.now().isoformat()
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/records/",
                json=record_data,
                headers=self._get_headers()
            )
            
            if response.status_code == 201:
                data = response.json()
                record_id = data.get("id")
                
                # Upload media if provided
                if record_id and (image_data or audio_data):
                    self._upload_media(record_id, image_data, audio_data)
                
                return record_id
            else:
                st.error(f"Failed to create record: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Create record error: {e}")
            return None
    
    def _upload_media(self, record_id: str, image_data: bytes = None, audio_data: bytes = None):
        """Upload media for a record"""
        try:
            if image_data:
                files = {"file": ("image.jpg", image_data, "image/jpeg")}
                response = self.session.post(
                    f"{self.base_url}/api/v1/records/upload",
                    files=files,
                    data={"record_id": record_id, "media_type": "image"},
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                
                if response.status_code != 200:
                    st.warning(f"Image upload failed: {response.text}")
            
            if audio_data:
                files = {"file": ("audio.wav", audio_data, "audio/wav")}
                response = self.session.post(
                    f"{self.base_url}/api/v1/records/upload",
                    files=files,
                    data={"record_id": record_id, "media_type": "audio"},
                    headers={"Authorization": f"Bearer {self.access_token}"}
                )
                
                if response.status_code != 200:
                    st.warning(f"Audio upload failed: {response.text}")
                    
        except Exception as e:
            st.warning(f"Media upload error: {e}")
    
    def get_records_nearby(self, latitude: float, longitude: float, 
                          radius_km: float = 50) -> List[Dict]:
        """Get records near a location"""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "radius_km": radius_km
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/records/search/nearby",
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("records", [])
            else:
                st.error(f"Failed to get nearby records: {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Nearby records error: {e}")
            return []
    
    def get_records_in_bbox(self, min_lat: float, max_lat: float, 
                           min_lon: float, max_lon: float) -> List[Dict]:
        """Get records within a bounding box"""
        try:
            params = {
                "min_lat": min_lat,
                "max_lat": max_lat,
                "min_lon": min_lon,
                "max_lon": max_lon
            }
            
            response = self.session.get(
                f"{self.base_url}/api/v1/records/search/bbox",
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("records", [])
            else:
                st.error(f"Failed to get bbox records: {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Bbox records error: {e}")
            return []
    
    def get_user_contributions(self, user_id: str = None) -> List[Dict]:
        """Get user contributions"""
        try:
            if not user_id:
                # Get current user's contributions
                profile = self.get_user_profile()
                if profile:
                    user_id = profile.get("id")
            
            if not user_id:
                return []
            
            response = self.session.get(
                f"{self.base_url}/api/v1/users/{user_id}/contributions",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("contributions", [])
            else:
                st.error(f"Failed to get contributions: {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Contributions error: {e}")
            return []
    
    def get_categories(self) -> List[Dict]:
        """Get available categories"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/categories/",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("categories", [])
            else:
                st.error(f"Failed to get categories: {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Categories error: {e}")
            return []
    
    def search_records(self, query: str = None, category_id: str = None, 
                      limit: int = 100) -> List[Dict]:
        """Search records with filters"""
        try:
            params = {"limit": limit}
            if query:
                params["q"] = query
            if category_id:
                params["category_id"] = category_id
            
            response = self.session.get(
                f"{self.base_url}/api/v1/records/",
                params=params,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json().get("records", [])
            else:
                st.error(f"Failed to search records: {response.text}")
                return []
                
        except Exception as e:
            st.error(f"Search error: {e}")
            return []
    
    def get_record(self, record_id: str) -> Optional[Dict]:
        """Get a specific record"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/records/{record_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Failed to get record: {response.text}")
                return None
                
        except Exception as e:
            st.error(f"Get record error: {e}")
            return None
    
    def update_record(self, record_id: str, updates: Dict) -> bool:
        """Update a record"""
        try:
            response = self.session.patch(
                f"{self.base_url}/api/v1/records/{record_id}",
                json=updates,
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                return True
            else:
                st.error(f"Failed to update record: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"Update record error: {e}")
            return False
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a record"""
        try:
            response = self.session.delete(
                f"{self.base_url}/api/v1/records/{record_id}",
                headers=self._get_headers()
            )
            
            if response.status_code == 204:
                return True
            else:
                st.error(f"Failed to delete record: {response.text}")
                return False
                
        except Exception as e:
            st.error(f"Delete record error: {e}")
            return False


# Global API client instance
api_client = IndicCorpusAPI()
