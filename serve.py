# serve.py

from flask import Flask, Response, abort
import plyvel

app = Flask(__name__)

db = plyvel.DB("tests/testdb", create_if_missing=False)
c_db = db.prefixed_db(b"c-")
m_db = db.prefixed_db(b"m-")

@app.route("/<path:key>")
def get_resource(key):
    key_bytes = key.encode("utf-8")
    value = c_db.get(key_bytes)
    if not value:
        abort(404, "Key not found")

    mimetype = m_db.get(key_bytes)
    if mimetype:
        return Response(value, content_type=mimetype.decode("utf-8"))
    return Response(value, content_type="text/plain")

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="127.0.0.1", port=9191)
