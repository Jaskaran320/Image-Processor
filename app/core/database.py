import sqlite3

DATABASE_NAME = 'image_processing.db'

def initialize_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id TEXT PRIMARY KEY,
            csv_filename TEXT,
            status TEXT,
            webhook_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT,
            serial_number TEXT,
            product_name TEXT,
            input_image_urls TEXT,
            output_image_urls TEXT,
            processing_status TEXT,
            FOREIGN KEY (request_id) REFERENCES requests(request_id)
        )
    ''')
    conn.commit()
    conn.close()

initialize_db()

def get_db_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()