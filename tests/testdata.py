# tests/testdata.py

import plyvel
from pathlib import Path

def create_test_db(path="tests/testdb"):
    Path(path).mkdir(parents=True, exist_ok=True)
    db = plyvel.DB(path, create_if_missing=True)
    c_db = db.prefixed_db(b"c-")
    m_db = db.prefixed_db(b"m-")

    # Insert sample data
    c_db.put(b"sample-text", b"Hello World!")
    m_db.put(b"sample-binary", b"application/octet-stream")
    c_db.put(b"sample-binary", b"\x89PNG\r\n\x1a\n")  # Dummy binary content

    db.close()
    print(f"✅ Test DB created at {path}")

if __name__ == "__main__":
    create_test_db()
