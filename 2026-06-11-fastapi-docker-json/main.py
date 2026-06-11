from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI()

TASKS_FILE = "tasks.json"

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

class Task(TaskBase):
    id: int

def read_tasks() -> List[dict]:
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def write_tasks(tasks: List[dict]):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

@app.get("/tasks", response_model=List[Task])
def get_tasks():
    return read_tasks()

@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    tasks = read_tasks()
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    tasks = read_tasks()
    
    new_id = max([t["id"] for t in tasks], default=0) + 1
    
    task_data = task.model_dump()
    task_data["id"] = new_id
    
    tasks.append(task_data)
    write_tasks(tasks)
    return task_data

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, updated_task: TaskUpdate):
    tasks = read_tasks()
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            # Get only the fields that were actually sent in the request
            update_data = updated_task.model_dump(exclude_unset=True)
            
            # Merge with existing data
            for key, value in update_data.items():
                tasks[i][key] = value
                
            write_tasks(tasks)
            return tasks[i]
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    tasks = read_tasks()
    new_tasks = [t for t in tasks if t["id"] != task_id]
    if len(new_tasks) == len(tasks):
        raise HTTPException(status_code=404, detail="Task not found")
    write_tasks(new_tasks)
    return {"message": "Task deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
