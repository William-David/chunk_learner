"""Database setup and connection management."""

import sqlite3
from pathlib import Path
from typing import Optional


# Database file location
DB_PATH = Path(__file__).parent.parent.parent / "data" / "chunk_learner.db"


def get_connection() -> sqlite3.Connection:
    """Get a database connection.
    
    Returns:
        sqlite3.Connection: Database connection with row factory enabled
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This lets us access columns by name
    return conn


def init_database() -> None:
    """Initialize the database with required tables.
    
    Creates the chunks and dependencies tables if they don't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create chunks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            difficulty INTEGER NOT NULL CHECK(difficulty BETWEEN 1 AND 5),
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    # Create dependencies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk_id INTEGER NOT NULL,
            depends_on_chunk_id INTEGER NOT NULL,
            FOREIGN KEY (chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
            FOREIGN KEY (depends_on_chunk_id) REFERENCES chunks(id) ON DELETE CASCADE,
            UNIQUE(chunk_id, depends_on_chunk_id)
        )
    """)
    
    conn.commit()
    conn.close()


def database_exists() -> bool:
    """Check if the database file exists.
    
    Returns:
        bool: True if database exists, False otherwise
    """
    return DB_PATH.exists()
