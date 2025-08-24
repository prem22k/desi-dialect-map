import sqlite3
import pandas as pd
import streamlit as st
import uuid
from datetime import datetime
import io
import os
import base64
from PIL import Image
import hashlib

# Create images directory if it doesn't exist
IMAGES_DIR = "uploaded_images"
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)


def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(conn, username, password, email=None):
    """Create a new user account"""
    try:
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)

        sql = """ INSERT INTO users(id, username, password_hash, email)
                  VALUES(?,?,?,?) """
        cur = conn.cursor()
        cur.execute(sql, (user_id, username, password_hash, email))
        conn.commit()
        return user_id
    except Exception as e:
        st.error(f"Error creating user: {e}")
        return None


def authenticate_user(conn, username, password):
    """Authenticate user login"""
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username FROM users WHERE username=? AND password_hash=?",
            (username, hash_password(password)),
        )
        user = cur.fetchone()
        return user if user else None
    except Exception as e:
        st.error(f"Authentication error: {e}")
        return None


def create_connection():
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect("dialect_map.db")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def create_table(conn):
    """Create the submissions table if it doesn't exist"""
    try:
        c = conn.cursor()
        # Add user_id and is_public fields for privacy control
        c.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                dialect_word TEXT NOT NULL,
                location_text TEXT NOT NULL,
                image_path TEXT,
                latitude REAL,
                longitude REAL,
                is_public BOOLEAN DEFAULT 1,
                is_verified BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Create users table for basic authentication
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)

    except sqlite3.Error as e:
        print(e)


def add_submission(
    conn, dialect_word, location_text, image_data, user_id=None, is_public=True
):
    """Add a new submission to SQLite and save image locally"""
    try:
        # Generate unique ID for the submission
        submission_id = str(uuid.uuid4())

        # Save image to local file system
        image_path = f"{IMAGES_DIR}/{submission_id}.jpg"

        try:
            # Convert image data to PIL Image and save as JPEG
            image = Image.open(io.BytesIO(image_data))
            # Convert to RGB if necessary (for PNG with transparency)
            if image.mode in ("RGBA", "LA", "P"):
                image = image.convert("RGB")
            image.save(image_path, "JPEG", quality=85)
        except Exception as e:
            st.warning(f"Image processing failed: {e}")
            return None

        # Add submission to SQLite
        if conn:
            sql = """ INSERT INTO submissions(id, user_id, dialect_word, location_text, image_path, is_public)
                      VALUES(?,?,?,?,?,?) """
            cur = conn.cursor()
            cur.execute(
                sql,
                (
                    submission_id,
                    user_id,
                    dialect_word,
                    location_text,
                    image_path,
                    is_public,
                ),
            )
            conn.commit()
            return submission_id

        return None
    except Exception as e:
        st.error(f"Error adding submission: {e}")
        return None


def get_all_submissions(conn, user_id=None, public_only=True):
    """Query submissions from SQLite with privacy control"""
    try:
        if public_only:
            # Only show public submissions
            df = pd.read_sql_query(
                "SELECT id, dialect_word, location_text, latitude, longitude, image_path, is_verified FROM submissions WHERE is_public=1",
                conn,
            )
        elif user_id:
            # Show user's own submissions + public ones
            df = pd.read_sql_query(
                "SELECT id, dialect_word, location_text, latitude, longitude, image_path, is_verified FROM submissions WHERE is_public=1 OR user_id=?",
                conn,
                params=(user_id,),
            )
        else:
            # Show all submissions (admin only)
            df = pd.read_sql_query(
                "SELECT id, dialect_word, location_text, latitude, longitude, image_path, is_verified FROM submissions",
                conn,
            )
        return df
    except Exception as e:
        st.error(f"Error getting submissions: {e}")
        return pd.DataFrame()


def get_image(conn, submission_id):
    """Retrieve an image from local file system"""
    try:
        # Get image path from SQLite
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM submissions WHERE id=?", (submission_id,))
        row = cur.fetchone()

        if row and row[0] and os.path.exists(row[0]):
            # Read image file and return bytes
            with open(row[0], "rb") as f:
                return f.read()

        return None
    except Exception as e:
        st.error(f"Error getting image: {e}")
        return None


def get_user_submissions(conn, user_id):
    """Get submissions for a specific user"""
    try:
        df = pd.read_sql_query(
            "SELECT id, dialect_word, location_text, latitude, longitude, image_path, is_public, is_verified FROM submissions WHERE user_id=?",
            conn,
            params=(user_id,),
        )
        return df
    except Exception as e:
        st.error(f"Error getting user submissions: {e}")
        return pd.DataFrame()


def get_random_submission(conn, public_only=True):
    """Get a random submission from SQLite"""
    try:
        if public_only:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, dialect_word, location_text FROM submissions WHERE is_public=1 ORDER BY RANDOM() LIMIT 1"
            )
        else:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, dialect_word, location_text FROM submissions ORDER BY RANDOM() LIMIT 1"
            )
        return cur.fetchone()
    except Exception as e:
        st.error(f"Error getting random submission: {e}")
        return None


def update_coordinates(conn, submission_id, latitude, longitude):
    """Update latitude and longitude for a submission"""
    try:
        if conn:
            c = conn.cursor()
            c.execute(
                "UPDATE submissions SET latitude=?, longitude=? WHERE id=?",
                (latitude, longitude, submission_id),
            )
            conn.commit()
            return True
        return False
    except Exception as e:
        st.error(f"Error updating coordinates: {e}")
        return False


def initialize_database():
    """Initialize the database and create the table"""
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        conn.close()
        return True
    else:
        print("Error! cannot create the database connection.")
        return False


def toggle_submission_privacy(conn, submission_id, user_id):
    """Toggle submission between public and private (only owner can do this)"""
    try:
        if conn:
            # Check if user owns this submission
            cur = conn.cursor()
            cur.execute("SELECT user_id FROM submissions WHERE id=?", (submission_id,))
            row = cur.fetchone()

            if row and row[0] == user_id:
                # Toggle privacy
                cur.execute(
                    "UPDATE submissions SET is_public = NOT is_public WHERE id=?",
                    (submission_id,),
                )
                conn.commit()
                return True
            else:
                st.error("You can only modify your own submissions")
                return False
        return False
    except Exception as e:
        st.error(f"Error updating privacy: {e}")
        return False


def delete_submission(conn, submission_id, user_id):
    """Delete a submission (only owner can do this)"""
    try:
        if conn:
            # Check if user owns this submission
            cur = conn.cursor()
            cur.execute(
                "SELECT user_id, image_path FROM submissions WHERE id=?",
                (submission_id,),
            )
            row = cur.fetchone()

            if row and row[0] == user_id:
                # Delete image file
                if row[1] and os.path.exists(row[1]):
                    os.remove(row[1])

                # Delete database entry
                cur.execute("DELETE FROM submissions WHERE id=?", (submission_id,))
                conn.commit()
                return True
            else:
                st.error("You can only delete your own submissions")
                return False
        return False
    except Exception as e:
        st.error(f"Error deleting submission: {e}")
        return False


def cleanup_old_images():
    """Clean up orphaned image files that don't have database entries"""
    try:
        if not os.path.exists(IMAGES_DIR):
            return

        # Get all image files
        image_files = [f for f in os.listdir(IMAGES_DIR) if f.endswith(".jpg")]

        # Get all image paths from database
        conn = create_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT image_path FROM submissions")
            db_paths = [row[0] for row in cur.fetchall()]
            conn.close()

            # Remove orphaned files
            for image_file in image_files:
                image_path = os.path.join(IMAGES_DIR, image_file)
                if image_path not in db_paths:
                    try:
                        os.remove(image_path)
                    except:
                        pass
    except Exception as e:
        print(f"Cleanup error: {e}")
