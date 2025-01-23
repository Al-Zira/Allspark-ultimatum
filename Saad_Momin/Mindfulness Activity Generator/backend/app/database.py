import sqlite3
from datetime import datetime, timedelta
import json
import pandas as pd
from typing import Dict, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        """Initialize database and create tables if they don't exist."""
        try:
            # Connect to database without deleting it
            self.conn = sqlite3.connect('mindfulness.db', check_same_thread=False)
            self.create_tables()
            
            # Initialize default user only if users table is empty
            cursor = self.conn.execute('SELECT COUNT(*) FROM users')
            if cursor.fetchone()[0] == 0:
                self._initialize_default_data()
                
        except Exception as e:
            logger.error(f"Database initialization error: {str(e)}")
            raise

    def _initialize_default_data(self):
        """Initialize default user and sample data."""
        try:
            with self.conn:
                # Create default user if not exists
                self.conn.execute('''
                    INSERT OR IGNORE INTO users (id, name, age, stress_level, interests)
                    VALUES (1, 'Guest', 25, 'Moderate', '["Meditation"]')
                ''')
        except Exception as e:
            logger.error(f"Error initializing default data: {str(e)}")
            raise

    def create_tables(self):
        """Create necessary database tables if they don't exist."""
        try:
            with self.conn:
                # Users table with enhanced settings and goals
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        age INTEGER,
                        stress_level TEXT,
                        interests TEXT,
                        daily_goal_minutes INTEGER DEFAULT 10,
                        weekly_goal_minutes INTEGER DEFAULT 70,
                        theme TEXT DEFAULT 'Dark',
                        accent_color TEXT DEFAULT '#64B5F6',
                        reminder_time TEXT,
                        enable_notifications BOOLEAN DEFAULT FALSE,
                        preferred_times TEXT,
                        focus_areas TEXT,
                        difficulty_level TEXT DEFAULT 'Beginner',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP
                    )
                ''')
                
                # Activities table with enhanced tracking
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        activity_text TEXT,
                        category TEXT,
                        duration INTEGER,
                        rating INTEGER,
                        mood_before TEXT,
                        mood_after TEXT,
                        feedback TEXT,
                        completed BOOLEAN DEFAULT FALSE,
                        completed_at TIMESTAMP,
                        scheduled_for TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        routine_id INTEGER,
                        FOREIGN KEY (user_id) REFERENCES users (id),
                        FOREIGN KEY (routine_id) REFERENCES user_routines (id)
                    )
                ''')
                
                # Mood tracking table
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS mood_tracker (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        mood TEXT,
                        energy_level INTEGER,
                        stress_level INTEGER,
                        notes TEXT,
                        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id)
                    )
                ''')
                
                # User routines table
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS user_routines (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        name TEXT NOT NULL,
                        steps TEXT NOT NULL,
                        duration INTEGER,
                        category TEXT,
                        description TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_practiced TIMESTAMP,
                        practice_count INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                
                # Practice history
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS practice_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        activity_id INTEGER,
                        routine_id INTEGER,
                        duration INTEGER,
                        completed_at TIMESTAMP,
                        mood_before TEXT,
                        mood_after TEXT,
                        notes TEXT,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (activity_id) REFERENCES activities(id),
                        FOREIGN KEY (routine_id) REFERENCES user_routines(id)
                    )
                ''')
        except Exception as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise

    def get_user_stats(self, user_id: int) -> Dict:
        """Get user's statistics and progress."""
        try:
            # Get previous total minutes (before today)
            previous_total = self.conn.execute('''
                SELECT COALESCE(SUM(duration), 0)
                FROM practice_history
                WHERE user_id = ? 
                AND date(completed_at) < date('now')
            ''', (user_id,)).fetchone()[0]

            # Get today's total minutes
            today_total = self.conn.execute('''
                SELECT COALESCE(SUM(duration), 0)
                FROM practice_history
                WHERE user_id = ? 
                AND date(completed_at) = date('now')
            ''', (user_id,)).fetchone()[0]

            # Calculate streak
            streak = self.calculate_streak(user_id)
            
            # Get monthly progress
            monthly_progress = self.conn.execute('''
                SELECT date(completed_at) as practice_date,
                       SUM(duration) as total_minutes
                FROM practice_history
                WHERE user_id = ?
                AND completed_at >= date('now', '-30 days')
                GROUP BY date(completed_at)
                ORDER BY practice_date
            ''', (user_id,)).fetchall()
            
            progress_data = [
                {"date": row[0], "minutes": row[1]}
                for row in monthly_progress
            ]
            
            return {
                "total_minutes": previous_total + today_total,
                "previous_total": previous_total,
                "today_total": today_total,
                "current_streak": streak,
                "monthly_progress": progress_data
            }
        except Exception as e:
            logger.error(f"Error getting user stats: {str(e)}")
            return {
                "total_minutes": 0,
                "previous_total": 0,
                "today_total": 0,
                "current_streak": 0,
                "monthly_progress": []
            }

    def calculate_streak(self, user_id: int) -> int:
        """Calculate current streak of consecutive days with completed activities."""
        try:
            # Get all practice dates in reverse order
            dates = self.conn.execute('''
                SELECT DISTINCT date(completed_at) as practice_date
                FROM practice_history
                WHERE user_id = ?
                ORDER BY practice_date DESC
            ''', (user_id,)).fetchall()
            
            if not dates:
                return 0
            
            from datetime import datetime, timedelta
            
            streak = 0
            current_date = datetime.now().date()
            
            for date_row in dates:
                practice_date = datetime.strptime(date_row[0], '%Y-%m-%d').date()
                
                # If this is the first date we're checking
                if streak == 0:
                    # If the last practice was today or yesterday, start counting
                    if practice_date >= current_date - timedelta(days=1):
                        streak = 1
                    else:
                        return 0
                # For subsequent dates
                elif practice_date == current_date - timedelta(days=streak):
                    streak += 1
                else:
                    break
                
            return streak
        except Exception as e:
            logger.error(f"Error calculating streak: {str(e)}")
            return 0

    def get_monthly_progress(self, user_id: int) -> List[Dict]:
        """Get user's monthly progress data."""
        try:
            cursor = self.conn.execute('''
                SELECT date(completed_at) as date,
                       SUM(duration) as total_minutes
                FROM activities
                WHERE user_id = ?
                AND completed = 1
                AND completed_at >= date('now', '-30 days')
                GROUP BY date(completed_at)
                ORDER BY date(completed_at)
            ''', (user_id,))
            
            return [{"date": row[0], "minutes": row[1]} for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting monthly progress: {str(e)}")
            return []

    def save_activity(self, user_id: int, activity_data: Dict) -> int:
        """Save a new activity."""
        try:
            cursor = self.conn.execute('''
                INSERT INTO activities (
                    user_id, activity_text, category, duration,
                    mood_before, scheduled_for, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                activity_data.get('text'),
                activity_data.get('category'),
                activity_data.get('duration'),
                activity_data.get('mood_before'),
                activity_data.get('scheduled_for')
            ))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error saving activity: {str(e)}")
            raise

    def get_user_routines(self, user_id: int) -> List[Dict]:
        """Get user's saved routines."""
        try:
            cursor = self.conn.execute('''
                SELECT id, name, steps, duration, category, description,
                       created_at, last_practiced, practice_count
                FROM user_routines
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            routines = []
            for row in cursor.fetchall():
                try:
                    steps = json.loads(row[2]) if row[2] else []
                except json.JSONDecodeError:
                    steps = row[2].split('\n') if row[2] else []
                
                routine = {
                    'id': row[0],
                    'name': row[1],
                    'steps': steps,
                    'duration': row[3],
                    'category': row[4] or 'Custom',
                    'description': row[5] or '',
                    'created_at': row[6],
                    'last_practiced': row[7],
                    'practice_count': row[8] or 0
                }
                routines.append(routine)
            
            return routines
        except Exception as e:
            logger.error(f"Error getting user routines: {str(e)}")
            return []

    def save_routine(self, user_id: int, routine: Dict):
        """Save a new routine."""
        try:
            steps_json = json.dumps(routine['steps'])
            self.conn.execute('''
                INSERT INTO user_routines (
                    user_id, name, steps, duration, category,
                    description, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                user_id,
                routine['name'],
                steps_json,
                routine['duration'],
                routine.get('category', 'Custom'),
                routine.get('description', '')
            ))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error saving routine: {str(e)}")
            raise

    def get_mood_data(self, user_id: int, days: int = 30) -> Dict:
        """Get user's mood tracking data."""
        try:
            cursor = self.conn.execute('''
                SELECT mood, energy_level, stress_level, recorded_at
                FROM mood_tracker
                WHERE user_id = ?
                AND recorded_at >= date('now', ?)
                ORDER BY recorded_at
            ''', (user_id, f'-{days} days'))
            
            data = cursor.fetchall()
            return {
                'moods': [row[0] for row in data],
                'energy_levels': [row[1] for row in data],
                'stress_levels': [row[2] for row in data],
                'dates': [row[3] for row in data]
            }
        except Exception as e:
            logger.error(f"Error getting mood data: {str(e)}")
            return {'moods': [], 'energy_levels': [], 'stress_levels': [], 'dates': []} 

    def complete_activity(self, user_id: int, activity_id: int, mood_after: str = None) -> bool:
        """Mark an activity as completed."""
        try:
            self.conn.execute('''
                UPDATE activities
                SET completed = TRUE,
                    completed_at = CURRENT_TIMESTAMP,
                    mood_after = ?
                WHERE id = ? AND user_id = ?
            ''', (mood_after, activity_id, user_id))
            
            # Also record in practice history
            self.conn.execute('''
                INSERT INTO practice_history (
                    user_id, activity_id, duration, completed_at,
                    mood_before, mood_after
                )
                SELECT user_id, id, duration, CURRENT_TIMESTAMP,
                       mood_before, ?
                FROM activities
                WHERE id = ? AND user_id = ?
            ''', (mood_after, activity_id, user_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error completing activity: {str(e)}")
            return False 