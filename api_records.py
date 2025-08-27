import requests
import streamlit as st
import json
import uuid
import io
from typing import Optional, Dict, Any, List
from PIL import Image
import base64
from api_auth import api_auth
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
        """Get request headers"""
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
        """Get all records with optional filtering and pagination"""
        params = {
            "skip": skip,
            "limit": limit
        }
        if category_id:
            params["category_id"] = category_id
        if user_id:
            params["user_id"] = user_id
        if media_type:
            params["media_type"] = media_type
        
        result = self._make_request("GET", "/records/", params=params)
        if isinstance(result, list):
            return result
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
    
    def search_nearby(self, latitude: float, longitude: float, distance_meters: int = 5000,
                     category_id: Optional[str] = None, media_type: Optional[str] = None,
                     skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for records within a specified distance of a point"""
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
        
        result = self._make_request("GET", "/records/search/nearby", params=params)
        if isinstance(result, list):
            return result
        return []
    
    def search_bbox(self, min_lat: float, min_lng: float, max_lat: float, max_lng: float,
                   category_id: Optional[str] = None, media_type: Optional[str] = None,
                   skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Search for records within a bounding box"""
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
        
        result = self._make_request("GET", "/records/search/bbox", params=params)
        if isinstance(result, list):
            return result
        return []
    
    def get_records_with_distance(self, latitude: float, longitude: float,
                                max_distance_meters: Optional[int] = None,
                                skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get records with calculated distances from a reference point"""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "skip": skip,
            "limit": limit
        }
        if max_distance_meters:
            params["max_distance_meters"] = max_distance_meters
        
        result = self._make_request("GET", "/records/search/distance", params=params)
        if isinstance(result, list):
            return result
        return []
    
    def upload_file_chunk(self, chunk_data: bytes, filename: str, chunk_index: int,
                         total_chunks: int, upload_uuid: str) -> bool:
        """Upload a single chunk of a file"""
        files = {
            "chunk": (filename, chunk_data, "application/octet-stream")
        }
        data = {
            "filename": filename,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
            "upload_uuid": upload_uuid
        }
        
        result = self._make_request("POST", "/records/upload/chunk", data=data, files=files)
        return "error" not in result
    
    def finalize_upload(self, title: str, description: str, category_id: str,
                       media_type: str, upload_uuid: str, filename: str, total_chunks: int,
                       language: str, latitude: Optional[float] = None, longitude: Optional[float] = None,
                       release_rights: str = "creator", use_uid_filename: bool = False) -> Optional[Dict[str, Any]]:
        """Finalize chunked upload and create a record"""
        data = {
            "title": title,
            "description": description,
            "category_id": category_id,
            "user_id": api_auth.user_info.get("user_id") if api_auth.user_info else None,
            "media_type": media_type,
            "upload_uuid": upload_uuid,
            "filename": filename,
            "total_chunks": total_chunks,
            "release_rights": release_rights,
            "language": language,
            "use_uid_filename": use_uid_filename
        }
        
        if latitude is not None:
            data["latitude"] = latitude
        if longitude is not None:
            data["longitude"] = longitude
        
        result = self._make_request("POST", "/records/upload", data=data)
        if "error" not in result:
            return result
        return None
    
    def upload_image_record(self, image_data: bytes, title: str, description: str,
                          location: Dict[str, float], language: str, category_id: str) -> Optional[Dict[str, Any]]:
        """Upload an image record with chunked upload"""
        try:
            # Generate upload UUID
            upload_uuid = str(uuid.uuid4())
            filename = f"dialect_image_{upload_uuid}.jpg"
            
            # Convert image to JPEG if needed
            image = Image.open(io.BytesIO(image_data))
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            
            # Save as JPEG
            img_buffer = io.BytesIO()
            image.save(img_buffer, format="JPEG", quality=85)
            img_data = img_buffer.getvalue()
            
            # Split into chunks (1MB chunks)
            chunk_size = 1024 * 1024
            chunks = [img_data[i:i + chunk_size] for i in range(0, len(img_data), chunk_size)]
            total_chunks = len(chunks)
            
            # Upload chunks
            for i, chunk in enumerate(chunks):
                if not self.upload_file_chunk(chunk, filename, i, total_chunks, upload_uuid):
                    st.error(f"Failed to upload chunk {i + 1}/{total_chunks}")
                    return None
            
            # Finalize upload
            return self.finalize_upload(
                title=title,
                description=description,
                category_id=category_id,
                media_type="image",
                upload_uuid=upload_uuid,
                filename=filename,
                total_chunks=total_chunks,
                language=language,
                latitude=location.get("latitude"),
                longitude=location.get("longitude")
            )
            
        except Exception as e:
            st.error(f"Image upload failed: {str(e)}")
            return None


# Global API records instance
api_records = CorpusAPIRecords()


def get_all_records_cached() -> List[Dict[str, Any]]:
    """Get all records from API (cached)"""
    if not api_auth.is_authenticated():
        return []
    
    try:
        return api_records.get_records(limit=1000)
    except Exception as e:
        st.error(f"Failed to fetch all records: {str(e)}")
        return []


def get_records_for_map() -> List[Dict[str, Any]]:
    """Get records suitable for map display"""
    if not api_auth.is_authenticated():
        return []
    
    try:
        records = api_records.get_records(media_type="image", limit=1000)
        
        # Transform records to match our app's expected format
        transformed_records = []
        for record in records:
            if record.get("location") and record.get("location").get("latitude") and record.get("location").get("longitude"):
                transformed_records.append({
                    "id": record.get("uid"),
                    "dialect_word": record.get("title"),
                    "location_text": record.get("description", ""),
                    "latitude": record.get("location", {}).get("latitude"),
                    "longitude": record.get("location", {}).get("longitude"),
                    "image_path": record.get("file_url"),
                    "is_verified": record.get("reviewed", False),
                    "user_id": record.get("user_id"),
                    "created_at": record.get("created_at")
                })
        
        return transformed_records
    except Exception as e:
        st.error(f"Failed to fetch records: {str(e)}")
        return []


def get_random_record() -> Optional[Dict[str, Any]]:
    """Get a random record for display"""
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
                "location_text": record.get("description", "")
            }
        return None
    except Exception as e:
        st.error(f"Failed to fetch random record: {str(e)}")
        return None


def add_record_to_api(dialect_word: str, location_text: str, image_data: bytes,
                     latitude: float, longitude: float, category_id: Optional[str] = None) -> Optional[str]:
    """Add a new record to the API"""
    if not api_auth.is_authenticated():
        st.error("Please login to submit records")
        return None
    
    # Get or create default category if none provided
    if not category_id:
        default_category = get_default_category()
        if default_category:
            category_id = default_category.get("id")
        else:
            st.error("No category available. Please create a category first.")
            return None
    
    # Default language
    language = "hindi"  # In a full implementation, this could be detected or selected
    
    result = api_records.upload_image_record(
        image_data=image_data,
        title=dialect_word,
        description=location_text,
        location={"latitude": latitude, "longitude": longitude},
        language=language,
        category_id=category_id
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
