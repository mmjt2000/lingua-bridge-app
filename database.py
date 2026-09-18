# -*- coding: utf-8 -*-
"""
Base de données SQLite pour Lingua Bridge App
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = "lingua_bridge.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Crée les tables si elles n'existent pas."""
    conn = get_connection()
    c = conn.cursor()

    # Table utilisateurs
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table sessions (39 sessions du cours)
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_num TEXT UNIQUE NOT NULL,
            week INTEGER NOT NULL,
            date TEXT NOT NULL,
            day TEXT NOT NULL,
            lesson TEXT NOT NULL,
            content TEXT NOT NULL,
            duration TEXT NOT NULL,
            attended INTEGER DEFAULT 0,
            score REAL,
            notes TEXT,
            updated_at TIMESTAMP
        )
    """)

    # Table matériaux (liens vers PDFs/PPTX)
    c.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lesson TEXT NOT NULL,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            type TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Table exercices soumis par l'élève
    c.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            lesson TEXT NOT NULL,
            exercise_num INTEGER NOT NULL,
            answer TEXT,
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            feedback TEXT,
            FOREIGN KEY (student_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()


def create_user(username, password, role, full_name, email=None):
    """Crée un utilisateur."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username, password, role, full_name, email) "
            "VALUES (?, ?, ?, ?, ?)",
            (username, password, role, full_name, email)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def authenticate(username, password):
    """Vérifie login + password."""
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ? AND password = ?",
        (username, password)
    ).fetchone()
    conn.close()
    return user


def get_all_sessions():
    """Récupère les 39 sessions."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM sessions ORDER BY week, session_num"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_session_by_num(session_num):
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM sessions WHERE session_num = ?",
        (session_num,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def update_session(session_num, attended, score=None, notes=None):
    """Met à jour une session."""
    conn = get_connection()
    conn.execute("""
        UPDATE sessions
        SET attended = ?, score = ?, notes = ?, updated_at = ?
        WHERE session_num = ?
    """, (attended, score, notes, datetime.now().isoformat(), session_num))
    conn.commit()
    conn.close()


def get_stats():
    """Statistiques globales."""
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    attended = conn.execute(
        "SELECT COUNT(*) FROM sessions WHERE attended = 1"
    ).fetchone()[0]
    avg_score = conn.execute(
        "SELECT AVG(score) FROM sessions WHERE score IS NOT NULL"
    ).fetchone()[0]
    conn.close()

    return {
        "total": total,
        "attended": attended,
        "avg_score": round(avg_score, 1) if avg_score else 0,
        "attendance_rate": round(attended / total * 100, 1) if total else 0
    }
def save_submission(student_id, lesson, exercise_num, answer):
    """Sauvegarde une réponse d'élève."""
    conn = get_connection()
    # Vérifier si elle existe déjà
    existing = conn.execute("""
        SELECT id FROM submissions
        WHERE student_id = ? AND lesson = ? AND exercise_num = ?
    """, (student_id, lesson, exercise_num)).fetchone()

    if existing:
        conn.execute("""
            UPDATE submissions
            SET answer = ?, submitted_at = ?, feedback = NULL
            WHERE id = ?
        """, (answer, datetime.now().isoformat(), existing["id"]))
    else:
        conn.execute("""
            INSERT INTO submissions (student_id, lesson, exercise_num, answer)
            VALUES (?, ?, ?, ?)
        """, (student_id, lesson, exercise_num, answer))
    conn.commit()
    conn.close()


def get_student_submissions(student_id):
    """Récupère toutes les soumissions d'un élève."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT * FROM submissions
        WHERE student_id = ?
        ORDER BY lesson, exercise_num
    """, (student_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_pending_submissions():
    """Récupère toutes les soumissions sans feedback (pour le prof)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, u.full_name
        FROM submissions s
        JOIN users u ON u.id = s.student_id
        WHERE s.feedback IS NULL OR s.feedback = ''
        ORDER BY s.submitted_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_submissions_with_feedback():
    """Récupère toutes les soumissions avec feedback (pour historique)."""
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.*, u.full_name
        FROM submissions s
        JOIN users u ON u.id = s.student_id
        WHERE s.feedback IS NOT NULL AND s.feedback != ''
        ORDER BY s.submitted_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_feedback(submission_id, feedback):
    """Sauvegarde le feedback du prof."""
    conn = get_connection()
    conn.execute("""
        UPDATE submissions SET feedback = ? WHERE id = ?
    """, (feedback, submission_id))
    conn.commit()
    conn.close()


def get_student_id_by_username(username):
    """Récupère l'ID d'un élève par son username."""
    conn = get_connection()
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None

def change_password(username, new_password):
    """Change le mot de passe d'un utilisateur."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_password, username)
    )
    conn.commit()
    conn.close()
    return True


def change_password(username, new_password):
    """Change le mot de passe d'un utilisateur."""
    conn = get_connection()
    conn.execute(
        "UPDATE users SET password = ? WHERE username = ?",
        (new_password, username)
    )
    conn.commit()
    conn.close()
    return True
