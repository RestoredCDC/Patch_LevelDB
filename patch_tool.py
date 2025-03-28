# patch_tool.py

import plyvel
import hashlib
import json
import argparse
from datetime import datetime
from pathlib import Path

AUDIT_LOG = Path("audit/patch_log.jsonl")

def compute_digest(data):
    return hashlib.md5(data).hexdigest()

def log_patch(entry):
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")

def apply_patch(patch_db_path, key, new_value, reason, author="restoredcdc-bot"):
    patch_db = plyvel.DB(patch_db_path, create_if_missing=True)

    # Encode key/value
    if isinstance(key, str):
        key = key.encode("utf-8")
    if isinstance(new_value, str):
        new_value = new_value.encode("utf-8")

    # Compute digest
    patch_digest = compute_digest(new_value)

    # Insert patch
    patch_db.put(key, new_value)
    patch_db.close()

    # Log it
    entry = {
        "key": key.decode("utf-8"),
        "action": "added_or_modified",
        "patch_digest": patch_digest,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "author": author
    }
    log_patch(entry)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply a patch to the patch LevelDB and log it.")
    parser.add_argument("patch_db", help="Path to patch LevelDB")
    parser.add_argument("key", help="Key to patch (e.g., /cdc/pages/example.html)")
    parser.add_argument("value_file", help="Path to file containing new value")
    parser.add_argument("reason", help="Reason for the patch")
    parser.add_argument("--author", default="restoredcdc-bot", help="Author name for audit log")

    args = parser.parse_args()

    with open(args.value_file, "rb") as f:
        new_value = f.read()

    apply_patch(args.patch_db, args.key, new_value, args.reason, args.author)

