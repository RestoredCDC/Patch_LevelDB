# tests/test_patchlib.py

import os
import shutil
import json
import pytest
import plyvel
import uuid
from pathlib import Path

import patchlib

TEST_DB_PATH = f"tests/testdb_{uuid.uuid4().hex}"

TEST_AUDIT_LOG = "tests/test_audit.jsonl"

@pytest.fixture(autouse=True, scope="module")
def setup_and_teardown():
    if os.path.exists(TEST_DB_PATH):
        shutil.rmtree(TEST_DB_PATH)
    if os.path.exists(TEST_AUDIT_LOG):
        os.remove(TEST_AUDIT_LOG)
    os.makedirs("tests", exist_ok=True)
    db, c_db, m_db = patchlib.initialize_db(TEST_DB_PATH)
    db.close()
    yield
    if os.path.exists(TEST_AUDIT_LOG):
        os.remove(TEST_AUDIT_LOG)



def test_apply_text_patch():
    db, c_db, m_db = patchlib.initialize_db(TEST_DB_PATH)
    patchlib.apply_patch_action(
        c_db, m_db,
        key="test-text",
        action="add",
        reason="test text insert",
        data="tests/dummy.txt",
        mode="text",
        audit_log_path=TEST_AUDIT_LOG
    )
    assert c_db.get(b"test-text") is not None
    db.close()


def test_apply_binary_patch():
    db, c_db, m_db = patchlib.initialize_db(TEST_DB_PATH)
    with open("tests/dummy.bin", "wb") as f:
        f.write(b"\x00\x01\x02")
    patchlib.apply_patch_action(
        c_db, m_db,
        key="test-bin",
        action="add",
        reason="test binary insert",
        filepath="tests/dummy.bin",
        mimetype="application/octet-stream",
        mode="binary",
        audit_log_path=TEST_AUDIT_LOG
    )
    assert c_db.get(b"test-bin") is not None
    assert m_db.get(b"test-bin") == b"application/octet-stream"
    db.close()
    os.remove("tests/dummy.bin")


def test_remove_patch():
    db, c_db, m_db = patchlib.initialize_db(TEST_DB_PATH)
    c_db.put(b"remove-me", b"bye")
    patchlib.apply_patch_action(
        c_db, m_db,
        key="remove-me",
        action="remove",
        reason="test remove",
        audit_log_path=TEST_AUDIT_LOG
    )
    assert c_db.get(b"remove-me") is None
    db.close()


def test_audit_log_written():
    db, c_db, m_db = patchlib.initialize_db(TEST_DB_PATH)
    patchlib.apply_patch_action(
        c_db, m_db,
        key="audit-check",
        action="add",
        reason="audit test",
        data="tests/dummy.txt",
        mode="text",
        audit_log_path=TEST_AUDIT_LOG
    )
    db.close()
    assert os.path.exists(TEST_AUDIT_LOG)
    with open(TEST_AUDIT_LOG) as f:
        logs = [json.loads(line) for line in f]
    assert any(entry['key'] == 'audit-check' for entry in logs)
