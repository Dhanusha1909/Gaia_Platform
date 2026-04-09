import sqlite3
import os
from datetime import datetime

print("=" * 60)
print("GAIA FEEDBACK SYSTEM DIAGNOSTIC")
print("=" * 60)

db_path = "data/gaia.db"

# Step 1: Check database exists
print("\n[1] Checking database...")
if os.path.exists(db_path):
    print(f"    ✅ Database found: {db_path}")
    print(f"    Size: {os.path.getsize(db_path)} bytes")
else:
    print(f"    ❌ Database NOT found!")
    exit()

# Step 2: Check all tables
print("\n[2] Checking tables...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"    Tables: {tables}")

# Step 3: Check feedback table specifically
print("\n[3] Checking feedback table...")
if 'feedback' in tables:
    print("    ✅ Feedback table exists")
    
    # Check structure
    cursor.execute("PRAGMA table_info(feedback)")
    columns = cursor.fetchall()
    print(f"    Columns: {[col[1] for col in columns]}")
    
    # Check records
    cursor.execute("SELECT COUNT(*) FROM feedback")
    count = cursor.fetchone()[0]
    print(f"    Records: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM feedback")
        rows = cursor.fetchall()
        print("\n    📋 Existing Feedback:")
        for row in rows:
            print(f"       ID: {row[0]}, Tracking: {row[1]}, Rating: {row[2]}")
else:
    print("    ❌ Feedback table MISSING!")
    print("    Creating it now...")
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
    print("    ✅ Feedback table created!")

# Step 4: Check complaints table
print("\n[4] Checking complaints...")
cursor.execute("SELECT COUNT(*) FROM complaints")
complaint_count = cursor.fetchone()[0]
print(f"    Total complaints: {complaint_count}")

if complaint_count > 0:
    cursor.execute("SELECT tracking_id, status FROM complaints LIMIT 5")
    complaints = cursor.fetchall()
    print("    Recent complaints:")
    for c in complaints:
        print(f"       - {c[0]} : {c[1]}")

# Step 5: Test direct insert
print("\n[5] Testing direct insert...")
test_id = f"TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
try:
    cursor.execute('''
        INSERT INTO feedback (tracking_id, rating, feedback_text, is_read, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (test_id, "Good", "Test feedback", 0, datetime.now()))
    conn.commit()
    print(f"    ✅ Direct insert successful for: {test_id}")
except Exception as e:
    print(f"    ❌ Direct insert failed: {e}")

# Step 6: Verify insert worked
cursor.execute("SELECT COUNT(*) FROM feedback")
new_count = cursor.fetchone()[0]
print(f"\n[6] Final feedback count: {new_count}")

conn.close()

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)