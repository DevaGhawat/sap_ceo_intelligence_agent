import json
from datetime import datetime

from src.config import DATA_DIR


MEMORY_PATH = DATA_DIR / "agent_memory.jsonl"


def save_agent_run(record):
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    record["saved_at"] = datetime.now().isoformat(timespec="seconds")

    with open(MEMORY_PATH, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")

    return str(MEMORY_PATH)


def load_recent_agent_runs(limit=5):
    if not MEMORY_PATH.exists():
        return []

    with open(MEMORY_PATH, "r", encoding="utf-8") as file:
        lines = file.readlines()

    records = []

    for line in lines[-limit:]:
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue

    return records