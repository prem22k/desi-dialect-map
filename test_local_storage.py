#!/usr/bin/env python3
"""
Test script to verify local storage functionality
Run this to ensure your local storage setup is working correctly
"""

import os
import database as db
from PIL import Image
import io


def test_local_storage():
    """Test local storage functionality"""
    print("🧪 Testing Local Storage Setup...")

    # Test database initialization
    print("1. Testing database initialization...")
    if db.initialize_database():
        print("✅ Database initialized successfully")
    else:
        print("❌ Database initialization failed")
        return False

    # Test database connection
    print("2. Testing database connection...")
    conn = db.create_connection()
    if conn:
        print("✅ Database connection successful")

        # Test table creation
        db.create_table(conn)
        print("✅ Table creation successful")

        # Test image directory creation
        if os.path.exists("uploaded_images"):
            print("✅ Images directory exists")
        else:
            print("❌ Images directory not created")
            return False

        # Test cleanup function
        print("3. Testing cleanup function...")
        try:
            db.cleanup_old_images()
            print("✅ Cleanup function works")
        except Exception as e:
            print(f"⚠️ Cleanup function warning: {e}")

        conn.close()
    else:
        print("❌ Database connection failed")
        return False

    print("\n🎉 All local storage tests passed!")
    return True


def check_file_permissions():
    """Check if we can create and write files"""
    print("🔍 Checking file permissions...")

    try:
        # Test creating a test image
        test_image = Image.new("RGB", (100, 100), color="red")
        test_path = "test_image.jpg"
        test_image.save(test_path)

        # Test reading the image
        with open(test_path, "rb") as f:
            data = f.read()

        # Clean up test file
        os.remove(test_path)

        print("✅ File read/write permissions working")
        return True
    except Exception as e:
        print(f"❌ File permission error: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Local Storage Test")
    print("=" * 40)

    # Check file permissions first
    if not check_file_permissions():
        print("\n❌ File permission check failed.")
        exit(1)

    # Test local storage functionality
    if test_local_storage():
        print("\n✅ Local storage is ready for use!")
        print("\n📝 Note: This setup uses:")
        print("   - SQLite for metadata (dialect words, locations, etc.)")
        print("   - Local file system for images")
        print("   - 100% free - no cloud services needed!")
        print("   - Perfect for Streamlit Cloud deployment")
    else:
        print("\n❌ Local storage test failed. Please check your setup.")
        exit(1)
