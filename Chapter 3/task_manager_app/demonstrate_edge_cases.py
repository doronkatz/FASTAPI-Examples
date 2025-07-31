#!/usr/bin/env python3
"""
Demonstration script for edge case testing of the Task Manager API.
This script shows various edge cases and how the API handles them.
"""

import requests
import json
from typing import Dict, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print a section header."""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def make_request(method: str, endpoint: str, data: Dict[str, Any] = None, 
                 headers: Dict[str, str] = None) -> None:
    """Make an HTTP request and print the results."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            print(f"Unsupported method: {method}")
            return
            
        print(f"\n{method} {endpoint}")
        if data:
            print(f"Request Body: {json.dumps(data, indent=2)}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except requests.exceptions.ConnectionError:
        print(f"\nError: Cannot connect to API at {BASE_URL}")
        print("Please ensure the API is running with: uvicorn main:app --reload")
    except Exception as e:
        print(f"\nError: {str(e)}")

def demonstrate_edge_cases():
    """Demonstrate various edge cases."""
    
    print("Task Manager API - Edge Case Demonstration")
    print("==========================================")
    
    # 1. Empty Task List
    print_section("1. Empty Task List")
    make_request("GET", "/tasks")
    
    # 2. Invalid Task IDs
    print_section("2. Invalid Task IDs")
    
    # String ID
    make_request("GET", "/tasks/abc")
    
    # Float ID
    make_request("GET", "/tasks/1.5")
    
    # Negative ID
    make_request("GET", "/tasks/-1")
    
    # Very large ID
    make_request("GET", "/tasks/999999")
    
    # 3. Missing Required Fields
    print_section("3. Missing Required Fields")
    
    # Empty payload
    make_request("POST", "/tasks", {})
    
    # Missing description and status
    make_request("POST", "/tasks", {"title": "Only Title"})
    
    # Missing title (for update)
    make_request("PUT", "/tasks/1", {"description": "No title provided"})
    
    # 4. Extra Fields
    print_section("4. Extra Fields (Should Be Ignored)")
    
    make_request("POST", "/tasks", {
        "title": "Task with Extras",
        "description": "Testing extra fields",
        "status": "pending",
        "priority": "high",  # Extra field
        "assignee": "John Doe",  # Extra field
        "due_date": "2024-12-31"  # Extra field
    })
    
    # 5. Bad Input Data
    print_section("5. Bad Input Data")
    
    # Null values
    make_request("POST", "/tasks", {
        "title": None,
        "description": "Valid description",
        "status": "pending"
    })
    
    # Wrong types
    make_request("POST", "/tasks", {
        "title": 123,  # Should be string
        "description": ["Not", "A", "String"],  # Should be string
        "status": True  # Should be string
    })
    
    # Empty strings
    make_request("POST", "/tasks", {
        "title": "",
        "description": "",
        "status": ""
    })
    
    # 6. Special Characters and Unicode
    print_section("6. Special Characters and Unicode")
    
    make_request("POST", "/tasks", {
        "title": "Task: <script>alert('XSS')</script> & SQL: '; DROP TABLE;",
        "description": "Unicode: 你好世界 🌍 ñ é ü 😀😃😄",
        "status": "pending"
    })
    
    # 7. Malformed JSON
    print_section("7. Malformed JSON")
    
    # Send malformed JSON
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        f"{BASE_URL}/tasks",
        data='{invalid json',  # Malformed JSON
        headers=headers
    )
    print(f"\nPOST /tasks (with malformed JSON)")
    print(f"Request Body: {{invalid json")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")
    
    # 8. Very Long Strings
    print_section("8. Very Long Strings")
    
    long_string = "A" * 1000  # 1000 character string
    make_request("POST", "/tasks", {
        "title": "Task with long description",
        "description": long_string,
        "status": "pending"
    })
    
    # 9. Rapid Task Creation (Testing ID Generation)
    print_section("9. Rapid Task Creation")
    
    print("\nCreating 5 tasks rapidly...")
    for i in range(5):
        response = requests.post(f"{BASE_URL}/tasks", json={
            "title": f"Rapid Task {i+1}",
            "description": f"Testing rapid creation {i+1}",
            "status": "pending"
        })
        if response.status_code == 200:
            task = response.json()
            print(f"Created task with ID: {task['id']}")
    
    # 10. HTTP Method Restrictions
    print_section("10. HTTP Method Restrictions")
    
    # Try PATCH on /tasks
    response = requests.patch(f"{BASE_URL}/tasks")
    print(f"\nPATCH /tasks")
    print(f"Status Code: {response.status_code}")
    
    # Try POST on /tasks/1
    response = requests.post(f"{BASE_URL}/tasks/1", json={"title": "Test"})
    print(f"\nPOST /tasks/1")
    print(f"Status Code: {response.status_code}")

if __name__ == "__main__":
    demonstrate_edge_cases()
    print("\n\nEdge case demonstration complete!")
    print("Check the edge_case_test_report.md for detailed test results.")
