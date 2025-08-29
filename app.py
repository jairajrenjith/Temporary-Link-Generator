from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3, time, secrets, re, os

app = Flask(__name__)
DB_NAME = "database.db"

# --- Utilities --------------------------------------------------------------
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS links (
                token TEXT PRIMARY KEY,
                original TEXT NOT NULL,
                expiry REAL NOT NULL,
                created REAL NOT NULL
            )
        """)
init_db()

URL_REGEX = re.compile(r"^https?://", re.I)

# --- Routes -----------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original = request.form.get("link", "").strip()
        duration = request.form.get("duration", "").strip()
        try:
            duration = int(duration)
        except Exception:
            return render_template("index.html", error="Enter a valid duration in minutes.", old_link=original), 400

        if not original:
            return render_template("index.html", error="Please enter a URL.", old_link=original), 400
        if not URL_REGEX.search(original):
            return render_template("index.html", error="URL must start with http:// or https://", old_link=original), 400
        if duration < 1 or duration > 60*24*14:
            return render_template("index.html", error="Duration must be between 1 minute and 20160 minutes (14 days).", old_link=original), 400

        expiry = time.time() + (duration * 60)
        token = secrets.token_urlsafe(10)

        with get_db() as conn:
            conn.execute("INSERT INTO links (token, original, expiry, created) VALUES (?, ?, ?, ?)",
                         (token, original, expiry, time.time()))

        temp_link = request.host_url.rstrip("/") + url_for("temp_redirect", token=token)
        return render_template("result.html", temp_link=temp_link, duration=duration)

    return render_template("index.html")

@app.route("/t/<token>")
def temp_redirect(token):
    with get_db() as conn:
        row = conn.execute("SELECT original, expiry FROM links WHERE token=?", (token,)).fetchone()

    if not row:
        return render_template("expired.html", reason="Invalid or already expired link."), 404

    original, expiry = row["original"], row["expiry"]
    if time.time() > expiry:
        with get_db() as conn:
            conn.execute("DELETE FROM links WHERE token=?", (token,))
        return render_template("expired.html", reason="This link timed out."), 410

    return redirect(original, code=302)

# A minimal dashboard to verify your app (not publicized)
@app.route("/health")
def health():
    # do not expose internals; just say ok
    return {"status": "ok", "ts": int(time.time())}

# --- Error Handling ---------------------------------------------------------
@app.errorhandler(404)
def err404(e):
    return render_template("expired.html", reason="The page you requested does not exist."), 404

@app.errorhandler(500)
def err500(e):
    return render_template("expired.html", reason="Server hiccup. Try again."), 500

# --- Security Headers -------------------------------------------------------
@app.after_request
def add_headers(resp):
    resp.headers["X-Frame-Options"] = "DENY"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    resp.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
    # CSP relaxed to allow Tailwind CDN and inline JS used by countdown/copy
    resp.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
    return resp

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
