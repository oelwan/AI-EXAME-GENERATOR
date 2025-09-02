import sqlite3
from datetime import datetime
import hashlib
import os
import json

class Database:
    def __init__(self):
        self.db_path = "data/users.db"
        self._init_db()

    def _init_db(self):
        """Initialize the database and create tables if they don't exist."""
        os.makedirs("data", exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                student_id TEXT UNIQUE NOT NULL,
                department TEXT NOT NULL,
                user_type TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        ''')
        
        # Create quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                course TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                questions TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (professor_id) REFERENCES users (id)
            )
        ''')
        
        # Create quiz submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                answers TEXT NOT NULL,
                score REAL,
                feedback TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (quiz_id) REFERENCES quizzes (id),
                FOREIGN KEY (student_id) REFERENCES users (id)
            )
        ''')
        
        # Create practice quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS practice_quizzes (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                student_id INTEGER NOT NULL,
                questions TEXT NOT NULL,
                start_time TEXT NOT NULL,
                score REAL,
                difficulty TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def _hash_password(self, password):
        """Hash the password using SHA-256."""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, user_data):
        """Register a new user in the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if email or student_id already exists
            cursor.execute("SELECT * FROM users WHERE email = ? OR student_id = ?", 
                         (user_data["email"], user_data["student_id"]))
            if cursor.fetchone():
                raise ValueError("Email or Student ID already registered")
            
            # Insert new user
            cursor.execute('''
                INSERT INTO users (name, email, student_id, department, user_type, password_hash, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data["name"],
                user_data["email"],
                user_data["student_id"],
                user_data["department"],
                user_data["user_type"],
                self._hash_password(user_data["password"]),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()

    def verify_user(self, email, password):
        """Verify user credentials."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()
            
            if user and user[6] == self._hash_password(password):  # password_hash is at index 6
                return {
                    "id": user[0],
                    "name": user[1],
                    "email": user[2],
                    "student_id": user[3],
                    "department": user[4],
                    "user_type": user[5]
                }
            return None
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()

    def get_all_users(self):
        """Get all users from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            return [{
                "id": user[0],
                "name": user[1],
                "email": user[2],
                "student_id": user[3],
                "department": user[4],
                "user_type": user[5],
                "created_at": user[7]
            } for user in users]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()

    def delete_user(self, user_id):
        """Delete a user from the database by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            cursor.close()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        except ValueError as e:
            raise ValueError(str(e))
        finally:
            conn.close()

    def initialize_default_users(self):
        """Initialize default users, including the developer account and demo accounts."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if the developer account exists
            cursor.execute("SELECT * FROM users WHERE email = ?", ("demo@bahcesehir.edu.tr",))
            developer = cursor.fetchone()
            
            # If developer account doesn't exist, create it
            if not developer:
                developer_data = {
                    "name": "Demo Developer",
                    "email": "demo@bahcesehir.edu.tr",
                    "student_id": "0000",
                    "department": "IT",
                    "user_type": "developer",
                    "password": "1234"
                }
                self.register_user(developer_data)
                print("Developer account created successfully")
            
            # Create demo student account for testing
            cursor.execute("SELECT * FROM users WHERE email = ?", ("student.demo@bahcesehir.edu.tr",))
            demo_student = cursor.fetchone()
            
            if not demo_student:
                student_data = {
                    "name": "Demo Student",
                    "email": "student.demo@bahcesehir.edu.tr",
                    "student_id": "1001",
                    "department": "Computer Science",
                    "user_type": "student",
                    "password": "demo123"
                }
                self.register_user(student_data)
                print("Demo student account created successfully")
            
            cursor.close()
            return True
        except sqlite3.Error as e:
            print(f"Error initializing default users: {str(e)}")
            # Create tables if they don't exist
            self._init_db()
            return False
        finally:
            conn.close()
            
    def save_quiz(self, quiz_data):
        """Save a quiz to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert questions to JSON string
            questions_json = json.dumps(quiz_data["questions"])
            
            # Insert quiz
            cursor.execute('''
                INSERT INTO quizzes (
                    title, description, course, start_time, end_time, 
                    duration_minutes, professor_id, questions, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quiz_data["title"],
                quiz_data["description"],
                quiz_data["course"],
                quiz_data["start_time"],
                quiz_data["end_time"],
                quiz_data["duration_minutes"],
                quiz_data["professor_id"],
                questions_json,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            
            quiz_id = cursor.lastrowid
            conn.commit()
            return quiz_id
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def save_practice_quiz(self, quiz_data):
        """Save a practice quiz to the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Convert questions to JSON string
            questions_json = json.dumps(quiz_data["questions"])
            
            # Insert or update practice quiz
            cursor.execute('''
                INSERT OR REPLACE INTO practice_quizzes (
                    id, title, description, student_id, questions, 
                    start_time, score, difficulty, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                quiz_data["id"],
                quiz_data["title"],
                quiz_data.get("description", ""),
                quiz_data["student_id"],
                questions_json,
                quiz_data["start_time"],
                quiz_data.get("score", None),
                quiz_data.get("difficulty", "Medium"),
                quiz_data.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            ))
            
            conn.commit()
            return quiz_data["id"]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
    
    def get_practice_quizzes(self, student_id):
        """Get practice quizzes for a student."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM practice_quizzes WHERE student_id = ? ORDER BY created_at DESC", (student_id,))
            quizzes = cursor.fetchall()
            
            return [{
                "id": quiz[0],
                "title": quiz[1],
                "description": quiz[2],
                "student_id": quiz[3],
                "questions": json.loads(quiz[4]),
                "start_time": quiz[5],
                "score": quiz[6],
                "difficulty": quiz[7],
                "created_at": quiz[8]
            } for quiz in quizzes]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def update_practice_quiz_score(self, quiz_id, score):
        """Update the score of a practice quiz."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("UPDATE practice_quizzes SET score = ? WHERE id = ?", (score, quiz_id))
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def get_quiz(self, quiz_id):
        """Get a quiz by ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
            quiz = cursor.fetchone()
            
            if quiz:
                return {
                    "id": quiz[0],
                    "title": quiz[1],
                    "description": quiz[2],
                    "course": quiz[3],
                    "start_time": quiz[4],
                    "end_time": quiz[5],
                    "duration_minutes": quiz[6],
                    "professor_id": quiz[7],
                    "questions": json.loads(quiz[8]),
                    "created_at": quiz[9]
                }
            return None
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def get_professor_quizzes(self, professor_id):
        """Get all quizzes created by a professor."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM quizzes WHERE professor_id = ?", (professor_id,))
            quizzes = cursor.fetchall()
            
            return [{
                "id": quiz[0],
                "title": quiz[1],
                "description": quiz[2],
                "course": quiz[3],
                "start_time": quiz[4],
                "end_time": quiz[5],
                "duration_minutes": quiz[6],
                "professor_id": quiz[7],
                "created_at": quiz[9]
            } for quiz in quizzes]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def get_available_quizzes_for_student(self, student_id):
        """Get all available quizzes for a student that are within the time window."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Format current datetime properly for comparison
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get quizzes that are currently active (start_time has passed AND end_time has not passed)
            # and haven't been submitted by the student
            cursor.execute("""
                SELECT q.* FROM quizzes q
                LEFT JOIN quiz_submissions s ON q.id = s.quiz_id AND s.student_id = ?
                WHERE q.start_time <= ? AND q.end_time >= ? AND s.id IS NULL
            """, (student_id, now, now))
            
            quizzes = cursor.fetchall()
            
            return [{
                "id": quiz[0],
                "title": quiz[1],
                "description": quiz[2],
                "course": quiz[3],
                "start_time": quiz[4],
                "end_time": quiz[5],
                "duration_minutes": quiz[6],
                "professor_id": quiz[7],
                "questions": json.loads(quiz[8]),
                "created_at": quiz[9],
                "status": "active"
            } for quiz in quizzes]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def start_quiz_submission(self, quiz_id, student_id):
        """Start a new quiz submission and return the submission ID."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if student already has a submission for this quiz
            cursor.execute("""
                SELECT * FROM quiz_submissions 
                WHERE quiz_id = ? AND student_id = ?
            """, (quiz_id, student_id))
            
            existing = cursor.fetchone()
            if existing:
                raise ValueError("You have already submitted this quiz")
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Insert new submission
            cursor.execute('''
                INSERT INTO quiz_submissions (
                    quiz_id, student_id, answers, start_time, created_at
                )
                VALUES (?, ?, ?, ?, ?)
            ''', (
                quiz_id,
                student_id,
                json.dumps({}),  # Empty answers initially
                now,
                now
            ))
            
            submission_id = cursor.lastrowid
            conn.commit()
            return submission_id
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def submit_quiz_answers(self, submission_id, answers, score=None, feedback=None, visible_to_students=False):
        """Update a quiz submission with answers and optionally score and feedback."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update submission
            cursor.execute('''
                UPDATE quiz_submissions 
                SET answers = ?, score = ?, feedback = ?, end_time = ?, visible_to_students = ?
                WHERE id = ?
            ''', (
                json.dumps(answers),
                score,
                feedback,
                now,
                1 if visible_to_students else 0,
                submission_id
            ))
            
            conn.commit()
            return True
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def get_student_submissions(self, student_id):
        """Get all quiz submissions for a student."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Join with quizzes to get quiz title
            cursor.execute("""
                SELECT s.*, q.title, q.course FROM quiz_submissions s
                JOIN quizzes q ON s.quiz_id = q.id
                WHERE s.student_id = ?
            """, (student_id,))
            
            submissions = cursor.fetchall()
            
            return [{
                "id": sub[0],
                "quiz_id": sub[1],
                "student_id": sub[2],
                "answers": json.loads(sub[3]) if sub[3] else {},
                "score": sub[4],
                "feedback": sub[5],
                "start_time": sub[6],
                "end_time": sub[7],
                "created_at": sub[8],
                "quiz_title": sub[9],
                "course": sub[10]
            } for sub in submissions]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close()
            
    def get_quiz_submissions(self, quiz_id):
        """Get all submissions for a quiz."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Join with users to get student name
            cursor.execute("""
                SELECT s.*, u.name, u.student_id as student_number FROM quiz_submissions s
                JOIN users u ON s.student_id = u.id
                WHERE s.quiz_id = ?
            """, (quiz_id,))
            
            submissions = cursor.fetchall()
            
            return [{
                "id": sub[0],
                "quiz_id": sub[1],
                "student_id": sub[2],
                "answers": json.loads(sub[3]) if sub[3] else {},
                "score": sub[4],
                "feedback": sub[5],
                "start_time": sub[6],
                "end_time": sub[7],
                "created_at": sub[8],
                "student_name": sub[9],
                "student_number": sub[10]
            } for sub in submissions]
        except sqlite3.Error as e:
            raise Exception(f"Database error: {str(e)}")
        finally:
            conn.close() 