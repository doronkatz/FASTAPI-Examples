"""
Pytest configuration file containing shared fixtures for testing the FastAPI task manager application.

This file provides fixtures that:
1. Create a temporary CSV file with sample task data
2. Override the application's database dependency to use the temporary file
3. Clean up the temporary file after tests complete
"""

import pytest
import csv
import os
import tempfile
from fastapi.testclient import TestClient
from main import app
from models import TaskWithId
import operations

@pytest.fixture
def temp_csv_file():
    """Create a temporary CSV file for testing with sample task data."""
    # Create a temporary file
    fd, temp_path = tempfile.mkstemp(suffix='.csv')
    
    # Sample task data for testing
    sample_tasks = [
        {'id': '1', 'title': 'Test Task 1', 'description': 'Description for task 1', 'status': 'pending'},
        {'id': '2', 'title': 'Test Task 2', 'description': 'Description for task 2', 'status': 'in_progress'},
        {'id': '3', 'title': 'Test Task 3', 'description': 'Description for task 3', 'status': 'completed'}
    ]
    
    # Write sample data to the temporary file
    with os.fdopen(fd, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'status'])
        writer.writeheader()
        writer.writerows(sample_tasks)
    
    yield temp_path
    
    # Cleanup: remove the temporary file after test completes
    try:
        os.unlink(temp_path)
    except FileNotFoundError:
        pass  # File already deleted

@pytest.fixture
def mock_database_file(temp_csv_file, monkeypatch):
    """
    Override the database filename to use the temporary CSV file.
    
    This fixture patches both:
    1. The DATABASE_FILENAME constant in the operations module
    2. The open() function to redirect 'tasks.csv' to our temporary file
    """
    # Patch the DATABASE_FILENAME in operations module
    monkeypatch.setattr(operations, 'DATABASE_FILENAME', temp_csv_file)
    
    # For the hardcoded 'tasks.csv' in main.py's delete_task function,
    # we need to patch the open function
    original_open = open
    
    def mock_open(file, *args, **kwargs):
        if file == 'tasks.csv':
            return original_open(temp_csv_file, *args, **kwargs)
        return original_open(file, *args, **kwargs)
    
    monkeypatch.setattr('builtins.open', mock_open)
    
    yield temp_csv_file

@pytest.fixture
def client(mock_database_file):
    """Create a FastAPI test client with the mocked database."""
    return TestClient(app)

@pytest.fixture
def sample_task_data():
    """Provide sample task data for creating new tasks in tests."""
    return {
        "title": "New Test Task",
        "description": "This is a new test task",
        "status": "pending"
    }

@pytest.fixture
def expected_tasks():
    """Provide expected task data that matches the sample CSV content."""
    return [
        TaskWithId(id=1, title='Test Task 1', description='Description for task 1', status='pending'),
        TaskWithId(id=2, title='Test Task 2', description='Description for task 2', status='in_progress'),
        TaskWithId(id=3, title='Test Task 3', description='Description for task 3', status='completed')
    ]

@pytest.fixture(autouse=True)
def ensure_clean_state():
    """
    Ensure a clean state before and after each test.
    This fixture runs automatically for all tests.
    """
    # Setup: nothing needed before test
    yield
    # Teardown: ensure no stray tasks.csv file exists
    if os.path.exists('tasks.csv'):
        os.unlink('tasks.csv')
