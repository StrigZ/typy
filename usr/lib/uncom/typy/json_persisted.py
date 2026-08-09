import json
import os
from dataclasses import asdict, fields
from utility import ensure_folder_exists


class JsonPersisted:
    def _load_raw(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_raw(self, path: str, data: dict):
        ensure_folder_exists(os.path.dirname(path))
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def _parse_record(self, cls, raw: dict):
        known = {f.name for f in fields(cls)}
        return cls(**{k: v for k, v in raw.items() if k in known})

    def _record_to_dict(self, record) -> dict:
        return asdict(record)
