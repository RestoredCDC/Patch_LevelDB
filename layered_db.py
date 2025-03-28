# layered_db.py

import plyvel

class LayeredDB:
    def __init__(self, patch_path, base_path):
        self.patch_db = plyvel.DB(patch_path, create_if_missing=True)
        self.base_db = plyvel.DB(base_path, create_if_missing=False)

    def get(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')

        val = self.patch_db.get(key)
        if val is not None:
            return val
        return self.base_db.get(key)

    def has_key(self, key):
        if isinstance(key, str):
            key = key.encode('utf-8')
        return self.patch_db.get(key) is not None or self.base_db.get(key) is not None

    def all_keys(self):
        keys = set()
        for key, _ in self.base_db:
            keys.add(key)
        for key, _ in self.patch_db:
            keys.add(key)
        return sorted(keys)

    def close(self):
        self.patch_db.close()
        self.base_db.close()

