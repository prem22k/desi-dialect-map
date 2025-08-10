import sqlite3
import pandas as pd

def create_connection():
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('dialect_map.db')
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_table(conn):
    """Create the submissions table if it doesn't exist"""
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dialect_word TEXT NOT NULL,
                location_text TEXT NOT NULL,
                image_data BLOB NOT NULL,
                latitude REAL,
                longitude REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    except sqlite3.Error as e:
        print(e)

def add_submission(conn, dialect_word, location_text, image_data):
    """Add a new submission to the submissions table"""
    sql = ''' INSERT INTO submissions(dialect_word,location_text,image_data)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, (dialect_word, location_text, image_data))
    conn.commit()
    return cur.lastrowid

def get_all_submissions(conn):
    """Query all rows in the submissions table"""
    df = pd.read_sql_query("SELECT id, dialect_word, location_text, latitude, longitude FROM submissions", conn)
    return df

def get_image(conn, submission_id):
    """Retrieve an image from the database by its ID"""
    cur = conn.cursor()
    cur.execute("SELECT image_data FROM submissions WHERE id=?", (submission_id,))
    row = cur.fetchone()
    return row[0] if row else None

def get_random_submission(conn):
    """Get a random submission from the database."""
    cur = conn.cursor()
    cur.execute("SELECT id, dialect_word, location_text FROM submissions ORDER BY RANDOM() LIMIT 1")
    return cur.fetchone()

def initialize_database():
    """Initialize the database and create the table"""
    conn = create_connection()
    if conn is not None:
        create_table(conn)
        conn.close()
    else:
        print("Error! cannot create the database connection.")
