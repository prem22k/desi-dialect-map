"""Configuration settings for the Dialect Map application"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API settings
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.corpus.swecha.org")
VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"

# File upload settings for images
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1024 * 1024))  # 1MB chunks
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 100 * 1024 * 1024))  # 100MB max

# Supported image formats
SUPPORTED_IMAGE_FORMATS = os.getenv(
    "SUPPORTED_IMAGE_FORMATS", 
    "jpg,jpeg,png,gif,bmp,webp,svg,tiff,ico,heic,heif"
).split(",")

# Image upload specific settings
IMAGE_QUALITY = 85  # JPEG quality for compression
MAX_IMAGE_DIMENSION = 2048  # Max width/height in pixels
THUMBNAIL_SIZE = (300, 300)  # Thumbnail dimensions

# Upload validation
MIN_IMAGE_SIZE = 1024  # 1KB minimum
ALLOWED_MIME_TYPES = [
    "image/jpeg", "image/jpg", "image/png", "image/gif", 
    "image/bmp", "image/webp", "image/svg+xml", "image/tiff",
    "image/x-icon", "image/heic", "image/heif"
]
