# Patch_LevelDB

A transparent patching and correction layer for an immutable LevelDB dataset—designed for RestoredCDC or similar archival projects.

---

## ✨ Overview
This project allows you to preserve the original LevelDB dataset (the "base crawl") and layer on top of it a second LevelDB ("patch DB") containing only corrections or additions.

- No modifications are made to the original dataset.
- All changes are logged in a structured, auditable format.
- Ideal for correcting broken links, missing images, or inserting disclaimers.

---

## 🌐 Architecture

```
+--------------------------+
|   Patch LevelDB         |  ← Check here first
+--------------------------+
           |
           v
+--------------------------+
|   Base (Original) DB    |  ← Fallback if not patched
+--------------------------+
```

Handled via the `LayeredDB` class in `layered_db.py`.

---

## 🚀 Quickstart

### 1. Clone & Install
```bash
git clone git@github.com:RestoredCDC/Patch_LevelDB.git
cd Patch_LevelDB
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Apply a Patch
```bash
python patch_tool.py patches/patchdb \
  /cdc/pages/about/index.html \
  banner.html \
  "Added disclaimer banner to about page"
```

- This will insert the contents of `banner.html` as the new value for that key.
- It will also append an entry to `audit/patch_log.jsonl`.

---

## 📒 Audit Logging
Every patch is recorded as a JSON line in `audit/patch_log.jsonl`. Example:

```json
{
  "key": "/cdc/pages/about/index.html",
  "action": "added_or_modified",
  "patch_digest": "a925c44f92a071e92868f8cb8e17d020",
  "reason": "Added disclaimer banner",
  "timestamp": "2025-03-27T15:32:10Z",
  "author": "restoredcdc-bot"
}
```

---

## 📊 File Structure

```
Patch_LevelDB/
├── layered_db.py         # Read logic for base + patch fallback
├── patch_tool.py         # CLI to add patches and log them
├── audit/
│   └── patch_log.jsonl  # JSONL-formatted audit trail
├── patches/              # Patch DB lives here
├── tests/                # Test coverage
├── requirements.txt
└── README.md
```

---

## 📈 Future Plans
- Add `--dry-run` and `--diff` preview to `patch_tool.py`
- Patch validator (check if key exists in base or is referenced)
- Merge script (optional: bake patches into new unified DB)

---

## 🙏 Credits
Developed by and for the [RestoredCDC](https://github.com/RestoredCDC) project.

Contributions and forks welcome!


