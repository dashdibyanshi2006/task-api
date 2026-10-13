![Swagger UI Screenshot](screenshots/swagger-ui.png)
# Task API

A simple in-memory To-Do REST API built with Python and FastAPI as part of the **FlyRank AI Backend Track — Week 2, Assignment A1**.

This project helped me understand how backend APIs work by building and testing endpoints for creating, retrieving, updating, and deleting tasks.

## Features

- Retrieve API information and check server health.
- View all tasks or retrieve a specific task by ID.
- Create new tasks with a title.
- Update a task's title and completion status.
- Delete tasks by ID.
- Handle invalid requests and return appropriate HTTP status codes.
- Explore and test endpoints through FastAPI's interactive Swagger UI.

## Technologies Used

- **Python** — application logic.
- **FastAPI** — building the REST API.
- **Uvicorn** — running the development server.
- **Swagger UI** — testing API endpoints interactively.
- **Git and GitHub** — version control and project hosting.

### Input Validation

- Task titles are required when creating a task.
- Titles must be strings and cannot be empty or contain only whitespace.
- Leading and trailing whitespace is removed from new task titles.
- Task updates must include at least one field (`title` and/or `done`).
- The `done` field must be a boolean (`true` or `false`).
- Requests for nonexistent task IDs return a `404 Not Found` response.

## Getting Started

### Prerequisites

- Python installed.
- A terminal and a code editor.

### Installation and Setup

Clone the repository:

```bash
git clone <your-github-repository-url>
cd "Task API"
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install fastapi uvicorn
```

Start the development server:

```bash
fastapi dev main.py
```

Open the following URL in your browser to access the interactive API documentation:

http://127.0.0.1:8000/docs

The API runs locally and stores tasks in memory. Task changes are not persistent and reset when the server restarts.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Retrieve API information |
| GET | `/health` | Check server health |
| GET | `/tasks` | Retrieve all tasks |
| GET | `/tasks/{task_id}` | Retrieve a task by ID |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{task_id}` | Update a task |
| DELETE | `/tasks/{task_id}` | Delete a task |

### Example Request

Create a task using `POST /tasks`:

```json
{
  "title": "Finish FlyRank assignment"
}
```

A successful creation returns **201 Created** and a task containing its ID, title, and completion status.

## HTTP Status Codes and Error Handling

| Status code | Meaning |
|---|---|
| `200 OK` | Request completed successfully |
| `201 Created` | A new task was created |
| `204 No Content` | A task was deleted successfully |
| `400 Bad Request` | The request contains invalid task data |
| `404 Not Found` | The requested task does not exist |

The API validates task titles and returns error messages for invalid requests. It also returns a `404` response when a task ID cannot be found.

## Swagger UI

FastAPI automatically generates interactive API documentation, allowing endpoints to be tested without a separate API client.

![Swagger UI Screenshot](screenshots/swagger-ui.png)

## What I Learned

While building this project, I practised:

- Understanding REST APIs and CRUD operations.
- Creating endpoints using FastAPI decorators.
- Handling HTTP methods such as GET, POST, PUT, and DELETE.
- Reading JSON request bodies and returning JSON responses.
- Working with Python lists and dictionaries to store task data.
- Using path parameters to retrieve, update, and delete individual tasks.
- Using `if` conditions, `for` loops, and `return` statements to control program flow.
- Understanding Python exceptions, including `raise`, and handling missing resources.
- Validating user input and distinguishing between client errors (`400` and `404`) and server errors (`500`).
- Using f-strings to create dynamic error messages.
- Running a local development server and testing requests using `curl`.
- Understanding virtual environments and why in-memory data resets when the server restarts.
- Testing API behaviour and checking that changes do not break previously working functionality.

## Future Improvements

- Store tasks in a database so they persist after restarting the server.
- Improve request validation using Pydantic models.
- Add automated tests for the API endpoints.
- Improve task ID generation to prevent duplicate IDs after deletion.

## Project Context

Built as a beginner backend project for the FlyRank AI Backend Track, Week 2, Assignment A1.
