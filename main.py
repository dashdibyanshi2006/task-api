import sqlite3
from contextlib import asynccontextmanager, closing, contextmanager
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse


DB_PATH = Path(__file__).with_name("tasks.db")
SEED_TASKS = [("Buy milk", 0), ("Buy Sugar", 0), ("Buy Flour", 0)]


@contextmanager
def database():
    with closing(sqlite3.connect(DB_PATH)) as conn, conn:
        conn.row_factory = sqlite3.Row
        yield conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    with database() as conn:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                done INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        # SQLite keeps this sequence after all rows are deleted.
        seeded = conn.execute(
            "SELECT 1 FROM sqlite_sequence WHERE name = ?", ("tasks",)
        ).fetchone()
        if count == 0 and seeded is None:
            conn.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS)
    yield


app = FastAPI(lifespan=lifespan)

tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Buy Sugar", "done": False},
    {"id": 3, "title": "Buy Flour", "done": False},
]

@app.get("/", description="Get API information")
def home():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", description="Check API health status")
def health():
    return {"status": "ok"}

@app.get("/tasks" ,description="Get all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", description="Get a task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.post("/tasks", description="Create a new task")
def create_task(body: dict):
    if "title" not in body or not isinstance(body["title"], str) or not body["title"].strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})

    new_task = {"id": max((task["id"] for task in tasks), default=0) + 1, "title": body["title"].strip(), "done": False}
    tasks.append(new_task)
    return JSONResponse(status_code=201, content=new_task)

@app.put("/tasks/{task_id}", description="Update a task by ID")
def update_task(task_id: int, body: dict):
    for task in tasks:
        if task["id"] == task_id:
            if "title" not in body and "done" not in body:
                return JSONResponse(status_code=400, content={"error": "send title and/or done"})


            if "title" in body:
                if not isinstance(body["title"], str) or not body["title"].strip():
                    return JSONResponse(status_code=400, content={"error": "title must be a non-empty string"})
                task["title"] = body["title"]


            if "done" in body:
                if not isinstance(body["done"], bool):
                    return JSONResponse(status_code=400, content={"error": "done must be true or false"})
                task["done"] = body["done"]

            return task

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.delete("/tasks/{task_id}", description="Delete a task by ID")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return Response(status_code=204)

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )
