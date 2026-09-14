# CodeCraftHub

A simple REST API for tracking courses you want to learn — built with
**Flask** and a **JSON file** for storage. No database, no user accounts,
no authentication. It exists to teach REST API basics: what the different
HTTP methods (`GET`, `POST`, `PUT`, `DELETE`) do, how a request/response
cycle works, and how status codes communicate success or failure.

If you're new to REST APIs, here's the one-sentence version: a REST API
lets other programs (like `curl`, a browser, or a frontend app) create,
read, update, and delete data over plain HTTP requests, and the server
replies with JSON.

## Table of contents

- [Features](#features)
- [Project structure](#project-structure)
- [Installation](#installation)
- [Running the application](#running-the-application)
- [API endpoints](#api-endpoints)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Features

- Full CRUD (Create, Read, Update, Delete) for courses via a REST API
- Each course tracks a name, description, target completion date, status,
  and an auto-generated id + creation timestamp
- Status is restricted to three values (`Not Started`, `In Progress`,
  `Completed`) so data stays consistent
- Filter the course list by status (`GET /api/courses?status=In Progress`)
- Data persists in a plain JSON file (`courses.json`) — open it in any text
  editor to see exactly what the API is storing
- The data file is created automatically the first time you run the app
- Clear, descriptive JSON error messages for bad input (missing fields,
  invalid status, invalid date, etc.) instead of generic failures
- No setup beyond Python — no database server, no accounts, no API keys

## Project structure

```
codecrafthub/
├── app.py              # Everything: Flask routes, validation, and JSON file storage
├── courses.json         # The "database" — a JSON array of course objects (auto-created)
├── requirements.txt     # Python dependencies (just Flask)
├── README.md            # This file
└── TESTING.md           # Copy-paste curl tests for every endpoint
```

Why one file? `app.py` is small enough that splitting storage into its own
module would add indirection without much benefit — for a beginner project,
being able to read the whole API top to bottom in one file is worth more
than "proper" separation. As the app grows (a database, multiple files of
routes), that tradeoff would flip.

Here's what each piece is actually responsible for:

- **`app.py`** — defines the Flask app, the five routes, the validation
  rules (what makes a course "valid"), and the functions that read/write
  `courses.json`.
- **`courses.json`** — the entire "database." It's a JSON array; every
  course is one object in that array. You never edit this by hand — the
  API reads and rewrites it on every request — but it's plain text, so you
  can open it to see the current state at any time.
- **`requirements.txt`** — lists the one external package this project
  needs (Flask), so `pip install -r requirements.txt` can install it.

## Installation

You need **Python 3.8+** installed. Check your version:

```bash
python3 --version
```

Then, step by step:

**1. Navigate to the project folder**

```bash
cd codecrafthub
```

**2. Create a virtual environment**

A virtual environment keeps this project's Python packages separate from
everything else on your machine, so installing Flask here can't conflict
with other projects.

```bash
python3 -m venv venv
```

**3. Activate the virtual environment**

```bash
source venv/bin/activate
```

On Windows (Command Prompt), use `venv\Scripts\activate.bat` instead. You'll
know it worked because your terminal prompt will now start with `(venv)`.

**4. Install dependencies**

```bash
pip install -r requirements.txt
```

This installs Flask (the only dependency). You should see it download and
install with no errors.

That's the whole install — there's no database to set up, no config files
to edit, no environment variables to set.

## Running the application

With the virtual environment still active:

```bash
python app.py
```

You should see output like:

```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

The API is now running at **`http://127.0.0.1:5000`**. Leave this terminal
window open — the server keeps running until you stop it (`Ctrl+C`) or close
the terminal. Open a **second** terminal window to send requests to it with
`curl` while the first one keeps the server running.

The first time you run it, `app.py` automatically creates an empty
`courses.json` (containing `[]`) if one doesn't already exist — you don't
need to create it yourself.

To stop the server, go back to that terminal and press `Ctrl+C`.

## API endpoints

Every endpoint starts with `/api/courses`. Requests and responses are JSON.

| Method | Endpoint             | Description                                 |
|--------|-----------------------|-----------------------------------------------|
| POST   | `/api/courses`        | Add a new course                              |
| GET    | `/api/courses`        | Get all courses (`?status=` filters)          |
| GET    | `/api/courses/<id>`   | Get one specific course                       |
| PUT    | `/api/courses/<id>`   | Update a course (send only the fields to change) |
| DELETE | `/api/courses/<id>`   | Delete a course                               |

**What each HTTP method means**, if these are new to you:

- **GET** — read data, never changes anything
- **POST** — create something new
- **PUT** — update something that already exists
- **DELETE** — remove something

### Data model

Each course is a JSON object with these fields:

```json
{
  "id": 1,
  "name": "Learn Flask",
  "description": "Build REST APIs",
  "target_date": "2026-12-01",
  "status": "Not Started",
  "created_at": "2026-09-10T19:45:18.985210Z"
}
```

| Field | Type | Required? | Notes |
|---|---|---|---|
| `id` | integer | auto-generated | starts at 1, never reused |
| `name` | string | yes | |
| `description` | string | yes | |
| `target_date` | string | yes | must be `YYYY-MM-DD` |
| `status` | string | yes | one of `Not Started`, `In Progress`, `Completed` |
| `created_at` | string | auto-generated | UTC timestamp, set once at creation |

### Examples

```bash
# Create a course
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name":"Learn Flask","description":"Build REST APIs","target_date":"2026-12-01","status":"Not Started"}'

# List all courses
curl http://127.0.0.1:5000/api/courses

# List only courses that are In Progress
curl "http://127.0.0.1:5000/api/courses?status=In%20Progress"

# Get a single course by id
curl http://127.0.0.1:5000/api/courses/1

# Update just the status of course 1
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status":"In Progress"}'

# Delete course 1
curl -X DELETE http://127.0.0.1:5000/api/courses/1
```

Example response after creating a course (`201 Created`):

```json
{
  "id": 1,
  "name": "Learn Flask",
  "description": "Build REST APIs",
  "target_date": "2026-12-01",
  "status": "Not Started",
  "created_at": "2026-09-10T19:45:18.985210Z"
}
```

### Error handling

Every error comes back as a JSON body with a descriptive `error` message
and an appropriate HTTP status code:

- **400 Bad Request** — missing required fields, invalid `status` value,
  `target_date` not in `YYYY-MM-DD` format, or a malformed JSON body
- **404 Not Found** — the course `id` doesn't exist, or the URL/route
  itself doesn't exist
- **500 Internal Server Error** — `courses.json` couldn't be read or
  written (e.g. a permissions problem or a full disk)

Example — requesting a course that doesn't exist:

```bash
curl http://127.0.0.1:5000/api/courses/999
```

```json
{ "error": "Course with id 999 not found" }
```

## Testing

See **[TESTING.md](TESTING.md)** for a full copy-paste `curl` walkthrough —
every endpoint, example payloads, expected success responses, and every
error case (missing fields, invalid status, invalid date, not-found, etc.)
with the exact JSON you should see back.

Quick smoke test to confirm everything's working, once the server is running:

```bash
curl http://127.0.0.1:5000/api/courses
```

An empty API (fresh `courses.json`) returns:

```json
[]
```

If you get that, the server and file storage are both working correctly.

**Tip:** pipe responses through `python3 -m json.tool` for readable
pretty-printed output:

```bash
curl -s http://127.0.0.1:5000/api/courses | python3 -m json.tool
```

## Troubleshooting

**`command not found: python3`**
Python isn't installed, or it's installed as `python` instead of `python3`
on your system. Try `python --version` — if that shows Python 3.x, use
`python` in place of `python3` in the commands above.

**`Address already in use` / `port 5000 is in use`**
Another program (often macOS's AirPlay Receiver, or a previous run of this
app you forgot to stop) is already using port 5000. Either stop that
process, or run this app on a different port:

```bash
# In app.py, change app.run(debug=True, port=5000) to a different port, e.g. 5001
```

Then use that port in your `curl` commands instead.

**Getting `403 Forbidden` with a `Server: AirTunes` header, instead of your API's JSON**
This means your request never actually reached Flask. On macOS, `localhost`
often resolves to the IPv6 address `::1` before the IPv4 address
`127.0.0.1` — and macOS's AirPlay Receiver also listens on `::1:5000`.
Flask (as configured in this project) only binds to `127.0.0.1` (IPv4), so
a request to `http://localhost:5000` can silently get routed to AirPlay
instead of your app, and AirPlay replies with an empty `403`.

**Fix:** always use `http://127.0.0.1:5000` instead of `http://localhost:5000`
in your `curl` commands (and browser/Postman requests) for this project —
that forces IPv4 and reaches Flask directly.

**`ModuleNotFoundError: No module named 'flask'`**
Your virtual environment isn't activated, or dependencies weren't
installed. Run:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

You should see `(venv)` at the start of your terminal prompt when the
virtual environment is active.

**`curl: (7) Failed to connect to 127.0.0.1 port 5000`**
The server isn't running. Make sure `python app.py` is running in another
terminal window and that it printed `Running on http://127.0.0.1:5000`
with no errors above it.

**Getting a 404 for a course you just created**
Course ids are assigned in order and are never reused — if you deleted
course 1 earlier, the next new course won't be id 1 again. Run
`curl http://127.0.0.1:5000/api/courses` to see the current ids.

**Getting a 400 error you don't understand**
Read the `error` field in the JSON response — it names exactly which field
is wrong and why (e.g. `"'target_date' must be a valid date in YYYY-MM-DD
format"`). Double check your JSON is valid (matching quotes and braces) and
that you're sending the `-H "Content-Type: application/json"` header.

**Changes to `courses.json` don't show up / data looks wrong**
Don't edit `courses.json` by hand while the server is running — the next
request will overwrite your changes. Stop the server, edit the file, then
restart it if you need to change data outside the API.

**Want to start over with no data?**
Stop the server, then reset the file:

```bash
echo "[]" > courses.json
```

The next course you create will get `id: 1` again.
