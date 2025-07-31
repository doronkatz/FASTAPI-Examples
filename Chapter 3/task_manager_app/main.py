from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from models import Task, TaskWithId
from operations import read_all_tasks, read_task_by_id, create_task, update_task
import csv

app = FastAPI()

@app.get("/tasks", response_model=list[TaskWithId])
def get_tasks():
    return read_all_tasks()

@app.get("/tasks/{task_id}", response_model=TaskWithId)
def get_task(task_id: int):
    task = read_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=TaskWithId)
def add_task(task: Task):
    return create_task(task)

class UpdateTask(BaseModel):
    title: str
    description: str | None = None
    status: str | None = None
@app.put("/tasks/{task_id}", response_model=TaskWithId)
def modify_task(task_id: int, updated_task: UpdateTask):
    task = update_task(task_id, updated_task)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = read_all_tasks()
    
    # Check if task exists
    task_exists = any(task.id == task_id for task in tasks)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Remove the task
    tasks = [task for task in tasks if task.id != task_id]
    
    with open('tasks.csv', mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'status'])
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.model_dump())
    
    return {"message": "Task deleted successfully"}
