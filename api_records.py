import requests
import streamlit as st
import json
import uuid
import base64
import os
from typing import Optional, Dict, Any, List
from api_auth import api_auth
from config.settings import CHUNK_SIZE, MAX_FILE_SIZE, SUPPORTED_IMAGE_FORMATS
from api_categories import get_default_category

# API Configuration
API_BASE_URL = "https://api.corpus.swecha.org"
API_VERSION = "v1"

class CorpusAPIRecords:
    """Record management handler for Indic Corpus Collections API"""
    
    def __init__(self):
        self.base_url = f"{API_BASE_URL}/api/{API_VERSION}"
        self.session = requests.Session()
    
    def _get_headers(self, include_auth: bool = True) -> Dict[str, str]:
        """Get request headers with Bearer token"""
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json"
        }
        if include_auth and api_auth.access_token:
            headers["Authorization"] = f"Bearer {api_auth.access_token}"
        return headers
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, 
                     params: Optional[Dict] = None, files: Optional[Dict] = None,
                     include_auth: bool = True) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_auth)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                if files:
                    # Remove Content-Type for file uploads
                    headers.pop("Content-Type", None)
                    response = self.session.post(url, headers=headers, data=data, files=files)
                else:
                    response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
            elif method.upper() == "PATCH":
                response = self.session.patch(url, headers=headers, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
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
    
    def get_records(self, category_id: Optional[str] = None, user_id: Optional[str] = None,
                   media_type: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get user's own records with Bearer token (API restricts to authenticated user's records)"""
        if not api_auth.access_token:
            st.warning("Authentication required to fetch records")
            return []
        
        # When using Bearer token, API typically returns only user's own records
        # Don't pass user_id as it's inferred from the token
        params = {
            "skip": skip,
            "limit": limit
        }
        if category_id:
            params["category_id"] = category_id
        if media_type:
            params["media_type"] = media_type
        
        try:
            result = self._make_request("GET", "/records/", params=params, include_auth=True)
            if isinstance(result, list):
                return result
            elif isinstance(result, dict) and "error" in result:
                st.error(f"Failed to fetch records: {result['error']}")
                return []
            return []
        except Exception as e:
            st.error(f"Error fetching records: {str(e)}")
            return []
    
    def get_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific record by ID"""
        result = self._make_request("GET", f"/records/{record_id}")
        if "error" not in result:
            return result
        return None
    
    def create_record(self, title: str, description: str, media_type: str, 
                     location: Dict[str, float], language: str, category_id: str,
                     file_url: Optional[str] = None, file_name: Optional[str] = None,
                     file_size: int = 0, release_rights: str = "creator") -> Optional[Dict[str, Any]]:
        """Create a new record"""
        data = {
            "title": title,
            "description": description,
            "media_type": media_type,
            "location": location,
            "language": language,
            "category_id": category_id,
            "release_rights": release_rights,
            "user_id": api_auth.user_info.get("user_id") if api_auth.user_info else None
        }
        
        if file_url:
            data["file_url"] = file_url
        if file_name:
            data["file_name"] = file_name
        if file_size:
            data["file_size"] = file_size
        
        result = self._make_request("POST", "/records/", data=data)
        if "error" not in result:
            return result
        return None
    
    def update_record(self, record_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a record"""
        result = self._make_request("PUT", f"/records/{record_id}", data=kwargs)
        if "error" not in result:
            return result
        return None
    
    def patch_record(self, record_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Patch a record (partial update)"""
        result = self._make_request("PATCH", f"/records/{record_id}", data=kwargs)
        if "error" not in result:
            return result
        return None
    
    def delete_record(self, record_id: str) -> bool:
        """Delete a record"""
        result = self._make_request("DELETE", f"/records/{record_id}")
        return "error" not in result
    
    def search_nearby(self, latitude: float, longitude: float, distance_meters: float,
                     category_id: Optional[str] = None, media_type: Optional[str] = None,
                     skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for records within a specified distance of a point using Bearer token"""
        # Validate parameters according to API spec
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (0 < distance_meters <= 50000):
            raise ValueError("Distance must be between 0 and 50000 meters")
        if not (0 <= skip):
            raise ValueError("Skip must be >= 0")
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "distance_meters": distance_meters,
            "skip": skip,
            "limit": limit
        }
        if category_id:
            params["category_id"] = category_id
        if media_type:
            params["media_type"] = media_type
        
        result = self._make_request("GET", "/records/search/nearby", params=params, include_auth=True)
        if isinstance(result, list):
            return result
        return []
    
    def search_bbox(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float,
                   category_id: Optional[str] = None, media_type: Optional[str] = None,
                   skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for records within a bounding box using Bearer token"""
        # Validate parameters according to API spec
        if not (-90 <= min_lat <= 90) or not (-90 <= max_lat <= 90):
            raise ValueError("Latitude values must be between -90 and 90")
        if not (-180 <= min_lng <= 180) or not (-180 <= max_lng <= 180):
            raise ValueError("Longitude values must be between -180 and 180")
        if min_lat >= max_lat:
            raise ValueError("min_lat must be less than max_lat")
        if min_lng >= max_lng:
            raise ValueError("min_lng must be less than max_lng")
        if not (0 <= skip):
            raise ValueError("Skip must be >= 0")
        if not (1 <= limit <= 1000):
            raise ValueError("Limit must be between 1 and 1000")
        
        params = {
            "min_lat": min_lat,
            "min_lng": min_lng,
            "max_lat": max_lat,
            "max_lng": max_lng,
            "skip": skip,
            "limit": limit
        }
        if category_id:
            params["category_id"] = category_id
        if media_type:
            params["media_type"] = media_type
        
        result = self._make_request("GET", "/records/search/bbox", params=params, include_auth=True)
        if isinstance(result, list):
            return result
        return []
    
    def get_records_with_distance(self, latitude: float, longitude: float,
                                max_distance_meters: Optional[float] = None,
                                skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get records with calculated distances from a reference point using Bearer token"""
        # Validate parameters according to API spec
        if not (-90 <= latitude <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if max_distance_meters is not None and not (0 < max_distance_meters <= 100000):
            raise ValueError("Max distance must be between 0 and 100000 meters")
        if not (0 <= skip):
            raise ValueError("Skip must be >= 0")
        if not (1 <= limit <= 500):
            raise ValueError("Limit must be between 1 and 500")
        
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "skip": skip,
            "limit": limit
        }
        if max_distance_meters is not None:
            params["max_distance_meters"] = max_distance_meters
        
        result = self._make_request("GET", "/records/search/distance", params=params, include_auth=True)
        if isinstance(result, list):
            return result
        return []
    
    def upload_file_chunk(self, chunk_data: bytes, filename: str, chunk_index: int,
                         total_chunks: int, upload_uuid: str) -> Dict[str, Any]:
        """Upload a single chunk of a file using multipart/form-data"""
        
        # Prepare multipart form data as per API spec
        files = {
            'chunk': ('chunk', chunk_data, 'application/octet-stream'),
            'filename': (None, filename),
            'chunk_index': (None, str(chunk_index)),
            'total_chunks': (None, str(total_chunks)),
            'upload_uuid': (None, upload_uuid)
        }
        
        url = f"{self.base_url}/records/upload/chunk"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_auth.access_token}"
        }
        
        try:
            response = self.session.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Chunk upload failed: {str(e)}")
            if hasattr(e.response, 'text'):
                st.error(f"Response: {e.response.text}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON response: {str(e)}")
            return {"error": "Invalid response format"}
    
    def finalize_upload(self, title: str, description: str, category_id: str,
                       media_type: str, upload_uuid: str, filename: str, total_chunks: int,
                       language: str, latitude: Optional[float] = None, longitude: Optional[float] = None,
                       release_rights: str = "family_or_friend", use_uid_filename: bool = False) -> Optional[Dict[str, Any]]:
        """Finalize chunked upload and create a record using application/x-www-form-urlencoded"""
        
        if not api_auth.user_info or not api_auth.user_info.get("user_id"):
            st.error("User ID not available. Please login again.")
            return {"error": "User not authenticated"}
        
        # Prepare all required form data parameters as per API spec
        data = {
            "title": title,
            "description": description if description else "",
            "category_id": category_id,
            "user_id": api_auth.user_info.get("user_id"),
            "media_type": media_type,
            "upload_uuid": upload_uuid,
            "filename": filename,
            "total_chunks": total_chunks,  # Keep as integer
            "release_rights": release_rights,
            "language": language,
            "use_uid_filename": use_uid_filename  # Keep as boolean
        }
        
        # Add coordinates if provided (as numbers, not strings)
        if latitude is not None:
            data["latitude"] = latitude
        if longitude is not None:
            data["longitude"] = longitude
        
        # Make request with form data and Bearer token
        url = f"{self.base_url}/records/upload"
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_auth.access_token}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        try:
            response = self.session.post(url, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Upload finalization failed: {str(e)}")
            if hasattr(e.response, 'text'):
                st.error(f"Response: {e.response.text}")
            return {"error": str(e)}
        except json.JSONDecodeError as e:
            st.error(f"Invalid JSON response: {str(e)}")
            return {"error": "Invalid response format"}
    
    def upload_image_record(self, image_data: bytes, title: str, description: str,
                          location: Dict[str, float], language: str, category_id: str,
                          filename: str = None, release_rights: str = "family_or_friend") -> Optional[Dict[str, Any]]:
        """Upload an image record with chunked upload using proper settings"""
        try:
            # Validate image size
            if len(image_data) > MAX_FILE_SIZE:
                st.error(f"Image too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.1f}MB")
                return None
            
            # Generate unique upload ID
            upload_uuid = str(uuid.uuid4())
            
            # Use provided filename or generate one
            if not filename:
                filename = f"dialect_image_{upload_uuid}.jpg"
            
            # Validate file extension
            file_ext = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
            if file_ext not in SUPPORTED_IMAGE_FORMATS:
                st.error(f"Unsupported format. Supported: {', '.join(SUPPORTED_IMAGE_FORMATS)}")
                return None
            
            # Calculate chunks using config settings
            total_size = len(image_data)
            total_chunks = (total_size + CHUNK_SIZE - 1) // CHUNK_SIZE
            
            st.info(f"Uploading {filename} in {total_chunks} chunks...")
            
            # Upload chunks with progress
            progress_bar = st.progress(0)
            for i in range(total_chunks):
                start = i * CHUNK_SIZE
                end = min(start + CHUNK_SIZE, total_size)
                chunk = image_data[start:end]
                
                result = self.upload_file_chunk(
                    chunk_data=chunk,
                    filename=filename,
                    chunk_index=i,
                    total_chunks=total_chunks,
                    upload_uuid=upload_uuid
                )
                
                if "error" in result:
                    st.error(f"Failed to upload chunk {i+1}/{total_chunks}: {result.get('error')}")
                    return None
                
                # Update progress
                progress_bar.progress((i + 1) / total_chunks)
                st.write(f"Uploaded chunk {i+1}/{total_chunks}")
            
            st.success("All chunks uploaded successfully!")
            
            # Finalize upload with proper parameters
            st.info("Finalizing upload...")
            result = self.finalize_upload(
                title=title,
                description=description,
                category_id=category_id,
                media_type="image",
                upload_uuid=upload_uuid,
                filename=filename,
                total_chunks=total_chunks,
                language=language,
                latitude=location.get("latitude"),
                longitude=location.get("longitude"),
                release_rights=release_rights
            )
            
            if result and "error" not in result:
                st.success("Image uploaded successfully!")
                return result
            else:
                st.error(f"Upload finalization failed: {result.get('error') if result else 'Unknown error'}")
                return None
            
        except Exception as e:
            st.error(f"Image upload failed: {str(e)}")
            return None


# Global API records instance
api_records = CorpusAPIRecords()


def get_user_records_cached() -> List[Dict[str, Any]]:
    """Get user's records from API (cached)"""
    if not api_auth.is_authenticated():
        return []
    
    try:
        return api_records.get_records(limit=1000)
    except Exception as e:
        st.error(f"Failed to fetch your records: {str(e)}")
        return []


def get_user_records_for_map() -> List[Dict[str, Any]]:
    """Get user's image records for map display (Bearer token restricts to user's own records)"""
    if not api_auth.is_authenticated():
        return []
    
    try:
        # With Bearer token, this returns only the authenticated user's records
        records = api_records.get_records(media_type="image", limit=1000)
        
        if not records:
            st.info("📍 You haven't uploaded any image records yet. Upload your first dialect word to see it on the map!")
            return []
        
        # Transform records to match our app's expected format using new API structure
        transformed_records = []
        for record in records:
            # New API structure has location as nested object
            latitude = None
            longitude = None
            
            if record.get("location"):
                latitude = record["location"].get("latitude")
                longitude = record["location"].get("longitude")
            
            if latitude and longitude:
                transformed_records.append({
                    "id": record.get("uid"),
                    "dialect_word": record.get("title"),
                    "location_text": record.get("description", ""),
                    "latitude": latitude,
                    "longitude": longitude,
                    "image_path": record.get("file_url"),
                    "is_verified": record.get("reviewed", False),
                    "user_id": record.get("user_id"),
                    "created_at": record.get("created_at"),
                    "updated_at": record.get("updated_at"),
                    "language": record.get("language"),
                    "media_type": record.get("media_type"),
                    "release_rights": record.get("release_rights"),
                    "status": record.get("status"),
                    "file_name": record.get("file_name"),
                    "file_size": record.get("file_size"),
                    "reviewed_by": record.get("reviewed_by"),
                    "reviewed_at": record.get("reviewed_at"),
                    "duration_seconds": record.get("duration_seconds"),
                    "category_id": record.get("category_id")
                })
        
        return transformed_records
    except Exception as e:
        st.error(f"Failed to fetch your records: {str(e)}")
        return []


def get_random_user_record() -> Optional[Dict[str, Any]]:
    """Get a random record from user's own records"""
    if not api_auth.is_authenticated():
        return None
    
    try:
        records = api_records.get_records(media_type="image", limit=100)
        if records:
            import random
            record = random.choice(records)
            return {
                "id": record.get("uid"),
                "dialect_word": record.get("title"),
                "location_text": record.get("description", ""),
                "language": record.get("language"),
                "status": record.get("status")
            }
        return None
    except Exception as e:
        st.error(f"Failed to fetch your records: {str(e)}")
        return None


def add_record_to_api(dialect_word: str, location_text: str, image_data: bytes,
                     latitude: float, longitude: float, category_id: Optional[str] = None,
                     language: str = "hindi", release_rights: str = "family_or_friend") -> Optional[str]:
    """Add a new record to the API"""
    if not api_auth.is_authenticated():
        st.error("Please login to submit records")
        return None
    
    # Get or create default category if none provided
    if not category_id:
        default_category = get_default_category()
        if default_category:
            category_id = default_category.get("id") or default_category.get("category_id")
        else:
            st.error("No category available. Please create a category first.")
            return None
    
    result = api_records.upload_image_record(
        image_data=image_data,
        title=dialect_word,
        description=location_text,
        location={"latitude": latitude, "longitude": longitude},
        language=language,
        category_id=category_id,
        release_rights=release_rights
    )
    
    if result:
        return result.get("uid")
    return None


def get_image_from_api(record_id: str) -> Optional[bytes]:
    """Get image data from API record"""
    if not api_auth.is_authenticated():
        return None
    
    # Handle demo data
    if record_id.startswith("demo_"):
        return None  # Demo records don't have images
    
    try:
        record = api_records.get_record(record_id)
        if record and record.get("file_url"):
            try:
                response = requests.get(record["file_url"])
                response.raise_for_status()
                return response.content
            except Exception as e:
                st.error(f"Failed to fetch image: {str(e)}")
                return None
        return None
    except Exception as e:
        st.error(f"Failed to get record: {str(e)}")
        return None
