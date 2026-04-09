# modules/database.py
import sqlite3
import json
import pandas as pd # pyright: ignore[reportMissingModuleSource]
from datetime import datetime, timedelta
import os
import streamlit as st # pyright: ignore[reportMissingImports]

class DatabaseManager:
    """Manage SQLite database for GAIA"""
    
    def __init__(self, db_path="data/gaia.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()
    
    def _get_connection(self):
        """Get database connection with row factory for dict results"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_db(self):
        """Initialize database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Reports table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factory_name TEXT,
                report_text TEXT,
                gaia_score REAL,
                is_fake BOOLEAN,
                fraud_score REAL,
                created_at TIMESTAMP
            )
        ''')
        
        # Complaints table - FIXED with all required columns
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT UNIQUE NOT NULL,
                complaint_type TEXT,
                location TEXT,
                original_text TEXT,
                translated_text TEXT,
                language_code TEXT DEFAULT 'en',
                status TEXT DEFAULT 'PENDING',
                officer_assigned TEXT,
                inspection_date TEXT,
                resolution_date TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        ''')
        
        # Notifications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT,
                notification_type TEXT,
                content TEXT,
                sent_at TIMESTAMP
            )
        ''')
        
        # Feedback table - Create it here in init
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracking_id TEXT NOT NULL,
                rating TEXT,
                feedback_text TEXT,
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP,
                FOREIGN KEY (tracking_id) REFERENCES complaints(tracking_id)
            )
        ''')
        
        # Create index for faster tracking ID lookup
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tracking_id ON complaints(tracking_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_tracking ON feedback(tracking_id)')
        
        conn.commit()
        conn.close()
        print("✅ Database initialized successfully")
    
    # ============ Report Functions ============
    
    def save_report(self, factory_name, report_text, gaia_score, is_fake, fraud_score, industry=None):
        """Save analyzed report"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO reports (factory_name, report_text, gaia_score, is_fake, fraud_score, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (factory_name, report_text[:500], gaia_score, is_fake, fraud_score, datetime.now()))
            
            conn.commit()
            report_id = cursor.lastrowid
            conn.close()
            
            return report_id
        except Exception as e:
            print(f"Error saving report: {e}")
            return None
    
    def get_reports(self, limit=10):
        """Get recent reports"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM reports ORDER BY created_at DESC LIMIT ?', (limit,))
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting reports: {e}")
            return []
    
    # ============ Complaint Functions ============
    
    def save_complaint(self, tracking_id, complaint_type, location, original_text="", translated_text="", language_code="en"):
        """Save citizen complaint with tracking"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            now = datetime.now()
            
            cursor.execute('''
                INSERT INTO complaints 
                (tracking_id, complaint_type, location, original_text, translated_text, language_code, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (tracking_id, complaint_type, location, original_text, translated_text, language_code, 'PENDING', now, now))
            
            conn.commit()
            complaint_id = cursor.lastrowid
            conn.close()
            
            print(f"✅ Complaint saved with tracking_id: {tracking_id}")
            return complaint_id
            
        except Exception as e:
            print(f"Error saving complaint: {e}")
            return None
    
    def get_complaint_by_tracking_id(self, tracking_id):
        """Get complaint details by tracking ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM complaints WHERE tracking_id = ?', (tracking_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return dict(result)
            return None
            
        except Exception as e:
            print(f"Error getting complaint: {e}")
            return None
    
    def get_complaints(self, limit=10, status=None):
        """Get recent complaints"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if status:
                cursor.execute('SELECT * FROM complaints WHERE status = ? ORDER BY created_at DESC LIMIT ?', (status, limit))
            else:
                cursor.execute('SELECT * FROM complaints ORDER BY created_at DESC LIMIT ?', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting complaints: {e}")
            return []
    
    def update_complaint_status(self, tracking_id, status, officer_assigned=None, inspection_date=None):
        """Update complaint status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            updates = ["status = ?", "updated_at = ?"]
            params = [status, datetime.now()]
            
            if officer_assigned:
                updates.append("officer_assigned = ?")
                params.append(officer_assigned)
            
            if inspection_date:
                updates.append("inspection_date = ?")
                params.append(inspection_date)
            
            if status == "RESOLVED":
                updates.append("resolution_date = ?")
                params.append(datetime.now())
            
            query = f"UPDATE complaints SET {', '.join(updates)} WHERE tracking_id = ?"
            params.append(tracking_id)
            
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating complaint: {e}")
            return False
    
    def get_complaint_statistics(self):
        """Get complaint statistics"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute('SELECT status, COUNT(*) FROM complaints GROUP BY status')
            stats['by_status'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute('SELECT complaint_type, COUNT(*) FROM complaints GROUP BY complaint_type')
            stats['by_type'] = {row[0]: row[1] for row in cursor.fetchall()}
            
            cursor.execute('SELECT COUNT(*) FROM complaints')
            stats['total'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"Error getting statistics: {e}")
            return {}
    
    def get_all_tracking_ids(self):
        """Get all tracking IDs for testing"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT tracking_id, status FROM complaints ORDER BY created_at DESC LIMIT 10')
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"Error getting tracking IDs: {e}")
            return []
    
    # ============ Feedback Functions ============
    
    def save_feedback(self, tracking_id, rating, feedback_text):
        """Save citizen feedback for a complaint"""
        try:
            print(f"🔍 DEBUG: Saving feedback - tracking_id: {tracking_id}, rating: {rating}")
            
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create feedback table if not exists
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
            
            now = datetime.now()
            
            # Check if feedback already exists
            cursor.execute('SELECT id FROM feedback WHERE tracking_id = ?', (tracking_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing feedback
                cursor.execute('''
                    UPDATE feedback 
                    SET rating = ?, feedback_text = ?, is_read = 0, created_at = ?
                    WHERE tracking_id = ?
                ''', (rating, feedback_text, now, tracking_id))
                feedback_id = existing[0]
                print(f"🔄 Updated existing feedback for {tracking_id}")
            else:
                # Insert new feedback
                cursor.execute('''
                    INSERT INTO feedback (tracking_id, rating, feedback_text, is_read, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (tracking_id, rating, feedback_text, 0, now))
                feedback_id = cursor.lastrowid
                print(f"➕ Created new feedback for {tracking_id}")
            
            conn.commit()
            conn.close()
            
            print(f"✅ Feedback saved with ID: {feedback_id}")
            return feedback_id
            
        except Exception as e:
            print(f"❌ Error saving feedback: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_feedback_by_tracking_id(self, tracking_id):
        """Get feedback for a specific complaint"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, tracking_id, rating, feedback_text, is_read, created_at 
                FROM feedback 
                WHERE tracking_id = ? 
                ORDER BY created_at DESC
            ''', (tracking_id,))
            
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []
    
    def get_all_feedback(self, is_read=None):
        """Get all feedback, optionally filtered by read status"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if is_read is not None:
                cursor.execute('''
                    SELECT id, tracking_id, rating, feedback_text, is_read, created_at 
                    FROM feedback 
                    WHERE is_read = ? 
                    ORDER BY created_at DESC
                ''', (is_read,))
            else:
                cursor.execute('''
                    SELECT id, tracking_id, rating, feedback_text, is_read, created_at 
                    FROM feedback 
                    ORDER BY created_at DESC
                ''')
            
            results = cursor.fetchall()
            conn.close()
            return [dict(row) for row in results]
            
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return []
    
    def mark_feedback_as_read(self, feedback_id):
        """Mark feedback as read by officer"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('UPDATE feedback SET is_read = 1 WHERE id = ?', (feedback_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking feedback as read: {e}")
            return False
    
    def delete_feedback(self, feedback_id):
        """Delete a specific feedback by ID"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))
            conn.commit()
            success = cursor.rowcount > 0
            conn.close()
            return success
        except Exception as e:
            print(f"Error deleting feedback: {e}")
            return False

    def delete_all_read_feedback(self):
        """Delete all feedback that has been marked as read"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE is_read = 1")
            conn.commit()
            deleted_count = cursor.rowcount
            conn.close()
            return deleted_count
        except Exception as e:
            print(f"Error deleting read feedback: {e}")
            return 0

# Create instance
db = DatabaseManager()