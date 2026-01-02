"""Data models for chunk learner."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Chunk:
    """Represents a learning chunk/task."""
    
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    difficulty: int = 1  # 1-5 scale
    completed: bool = False
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


@dataclass
class Dependency:
    """Represents a dependency between two chunks."""
    
    id: Optional[int] = None
    chunk_id: int = 0
    depends_on_chunk_id: int = 0
