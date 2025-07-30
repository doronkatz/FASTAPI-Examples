# FastAPI Cookbook Examples

![FastAPI Cookbook Cover](https://camo.githubusercontent.com/5224f4a6b75cb2f757d8e332af9b5be7a66540e50f4833f4f234d389b7d55ddf/68747470733a2f2f636f6e74656e742e7061636b742e636f6d2f5f2f696d6167652f6f726967696e616c2f4232313032352f636f7665725f696d6167655f6c617267652e6a7067)

This repository contains example projects and code snippets inspired by the [FastAPI Cookbook](https://github.com/PacktPublishing/FastAPI-Cookbook). The codebase demonstrates various FastAPI patterns, including:

- File upload and download endpoints
- SQL and NoSQL database integrations
- Modular routing
- Pydantic models and validation
- Error handling

## Structure

- `upload_and_download/`  
  Example FastAPI endpoints for uploading and downloading files.

- `sql_example/`  
  CRUD operations using SQLAlchemy with a SQLite database.

- `nosql_example/`  
  User management using MongoDB and Pydantic models.

- `bookstore/`  
  Book API with custom models and response handling.

- `fastapi_start/`  
  Basic FastAPI app and router example.

## Getting Started

1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pymongo sqlalchemy pydantic
   ```
3. Run any example:
   ```bash
   uvicorn upload_and_download.main:app --reload
   ```

## Reference

For more recipes and advanced usage, see the official [FastAPI Cookbook GitHub](https://github.com/PacktPublishing/FastAPI-Cookbook).

---
This codebase is for educational purposes and follows patterns from the FastAPI Cookbook.