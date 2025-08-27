"""
Configuration for Indic Corpus Collections API
"""

# API Configuration
API_BASE_URL = "https://api.indiccorpus.org"  # Replace with actual API URL when available

# API Endpoints
ENDPOINTS = {
    "auth": {
        "login": "/api/v1/auth/login",
        "register": "/api/v1/auth/signup/send-otp",
        "profile": "/api/v1/auth/me",
        "refresh": "/api/v1/auth/refresh",
    },
    "records": {
        "create": "/api/v1/records/",
        "list": "/api/v1/records/",
        "get": "/api/v1/records/{record_id}",
        "update": "/api/v1/records/{record_id}",
        "delete": "/api/v1/records/{record_id}",
        "upload": "/api/v1/records/upload",
        "nearby": "/api/v1/records/search/nearby",
        "bbox": "/api/v1/records/search/bbox",
    },
    "users": {
        "contributions": "/api/v1/users/{user_id}/contributions",
        "profile": "/api/v1/users/{user_id}",
    },
    "categories": {
        "list": "/api/v1/categories/",
        "get": "/api/v1/categories/{category_id}",
    }
}

# Default settings
DEFAULT_TIMEOUT = 30  # seconds
DEFAULT_RETRIES = 3
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

# Supported media types
SUPPORTED_IMAGE_TYPES = ["jpg", "jpeg", "png", "gif"]
SUPPORTED_AUDIO_TYPES = ["wav", "mp3", "m4a", "ogg"]

# Error messages
ERROR_MESSAGES = {
    "connection": "Unable to connect to Indic Corpus API. Please check your internet connection.",
    "authentication": "Authentication failed. Please check your credentials.",
    "permission": "You don't have permission to perform this action.",
    "not_found": "The requested resource was not found.",
    "validation": "Invalid data provided. Please check your input.",
    "server_error": "Server error occurred. Please try again later.",
    "timeout": "Request timed out. Please try again.",
}

# Success messages
SUCCESS_MESSAGES = {
    "login": "Successfully logged in to Indic Corpus API!",
    "register": "Registration initiated! Please check your email/phone for OTP verification.",
    "record_created": "Record created successfully!",
    "record_updated": "Record updated successfully!",
    "record_deleted": "Record deleted successfully!",
    "upload_success": "File uploaded successfully!",
}

# Feature flags
FEATURES = {
    "api_integration": True,
    "user_authentication": True,
    "record_management": True,
    "media_upload": True,
    "geographic_search": True,
    "analytics": True,
    "categories": True,
}

# Development settings
DEBUG = False  # Set to True for development
LOG_REQUESTS = False  # Set to True to log API requests

# Rate limiting
RATE_LIMIT = {
    "requests_per_minute": 60,
    "requests_per_hour": 1000,
}

# Cache settings
CACHE_TTL = 300  # 5 minutes
CACHE_ENABLED = True
