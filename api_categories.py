import requests
import streamlit as st
import json
from typing import Optional, Dict, Any, List
from api_auth import api_auth

# API Configuration
API_BASE_URL = "https://api.corpus.swecha.org"
API_VERSION = "v1"

class CorpusAPICategories:
    """Categories management handler for Indic Corpus Collections API"""
    
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
                     include_auth: bool = True) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(include_auth)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=headers, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=headers, json=data)
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
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories"""
        result = self._make_request("GET", "/categories/")
        if isinstance(result, list):
            return result
        return []
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        result = self._make_request("GET", f"/categories/{category_id}")
        if "error" not in result:
            return result
        return None
    
    def create_category(self, name: str, title: str, description: str = "", 
                       published: bool = False, rank: int = 0) -> Optional[Dict[str, Any]]:
        """Create a new category"""
        data = {
            "name": name,
            "title": title,
            "description": description,
            "published": published,
            "rank": rank
        }
        
        result = self._make_request("POST", "/categories/", data=data)
        if "error" not in result:
            return result
        return None
    
    def update_category(self, category_id: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a category"""
        result = self._make_request("PUT", f"/categories/{category_id}", data=kwargs)
        if "error" not in result:
            return result
        return None
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category"""
        result = self._make_request("DELETE", f"/categories/{category_id}")
        return "error" not in result


# Global API categories instance
api_categories = CorpusAPICategories()


def get_categories_cached() -> List[Dict[str, Any]]:
    """Get all categories from API (cached)"""
    if not api_auth.is_authenticated():
        return []
    
    try:
        return api_categories.get_categories()
    except Exception as e:
        st.error(f"Failed to fetch categories: {str(e)}")
        return []


def get_published_categories() -> List[Dict[str, Any]]:
    """Get only published categories"""
    categories = get_categories_cached()
    return [cat for cat in categories if cat.get("published", False)]


def get_category_by_id(category_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific category by ID"""
    if not api_auth.is_authenticated():
        return None
    
    return api_categories.get_category(category_id)


def create_dialect_category(name: str, title: str, description: str = "") -> Optional[Dict[str, Any]]:
    """Create a new dialect category"""
    if not api_auth.is_authenticated():
        st.error("Please login to create categories")
        return None
    
    return api_categories.create_category(
        name=name,
        title=title,
        description=description,
        published=True,
        rank=0
    )


def get_default_category() -> Optional[Dict[str, Any]]:
    """Get or create a default category for dialect records"""
    categories = get_published_categories()
    
    # Look for a default dialect category
    for category in categories:
        if "dialect" in category.get("name", "").lower() or "language" in category.get("name", "").lower():
            return category
    
    # If no dialect category exists, create one
    if api_auth.is_authenticated():
        default_category = create_dialect_category(
            name="dialect_words",
            title="Dialect Words",
            description="Words and phrases from various Indian dialects and languages"
        )
        return default_category
    
    return None


def get_category_options() -> List[tuple]:
    """Get category options for dropdown selection"""
    categories = get_published_categories()
    options = [("Select a category", None)]
    
    for category in categories:
        options.append((category.get("title", category.get("name", "Unknown")), category.get("id")))
    
    return options


def format_category_display(category: Dict[str, Any]) -> str:
    """Format category for display"""
    title = category.get("title", "")
    name = category.get("name", "")
    description = category.get("description", "")
    
    if title and title != name:
        return f"{title} ({name})"
    return name or "Unknown Category"


def get_category_statistics() -> Dict[str, Any]:
    """Get statistics about categories"""
    try:
        categories = get_categories_cached()
        
        stats = {
            "total_categories": len(categories),
            "published_categories": len([c for c in categories if c.get("published", False)]),
            "unpublished_categories": len([c for c in categories if not c.get("published", False)]),
            "categories_by_rank": {}
        }
        
        # Group by rank
        for category in categories:
            rank = category.get("rank", 0)
            if rank not in stats["categories_by_rank"]:
                stats["categories_by_rank"][rank] = 0
            stats["categories_by_rank"][rank] += 1
        
        return stats
    except Exception as e:
        st.error(f"Failed to get category statistics: {str(e)}")
        return {
            "total_categories": 0,
            "published_categories": 0,
            "unpublished_categories": 0,
            "categories_by_rank": {}
        }
