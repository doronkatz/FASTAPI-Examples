import csv
from typing import List, Optional
from models import Task, TaskWithId, TaskV2, TaskV2WithId

DATABASE_FILENAME = 'tasks.csv'
columns = ['id', 'title', 'description', 'status']
def read_all_tasks() -> list[TaskWithId]:
    tasks = []
    try:
        with open(DATABASE_FILENAME, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['id'] = int(row['id'])  # Convert id to int
                task = TaskWithId(**row)
                tasks.append(task)
    except FileNotFoundError:
        pass  # If the file does not exist, return an empty list
    return tasks

def read_task_by_id(task_id: int) -> Optional[TaskWithId]:
    with open(DATABASE_FILENAME, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if int(row['id']) == task_id:
                row['id'] = int(row['id'])  # Convert id to int
                return TaskWithId(**row)
            
def get_next_id():
    try:
        with open(DATABASE_FILENAME, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            if rows:
                return int(rows[-1]['id']) + 1
    except FileNotFoundError:
        return 1

'''Create new task'''
def create_task(task: Task) -> TaskWithId:
    tasks = read_all_tasks()
    task_id = task.id if task.id is not None else max((t.id for t in tasks), default=0) + 1
    task_with_id = TaskWithId(id=task_id, **task.dict(exclude={"id"}))
    tasks.append(task_with_id)

    with open(DATABASE_FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'title', 'description', 'status'])
        writer.writeheader()
        for t in tasks:
            writer.writerow(t.model_dump())

    return task_with_id

'''Update existing task'''
def update_task(task_id: int, updated_task) -> Optional[TaskWithId]:
    tasks = read_all_tasks()
    for i, task in enumerate(tasks):
        if task.id == task_id:
            # Get the current task data
            task_data = task.model_dump()
            # Update only the fields that are provided (not None)
            update_data = updated_task.model_dump(exclude_unset=False)
            for field, value in update_data.items():
                if value is not None:
                    task_data[field] = value
            # Create the updated task with id
            updated_task_with_id = TaskWithId(**task_data)
            tasks[i] = updated_task_with_id
            break
    else:
        return None

    with open(DATABASE_FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.model_dump())
    return updated_task_with_id

'''Delete task by ID'''
def delete_task(task_id: int) -> bool:
    tasks = read_all_tasks()
    tasks = [task for task in tasks if task.id != task_id]
    with open(DATABASE_FILENAME, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        for task in tasks:
            writer.writerow(task.model_dump())
    return len(tasks) < len(tasks)

def read_all_tasks_v2() -> List[TaskV2WithId]:
    tasks = []
    try:
        with open(DATABASE_FILENAME, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                row['id'] = int(row['id'])  # Convert id to int
                task = TaskV2WithId(**row)
                tasks.append(task)
    except FileNotFoundError:
        pass  # If the file does not exist, return an empty list
    return tasks