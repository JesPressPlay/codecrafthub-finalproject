# Testing the CodeCraftHub API

Copy-paste `curl` commands for every endpoint, plus the error cases you should
expect the API to catch. Run these in order from a **fresh `courses.json`**
(`echo "[]" > courses.json`) so the ids match what's shown below — if you've
already created courses, ids will differ, but the responses will have the
same shape.

## Start the server first

```bash
source venv/bin/activate
python app.py
```

Leave that running in one terminal, and run the `curl` commands below in another.

---

## 1. POST /api/courses — create a course

**Payload:**
```json
{
  "name": "Learn Flask",
  "description": "Build REST APIs with Python and Flask",
  "target_date": "2026-12-01",
  "status": "Not Started"
}
```

**Command:**
```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Learn Flask",
    "description": "Build REST APIs with Python and Flask",
    "target_date": "2026-12-01",
    "status": "Not Started"
  }'
```

**Expected response — `201 Created`:**
```json
{
  "id": 1,
  "name": "Learn Flask",
  "description": "Build REST APIs with Python and Flask",
  "target_date": "2026-12-01",
  "status": "Not Started",
  "created_at": "2026-09-10T19:48:00.216833Z"
}
```

Create a second one to use in later examples:

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Learn Docker",
    "description": "Containerize applications for deployment",
    "target_date": "2026-11-15",
    "status": "In Progress"
  }'
```

→ creates course `id: 2`.

---

## 2. GET /api/courses — list all courses

**Command:**
```bash
curl http://127.0.0.1:5000/api/courses
```

**Expected response — `200 OK`:**
```json
[
  {
    "id": 1,
    "name": "Learn Flask",
    "description": "Build REST APIs with Python and Flask",
    "target_date": "2026-12-01",
    "status": "Not Started",
    "created_at": "2026-09-10T19:48:00.216833Z"
  },
  {
    "id": 2,
    "name": "Learn Docker",
    "description": "Containerize applications for deployment",
    "target_date": "2026-11-15",
    "status": "In Progress",
    "created_at": "2026-09-10T19:48:00.226856Z"
  }
]
```

### Optional: filter by status

```bash
curl "http://127.0.0.1:5000/api/courses?status=In%20Progress"
```

Returns only courses with `"status": "In Progress"` (just course `id: 2` here).
Note the space in `In Progress` is URL-encoded as `%20`.

---

## 3. GET /api/courses/\<id\> — get a specific course

**Command:**
```bash
curl http://127.0.0.1:5000/api/courses/1
```

**Expected response — `200 OK`:**
```json
{
  "id": 1,
  "name": "Learn Flask",
  "description": "Build REST APIs with Python and Flask",
  "target_date": "2026-12-01",
  "status": "Not Started",
  "created_at": "2026-09-10T19:48:00.216833Z"
}
```

---

## 4. PUT /api/courses/\<id\> — update a course

You can send just the fields you want to change — anything you leave out
keeps its current value.

### Partial update (status only)

**Payload:**
```json
{ "status": "In Progress" }
```

**Command:**
```bash
curl -X PUT http://127.0.0.1:5000/api/courses/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "In Progress"}'
```

**Expected response — `200 OK`:**
```json
{
  "id": 1,
  "name": "Learn Flask",
  "description": "Build REST APIs with Python and Flask",
  "target_date": "2026-12-01",
  "status": "In Progress",
  "created_at": "2026-09-10T19:48:00.216833Z"
}
```

### Full update (all fields)

**Payload:**
```json
{
  "name": "Learn Docker & Compose",
  "description": "Containerize and orchestrate multi-service apps",
  "target_date": "2026-11-30",
  "status": "Completed"
}
```

**Command:**
```bash
curl -X PUT http://127.0.0.1:5000/api/courses/2 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Learn Docker & Compose",
    "description": "Containerize and orchestrate multi-service apps",
    "target_date": "2026-11-30",
    "status": "Completed"
  }'
```

**Expected response — `200 OK`:**
```json
{
  "id": 2,
  "name": "Learn Docker & Compose",
  "description": "Containerize and orchestrate multi-service apps",
  "target_date": "2026-11-30",
  "status": "Completed",
  "created_at": "2026-09-10T19:48:00.226856Z"
}
```

Note `created_at` never changes — it's set once, at creation.

---

## 5. DELETE /api/courses/\<id\> — delete a course

**Command:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/courses/1
```

**Expected response — `200 OK`:**
```json
{
  "message": "Course deleted",
  "course": {
    "id": 1,
    "name": "Learn Flask",
    "description": "Build REST APIs with Python and Flask",
    "target_date": "2026-12-01",
    "status": "In Progress",
    "created_at": "2026-09-10T19:48:00.216833Z"
  }
}
```

---

## Error scenarios

### Missing required field (POST)

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{"name": "Learn Kubernetes"}'
```

`400 Bad Request`:
```json
{ "error": "'description' is required" }
```

### Invalid status value

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Learn Kubernetes",
    "description": "Container orchestration",
    "target_date": "2026-10-01",
    "status": "Maybe Later"
  }'
```

`400 Bad Request`:
```json
{ "error": "'status' must be one of ['Not Started', 'In Progress', 'Completed']" }
```

Same error shape applies to `PUT` with a bad status:

```bash
curl -X PUT http://127.0.0.1:5000/api/courses/2 \
  -H "Content-Type: application/json" \
  -d '{"status": "Sort Of Done"}'
```

### Invalid date format

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Learn Kubernetes",
    "description": "Container orchestration",
    "target_date": "10/01/2026",
    "status": "Not Started"
  }'
```

`400 Bad Request`:
```json
{ "error": "'target_date' must be a valid date in YYYY-MM-DD format" }
```

### Malformed JSON body

```bash
curl -X POST http://127.0.0.1:5000/api/courses \
  -H "Content-Type: application/json" \
  -d '{not valid json'
```

`400 Bad Request`:
```json
{ "error": "Request body must be valid JSON" }
```

### Course not found (GET / PUT / DELETE)

```bash
curl http://127.0.0.1:5000/api/courses/999
curl -X PUT http://127.0.0.1:5000/api/courses/999 -H "Content-Type: application/json" -d '{"status": "Completed"}'
curl -X DELETE http://127.0.0.1:5000/api/courses/999
```

All three return `404 Not Found`:
```json
{ "error": "Course with id 999 not found" }
```

### Unknown route

```bash
curl http://127.0.0.1:5000/api/nope
```

`404 Not Found`:
```json
{ "error": "Resource not found" }
```

---

## Quick reference table

| # | Method | Endpoint | Body required | Expected success | Expected error |
|---|--------|----------|----------------|--------------------|-----------------|
| 1 | POST | `/api/courses` | yes (all fields) | `201` + created course | `400` missing field / bad status / bad date / bad JSON |
| 2 | GET | `/api/courses` | no | `200` + array | — |
| 3 | GET | `/api/courses/<id>` | no | `200` + course | `404` not found |
| 4 | PUT | `/api/courses/<id>` | yes (any subset) | `200` + updated course | `400` bad status/date, `404` not found |
| 5 | DELETE | `/api/courses/<id>` | no | `200` + deleted course | `404` not found |

**Tip:** pipe any response through `python3 -m json.tool` (or add `| jq .` if
you have `jq` installed) if you want prettier output than raw `curl` gives you:

```bash
curl -s http://127.0.0.1:5000/api/courses | python3 -m json.tool
```
