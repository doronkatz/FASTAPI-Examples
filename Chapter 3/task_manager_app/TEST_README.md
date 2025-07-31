# Test Fixtures for FastAPI Task Manager

This project includes pytest fixtures that create a temporary CSV database for testing the FastAPI application.

## Test Setup

The test fixtures are defined in `conftest.py` and provide:

1. **Temporary CSV Database**: Creates a temporary CSV file with sample task data
2. **Database Override**: Patches the application to use the temporary file instead of `tasks.csv`
3. **Automatic Cleanup**: Removes the temporary file after tests complete

## Available Fixtures

### `temp_csv_file`
Creates a temporary CSV file with 3 sample tasks:
- Task 1: pending status
- Task 2: in_progress status  
- Task 3: completed status

### `mock_database_file`
Overrides the application's database dependency to point to the temporary CSV file.

### `client`
Provides a FastAPI TestClient configured to use the mocked database.

### `sample_task_data`
Returns sample data for creating new tasks in tests.

### `expected_tasks`
Returns a list of TaskWithId objects matching the sample CSV content.

### `ensure_clean_state`
Automatically runs for all tests to ensure no stray `tasks.csv` file exists.

## Running Tests

```bash
python3 -m pytest test_app.py -v
```

## Example Test Usage

```python
def test_get_all_tasks(client, expected_tasks):
    """Test getting all tasks from the temporary database."""
    response = client.get("/tasks")
    assert response.status_code == 200
    
    tasks = response.json()
    assert len(tasks) == 3
```

The fixtures handle all setup and teardown automatically, ensuring tests run in isolation with a clean database state.
