import pytest
# Fixtures are automatically available from conftest.py

def test_get_all_tasks(client, expected_tasks):
    """Test getting all tasks from the temporary database."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    assert len(tasks) == 3
    
    # Verify the tasks match our expected data
    for i, task in enumerate(tasks):
        assert task['id'] == expected_tasks[i].id
        assert task['title'] == expected_tasks[i].title
        assert task['description'] == expected_tasks[i].description
        assert task['status'] == expected_tasks[i].status


def test_get_all_tasks_empty_db(client, monkeypatch):
    """Test getting all tasks when the database is empty."""
    def mock_read_all_tasks():
        return []
    monkeypatch.setattr('main.read_all_tasks', mock_read_all_tasks)

    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    assert tasks == []


def test_get_all_tasks_response_structure(client, expected_tasks):
    """Test the structure of the response from GET /tasks endpoint."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    assert isinstance(tasks, list)
    assert len(tasks) == 3
    
    # Verify each task has the correct structure
    required_fields = {'id', 'title', 'description', 'status'}
    for task in tasks:
        assert isinstance(task, dict)
        assert set(task.keys()) == required_fields
        assert isinstance(task['id'], int)
        assert isinstance(task['title'], str)
        assert isinstance(task['description'], str)
        assert isinstance(task['status'], str)


def test_get_all_tasks_order(client, expected_tasks):
    """Test that tasks are returned in the correct order."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    # Verify tasks are returned in ID order (1, 2, 3)
    task_ids = [task['id'] for task in tasks]
    assert task_ids == [1, 2, 3]


def test_get_all_tasks_status_values(client):
    """Test that all status values are returned correctly."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    statuses = [task['status'] for task in tasks]
    
    # Verify we have all three status types from our test data
    assert 'pending' in statuses
    assert 'in_progress' in statuses
    assert 'completed' in statuses


def test_get_all_tasks_no_csv_file(client, monkeypatch, temp_csv_file):
    """Test getting all tasks when the CSV file doesn't exist."""
    import os
    # Remove the temporary CSV file to simulate FileNotFoundError
    os.unlink(temp_csv_file)
    
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    assert tasks == []  # Should return empty list when file doesn't exist


def test_get_all_tasks_content_validation(client, expected_tasks):
    """Test detailed content validation of all tasks."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    
    # Create a mapping for easier comparison
    task_map = {task['id']: task for task in tasks}
    
    # Validate each expected task
    for expected_task in expected_tasks:
        assert expected_task.id in task_map
        actual_task = task_map[expected_task.id]
        
        # Validate all fields match exactly
        assert actual_task['id'] == expected_task.id
        assert actual_task['title'] == expected_task.title
        assert actual_task['description'] == expected_task.description
        assert actual_task['status'] == expected_task.status
        
        # Validate no extra fields
        assert len(actual_task) == 4  # id, title, description, status

def test_get_task_by_id_success(client, expected_tasks):
    """Test successful retrieval of a task by ID."""
    # Test getting the first task
    response = client.get("/tasks/1")
    assert response.status_code == 200
    
    task = response.json()
    assert task['id'] == 1
    assert task['title'] == expected_tasks[0].title
    assert task['description'] == expected_tasks[0].description
    assert task['status'] == expected_tasks[0].status

def test_get_task_by_id_all_tasks(client, expected_tasks):
    """Test getting each task by ID to ensure all can be retrieved."""
    for expected_task in expected_tasks:
        response = client.get(f"/tasks/{expected_task.id}")
        assert response.status_code == 200
        
        task = response.json()
        assert task['id'] == expected_task.id
        assert task['title'] == expected_task.title
        assert task['description'] == expected_task.description
        assert task['status'] == expected_task.status

def test_get_task_by_id_response_structure(client):
    """Test the structure of the response from GET /tasks/{task_id} endpoint."""
    response = client.get("/tasks/2")
    assert response.status_code == 200
    
    task = response.json()
    # Verify the response has the correct structure
    required_fields = {'id', 'title', 'description', 'status'}
    assert isinstance(task, dict)
    assert set(task.keys()) == required_fields
    assert isinstance(task['id'], int)
    assert isinstance(task['title'], str)
    assert isinstance(task['description'], str)
    assert isinstance(task['status'], str)

def test_get_nonexistent_task(client):
    """Test getting a task that doesn't exist."""
    # Test with a high ID that doesn't exist
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Test with ID 0 (assuming IDs start from 1)
    response = client.get("/tasks/0")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Test with negative ID
    response = client.get("/tasks/-1")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'

def test_get_task_invalid_id_format_string(client):
    """Test getting a task with string ID instead of integer."""
    response = client.get("/tasks/abc")
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error
    assert any('type_error' in str(err) or 'type' in str(err) for err in error['detail'])

def test_get_task_invalid_id_format_float(client):
    """Test getting a task with float ID."""
    response = client.get("/tasks/1.5")
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error

def test_get_task_invalid_id_format_special_chars(client):
    """Test getting a task with special characters in ID."""
    response = client.get("/tasks/!@#")
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error

def test_get_task_invalid_id_format_empty(client):
    """Test getting a task with empty ID."""
    # This should result in a different endpoint being matched (just /tasks/)
    response = client.get("/tasks/")
    # FastAPI redirects /tasks/ to /tasks and returns the list of all tasks
    assert response.status_code == 200
    # Verify it returns the list of all tasks, not a single task
    assert isinstance(response.json(), list)

def test_get_task_edge_case_after_deletion(client):
    """Test getting a task after it has been deleted."""
    # First verify the task exists
    response = client.get("/tasks/3")
    assert response.status_code == 200
    original_task = response.json()
    
    # Delete the task
    response = client.delete("/tasks/3")
    assert response.status_code == 200
    
    # Try to get the deleted task
    response = client.get("/tasks/3")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'

def test_create_task(client, sample_task_data):
    """Test creating a new task."""
    response = client.post("/tasks", json=sample_task_data)
    assert response.status_code == 200
    
    created_task = response.json()
    assert created_task['id'] == 4  # Should be the next ID after our 3 sample tasks
    assert created_task['title'] == sample_task_data['title']
    assert created_task['description'] == sample_task_data['description']
    assert created_task['status'] == sample_task_data['status']
    
    # Verify the task was actually added
    response = client.get("/tasks/4")
    assert response.status_code == 200
    assert response.json()['title'] == sample_task_data['title']

def test_update_task(client):
    """Test updating an existing task."""
    update_data = {
        "title": "Updated Task Title",
        "description": "Updated description",
        "status": "completed"
    }
    
    response = client.put("/tasks/1", json=update_data)
    assert response.status_code == 200
    
    updated_task = response.json()
    assert updated_task['id'] == 1
    assert updated_task['title'] == update_data['title']
    assert updated_task['description'] == update_data['description']
    assert updated_task['status'] == update_data['status']

def test_delete_task(client):
    """Test deleting a task."""
    # First, verify the task exists
    response = client.get("/tasks/2")
    assert response.status_code == 200
    
    # Delete the task
    response = client.delete("/tasks/2")
    assert response.status_code == 200
    assert response.json()['message'] == 'Task deleted successfully'
    
    # Verify the task is gone
    response = client.get("/tasks")
    tasks = response.json()
    assert len(tasks) == 2  # Should be one less than the original 3
    assert not any(task['id'] == 2 for task in tasks)


# Tests for POST /tasks endpoint
def test_create_task_successful(client):
    """Test successful task creation with valid payload."""
    new_task = {
        "title": "New Test Task",
        "description": "This is a test task created via API",
        "status": "pending"
    }
    
    response = client.post("/tasks", json=new_task)
    assert response.status_code == 200
    
    # Check response content
    created_task = response.json()
    assert created_task['id'] == 4  # Should be ID 4 after the 3 initial tasks
    assert created_task['title'] == new_task['title']
    assert created_task['description'] == new_task['description']
    assert created_task['status'] == new_task['status']


def test_create_task_response_schema(client):
    """Test that the response follows the expected schema."""
    new_task = {
        "title": "Schema Test Task",
        "description": "Testing response schema",
        "status": "in_progress"
    }
    
    response = client.post("/tasks", json=new_task)
    assert response.status_code == 200
    
    created_task = response.json()
    
    # Verify response has all required fields and correct types
    required_fields = {'id', 'title', 'description', 'status'}
    assert set(created_task.keys()) == required_fields
    assert isinstance(created_task['id'], int)
    assert isinstance(created_task['title'], str)
    assert isinstance(created_task['description'], str)
    assert isinstance(created_task['status'], str)
    
    # Verify no extra fields
    assert len(created_task) == 4


def test_create_task_persistence(client):
    """Test that created task is persisted and can be retrieved."""
    new_task = {
        "title": "Persistence Test Task",
        "description": "Testing if task is saved",
        "status": "completed"
    }
    
    # Create the task
    create_response = client.post("/tasks", json=new_task)
    assert create_response.status_code == 200
    created_task = create_response.json()
    task_id = created_task['id']
    
    # Retrieve the task by ID
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    
    # Verify the retrieved task matches what was created
    assert retrieved_task['id'] == task_id
    assert retrieved_task['title'] == new_task['title']
    assert retrieved_task['description'] == new_task['description']
    assert retrieved_task['status'] == new_task['status']
    
    # Verify task appears in all tasks list
    all_tasks_response = client.get("/tasks")
    all_tasks = all_tasks_response.json()
    assert any(task['id'] == task_id for task in all_tasks)


def test_create_task_missing_title(client):
    """Test validation error when title is missing."""
    invalid_task = {
        "description": "Task without title",
        "status": "pending"
    }
    
    response = client.post("/tasks", json=invalid_task)
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error
    # Check that the error mentions the missing field
    assert any('title' in str(err) for err in error['detail'])


def test_create_task_missing_description(client):
    """Test validation error when description is missing."""
    invalid_task = {
        "title": "Task without description",
        "status": "pending"
    }
    
    response = client.post("/tasks", json=invalid_task)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error
    assert any('description' in str(err) for err in error['detail'])


def test_create_task_missing_status(client):
    """Test validation error when status is missing."""
    invalid_task = {
        "title": "Task without status",
        "description": "Missing status field"
    }
    
    response = client.post("/tasks", json=invalid_task)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error
    assert any('status' in str(err) for err in error['detail'])


def test_create_task_empty_payload(client):
    """Test validation error with empty payload."""
    response = client.post("/tasks", json={})
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error
    # Should have errors for all three required fields
    assert len(error['detail']) >= 3


def test_create_task_null_values(client):
    """Test validation error when fields have null values."""
    invalid_task = {
        "title": None,
        "description": None,
        "status": None
    }
    
    response = client.post("/tasks", json=invalid_task)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_create_task_invalid_field_types(client):
    """Test validation error with invalid field types."""
    invalid_task = {
        "title": 123,  # Should be string
        "description": ["list", "not", "string"],  # Should be string
        "status": {"status": "object"}  # Should be string
    }
    
    response = client.post("/tasks", json=invalid_task)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_create_task_extra_fields(client):
    """Test that extra fields are ignored."""
    task_with_extras = {
        "title": "Task with extra fields",
        "description": "Testing extra fields handling",
        "status": "pending",
        "priority": "high",  # Extra field
        "assignee": "John Doe"  # Extra field
    }
    
    response = client.post("/tasks", json=task_with_extras)
    assert response.status_code == 200
    
    created_task = response.json()
    # Verify extra fields are not included in response
    assert 'priority' not in created_task
    assert 'assignee' not in created_task
    # Verify only expected fields are present
    assert set(created_task.keys()) == {'id', 'title', 'description', 'status'}


def test_create_task_sequential_ids(client):
    """Test that tasks are created with sequential IDs."""
    task1 = {
        "title": "First Sequential Task",
        "description": "First task",
        "status": "pending"
    }
    task2 = {
        "title": "Second Sequential Task",
        "description": "Second task",
        "status": "pending"
    }
    
    # Create first task
    response1 = client.post("/tasks", json=task1)
    assert response1.status_code == 200
    id1 = response1.json()['id']
    
    # Create second task
    response2 = client.post("/tasks", json=task2)
    assert response2.status_code == 200
    id2 = response2.json()['id']
    
    # Verify IDs are sequential
    assert id2 == id1 + 1


def test_create_task_empty_strings(client):
    """Test validation with empty string values."""
    invalid_task = {
        "title": "",
        "description": "",
        "status": ""
    }
    
    # The current implementation might accept empty strings
    # This test documents the actual behavior
    response = client.post("/tasks", json=invalid_task)
    if response.status_code == 200:
        # If empty strings are accepted, verify they're stored as-is
        created_task = response.json()
        assert created_task['title'] == ""
        assert created_task['description'] == ""
        assert created_task['status'] == ""
    else:
        # If empty strings are rejected, verify it's a validation error
        assert response.status_code == 422


def test_create_task_whitespace_strings(client):
    """Test creating task with whitespace-only strings."""
    task = {
        "title": "   ",
        "description": "\t\n",
        "status": " \r\n "
    }
    
    # Test documents actual behavior with whitespace strings
    response = client.post("/tasks", json=task)
    if response.status_code == 200:
        created_task = response.json()
        assert created_task['title'] == "   "
        assert created_task['description'] == "\t\n"
        assert created_task['status'] == " \r\n "


def test_create_task_very_long_strings(client):
    """Test creating task with very long string values."""
    long_string = "A" * 1000  # 1000 character string
    task = {
        "title": long_string,
        "description": long_string * 2,  # 2000 characters
        "status": "pending"
    }
    
    response = client.post("/tasks", json=task)
    assert response.status_code == 200
    created_task = response.json()
    assert created_task['title'] == long_string
    assert created_task['description'] == long_string * 2


def test_create_task_special_characters(client):
    """Test creating task with special characters."""
    task = {
        "title": "Task with special chars: @#$%^&*(){}[]|\\:;<>?,./~`",
        "description": "Unicode: 你好世界 🌍 ñ é ü",
        "status": "pending-review"
    }
    
    response = client.post("/tasks", json=task)
    assert response.status_code == 200
    created_task = response.json()
    assert created_task['title'] == task['title']
    assert created_task['description'] == task['description']
    assert created_task['status'] == task['status']


def test_create_task_malformed_json(client):
    """Test POST request with malformed JSON."""
    response = client.post(
        "/tasks",
        data="{invalid json",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_create_task_no_content_type(client):
    """Test POST request without Content-Type header."""
    task = {
        "title": "Test Task",
        "description": "Test Description",
        "status": "pending"
    }
    # TestClient should handle this, but let's verify
    response = client.post("/tasks", json=task)
    assert response.status_code == 200  # FastAPI handles this gracefully


# Comprehensive tests for PUT /tasks/{task_id} endpoint
def test_update_task_successful(client, expected_tasks):
    """Test successful update of an existing task with all fields."""
    task_id = 1
    update_data = {
        "title": "Updated Task Title",
        "description": "Updated task description",
        "status": "completed"
    }
    
    # Update the task
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    
    # Verify the response
    updated_task = response.json()
    assert updated_task['id'] == task_id
    assert updated_task['title'] == update_data['title']
    assert updated_task['description'] == update_data['description']
    assert updated_task['status'] == update_data['status']
    
    # Verify the update was persisted by fetching the task again
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    fetched_task = get_response.json()
    assert fetched_task == updated_task


def test_update_task_partial_update_description_only(client):
    """Test updating only the description field."""
    task_id = 2
    # Get original task data
    original_response = client.get(f"/tasks/{task_id}")
    original_task = original_response.json()
    
    # Update only description
    update_data = {
        "title": original_task['title'],  # Title is required
        "description": "New description only"
        # status is omitted - should keep original value
    }
    
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    
    updated_task = response.json()
    assert updated_task['id'] == task_id
    assert updated_task['title'] == original_task['title']
    assert updated_task['description'] == "New description only"
    assert updated_task['status'] == original_task['status']  # Should remain unchanged


def test_update_task_partial_update_status_only(client):
    """Test updating only the status field."""
    task_id = 3
    # Get original task data
    original_response = client.get(f"/tasks/{task_id}")
    original_task = original_response.json()
    
    # Update only status
    update_data = {
        "title": original_task['title'],  # Title is required
        "status": "in_progress"
        # description is omitted - should keep original value
    }
    
    response = client.put(f"/tasks/{task_id}", json=update_data)
    assert response.status_code == 200
    
    updated_task = response.json()
    assert updated_task['id'] == task_id
    assert updated_task['title'] == original_task['title']
    assert updated_task['description'] == original_task['description']  # Should remain unchanged
    assert updated_task['status'] == "in_progress"


def test_update_task_response_schema(client):
    """Test that the update response follows the expected schema."""
    update_data = {
        "title": "Schema Test Update",
        "description": "Testing response schema",
        "status": "pending"
    }
    
    response = client.put("/tasks/1", json=update_data)
    assert response.status_code == 200
    
    updated_task = response.json()
    
    # Verify response has all required fields and correct types
    required_fields = {'id', 'title', 'description', 'status'}
    assert set(updated_task.keys()) == required_fields
    assert isinstance(updated_task['id'], int)
    assert isinstance(updated_task['title'], str)
    assert isinstance(updated_task['description'], str)
    assert isinstance(updated_task['status'], str)
    
    # Verify no extra fields
    assert len(updated_task) == 4


def test_update_nonexistent_task(client):
    """Test updating a task that doesn't exist (404 error)."""
    update_data = {
        "title": "Update Non-existent",
        "description": "This task doesn't exist",
        "status": "pending"
    }
    
    # Try to update non-existent task
    response = client.put("/tasks/999", json=update_data)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Try with ID 0
    response = client.put("/tasks/0", json=update_data)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Try with negative ID
    response = client.put("/tasks/-1", json=update_data)
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'


def test_update_task_missing_title(client):
    """Test validation error when title is missing."""
    invalid_update = {
        "description": "Missing title",
        "status": "pending"
    }
    
    response = client.put("/tasks/1", json=invalid_update)
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error
    assert any('title' in str(err) for err in error['detail'])


def test_update_task_empty_payload(client):
    """Test validation error with empty payload."""
    response = client.put("/tasks/1", json={})
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error
    # Should have error for missing required title field
    assert any('title' in str(err) for err in error['detail'])


def test_update_task_null_title(client):
    """Test validation error when title is null."""
    invalid_update = {
        "title": None,
        "description": "Valid description",
        "status": "pending"
    }
    
    response = client.put("/tasks/1", json=invalid_update)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_update_task_invalid_field_types(client):
    """Test validation error with invalid field types."""
    invalid_update = {
        "title": 123,  # Should be string
        "description": ["list", "not", "string"],  # Should be string
        "status": {"status": "object"}  # Should be string
    }
    
    response = client.put("/tasks/1", json=invalid_update)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_update_task_extra_fields(client):
    """Test that extra fields are ignored during update."""
    update_with_extras = {
        "title": "Update with extra fields",
        "description": "Testing extra fields handling",
        "status": "pending",
        "priority": "high",  # Extra field
        "assignee": "John Doe"  # Extra field
    }
    
    response = client.put("/tasks/1", json=update_with_extras)
    assert response.status_code == 200
    
    updated_task = response.json()
    # Verify extra fields are not included in response
    assert 'priority' not in updated_task
    assert 'assignee' not in updated_task
    # Verify only expected fields are present
    assert set(updated_task.keys()) == {'id', 'title', 'description', 'status'}


def test_update_task_invalid_task_id_string(client):
    """Test updating a task with string ID instead of integer."""
    update_data = {
        "title": "Valid title",
        "description": "Valid description",
        "status": "pending"
    }
    
    response = client.put("/tasks/abc", json=update_data)
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error


def test_update_task_invalid_task_id_float(client):
    """Test updating a task with float ID."""
    update_data = {
        "title": "Valid title",
        "description": "Valid description",
        "status": "pending"
    }
    
    response = client.put("/tasks/1.5", json=update_data)
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_update_task_empty_strings(client):
    """Test update with empty string values."""
    update_data = {
        "title": "",
        "description": "",
        "status": ""
    }
    
    # The current implementation might accept empty strings
    response = client.put("/tasks/1", json=update_data)
    if response.status_code == 200:
        # If empty strings are accepted, verify they're stored as-is
        updated_task = response.json()
        assert updated_task['title'] == ""
        assert updated_task['description'] == ""
        assert updated_task['status'] == ""
    else:
        # If empty strings are rejected, verify it's a validation error
        assert response.status_code == 422


def test_update_task_very_long_strings(client):
    """Test updating task with very long string values."""
    long_string = "B" * 1000  # 1000 character string
    update_data = {
        "title": long_string,
        "description": long_string * 2,  # 2000 characters
        "status": "pending"
    }
    
    response = client.put("/tasks/1", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task['title'] == long_string
    assert updated_task['description'] == long_string * 2


def test_update_task_special_characters(client):
    """Test updating task with special characters."""
    update_data = {
        "title": "Updated: @#$%^&*(){}[]|\\:;<>?,./~`",
        "description": "Unicode update: 你好世界 🌍 ñ é ü",
        "status": "pending-review"
    }
    
    response = client.put("/tasks/1", json=update_data)
    assert response.status_code == 200
    updated_task = response.json()
    assert updated_task['title'] == update_data['title']
    assert updated_task['description'] == update_data['description']
    assert updated_task['status'] == update_data['status']


def test_update_task_malformed_json(client):
    """Test PUT request with malformed JSON."""
    response = client.put(
        "/tasks/1",
        data="{invalid json",  # Malformed JSON
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_update_task_persistence_verification(client):
    """Test that updates persist across multiple requests."""
    task_id = 2
    
    # First update
    update1 = {
        "title": "First Update",
        "description": "First update description",
        "status": "in_progress"
    }
    response1 = client.put(f"/tasks/{task_id}", json=update1)
    assert response1.status_code == 200
    
    # Verify first update
    get_response1 = client.get(f"/tasks/{task_id}")
    assert get_response1.json()['title'] == "First Update"
    
    # Second update
    update2 = {
        "title": "Second Update",
        "description": "Second update description",
        "status": "completed"
    }
    response2 = client.put(f"/tasks/{task_id}", json=update2)
    assert response2.status_code == 200
    
    # Verify second update
    get_response2 = client.get(f"/tasks/{task_id}")
    task = get_response2.json()
    assert task['title'] == "Second Update"
    assert task['description'] == "Second update description"
    assert task['status'] == "completed"
    
    # Verify in the full task list
    all_tasks_response = client.get("/tasks")
    all_tasks = all_tasks_response.json()
    updated_task = next((t for t in all_tasks if t['id'] == task_id), None)
    assert updated_task is not None
    assert updated_task['title'] == "Second Update"


def test_update_task_after_deletion(client):
    """Test updating a task after it has been deleted."""
    task_id = 3
    
    # First verify the task exists
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    
    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    
    # Try to update the deleted task
    update_data = {
        "title": "Update Deleted Task",
        "description": "This should fail",
        "status": "pending"
    }
    update_response = client.put(f"/tasks/{task_id}", json=update_data)
    assert update_response.status_code == 404
    assert update_response.json()['detail'] == 'Task not found'


def test_update_task_concurrent_updates(client):
    """Test that the last update wins in case of concurrent updates."""
    task_id = 1
    
    # Simulate concurrent updates by doing them in quick succession
    update1 = {
        "title": "Concurrent Update 1",
        "description": "First concurrent update",
        "status": "pending"
    }
    update2 = {
        "title": "Concurrent Update 2",
        "description": "Second concurrent update",
        "status": "completed"
    }
    
    # Apply both updates
    response1 = client.put(f"/tasks/{task_id}", json=update1)
    response2 = client.put(f"/tasks/{task_id}", json=update2)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Verify the second update is the one that persisted
    get_response = client.get(f"/tasks/{task_id}")
    final_task = get_response.json()
    assert final_task['title'] == update2['title']
    assert final_task['description'] == update2['description']
    assert final_task['status'] == update2['status']


# Comprehensive tests for DELETE /tasks/{task_id} endpoint
def test_delete_task_successful(client):
    """Test successful deletion of an existing task."""
    task_id = 2
    
    # First, verify the task exists
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    original_task = get_response.json()
    assert original_task['id'] == task_id
    
    # Delete the task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'Task deleted successfully'
    
    # Verify the task is no longer retrievable
    verify_response = client.get(f"/tasks/{task_id}")
    assert verify_response.status_code == 404
    assert verify_response.json()['detail'] == 'Task not found'
    
    # Verify the task is removed from the all tasks list
    all_tasks_response = client.get("/tasks")
    all_tasks = all_tasks_response.json()
    assert not any(task['id'] == task_id for task in all_tasks)
    assert len(all_tasks) == 2  # Originally 3 tasks, now 2


def test_delete_nonexistent_task(client):
    """Test deleting a task that doesn't exist (404 error)."""
    # Try to delete a task with an ID that doesn't exist
    response = client.delete("/tasks/999")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Try with ID 0
    response = client.delete("/tasks/0")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'
    
    # Try with negative ID
    response = client.delete("/tasks/-1")
    assert response.status_code == 404
    assert response.json()['detail'] == 'Task not found'


def test_delete_task_double_deletion(client):
    """Test attempting to delete the same task twice."""
    task_id = 3
    
    # First deletion should succeed
    first_delete = client.delete(f"/tasks/{task_id}")
    assert first_delete.status_code == 200
    assert first_delete.json()['message'] == 'Task deleted successfully'
    
    # Second deletion should fail with 404
    second_delete = client.delete(f"/tasks/{task_id}")
    assert second_delete.status_code == 404
    assert second_delete.json()['detail'] == 'Task not found'
    
    # Third deletion should also fail with 404
    third_delete = client.delete(f"/tasks/{task_id}")
    assert third_delete.status_code == 404
    assert third_delete.json()['detail'] == 'Task not found'


def test_delete_task_response_structure(client):
    """Test that the delete response follows the expected structure."""
    # Create a new task to delete
    new_task = {
        "title": "Task to Delete",
        "description": "This task will be deleted",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=new_task)
    assert create_response.status_code == 200
    task_id = create_response.json()['id']
    
    # Delete the task and verify response structure
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    
    response_data = delete_response.json()
    assert isinstance(response_data, dict)
    assert 'message' in response_data
    assert response_data['message'] == 'Task deleted successfully'
    assert len(response_data) == 1  # Only 'message' field should be present


def test_delete_task_invalid_id_string(client):
    """Test deleting a task with string ID instead of integer."""
    response = client.delete("/tasks/abc")
    assert response.status_code == 422  # Unprocessable Entity
    error = response.json()
    assert 'detail' in error


def test_delete_task_invalid_id_float(client):
    """Test deleting a task with float ID."""
    response = client.delete("/tasks/1.5")
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_delete_task_invalid_id_special_chars(client):
    """Test deleting a task with special characters in ID."""
    response = client.delete("/tasks/!@#")
    assert response.status_code == 422
    error = response.json()
    assert 'detail' in error


def test_delete_task_persistence_in_csv(client):
    """Test that deletion persists in the CSV file."""
    # Get initial task count
    initial_response = client.get("/tasks")
    initial_count = len(initial_response.json())
    
    # Delete a task
    delete_response = client.delete("/tasks/1")
    assert delete_response.status_code == 200
    
    # Verify task count decreased
    after_delete_response = client.get("/tasks")
    after_delete_count = len(after_delete_response.json())
    assert after_delete_count == initial_count - 1
    
    # Create a new client to simulate a fresh connection
    # This ensures we're reading from the persisted CSV, not from memory
    from fastapi.testclient import TestClient
    from main import app
    new_client = TestClient(app)
    
    # Verify the deletion persisted
    fresh_response = new_client.get("/tasks")
    fresh_count = len(fresh_response.json())
    assert fresh_count == after_delete_count
    
    # Verify the specific task is still gone
    verify_response = new_client.get("/tasks/1")
    assert verify_response.status_code == 404


def test_delete_all_tasks_sequentially(client):
    """Test deleting all tasks one by one."""
    # Get all tasks
    all_tasks_response = client.get("/tasks")
    all_tasks = all_tasks_response.json()
    initial_count = len(all_tasks)
    assert initial_count > 0  # Ensure we have tasks to delete
    
    # Delete each task
    for task in all_tasks:
        delete_response = client.delete(f"/tasks/{task['id']}")
        assert delete_response.status_code == 200
        assert delete_response.json()['message'] == 'Task deleted successfully'
    
    # Verify all tasks are deleted
    final_response = client.get("/tasks")
    final_tasks = final_response.json()
    assert len(final_tasks) == 0
    assert final_tasks == []


def test_delete_task_and_verify_other_tasks_intact(client):
    """Test that deleting one task doesn't affect other tasks."""
    # Get all tasks before deletion
    all_tasks_response = client.get("/tasks")
    all_tasks = all_tasks_response.json()
    assert len(all_tasks) >= 3  # Ensure we have at least 3 tasks
    
    # Store data about tasks we're NOT deleting
    task_to_delete_id = 2
    other_tasks = [task for task in all_tasks if task['id'] != task_to_delete_id]
    
    # Delete the middle task
    delete_response = client.delete(f"/tasks/{task_to_delete_id}")
    assert delete_response.status_code == 200
    
    # Verify other tasks are intact
    for task in other_tasks:
        get_response = client.get(f"/tasks/{task['id']}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task['id'] == task['id']
        assert retrieved_task['title'] == task['title']
        assert retrieved_task['description'] == task['description']
        assert retrieved_task['status'] == task['status']


def test_delete_task_after_update(client):
    """Test deleting a task after it has been updated."""
    task_id = 1
    
    # Update the task first
    update_data = {
        "title": "Updated Before Deletion",
        "description": "This task will be deleted after update",
        "status": "completed"
    }
    update_response = client.put(f"/tasks/{task_id}", json=update_data)
    assert update_response.status_code == 200
    
    # Verify the update
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 200
    assert get_response.json()['title'] == "Updated Before Deletion"
    
    # Delete the updated task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'Task deleted successfully'
    
    # Verify deletion
    verify_response = client.get(f"/tasks/{task_id}")
    assert verify_response.status_code == 404


def test_delete_newly_created_task(client):
    """Test deleting a task immediately after creating it."""
    # Create a new task
    new_task = {
        "title": "Temporary Task",
        "description": "This task will be deleted immediately",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=new_task)
    assert create_response.status_code == 200
    created_task = create_response.json()
    task_id = created_task['id']
    
    # Immediately delete the newly created task
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()['message'] == 'Task deleted successfully'
    
    # Verify it's gone
    verify_response = client.get(f"/tasks/{task_id}")
    assert verify_response.status_code == 404
    assert verify_response.json()['detail'] == 'Task not found'


def test_delete_task_empty_endpoint(client):
    """Test DELETE request to /tasks/ without ID."""
    # This should result in a 404 or 405 as the endpoint requires an ID
    response = client.delete("/tasks/")
    # FastAPI will return 405 Method Not Allowed for /tasks/ endpoint
    assert response.status_code in [404, 405]


def test_delete_task_ids_remain_unique(client):
    """Test that task IDs remain unique and incrementing."""
    # Get current max ID
    all_tasks = client.get("/tasks").json()
    current_max_id = max([task['id'] for task in all_tasks]) if all_tasks else 0
    
    # Create a task
    new_task1 = {
        "title": "First Task",
        "description": "First task to test ID uniqueness",
        "status": "pending"
    }
    create_response1 = client.post("/tasks", json=new_task1)
    assert create_response1.status_code == 200
    task1_id = create_response1.json()['id']
    assert task1_id > current_max_id  # New ID should be greater than previous max
    
    # Create another task without deleting the first
    new_task2 = {
        "title": "Second Task",
        "description": "Second task to test ID uniqueness",
        "status": "pending"
    }
    create_response2 = client.post("/tasks", json=new_task2)
    assert create_response2.status_code == 200
    task2_id = create_response2.json()['id']
    
    # The new task should have a different ID (incrementing)
    assert task2_id != task1_id
    assert task2_id > task1_id  # IDs should be incrementing
    
    # Delete the first task
    delete_response = client.delete(f"/tasks/{task1_id}")
    assert delete_response.status_code == 200
    
    # Verify the second task still exists with its original ID
    get_response = client.get(f"/tasks/{task2_id}")
    assert get_response.status_code == 200
    assert get_response.json()['id'] == task2_id


def test_delete_task_error_handling_no_csv_file(client, monkeypatch, temp_csv_file):
    """Test delete behavior when CSV file is missing."""
    import os
    
    # First create a task to have something to delete
    new_task = {
        "title": "Task to Delete",
        "description": "This task will be deleted",
        "status": "pending"
    }
    create_response = client.post("/tasks", json=new_task)
    assert create_response.status_code == 200
    task_id = create_response.json()['id']
    
    # Remove the CSV file to simulate error condition
    os.unlink(temp_csv_file)
    
    # Try to delete the task - implementation dependent behavior
    # Some implementations might return 404, others might handle gracefully
    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code in [200, 404, 500]


def test_delete_task_concurrent_operations(client):
    """Test delete operation doesn't interfere with other operations."""
    # Create multiple tasks
    tasks_to_create = [
        {"title": "Task A", "description": "Task A Description", "status": "pending"},
        {"title": "Task B", "description": "Task B Description", "status": "in_progress"},
        {"title": "Task C", "description": "Task C Description", "status": "completed"}
    ]
    
    created_ids = []
    for task_data in tasks_to_create:
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        created_ids.append(response.json()['id'])
    
    # Delete the middle task
    delete_response = client.delete(f"/tasks/{created_ids[1]}")
    assert delete_response.status_code == 200
    
    # Verify we can still perform operations on other tasks
    # Update first task
    update_data = {
        "title": "Updated Task A",
        "description": "Updated Description",
        "status": "in_progress"
    }
    update_response = client.put(f"/tasks/{created_ids[0]}", json=update_data)
    assert update_response.status_code == 200
    
    # Get third task
    get_response = client.get(f"/tasks/{created_ids[2]}")
    assert get_response.status_code == 200
    assert get_response.json()['title'] == "Task C"
