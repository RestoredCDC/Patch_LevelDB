# 🌺 RestoredCDC LevelDB Patch Tool

[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-pytest-green)](#-running-tests)
[![Lint](https://img.shields.io/badge/lint-flake8%20%7C%20black%20%7C%20isort-blue)](#-linting--formatting)

---

A command-line tool for **patching, auditing**, and **managing LevelDB content**, designed for the RestoredCDC project.

---

## ✨ Features

✅ Supports **add**, **replace**, and **remove** operations  
✅ Handles both **text** and **binary** content  
✅ Automatic **audit logging** (JSON Lines)  
✅ Exports audit log as a simple **HTML report**  
✅ Tracks **MD5 checksums** for every patch  
✅ Patch **reason** and optional **MIME type** tracking  
✅ Includes unit tests via `pytest`

---

## 📦 Requirements

| Package    | Purpose          |
|------------|------------------|
| `plyvel`   | LevelDB bindings |
| `pytest`   | Testing          |
| `flake8`   | Linting          |
| `black`    | Code formatting  |
| `isort`    | Import sorting   |
| `flask` + `waitress` | Optional: serve patched content |

---

## 🛠 Installation

```bash
pip install -r requirements.txt
```

Or manually:

```bash
pip install plyvel flask waitress pytest flake8 black isort
```

---

## 🚦 Usage

### Apply a text patch
```bash
python cli.py apply-text --db path/to/patchdb --key mykey \
    --reason "Updated disclaimer text" --file disclaimer.txt \
    --mimetype text/plain
```

### Apply a binary patch
```bash
python cli.py add-binary --db path/to/patchdb --key logo \
    --reason "Updated logo" --file logo.png \
    --mimetype image/png
```

### Remove a patch (mode auto-detected)
```bash
python cli.py remove-patch --db path/to/patchdb --key oldfile --reason "Obsolete"
```

### List patches in the audit log
```bash
python cli.py list-patches
```

### Export audit log to HTML
```bash
python cli.py export-audit-html --output audit.html
```

---

## ✅ Running Tests

```bash
pytest tests/
```

---

## 🪑 Linting & Formatting

```bash
flake8
black patchlib.py cli.py tests/
isort patchlib.py cli.py tests/
```

---

## 📝 Notes

- The default audit log is located at `audit/patch_log.jsonl`.
- `remove-patch` automatically detects whether the content is text or binary.
- This tool is meant to manage **content patches**, not full database snapshots.
- For serving content from patched databases, see `serve.py`.

---

## 👷 Optional Improvements

If you're using this tool in production:
- Consider setting up a `Makefile`
- Enable `pre-commit` hooks for linting
- Auto-export audits during CI/CD

