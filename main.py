import sqlite3
from contextlib import asynccontextmanager, closing, contextmanager
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
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


@app.exception_handler(RequestValidationError)
async def invalid_request(request, exc):
    if all(error["loc"][:1] == ("body",) for error in exc.errors()):
        return JSONResponse(status_code=400, content={"error": "Expected a JSON object"})
    return await request_validation_exception_handler(request, exc)


@app.get("/", description="Get API information")
def home():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health", description="Check API health status")
def health():
    return {"status": "ok"}

def task_json(row):
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def task_not_found(task_id):
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.get("/tasks", description="Get all tasks")
def get_tasks():
    with database() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [task_json(row) for row in rows]


@app.get("/tasks/{task_id}", description="Get a task by ID")
def get_task(task_id: int):
    with database() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if row is None:
        return task_not_found(task_id)
    return task_json(row)


@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(body: dict):
    if "title" not in body or not isinstance(body["title"], str) or not body["title"].strip():
        return JSONResponse(status_code=400, content={"error": "title is required"})

    title = body["title"].strip()
    with database() as conn:
        cursor = conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, 0))
        task_id = cursor.lastrowid
    return {"id": task_id, "title": title, "done": False}


@app.put("/tasks/{task_id}", description="Update a task by ID")
def update_task(task_id: int, body: dict):
    with database() as conn:
        # Keep another writer from changing the task between the read and update.
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return task_not_found(task_id)

        if "title" not in body and "done" not in body:
            return JSONResponse(status_code=400, content={"error": "send title and/or done"})

        title = body.get("title", row["title"])
        if not isinstance(title, str) or not title.strip():
            return JSONResponse(status_code=400, content={"error": "title must be a non-empty string"})

        done = body.get("done", bool(row["done"]))
        if not isinstance(done, bool):
            return JSONResponse(status_code=400, content={"error": "done must be true or false"})

        conn.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, int(done), task_id))
    return {"id": task_id, "title": title, "done": done}


@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task by ID")
def delete_task(task_id: int):
    with database() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            return task_not_found(task_id)
    return Response(status_code=204)
