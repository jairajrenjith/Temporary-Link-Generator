from flask import Flask, render_template, request, redirect, url_for, abort
import uuid
import datetime
import random, string

app = Flask(__name__)

# In-memory storage for links
links = {}

# Generate random short IDs
def generate_random_id(length=8):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        original_url = request.form["url"]
        duration = int(request.form["duration"])  # minutes

        short_id = generate_random_id()
        expire_time = datetime.datetime.now() + datetime.timedelta(minutes=duration)

        links[short_id] = {"url": original_url, "expire": expire_time}

        return render_template("result.html",
                               temp_link=request.host_url + "t/" + short_id,
                               expire_time=expire_time.strftime("%Y-%m-%d %H:%M:%S"))

    return render_template("index.html")

@app.route("/t/<short_id>")
def temp_redirect(short_id):
    link = links.get(short_id)
    if not link:
        return render_template("expired.html")

    if datetime.datetime.now() > link["expire"]:
        del links[short_id]
        return render_template("expired.html")

    return render_template("viewer.html", original_url=link["url"])

if __name__ == "__main__":
    app.run(debug=True)
