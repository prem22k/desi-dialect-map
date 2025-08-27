# Indic Corpus Collections API Integration Guide

## 🎯 **Overview**

This guide explains how to integrate the **Indic Corpus Collections API** with your Desi Dialect Map project. The API provides professional authentication, data management, and advanced features for your dialect collection platform.

## 🚀 **What the API Provides**

### **✅ Authentication & User Management**
- **Secure Login/Logout** with username/password
- **OTP-based Authentication** for enhanced security
- **User Registration** with phone verification
- **Token-based Sessions** with automatic refresh
- **Password Management** (change, reset, forgot)

### **✅ Data Management**
- **Records CRUD Operations** (Create, Read, Update, Delete)
- **File Upload** with metadata
- **Categories Management** for organizing content
- **Search & Filtering** by location, category, etc.
- **Bulk Operations** for data processing

### **✅ Advanced Features**
- **Audio Processing** for pronunciation recordings
- **Content Analysis** using AI/ML
- **Geographic Search** (nearby, bounding box)
- **Statistics Generation** and reporting
- **Task Management** for background processing

### **✅ Professional Features**
- **Role-based Access Control**
- **User Contributions Tracking**
- **System Health Monitoring**
- **Data Export & Backup**
- **Notification System**

## 🔧 **Setup Instructions**

### **Step 1: Environment Configuration**

Create a `.env` file in your project root:

```bash
# API Configuration
INDIC_CORPUS_API_URL=https://your-api-endpoint.com
INDIC_CORPUS_API_KEY=your_api_key_here

# Optional: Override default settings
API_TIMEOUT=30
API_RETRY_ATTEMPTS=3
```

### **Step 2: Install Dependencies**

The required dependencies are already in `requirements.txt`:

```bash
pip install -r requirements.txt
```

### **Step 3: Choose Your Integration Approach**

#### **Option A: Full Integration (Recommended)**
Use `app_with_api.py` for complete API integration:

```bash
streamlit run app_with_api.py
```

#### **Option B: Minimal Integration**
Add API features to your existing `app.py`:

```python
import api_client as api

# Add to your sidebar or main app
if st.button("API Integration"):
    api.api_login_ui()
```

## 📱 **API Features in Detail**

### **1. Authentication System**

#### **Login Methods:**
```python
from api_client import get_api_client

api_client = get_api_client()

# Username/Password Login
response = api_client.login("username", "password")

# OTP-based Login
api_client.login_with_otp("+91XXXXXXXXXX")
api_client.verify_login_otp("+91XXXXXXXXXX", "123456")

# User Registration
api_client.signup_send_otp("+91XXXXXXXXXX")
api_client.signup_verify_otp("+91XXXXXXXXXX", "123456", "username", "password")
```

#### **Session Management:**
```python
# Check authentication status
if api_client.is_authenticated():
    user_info = api_client.get_current_user()
    print(f"Logged in as: {user_info['username']}")

# Refresh token
api_client.refresh_token()

# Logout
api_client.logout()
```

### **2. Data Synchronization**

#### **Sync Local Data to API:**
```python
# Get local submissions
import database as db
conn = db.create_connection()
local_submissions = db.get_all_submissions(conn, public_only=False)

# Sync with API
result = api_client.sync_local_data(local_submissions.to_dict('records'))
print(f"Synced {result['synced_count']}/{result['total_count']} submissions")
```

#### **Create Records in API:**
```python
record_data = {
    "dialect_word": "Cycle",
    "location_text": "Hyderabad",
    "latitude": 17.3850,
    "longitude": 78.4867,
    "category_id": "dialect_word",
    "media_type": "image",
    "is_public": True,
    "metadata": {
        "local_id": "uuid-here",
        "user_id": "user-uuid",
        "timestamp": "2024-01-01T00:00:00Z"
    }
}

response = api_client.create_record(record_data)
if "id" in response:
    print(f"Record created with ID: {response['id']}")
```

### **3. Advanced Search & Filtering**

#### **Geographic Search:**
```python
# Search nearby records
nearby_records = api_client.search_records_nearby(
    latitude=17.3850,
    longitude=78.4867,
    radius=10.0  # km
)

# Search within bounding box
bbox_records = api_client.search_records_bbox(
    min_lat=17.0, min_lon=78.0,
    max_lat=18.0, max_lon=79.0
)
```

#### **Category-based Search:**
```python
# Get records by category
records = api_client.get_records(
    skip=0,
    limit=100,
    category_id="dialect_word"
)
```

### **4. File Upload & Management**

#### **Upload with File:**
```python
metadata = {
    "dialect_word": "Cycle",
    "location_text": "Hyderabad",
    "category_id": "dialect_word"
}

response = api_client.upload_record(
    file_path="path/to/image.jpg",
    metadata=metadata
)
```

### **5. Task Management**

#### **Background Processing:**
```python
# Start audio processing
task = api_client.start_audio_processing("record_id")

# Start content analysis
task = api_client.start_content_analysis("record_id")

# Check task status
status = api_client.get_task_status(task["task_id"])

# Cancel task if needed
api_client.cancel_task(task["task_id"])
```

## 🎨 **UI Integration Examples**

### **Streamlit Authentication UI:**
```python
import streamlit as st
import api_client as api

# Show login form
if not st.session_state.get("api_authenticated"):
    api.api_login_ui()
else:
    api.api_user_info()
```

### **Data Sync UI:**
```python
# Show sync options
api.sync_data_ui()

# Show API status
api.api_status_check()
```

### **Custom Integration:**
```python
# Add API features to existing app
with st.sidebar:
    st.header("API Integration")
    
    if st.button("Login to API"):
        api.api_login_ui()
    
    if st.button("Sync Data"):
        api.sync_data_ui()
    
    if st.button("API Status"):
        api.api_status_check()
```

## 🔒 **Security Best Practices**

### **1. Environment Variables**
- Never hardcode API keys in your code
- Use `.env` files for local development
- Use Streamlit secrets for production deployment

### **2. Token Management**
- Store tokens securely in session state
- Implement automatic token refresh
- Clear tokens on logout

### **3. Error Handling**
- Always handle API errors gracefully
- Provide user-friendly error messages
- Log errors for debugging

### **4. Data Validation**
- Validate data before sending to API
- Sanitize user inputs
- Handle missing or invalid data

## 🚀 **Deployment Considerations**

### **Streamlit Cloud Deployment:**
1. **Add API credentials to Streamlit secrets:**
   ```toml
   # .streamlit/secrets.toml
   INDIC_CORPUS_API_URL = "https://your-api-endpoint.com"
   INDIC_CORPUS_API_KEY = "your_api_key_here"
   ```

2. **Update environment variable access:**
   ```python
   import streamlit as st
   
   api_url = st.secrets.get("INDIC_CORPUS_API_URL")
   api_key = st.secrets.get("INDIC_CORPUS_API_KEY")
   ```

### **Local Development:**
1. **Create `.env` file:**
   ```bash
   INDIC_CORPUS_API_URL=https://your-api-endpoint.com
   INDIC_CORPUS_API_KEY=your_api_key_here
   ```

2. **Load environment variables:**
   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

## 📊 **API Response Formats**

### **Authentication Responses:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "user-uuid",
    "username": "username",
    "email": "user@example.com",
    "phone": "+91XXXXXXXXXX"
  }
}
```

### **Record Responses:**
```json
{
  "id": "record-uuid",
  "dialect_word": "Cycle",
  "location_text": "Hyderabad",
  "latitude": 17.3850,
  "longitude": 78.4867,
  "category_id": "dialect_word",
  "media_type": "image",
  "is_public": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### **Error Responses:**
```json
{
  "error": "Authentication failed",
  "detail": "Invalid username or password",
  "status_code": 401
}
```

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **API Connection Failed:**
   - Check API URL in environment variables
   - Verify network connectivity
   - Check API server status

2. **Authentication Errors:**
   - Verify API key is correct
   - Check token expiration
   - Ensure proper authorization headers

3. **Data Sync Issues:**
   - Validate data format before sending
   - Check for required fields
   - Handle API rate limits

4. **File Upload Problems:**
   - Verify file format is supported
   - Check file size limits
   - Ensure proper file permissions

### **Debug Mode:**
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Test API connection
api_client = get_api_client()
health = api_client.health_check()
print(f"API Health: {health}")
```

## 📈 **Performance Optimization**

### **1. Caching:**
```python
@st.cache_data(ttl=300)
def get_api_records():
    api_client = get_api_client()
    return api_client.get_records(limit=100)
```

### **2. Batch Operations:**
```python
# Sync data in batches
def sync_data_in_batches(local_data, batch_size=50):
    for i in range(0, len(local_data), batch_size):
        batch = local_data[i:i + batch_size]
        result = api_client.sync_local_data(batch)
        print(f"Synced batch {i//batch_size + 1}")
```

### **3. Error Recovery:**
```python
def robust_api_call(func, max_retries=3):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
```

## 🎯 **Next Steps**

1. **Test the API integration** with your existing data
2. **Customize the UI** to match your app's design
3. **Implement advanced features** like audio processing
4. **Set up monitoring** for API usage and performance
5. **Plan data migration** strategy for production

## 📞 **Support**

For API-specific questions or issues:
- Check the API documentation
- Review error logs and responses
- Test with API health endpoints
- Contact API provider support

---

**🎉 You're now ready to integrate the Indic Corpus Collections API with your Desi Dialect Map project!**
