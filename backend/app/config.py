# backend/app/config.py
import os
import tempfile

# Wenn keine DATABASE_URL gesetzt ist → temporäre SQLite-Datei verwenden
if "DATABASE_URL" in os.environ:
    DATABASE_URL = os.environ["DATABASE_URL"]
else:
    # Erzeuge temporäre Datei-basierte SQLite-DB (nicht flüchtig wie :memory:)
    db_fd, db_path = tempfile.mkstemp(prefix="crypTax_", suffix=".db")
    DATABASE_URL = f"sqlite:///{db_path}"

# Optional weitere Settings
DEBUG = os.getenv("DEBUG", "True") == "True"
