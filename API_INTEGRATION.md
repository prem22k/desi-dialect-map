# 🚀 Indic Corpus Collections API Integration

## Overview

The Desi Dialect Map now integrates with the **Indic Corpus Collections API**, providing enhanced functionality for dialect data collection, management, and analysis. This integration allows users to:

- 📤 Submit dialect records to a centralized database
- 🗺️ Browse and search records from across India
- 📊 View analytics and user contributions
- 🔍 Search nearby records and filter by categories
- 👤 Manage user profiles and authentication

## 🔧 Implemented APIs

### 1. Authentication & User Management

#### ✅ **POST /api/v1/auth/login**
- **Purpose**: User login to get access token
- **Implementation**: `api_client.login(username, password)`
- **Usage**: Login form in API Mode tab

#### ✅ **POST /api/v1/auth/signup/send-otp**
- **Purpose**: User registration with OTP verification
- **Implementation**: `api_client.register_user(username, email, password, phone)`
- **Usage**: Registration form in API Mode tab

#### ✅ **GET /api/v1/auth/me**
- **Purpose**: Get current user profile
- **Implementation**: `api_client.get_user_profile()`
- **Usage**: Display user information and contributions

### 2. Records Management

#### ✅ **POST /api/v1/records/**
- **Purpose**: Create new dialect records
- **Implementation**: `api_client.create_record(dialect_word, location_text, latitude, longitude, image_data, audio_data, category_id)`
- **Usage**: Enhanced submission form with media upload

#### ✅ **GET /api/v1/records/**
- **Purpose**: Search and list records
- **Implementation**: `api_client.search_records(query, category_id, limit)`
- **Usage**: Browse records with search and filtering

#### ✅ **GET /api/v1/records/search/nearby**
- **Purpose**: Find records near a location
- **Implementation**: `api_client.get_records_nearby(latitude, longitude, radius_km)`
- **Usage**: Geographic search functionality

#### ✅ **GET /api/v1/records/search/bbox**
- **Purpose**: Find records within a bounding box
- **Implementation**: `api_client.get_records_in_bbox(min_lat, max_lat, min_lon, max_lon)`
- **Usage**: Map-based record discovery

#### ✅ **POST /api/v1/records/upload**
- **Purpose**: Upload media files for records
- **Implementation**: `api_client._upload_media(record_id, image_data, audio_data)`
- **Usage**: Automatic media upload when creating records

#### ✅ **PATCH /api/v1/records/{record_id}**
- **Purpose**: Update existing records
- **Implementation**: `api_client.update_record(record_id, updates)`
- **Usage**: Record editing functionality

#### ✅ **DELETE /api/v1/records/{record_id}**
- **Purpose**: Delete records
- **Implementation**: `api_client.delete_record(record_id)`
- **Usage**: Record management

### 3. User Contributions

#### ✅ **GET /api/v1/users/{user_id}/contributions**
- **Purpose**: Get user's contributions
- **Implementation**: `api_client.get_user_contributions(user_id)`
- **Usage**: User profile and analytics

### 4. Categories

#### ✅ **GET /api/v1/categories/**
- **Purpose**: Get available categories
- **Implementation**: `api_client.get_categories()`
- **Usage**: Category filtering and organization

## 🎯 Key Features

### 1. **Dual Mode Operation**
- **Local Mode**: Original SQLite-based functionality
- **API Mode**: Enhanced cloud-based functionality

### 2. **Enhanced Submission Form**
- Image and audio upload support
- Category selection
- Geographic coordinates
- Real-time validation

### 3. **Advanced Search & Discovery**
- Text-based search
- Category filtering
- Geographic search (nearby records)
- Bounding box search

### 4. **User Analytics**
- Contribution tracking
- Media type breakdown
- Recent activity
- Performance metrics

### 5. **Interactive Maps**
- API records visualization
- Geographic clustering
- Popup information
- Layer controls

## 📁 File Structure

```
├── api_client.py          # Main API client implementation
├── api_auth_ui.py         # Authentication and UI components
├── api_config.py          # Configuration and settings
├── app.py                 # Updated main app with API integration
└── API_INTEGRATION.md     # This documentation
```

## 🔄 API Client Architecture

### Core Components

1. **IndicCorpusAPI Class**
   - Handles all API interactions
   - Manages authentication tokens
   - Provides error handling and retry logic

2. **Session Management**
   - Automatic token refresh
   - Persistent authentication
   - Secure credential handling

3. **Media Handling**
   - Image and audio upload
   - Format validation
   - File size limits

4. **Geographic Features**
   - Coordinate validation
   - Distance calculations
   - Bounding box operations

## 🚀 Usage Guide

### 1. **Accessing API Mode**
1. Open the Desi Dialect Map app
2. Click on the "🚀 API Mode" tab
3. Login or register for an API account

### 2. **Submitting Records**
1. Navigate to the "📤 Submit" tab
2. Fill in dialect word and location
3. Upload image/audio (optional)
4. Select category (optional)
5. Click "Submit to API"

### 3. **Browsing Records**
1. Go to the "🗺️ Browse" tab
2. Use search and filter options
3. View records in table format
4. Explore geographic distribution on map

### 4. **Viewing Analytics**
1. Access the "📊 Analytics" tab
2. View your contribution statistics
3. Check recent activity
4. Explore available categories

## ⚙️ Configuration

### Environment Variables
```bash
# API Configuration
API_BASE_URL=https://api.indiccorpus.org
API_TIMEOUT=30
API_RETRIES=3

# Feature Flags
ENABLE_API_INTEGRATION=true
ENABLE_USER_AUTHENTICATION=true
ENABLE_MEDIA_UPLOAD=true
```

### Feature Flags
- `api_integration`: Enable/disable API features
- `user_authentication`: Enable user login/registration
- `record_management`: Enable record CRUD operations
- `media_upload`: Enable file upload functionality
- `geographic_search`: Enable location-based search
- `analytics`: Enable user analytics

## 🔒 Security Features

### Authentication
- JWT token-based authentication
- Automatic token refresh
- Secure credential storage
- Session management

### Data Protection
- HTTPS communication
- Input validation
- File type restrictions
- Size limits

### Privacy Controls
- User-specific data access
- Public/private record settings
- Contribution tracking
- Data export controls

## 📊 Error Handling

### Common Error Scenarios
1. **Network Issues**: Connection timeout handling
2. **Authentication**: Token expiration and refresh
3. **Validation**: Input data validation
4. **File Upload**: Size and format restrictions
5. **Rate Limiting**: Request throttling

### Error Recovery
- Automatic retry logic
- User-friendly error messages
- Graceful degradation
- Fallback to local mode

## 🔮 Future Enhancements

### Planned Features
1. **Real-time Updates**: WebSocket integration
2. **Advanced Analytics**: Machine learning insights
3. **Collaborative Features**: User interactions
4. **Mobile Support**: Responsive design
5. **Offline Mode**: Local caching

### API Extensions
1. **Batch Operations**: Bulk record management
2. **Advanced Search**: Full-text search
3. **Data Export**: Multiple format support
4. **Integration APIs**: Third-party connections
5. **Webhooks**: Event notifications

## 🛠️ Development

### Testing
```bash
# Test API connectivity
python -c "import api_client; print('API client loaded successfully')"

# Test authentication
python -c "from api_client import api_client; print(api_client.login('test', 'test'))"
```

### Debugging
- Enable debug mode in `api_config.py`
- Check request logs
- Monitor network traffic
- Validate API responses

### Contributing
1. Follow API documentation
2. Test all endpoints
3. Handle errors gracefully
4. Maintain backward compatibility

## 📞 Support

### Documentation
- API specification: `/api/v1/openapi.json`
- Interactive docs: API endpoint documentation
- Code examples: Implementation samples

### Troubleshooting
1. Check network connectivity
2. Verify API credentials
3. Review error logs
4. Test with simple requests

### Contact
- API Support: Contact the Indic Corpus team
- App Issues: Check GitHub repository
- Feature Requests: Submit via issue tracker

---

**Note**: This integration enhances the Desi Dialect Map with enterprise-grade features while maintaining the original local functionality. Users can choose between local and API modes based on their needs and connectivity.
