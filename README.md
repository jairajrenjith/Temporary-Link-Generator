# TempLink Nexus
Futuristic, neon-styled temporary link generator. Paste a URL, choose an expiry in minutes, get a shareable link that auto-expires.

## Run locally
```bash
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```

## Deploy
- Render / Railway / Heroku: use `Procfile` and set start command `gunicorn app:app`.
- Persistent storage: SQLite file `database.db` is created in the app dir.

## Notes
- Security headers included.
- For strict CSP, replace inline scripts by external files only and configure CSP.
- QR renderer here is a tiny decorative generator; swap with a real QR lib for production.
