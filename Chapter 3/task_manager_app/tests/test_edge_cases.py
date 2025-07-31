"""
Comprehensive edge case and validation tests for the Task Manager API.

This test suite explicitly tests:
- Empty task lists
- Invalid task IDs (non-existent, wrong types, edge values)
- Missing required fields
- Extra fields in requests
- Bad input data (wrong types, null values, empty strings)
- Malformed JSON
- Boundary conditions
- Concurrent operations
- Error handling scenarios
"""

import pytest
import json
from fastapi.testclient import TestClient

# Test fixtures are automatically available from conftest.py


class TestEmptyTaskList:
    """Test cases for empty task list scenarios."""
    
    def test_get_tasks_empty_database(self, client, monkeypatch):
        """Test GET /tasks when database is completely empty."""
        def mock_read_all_tasks():
            return []
        monkeypatch.setattr('main.read_all_tasks', mock_read_all_tasks)
        
        response = client.get("/tasks")
        assert response.status_code == 200
        assert response.json() == []
        assert isinstance(response.json(), list)
    
    def test_operations_on_empty_database(self, client, monkeypatch):
        """Test various operations when no tasks exist."""
        def mock_read_all_tasks():
            return []
        monkeypatch.setattr('main.read_all_tasks', mock_read_all_tasks)
        
        # Try to get a non-existent task
        response = client.get("/tasks/1")
        assert response.status_code == 404
        assert response.json()['detail'] == 'Task not found'
        
        # Try to update a non-existent task
        update_data = {"title": "Update", "description": "Test", "status": "pending"}
        response = client.put("/tasks/1", json=update_data)
        assert response.status_code == 404
        
        # Try to delete a non-existent task
        response = client.delete("/tasks/1")
        assert response.status_code == 404


class TestInvalidTaskIDs:
    """Test cases for invalid task ID scenarios."""
    
    def test_get_task_invalid_id_types(self, client):
        """Test GET /tasks/{id} with various invalid ID types."""
        invalid_ids = [
            "abc",           # String
            "1.5",           # Float
            "true",          # Boolean as string
            "null",          # Null as string
            "[1,2,3]",       # Array as string
            '{"id":1}',      # Object as string
            "1a2b3c",        # Alphanumeric
            "!@#$%",         # Special characters
            " ",             # Space
            "123 456",       # Space in number
            "1e10",          # Scientific notation
            "0x10",          # Hexadecimal
            "NaN",           # Not a Number
            "Infinity",      # Infinity
            "",              # Empty (will hit different endpoint)
        ]
        
        for invalid_id in invalid_ids:
            if invalid_id == "":  # Empty ID results in listing all tasks
                response = client.get(f"/tasks/{invalid_id}")
                assert response.status_code == 200
                assert isinstance(response.json(), list)
            else:
                response = client.get(f"/tasks/{invalid_id}")
                assert response.status_code == 422
                assert 'detail' in response.json()
    
    def test_boundary_task_ids(self, client):
        """Test task IDs at boundary values."""
        boundary_ids = [
            0,                    # Zero
            -1,                   # Negative
            -999999,              # Large negative
            999999999999,         # Very large positive
            2147483647,           # Max 32-bit int
            -2147483648,          # Min 32-bit int
            9223372036854775807,  # Max 64-bit int
        ]
        
        for task_id in boundary_ids:
            # GET request
            response = client.get(f"/tasks/{task_id}")
            assert response.status_code == 404
            assert response.json()['detail'] == 'Task not found'
            
            # PUT request
            update_data = {"title": "Test", "description": "Test", "status": "pending"}
            response = client.put(f"/tasks/{task_id}", json=update_data)
            assert response.status_code == 404
            
            # DELETE request
            response = client.delete(f"/tasks/{task_id}")
            assert response.status_code == 404


class TestMissingRequiredFields:
    """Test cases for missing required fields in requests."""
    
    def test_create_task_missing_fields(self, client):
        """Test POST /tasks with various missing field combinations."""
        # All possible combinations of missing fields
        invalid_payloads = [
            {},  # Empty payload
            {"title": "Only Title"},  # Missing description and status
            {"description": "Only Description"},  # Missing title and status
            {"status": "pending"},  # Missing title and description
            {"title": "Title", "description": "Desc"},  # Missing status
            {"title": "Title", "status": "pending"},  # Missing description
            {"description": "Desc", "status": "pending"},  # Missing title
        ]
        
        for payload in invalid_payloads:
            response = client.post("/tasks", json=payload)
            assert response.status_code == 422
            error = response.json()
            assert 'detail' in error
            
            # Verify error mentions the missing fields
            error_str = str(error['detail'])
            if 'title' not in payload:
                assert 'title' in error_str.lower()
            if 'description' not in payload:
                assert 'description' in error_str.lower()
            if 'status' not in payload:
                assert 'status' in error_str.lower()
    
    def test_update_task_missing_required_title(self, client):
        """Test PUT /tasks/{id} with missing required title field."""
        invalid_payloads = [
            {},  # Empty payload
            {"description": "New Description"},  # Missing title
            {"status": "completed"},  # Missing title
            {"description": "Desc", "status": "pending"},  # Missing title
        ]
        
        for payload in invalid_payloads:
            response = client.put("/tasks/1", json=payload)
            assert response.status_code == 422
            error = response.json()
            assert 'detail' in error
            assert 'title' in str(error['detail']).lower()


class TestExtraFields:
    """Test cases for extra/unexpected fields in requests."""
    
    def test_create_task_with_extra_fields(self, client):
        """Test POST /tasks with extra fields that should be ignored."""
        task_with_extras = {
            "title": "Task with Extra Fields",
            "description": "Testing extra fields",
            "status": "pending",
            # Extra fields that should be ignored
            "priority": "high",
            "assignee": "John Doe",
            "due_date": "2024-12-31",
            "tags": ["urgent", "important"],
            "metadata": {"key": "value"},
            "id": 999,  # ID should be auto-generated, not from request
        }
        
        response = client.post("/tasks", json=task_with_extras)
        assert response.status_code == 200
        
        created_task = response.json()
        # Verify only expected fields are present
        assert set(created_task.keys()) == {'id', 'title', 'description', 'status'}
        # Verify required fields have correct values
        assert created_task['title'] == task_with_extras['title']
        assert created_task['description'] == task_with_extras['description']
        assert created_task['status'] == task_with_extras['status']
        # Verify ID was auto-generated, not taken from request
        assert created_task['id'] != 999
        
        # Verify no extra fields were stored
        get_response = client.get(f"/tasks/{created_task['id']}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert 'priority' not in retrieved_task
        assert 'assignee' not in retrieved_task
        assert 'due_date' not in retrieved_task
        assert 'tags' not in retrieved_task
        assert 'metadata' not in retrieved_task
    
    def test_update_task_with_extra_fields(self, client):
        """Test PUT /tasks/{id} with extra fields that should be ignored."""
        update_with_extras = {
            "title": "Updated Task",
            "description": "Updated description",
            "status": "completed",
            # Extra fields
            "priority": "low",
            "completed_at": "2024-01-01T12:00:00",
            "notes": ["Note 1", "Note 2"],
        }
        
        response = client.put("/tasks/1", json=update_with_extras)
        assert response.status_code == 200
        
        updated_task = response.json()
        # Verify only expected fields are present
        assert set(updated_task.keys()) == {'id', 'title', 'description', 'status'}
        assert 'priority' not in updated_task
        assert 'completed_at' not in updated_task
        assert 'notes' not in updated_task


class TestBadInputData:
    """Test cases for various types of bad input data."""
    
    def test_create_task_with_null_values(self, client):
        """Test POST /tasks with null values for required fields."""
        null_payloads = [
            {"title": None, "description": "Valid", "status": "pending"},
            {"title": "Valid", "description": None, "status": "pending"},
            {"title": "Valid", "description": "Valid", "status": None},
            {"title": None, "description": None, "status": None},
        ]
        
        for payload in null_payloads:
            response = client.post("/tasks", json=payload)
            assert response.status_code == 422
            error = response.json()
            assert 'detail' in error
    
    def test_create_task_with_wrong_types(self, client):
        """Test POST /tasks with wrong data types for fields."""
        wrong_type_payloads = [
            # Numbers instead of strings
            {"title": 123, "description": 456, "status": 789},
            # Booleans instead of strings
            {"title": True, "description": False, "status": True},
            # Arrays instead of strings
            {"title": ["Task", "Title"], "description": ["Desc"], "status": ["pending"]},
            # Objects instead of strings
            {"title": {"text": "Title"}, "description": {"text": "Desc"}, "status": {"value": "pending"}},
            # Mixed wrong types
            {"title": 123, "description": ["Description"], "status": {"status": "pending"}},
        ]
        
        for payload in wrong_type_payloads:
            response = client.post("/tasks", json=payload)
            assert response.status_code == 422
            error = response.json()
            assert 'detail' in error
    
    def test_empty_strings(self, client):
        """Test handling of empty strings for required fields."""
        empty_string_payload = {
            "title": "",
            "description": "",
            "status": ""
        }
        
        response = client.post("/tasks", json=empty_string_payload)
        # The API might accept empty strings - document actual behavior
        if response.status_code == 200:
            # If accepted, verify they're stored as empty strings
            created_task = response.json()
            assert created_task['title'] == ""
            assert created_task['description'] == ""
            assert created_task['status'] == ""
            
            # Verify retrieval also returns empty strings
            get_response = client.get(f"/tasks/{created_task['id']}")
            assert get_response.status_code == 200
            retrieved = get_response.json()
            assert retrieved['title'] == ""
            assert retrieved['description'] == ""
            assert retrieved['status'] == ""
    
    def test_whitespace_only_strings(self, client):
        """Test handling of whitespace-only strings."""
        whitespace_payload = {
            "title": "   ",
            "description": "\t\n\r",
            "status": " \n "
        }
        
        response = client.post("/tasks", json=whitespace_payload)
        if response.status_code == 200:
            created_task = response.json()
            # Verify whitespace is preserved
            assert created_task['title'] == "   "
            assert created_task['description'] == "\t\n\r"
            assert created_task['status'] == " \n "
    
    def test_extremely_long_strings(self, client):
        """Test handling of very long string values."""
        # Test with strings of various lengths
        test_lengths = [1000, 10000, 100000]
        
        for length in test_lengths:
            long_string = "A" * length
            payload = {
                "title": f"Task {length}",
                "description": long_string,
                "status": "pending"
            }
            
            response = client.post("/tasks", json=payload)
            assert response.status_code == 200
            created_task = response.json()
            assert len(created_task['description']) == length
            
            # Verify it can be retrieved
            get_response = client.get(f"/tasks/{created_task['id']}")
            assert get_response.status_code == 200
            assert len(get_response.json()['description']) == length
    
    def test_special_characters_and_unicode(self, client):
        """Test handling of special characters and Unicode."""
        special_payloads = [
            # Special characters
            {
                "title": "!@#$%^&*(){}[]|\\:;\"'<>?,./~`",
                "description": "Line1\nLine2\rLine3\tTabbed",
                "status": "pending-review"
            },
            # Unicode characters
            {
                "title": "Unicode: 你好世界 🌍 ñ é ü ö ä",
                "description": "Emojis: 😀😃😄😁😆😅😂🤣",
                "status": "مكتمل"  # "completed" in Arabic
            },
            # Mixed special and Unicode
            {
                "title": "Mix: <tag>Test</tag> & 中文",
                "description": "SQL: '; DROP TABLE tasks; --",
                "status": "pending"
            },
        ]
        
        for payload in special_payloads:
            response = client.post("/tasks", json=payload)
            assert response.status_code == 200
            created_task = response.json()
            
            # Verify special characters are preserved
            assert created_task['title'] == payload['title']
            assert created_task['description'] == payload['description']
            assert created_task['status'] == payload['status']


class TestMalformedRequests:
    """Test cases for malformed requests."""
    
    def test_malformed_json(self, client):
        """Test requests with malformed JSON."""
        malformed_requests = [
            '{invalid json',                    # Missing closing brace
            '{"title": "Test"',                  # Incomplete JSON
            '{"title": "Test", "desc}',          # Broken string
            '{"title": Test}',                   # Unquoted value
            '{title: "Test"}',                   # Unquoted key
            '["Not", "An", "Object"]',           # Array instead of object
            '"Just a string"',                   # Plain string
            'null',                              # Null
            'true',                              # Boolean
            '123',                               # Number
            '{{double brackets}}',               # Invalid syntax
            '{"title": "Test",}',                # Trailing comma
        ]
        
        for malformed in malformed_requests:
            response = client.post(
                "/tasks",
                data=malformed,
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code in [422, 400]  # Either validation error or bad request
    
    def test_wrong_content_type(self, client):
        """Test requests with wrong content type."""
        valid_data = {"title": "Test", "description": "Test", "status": "pending"}
        
        # Test with various wrong content types
        wrong_content_types = [
            "text/plain",
            "application/xml",
            "text/html",
            "multipart/form-data",
            "application/x-www-form-urlencoded",
        ]
        
        for content_type in wrong_content_types:
            response = client.post(
                "/tasks",
                data=json.dumps(valid_data),
                headers={"Content-Type": content_type}
            )
            # FastAPI might still parse it correctly or return an error
            assert response.status_code in [200, 415, 422]


class TestConcurrentOperations:
    """Test cases for concurrent operations and race conditions."""
    
    def test_rapid_task_creation(self, client):
        """Test creating multiple tasks in rapid succession."""
        tasks_created = []
        
        for i in range(10):
            payload = {
                "title": f"Rapid Task {i}",
                "description": f"Created in rapid succession {i}",
                "status": "pending"
            }
            response = client.post("/tasks", json=payload)
            assert response.status_code == 200
            tasks_created.append(response.json())
        
        # Verify all tasks have unique IDs
        ids = [task['id'] for task in tasks_created]
        assert len(ids) == len(set(ids))  # All IDs should be unique
        
        # Verify IDs are sequential
        sorted_ids = sorted(ids)
        for i in range(1, len(sorted_ids)):
            assert sorted_ids[i] == sorted_ids[i-1] + 1
    
    def test_delete_and_recreate(self, client):
        """Test deleting a task and immediately creating a new one."""
        # Create a task
        create_response = client.post("/tasks", json={
            "title": "Task to Delete",
            "description": "Will be deleted",
            "status": "pending"
        })
        assert create_response.status_code == 200
        task_id = create_response.json()['id']
        
        # Delete it
        delete_response = client.delete(f"/tasks/{task_id}")
        assert delete_response.status_code == 200
        
        # Immediately create a new task
        recreate_response = client.post("/tasks", json={
            "title": "New Task",
            "description": "Created after deletion",
            "status": "pending"
        })
        assert recreate_response.status_code == 200
        new_id = recreate_response.json()['id']
        
        # New task should have a different ID
        assert new_id != task_id
        assert new_id > task_id  # IDs should be incrementing
    
    def test_update_nonexistent_after_delete(self, client):
        """Test updating a task immediately after another task is deleted."""
        # Delete task 2
        delete_response = client.delete("/tasks/2")
        assert delete_response.status_code == 200
        
        # Try to update the deleted task
        update_response = client.put("/tasks/2", json={
            "title": "Updated After Delete",
            "description": "Should fail",
            "status": "pending"
        })
        assert update_response.status_code == 404
        
        # Update a different task should still work
        update_response = client.put("/tasks/1", json={
            "title": "Updated Task 1",
            "description": "Should succeed",
            "status": "completed"
        })
        assert update_response.status_code == 200


class TestBoundaryConditions:
    """Test cases for boundary conditions."""
    
    def test_first_and_last_tasks(self, client):
        """Test operations on first and last tasks in the list."""
        # Get all tasks
        response = client.get("/tasks")
        tasks = response.json()
        assert len(tasks) > 0
        
        first_task = tasks[0]
        last_task = tasks[-1]
        
        # Test operations on first task
        response = client.get(f"/tasks/{first_task['id']}")
        assert response.status_code == 200
        
        # Test operations on last task
        response = client.get(f"/tasks/{last_task['id']}")
        assert response.status_code == 200
        
        # Delete last task
        response = client.delete(f"/tasks/{last_task['id']}")
        assert response.status_code == 200
        
        # Verify list is updated
        response = client.get("/tasks")
        updated_tasks = response.json()
        assert len(updated_tasks) == len(tasks) - 1
        assert not any(t['id'] == last_task['id'] for t in updated_tasks)
    
    def test_single_task_operations(self, client, monkeypatch):
        """Test operations when only one task exists."""
        # Mock to return only one task
        def mock_read_all_tasks():
            from models import TaskWithId
            return [TaskWithId(id=1, title="Only Task", description="The only one", status="pending")]
        
        monkeypatch.setattr('main.read_all_tasks', mock_read_all_tasks)
        
        # Get all tasks
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        
        # Get the single task
        response = client.get("/tasks/1")
        assert response.status_code == 200
        
        # Update the single task
        response = client.put("/tasks/1", json={
            "title": "Updated Only Task",
            "description": "Still the only one",
            "status": "completed"
        })
        assert response.status_code == 200


class TestErrorHandlingAndRecovery:
    """Test cases for error handling and recovery scenarios."""
    
    def test_invalid_operations_sequence(self, client):
        """Test a sequence of valid and invalid operations."""
        # Valid create
        response = client.post("/tasks", json={
            "title": "Valid Task",
            "description": "Valid description",
            "status": "pending"
        })
        assert response.status_code == 200
        valid_id = response.json()['id']
        
        # Invalid create (missing field)
        response = client.post("/tasks", json={"title": "Invalid"})
        assert response.status_code == 422
        
        # Valid get (should still work after invalid create)
        response = client.get(f"/tasks/{valid_id}")
        assert response.status_code == 200
        
        # Invalid update (wrong type)
        response = client.put(f"/tasks/{valid_id}", json={
            "title": ["Not", "A", "String"],
            "description": 123,
            "status": True
        })
        assert response.status_code == 422
        
        # Valid update (should still work after invalid update)
        response = client.put(f"/tasks/{valid_id}", json={
            "title": "Updated Successfully",
            "description": "After error",
            "status": "completed"
        })
        assert response.status_code == 200
        
        # Invalid delete (non-existent)
        response = client.delete("/tasks/9999")
        assert response.status_code == 404
        
        # Valid delete (should still work after invalid delete)
        response = client.delete(f"/tasks/{valid_id}")
        assert response.status_code == 200
    
    def test_partial_update_validation(self, client):
        """Test partial updates with various invalid combinations."""
        # Valid partial updates with null values
        response = client.put("/tasks/1", json={
            "title": "New Title",
            "description": None,  # Should keep existing
            "status": None        # Should keep existing
        })
        assert response.status_code == 200
        updated = response.json()
        assert updated['title'] == "New Title"
        assert updated['description'] is not None  # Should have original value
        assert updated['status'] is not None        # Should have original value


class TestAPISpecCompliance:
    """Test cases to ensure API adheres to specifications."""
    
    def test_response_schemas(self, client):
        """Test that all responses match expected schemas."""
        # Test GET /tasks response schema
        response = client.get("/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert isinstance(tasks, list)
        for task in tasks:
            assert isinstance(task, dict)
            assert set(task.keys()) == {'id', 'title', 'description', 'status'}
            assert isinstance(task['id'], int)
            assert isinstance(task['title'], str)
            assert isinstance(task['description'], str)
            assert isinstance(task['status'], str)
        
        # Test GET /tasks/{id} response schema
        if tasks:
            response = client.get(f"/tasks/{tasks[0]['id']}")
            assert response.status_code == 200
            task = response.json()
            assert isinstance(task, dict)
            assert set(task.keys()) == {'id', 'title', 'description', 'status'}
        
        # Test POST /tasks response schema
        response = client.post("/tasks", json={
            "title": "Schema Test",
            "description": "Testing schema",
            "status": "pending"
        })
        assert response.status_code == 200
        task = response.json()
        assert isinstance(task, dict)
        assert set(task.keys()) == {'id', 'title', 'description', 'status'}
        
        # Test PUT /tasks/{id} response schema
        response = client.put(f"/tasks/{task['id']}", json={
            "title": "Updated Schema Test",
            "description": "Updated",
            "status": "completed"
        })
        assert response.status_code == 200
        updated = response.json()
        assert isinstance(updated, dict)
        assert set(updated.keys()) == {'id', 'title', 'description', 'status'}
        
        # Test DELETE /tasks/{id} response schema
        response = client.delete(f"/tasks/{task['id']}")
        assert response.status_code == 200
        result = response.json()
        assert isinstance(result, dict)
        assert 'message' in result
        assert result['message'] == 'Task deleted successfully'
    
    def test_error_response_format(self, client):
        """Test that error responses follow consistent format."""
        # 404 errors
        not_found_response = client.get("/tasks/9999")
        assert not_found_response.status_code == 404
        error = not_found_response.json()
        assert 'detail' in error
        assert error['detail'] == 'Task not found'
        
        # 422 validation errors
        validation_response = client.post("/tasks", json={"title": "Only title"})
        assert validation_response.status_code == 422
        error = validation_response.json()
        assert 'detail' in error
        assert isinstance(error['detail'], list)
        for detail in error['detail']:
            assert 'loc' in detail
            assert 'msg' in detail
            assert 'type' in detail
    
    def test_http_methods_on_endpoints(self, client):
        """Test that only specified HTTP methods are allowed on endpoints."""
        # Test unsupported methods on /tasks
        response = client.request("PATCH", "/tasks")
        assert response.status_code == 405  # Method Not Allowed
        
        response = client.request("HEAD", "/tasks")
        assert response.status_code == 405 or response.status_code == 200  # HEAD might be allowed
        
        # Test unsupported methods on /tasks/{id}
        response = client.request("PATCH", "/tasks/1")
        assert response.status_code == 405
        
        response = client.request("POST", "/tasks/1")
        assert response.status_code == 405


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
