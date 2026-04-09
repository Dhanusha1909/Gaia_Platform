import sqlite3
import os

db_path = "data/gaia.db"

if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_id TEXT NOT NULL,
            rating TEXT,
            feedback_text TEXT,
            is_read BOOLEAN DEFAULT 0,
            created_at TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✅ Feedback table created successfully!")
    print("   You can now submit and view feedback.")
else:
    print(f"❌ Database not found at: {db_path}")
    print("   Please run the app and submit a complaint first.")