"""Tests for operations module."""

import pytest
import tempfile
import os
from pathlib import Path
from src.chunk_learner import database, operations


@pytest.fixture
def test_db():
    """Create a temporary database for testing."""
    # Save original DB path
    original_db_path = database.DB_PATH
    
    # Create temp database
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    database.DB_PATH = Path(temp_db.name)
    
    # Initialize database
    database.init_database()
    
    yield
    
    # Cleanup
    database.DB_PATH = original_db_path
    os.unlink(temp_db.name)


def test_create_chunk(test_db):
    """Test creating a new chunk."""
    chunk_id = operations.create_chunk("Learn Python", "Learn basic Python syntax", 2)
    assert chunk_id > 0
    
    chunk = operations.get_chunk_by_id(chunk_id)
    assert chunk is not None
    assert chunk.name == "Learn Python"
    assert chunk.difficulty == 2
    assert chunk.completed is False


def test_complete_chunk(test_db):
    """Test completing a chunk."""
    chunk_id = operations.create_chunk("Learn Python", "Learn basic Python syntax", 2)
    
    result = operations.complete_chunk(chunk_id)
    assert result is True
    
    chunk = operations.get_chunk_by_id(chunk_id)
    assert chunk.completed is True
    assert chunk.completed_at is not None


def test_get_all_chunks(test_db):
    """Test retrieving all chunks."""
    operations.create_chunk("Chunk 1", "Description 1", 1)
    operations.create_chunk("Chunk 2", "Description 2", 3)
    
    chunks = operations.get_all_chunks()
    assert len(chunks) == 2


def test_add_dependency(test_db):
    """Test adding dependencies between chunks."""
    chunk1_id = operations.create_chunk("Learn Pandas", "Learn pandas basics", 2)
    chunk2_id = operations.create_chunk("Build ML Model", "Create a simple model", 4)
    
    result = operations.add_dependency(chunk2_id, chunk1_id)
    assert result is True
    
    deps = operations.get_chunk_dependencies(chunk2_id)
    assert len(deps) == 1
    assert deps[0].id == chunk1_id


def test_get_next_available_chunk(test_db):
    """Test getting the next available chunk."""
    chunk1_id = operations.create_chunk("Learn Pandas", "Learn pandas basics", 2)
    chunk2_id = operations.create_chunk("Build ML Model", "Create a simple model", 4)
    operations.add_dependency(chunk2_id, chunk1_id)
    
    # Should return chunk1 since it has no dependencies
    next_chunk = operations.get_next_available_chunk()
    assert next_chunk is not None
    assert next_chunk.id == chunk1_id
    
    # Complete chunk1
    operations.complete_chunk(chunk1_id)
    
    # Now chunk2 should be available
    next_chunk = operations.get_next_available_chunk()
    assert next_chunk is not None
    assert next_chunk.id == chunk2_id
