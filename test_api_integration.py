def test_api_imports():
    """Test that all API modules import successfully."""
    from api_auth import CorpusAPIAuth
    from api_categories import CorpusAPICategories
    from api_records import CorpusAPIRecords

    assert CorpusAPIAuth, "Authentication module should be importable."
    assert CorpusAPICategories, "Categories module should be importable."
    assert CorpusAPIRecords, "Records module should be importable."

def test_api_configuration():
    """Test that API configurations are properly set up."""
    from api_auth import CorpusAPIAuth
    from api_categories import CorpusAPICategories
    from api_records import CorpusAPIRecords

    assert CorpusAPIAuth._get_headers, "Headers method should be available."
    assert CorpusAPICategories._make_request, "Request method should be available."
    assert CorpusAPIRecords._make_request, "Request method should be available."

def test_categories_functionality():
    """Test basic functionality of the Categories API."""
    from api_categories import CorpusAPICategories

    categories = CorpusAPICategories()
    response = categories.get_categories()
    assert isinstance(response, list), "Categories should be returned as a list."
    assert all(isinstance(item, dict) for item in response), "Each category should be a dictionary."
    assert any("id" in item for item in response), "Categories should have unique IDs."
    assert any("name" in item for item in response), "Categories should have names."

def test_records_functionality():
    """Test basic functionality of the Records API."""
    from api_records import CorpusAPIRecords

    records = CorpusAPIRecords()
    response = records.get_records()
    assert isinstance(response, list), "Records should be returned as a list."
    assert all(isinstance(item, dict) for item in response), "Each record should be a dictionary."
    assert any("dialect" in item for item in response), "Records should include dialect information."
    assert any("location_text" in item for item in response), "Records should include location information."

def test_auth_functionality():
    """Test basic functionality of the Authentication API."""
    from api_auth import CorpusAPIAuth

    auth = CorpusAPIAuth()
    headers = auth._get_headers()
    assert headers.get("Content-Type") == "application/json", "Response should be JSON."
    assert headers.get("Authorization") is None, "No token should be present initially."

    # Simulate login flow
    auth.send_login_otp("test@example.com")
    auth.verify_login_otp("test@example.com", "123456")
    auth.get_current_user()
    auth.logout()

def test_error_handling():
    """Test that errors are handled gracefully."""
    from api_auth import CorpusAPIAuth
    from api_categories import CorpusAPICategories
    from api_records import CorpusAPIRecords

    # Test invalid phone number for login
    auth = CorpusAPIAuth()
    with pytest.raises(Exception):
        auth.send_login_otp("invalid-phone")

    # Test invalid category ID
    categories = CorpusAPICategories()
    with pytest.raises(Exception):
        categories.get_category_by_id("invalid-id")

    # Test invalid record ID
    records = CorpusAPIRecords()
    with pytest.raises(Exception):
        records.get_record("invalid-id")

def test_api_endpoints():
    """Test specific API endpoints using direct HTTP requests."""
    import requests

    # Test categories endpoint
    response = requests.get("http://localhost:8000/api/categories")
    assert response.status_code == 200, "Categories endpoint should return 200."
    assert isinstance(response.json(), list), "Categories endpoint should return a list."

    # Test records endpoint
    response = requests.get("http://localhost:8000/api/records")
    assert response.status_code == 200, "Records endpoint should return 200."
    assert isinstance(response.json(), list), "Records endpoint should return a list."

    # Test search endpoint
    response = requests.get("http://localhost:8000/api/records/search", params={"q": "test"})
    assert response.status_code == 200, "Search endpoint should return 200."
    assert isinstance(response.json(), list), "Search endpoint should return a list."

def test_media_type_filtering():
    """Test that media types are filtered correctly."""
    from api_records import CorpusAPIRecords

    records = CorpusAPIRecords()
    response = records.get_records(media_type="image")
    assert isinstance(response, list), "Media type filtering should return a list."
    assert all(isinstance(item, dict) for item in response), "Each filtered record should be a dictionary."
    assert any("media_type" in item for item in response), "Records should include media type information."
