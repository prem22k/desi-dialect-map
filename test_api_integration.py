#!/usr/bin/env python3
"""
Test script for API integration functionality
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_imports():
    """Test that all API modules can be imported correctly"""
    try:
        import api_auth
        import api_records
        import api_categories
        import api_auth_ui
        print("✅ All API modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_api_configuration():
    """Test API configuration"""
    try:
        import api_auth
        import api_records
        import api_categories
        
        # Check that API base URLs are configured
        assert api_auth.API_BASE_URL == "https://api.corpus.swecha.org"
        assert api_records.API_BASE_URL == "https://api.corpus.swecha.org"
        assert api_categories.API_BASE_URL == "https://api.corpus.swecha.org"
        
        print("✅ API configuration is correct")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_categories_functionality():
    """Test categories functionality"""
    try:
        import api_categories
        
        # Test that categories instance can be created
        categories = api_categories.api_categories
        assert categories is not None
        
        # Test helper functions
        options = api_categories.get_category_options()
        assert isinstance(options, list)
        
        print("✅ Categories functionality working")
        return True
    except Exception as e:
        print(f"❌ Categories error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing API Integration...")
    print("=" * 50)
    
    tests = [
        test_api_imports,
        test_api_configuration,
        test_categories_functionality,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! API integration is ready.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

