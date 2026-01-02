"""Business logic operations for chunk management."""

import sqlite3
from datetime import datetime
from typing import List, Optional
from .database import get_connection
from .models import Chunk, Dependency


def create_chunk(name: str, description: str, difficulty: int) -> int:
    """Create a new learning chunk.
    
    Args:
        name: Name of the chunk
        description: Detailed description
        difficulty: Difficulty level (1-5)
        
    Returns:
        int: ID of the created chunk
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO chunks (name, description, difficulty) VALUES (?, ?, ?)",
        (name, description, difficulty)
    )
    
    chunk_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return chunk_id


def get_all_chunks() -> List[Chunk]:
    """Get all chunks from the database.
    
    Returns:
        List[Chunk]: List of all chunks
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM chunks ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    chunks = []
    for row in rows:
        chunk = Chunk(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            difficulty=row["difficulty"],
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        )
        chunks.append(chunk)
    
    return chunks


def get_chunk_by_id(chunk_id: int) -> Optional[Chunk]:
    """Get a specific chunk by ID.
    
    Args:
        chunk_id: ID of the chunk
        
    Returns:
        Optional[Chunk]: The chunk if found, None otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM chunks WHERE id = ?", (chunk_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return Chunk(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        difficulty=row["difficulty"],
        completed=bool(row["completed"]),
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
    )


def complete_chunk(chunk_id: int) -> bool:
    """Mark a chunk as completed.
    
    Args:
        chunk_id: ID of the chunk to complete
        
    Returns:
        bool: True if successful, False if chunk not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE chunks SET completed = 1, completed_at = ? WHERE id = ?",
        (datetime.now().isoformat(), chunk_id)
    )
    
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    
    return rows_affected > 0


def add_dependency(chunk_id: int, depends_on_chunk_id: int) -> bool:
    """Add a dependency between two chunks.
    
    Args:
        chunk_id: The chunk that has the dependency
        depends_on_chunk_id: The chunk that must be completed first
        
    Returns:
        bool: True if successful, False otherwise
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "INSERT INTO dependencies (chunk_id, depends_on_chunk_id) VALUES (?, ?)",
            (chunk_id, depends_on_chunk_id)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_chunk_dependencies(chunk_id: int) -> List[Chunk]:
    """Get all chunks that a given chunk depends on.
    
    Args:
        chunk_id: ID of the chunk
        
    Returns:
        List[Chunk]: List of dependency chunks
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.* FROM chunks c
        JOIN dependencies d ON c.id = d.depends_on_chunk_id
        WHERE d.chunk_id = ?
    """, (chunk_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    chunks = []
    for row in rows:
        chunk = Chunk(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            difficulty=row["difficulty"],
            completed=bool(row["completed"]),
            created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        )
        chunks.append(chunk)
    
    return chunks


def get_next_available_chunk() -> Optional[Chunk]:
    """Get the next chunk that can be worked on.
    
    Returns a chunk that:
    - Is not completed
    - Has all dependencies completed (or has no dependencies)
    
    Returns:
        Optional[Chunk]: Next available chunk, or None if none available
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Find chunks that are incomplete and have all dependencies met
    cursor.execute("""
        SELECT c.* FROM chunks c
        WHERE c.completed = 0
        AND NOT EXISTS (
            SELECT 1 FROM dependencies d
            JOIN chunks dep ON d.depends_on_chunk_id = dep.id
            WHERE d.chunk_id = c.id AND dep.completed = 0
        )
        ORDER BY c.difficulty ASC, c.created_at ASC
        LIMIT 1
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    return Chunk(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        difficulty=row["difficulty"],
        completed=bool(row["completed"]),
        created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
        completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
    )
