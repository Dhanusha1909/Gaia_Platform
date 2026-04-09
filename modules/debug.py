import os
import sqlite3

# Check if database file exists
db_path = "data/gaia.db"

if os.path.exists(db_path):
    print(f"✅ Database found at: {db_path}")
    
    # Connect and check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check complaints table
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='complaints'")
    if cursor.fetchone():
        print("✅ Complaints table exists")
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM complaints")
        count = cursor.fetchone()[0]
        print(f"📊 Total complaints in database: {count}")
        
        # Show all complaints
        if count > 0:
            cursor.execute("SELECT tracking_id, complaint_type, location, status FROM complaints")
            rows = cursor.fetchall()
            print("\n📋 Existing Complaints:")
            for row in rows:
                print(f"   - {row[0]} | {row[1]} | {row[2]} | {row[3]}")
        else:
            print("⚠️ No complaints found in database!")
    else:
        print("❌ Complaints table does not exist!")
    
    conn.close()
else:
    print(f"❌ Database not found at: {db_path}")
    print("   Please submit a complaint first to create the database.")