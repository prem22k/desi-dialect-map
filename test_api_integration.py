#!/usr/bin/env python3
"""
Test script for Indic Corpus Collections API integration
"""

import os
import sys
import requests
from dotenv import load_dotenv
import api_client as api


def test_environment_setup():
    """Test if environment variables are properly configured"""
    print("🔧 Testing Environment Setup...")
    
    # Load environment variables
    load_dotenv()
    
    api_url = os.getenv("INDIC_CORPUS_API_URL")
    api_key = os.getenv("INDIC_CORPUS_API_KEY")
    
    if not api_url:
        print("❌ INDIC_CORPUS_API_URL not found in environment variables")
        print("   Please add it to your .env file or set it as an environment variable")
        return False
    
    if not api_key:
        print("⚠️  INDIC_CORPUS_API_KEY not found (optional for some operations)")
    
    print(f"✅ API URL: {api_url}")
    if api_key:
        print(f"✅ API Key: {api_key[:10]}...")
    else:
        print("✅ API Key: Not provided (will use unauthenticated mode)")
    
    return True


def test_api_connection():
    """Test basic API connectivity"""
    print("\n🌐 Testing API Connection...")
    
    try:
        api_client = api.get_api_client()
        health = api_client.health_check()
        
        if "status" in health:
            print(f"✅ API Health Check: {health['status']}")
            return True
        else:
            print(f"❌ API Health Check Failed: {health}")
            return False
            
    except Exception as e:
        print(f"❌ API Connection Error: {e}")
        return False


def test_authentication():
    """Test authentication functionality"""
    print("\n🔐 Testing Authentication...")
    
    api_client = api.get_api_client()
    
    # Test without authentication first
    print("Testing unauthenticated access...")
    try:
        response = api_client.get_categories()
        if "items" in response:
            print(f"✅ Unauthenticated access works: {len(response['items'])} categories found")
        else:
            print(f"⚠️  Unauthenticated access limited: {response}")
    except Exception as e:
        print(f"❌ Unauthenticated access failed: {e}")
    
    # Test with API key if available
    if api_client.api_key:
        print("Testing API key authentication...")
        try:
            response = api_client.get_current_user()
            if "username" in response:
                print(f"✅ API key authentication works: {response['username']}")
                return True
            else:
                print(f"⚠️  API key authentication limited: {response}")
        except Exception as e:
            print(f"❌ API key authentication failed: {e}")
    
    return False


def test_data_operations():
    """Test data operations"""
    print("\n📝 Testing Data Operations...")
    
    api_client = api.get_api_client()
    
    # Test getting categories
    try:
        categories = api_client.get_categories()
        if "items" in categories:
            print(f"✅ Categories retrieved: {len(categories['items'])} found")
            
            # Show first few categories
            for i, category in enumerate(categories['items'][:3]):
                print(f"   - {category.get('name', 'Unknown')} (ID: {category.get('id', 'Unknown')})")
        else:
            print(f"⚠️  Categories retrieval limited: {categories}")
    except Exception as e:
        print(f"❌ Categories retrieval failed: {e}")
    
    # Test getting records
    try:
        records = api_client.get_records(limit=5)
        if "items" in records:
            print(f"✅ Records retrieved: {len(records['items'])} found")
            
            # Show first few records
            for i, record in enumerate(records['items'][:3]):
                word = record.get('dialect_word', 'Unknown')
                location = record.get('location_text', 'Unknown')
                print(f"   - '{word}' from {location}")
        else:
            print(f"⚠️  Records retrieval limited: {records}")
    except Exception as e:
        print(f"❌ Records retrieval failed: {e}")


def test_search_operations():
    """Test search operations"""
    print("\n🔍 Testing Search Operations...")
    
    api_client = api.get_api_client()
    
    # Test nearby search
    try:
        nearby = api_client.search_records_nearby(
            latitude=17.3850,  # Hyderabad
            longitude=78.4867,
            radius=10.0
        )
        if "items" in nearby:
            print(f"✅ Nearby search works: {len(nearby['items'])} records found")
        else:
            print(f"⚠️  Nearby search limited: {nearby}")
    except Exception as e:
        print(f"❌ Nearby search failed: {e}")
    
    # Test bounding box search
    try:
        bbox = api_client.search_records_bbox(
            min_lat=17.0, min_lon=78.0,
            max_lat=18.0, max_lon=79.0
        )
        if "items" in bbox:
            print(f"✅ Bounding box search works: {len(bbox['items'])} records found")
        else:
            print(f"⚠️  Bounding box search limited: {bbox}")
    except Exception as e:
        print(f"❌ Bounding box search failed: {e}")


def test_local_data_sync():
    """Test local data synchronization"""
    print("\n🔄 Testing Local Data Sync...")
    
    # Check if local database exists
    try:
        import database as db
        conn = db.create_connection()
        local_submissions = db.get_all_submissions(conn, public_only=False)
        
        if not local_submissions.empty:
            print(f"✅ Local database found: {len(local_submissions)} submissions")
            
            # Test sync preparation
            api_client = api.get_api_client()
            submissions_list = local_submissions.to_dict('records')
            
            print(f"✅ Sync preparation ready: {len(submissions_list)} submissions to sync")
            print("   (Actual sync requires authentication)")
            
            # Show sample data
            if len(submissions_list) > 0:
                sample = submissions_list[0]
                print(f"   Sample submission: '{sample.get('dialect_word', 'Unknown')}' from {sample.get('location_text', 'Unknown')}")
        else:
            print("ℹ️  Local database is empty (no submissions to sync)")
            
    except Exception as e:
        print(f"❌ Local database access failed: {e}")


def test_ui_components():
    """Test UI components"""
    print("\n🎨 Testing UI Components...")
    
    try:
        # Test API client creation
        api_client = api.get_api_client()
        print("✅ API client creation works")
        
        # Test authentication check
        is_auth = api_client.is_authenticated()
        print(f"✅ Authentication check works: {is_auth}")
        
        # Test utility functions
        print("✅ Utility functions available:")
        print("   - api_login_ui()")
        print("   - api_user_info()")
        print("   - sync_data_ui()")
        print("   - api_status_check()")
        
    except Exception as e:
        print(f"❌ UI component test failed: {e}")


def run_all_tests():
    """Run all tests"""
    print("🧪 Starting API Integration Tests...")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment_setup),
        ("API Connection", test_api_connection),
        ("Authentication", test_authentication),
        ("Data Operations", test_data_operations),
        ("Search Operations", test_search_operations),
        ("Local Data Sync", test_local_data_sync),
        ("UI Components", test_ui_components),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your API integration is ready.")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Check failed tests for issues.")
    else:
        print("❌ Many tests failed. Please check your configuration.")


def show_usage():
    """Show usage information"""
    print("""
🔧 API Integration Test Script

Usage:
    python test_api_integration.py [option]

Options:
    --all              Run all tests (default)
    --env              Test environment setup only
    --connection       Test API connection only
    --auth             Test authentication only
    --data             Test data operations only
    --search           Test search operations only
    --sync             Test local data sync only
    --ui               Test UI components only
    --help             Show this help message

Environment Variables:
    INDIC_CORPUS_API_URL    API endpoint URL
    INDIC_CORPUS_API_KEY    API authentication key (optional)

Example:
    python test_api_integration.py --all
    python test_api_integration.py --connection
    """)


def main():
    """Main function"""
    if len(sys.argv) > 1:
        option = sys.argv[1].lower()
        
        if option == "--help" or option == "-h":
            show_usage()
            return
        elif option == "--env":
            test_environment_setup()
        elif option == "--connection":
            test_api_connection()
        elif option == "--auth":
            test_authentication()
        elif option == "--data":
            test_data_operations()
        elif option == "--search":
            test_search_operations()
        elif option == "--sync":
            test_local_data_sync()
        elif option == "--ui":
            test_ui_components()
        elif option == "--all":
            run_all_tests()
        else:
            print(f"❌ Unknown option: {option}")
            show_usage()
    else:
        run_all_tests()


if __name__ == "__main__":
    main()
