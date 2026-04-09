import sqlite3
import os

db_path = "data/gaia.db"

print("=" * 50)
print("Feedback Database Debug")
print("=" * 50)

if os.path.exists(db_path):
    print(f"✅ Database found: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if feedback table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='feedback'")
    table_exists = cursor.fetchone()
    
    if table_exists:
        print("✅ Feedback table exists")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM feedback")
        count = cursor.fetchone()[0]
        print(f"📊 Total feedback records: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM feedback")
            rows = cursor.fetchall()
            print("\n📋 Feedback Records:")
            for row in rows:
                print(f"   ID: {row[0]}, Tracking: {row[1]}, Rating: {row[2]}")
    else:
        print("❌ Feedback table does NOT exist!")
        print("   Creating it now...")
        
        # Create the table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT NOT NULL,
                rating TEXT,
                feedback_text TEXT,
                is_read INTEGER DEFAULT 0,
                created_at TIMESTAMP
            )
        ''')
        conn.commit()
        print("✅ Feedback table created!")
    
    conn.close()
else:
    print(f"❌ Database not found at: {db_path}")

print("=" * 50)