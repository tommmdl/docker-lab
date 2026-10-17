import psycopg
from flask import Flask, jsonify, request, render_template
from werkzeug.exceptions import HTTPException
from database import connect

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 4096


@app.errorhandler(psycopg.Error)
def database_unavailable(error):
    app.logger.warning("Database request failed (%s)", type(error).__name__)
    return jsonify(error="database_unavailable"), 503


@app.errorhandler(HTTPException)
def http_error(error):
    return jsonify(error=error.name.lower().replace(" ", "_")), error.code


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/healthz")
def health():
    return jsonify(status="alive")


@app.get("/readyz")
def ready():
    with connect() as conn:
        conn.execute("SELECT 1 FROM notes LIMIT 0")
    return jsonify(status="ready")


@app.get("/notes")
def list_notes():
    with connect() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at FROM notes ORDER BY id DESC LIMIT 100"
        ).fetchall()
    return jsonify(notes=[dict(id=r[0], title=r[1], created_at=r[2].isoformat()) for r in rows])


@app.post("/notes")
def create_note():
    body = request.get_json(silent=True)
    if not isinstance(body, dict) or not isinstance(body.get("title"), str):
        return jsonify(error="title_must_be_a_string"), 400
    title = body["title"].strip()
    if not 1 <= len(title) <= 200:
        return jsonify(error="title_length_must_be_1_to_200"), 400
    with connect() as conn:
        row = conn.execute(
            "INSERT INTO notes (title) VALUES (%s) RETURNING id, title, created_at",
            (title,),
        ).fetchone()
    return jsonify(id=row[0], title=row[1], created_at=row[2].isoformat()), 201


@app.delete("/notes/<int:note_id>")
def delete_note(note_id):
    with connect() as conn:
        row = conn.execute("DELETE FROM notes WHERE id = %s RETURNING id", (note_id,)).fetchone()
    if row is None:
        return jsonify(error="note_not_found"), 404
    return "", 204
