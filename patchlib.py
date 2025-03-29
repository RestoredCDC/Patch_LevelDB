# patchlib.py

import hashlib
import html
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Optional

import plyvel

AUDIT_LOG = Path("audit/patch_log.jsonl")


def log_patch_entry(
    key: str,
    action: str,
    reason: str,
    digest: Optional[str] = None,
    mimetype: Optional[str] = None,
    audit_log_path: str = "audit/patch_log.jsonl",
) -> None:
    """
    Log a patch action to the audit log.

    :param key: The key that was patched.
    :param action: The action performed (add, replace, remove).
    :param reason: The reason for the patch.
    :param digest: Optional MD5 digest of the content.
    :param mimetype: Optional mimetype if the data is binary.
    :param audit_log_path: Path to the audit log file.
    """
    entry = {
        "key": key,
        "action": action,
        "reason": reason,
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if digest:
        entry["digest"] = digest
    if mimetype:
        entry["mimetype"] = mimetype
    with open(audit_log_path, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"✅ Patch logged for: {key}")
    

def compute_digest(data: bytes) -> str:
    """
    Compute MD5 digest for the given data.

    :param data: Data as bytes.
    :return: Hexadecimal digest string.
    """
    return hashlib.md5(data).hexdigest()


def apply_patch_action(
    patch_content_db: plyvel.DB,
    patch_mimetype_db: plyvel.DB,
    key: str,
    action: str,
    data: Optional[bytes] = None,
    filepath: Optional[str] = None,
    mimetype: Optional[str] = None,
    reason: str = "general patch",
    mode: Optional[str] = None,
    audit_log_path: str = "audit/patch_log.jsonl",
) -> None:
    """
    Apply a patch action (add, replace, remove) to the LevelDB.

    :param patch_content_db: DB for patch content.
    :param patch_mimetype_db: DB for mimetypes.
    :param key: Key to patch.
    :param action: Action type.
    :param data: Content data (for text mode).
    :param filepath: File path for binary content.
    :param mimetype: Mimetype of binary content.
    :param reason: Reason for the patch.
    :param mode: Patch mode (text or binary).
    :param audit_log_path: Audit log file.
    """
    key_bytes = key.encode("utf-8")

    if action == "remove" and mode is None:
        if patch_mimetype_db.get(key_bytes):
            mode = "binary"
        elif patch_content_db.get(key_bytes):
            mode = "text"
        else:
            print(f"⚠️  Warning: key '{key}' not found, defaulting to text mode.")
            mode = "text"

    if mode == "binary":
        if action in ("add", "replace"):
            with open(filepath, "rb") as f:
                data = f.read()
            patch_content_db.put(key_bytes, data)
            patch_mimetype_db.put(key_bytes, mimetype.encode("utf-8"))
        elif action == "remove":
            patch_content_db.delete(key_bytes)
            patch_mimetype_db.delete(key_bytes)

    elif mode == "text":
        if action in ("add", "replace"):
            with open(data, "rb") as f:
                content = f.read()
            patch_content_db.put(key_bytes, content)
        elif action == "remove":
            patch_content_db.delete(key_bytes)

    digest = None
    if action != "remove":
        if mode == "text":
            digest = compute_digest(content)
        elif mode == "binary":
            digest = compute_digest(data)

    log_patch_entry(
        key=key,
        action=action,
        reason=reason,
        digest=digest,
        mimetype=mimetype if mode == "binary" else None,
        audit_log_path=audit_log_path,
    )
    print(f"✅ Patch {action}d: {key} [mode: {mode}]")


def list_patches(audit_log_path: str = "audit/patch_log.jsonl") -> None:
    """
    Print the list of patches from the audit log.

    :param audit_log_path: Path to the audit log.
    """
    if not Path(audit_log_path).exists():
        print("No patches found.")
        return

    with open(audit_log_path, "r") as f:
        for i, line in enumerate(f, 1):
            entry = json.loads(line)
            print(f"Patch #{i}")
            print(f"  Key      : {entry['key']}")
            print(f"  Action   : {entry['action']}")
            print(f"  Reason   : {entry['reason']}")
            print(f"  Timestamp: {entry['timestamp']}")
            if "mimetype" in entry:
                print(f"  Mimetype : {entry['mimetype']}")
            print("  ---")


def export_audit_html(output_path: str) -> None:
    """
    Export the audit log to an HTML file.

    :param output_path: Output HTML file.
    """
    with open(AUDIT_LOG, "r") as f, open(output_path, "w") as out:
        out.write("<html><head><title>Patch Audit Report</title></head><body>\n")
        out.write("<h1>Patch Audit Log</h1><ul>\n")
        for line in f:
            entry = json.loads(line)
            out.write(
                f"<li><strong>{html.escape(entry['key'])}</strong>: "
                f"{html.escape(entry['reason'])}<br>\n"
            )
            out.write(f"Action: {entry['action']} | Time: {entry['timestamp']}\n")
            if "mimetype" in entry:
                out.write(f" | Mimetype: {entry['mimetype']}\n")
            out.write("</li>\n")
        out.write("</ul></body></html>")
    print(f"✅ Exported audit log to {output_path}")


def initialize_db(db_path: str):
    """
    Initialize patch databases.

    :param db_path: Path to LevelDB.
    :return: Tuple of (main db, content db, mimetype db).
    """
    patch_db = plyvel.DB(db_path, create_if_missing=True)
    patch_content_db = patch_db.prefixed_db(b"c-")
    patch_mimetype_db = patch_db.prefixed_db(b"m-")
    return patch_db, patch_content_db, patch_mimetype_db
