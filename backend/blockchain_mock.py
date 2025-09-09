import json, hashlib, time, os
from pathlib import Path

LEDGER_PATH = Path(__file__).parent / "ledger.jsonl"

def _hash_record(record: dict) -> str:
    # Stable string for hash
    s = json.dumps(record, sort_keys=True, separators=(",",":"))
    return hashlib.sha256(s.encode()).hexdigest()

def append_entry(entry: dict) -> dict:
    """Append an entry to append-only ledger with prev_hash linking (hash chain)."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    prev_hash = "GENESIS"
    if LEDGER_PATH.exists():
        with LEDGER_PATH.open("rb") as f:
            # read last line efficiently
            f.seek(0, os.SEEK_END)
            pos = f.tell() - 1
            while pos > 0 and f.read(1) != b"\n":
                pos -= 1
                f.seek(pos, os.SEEK_SET)
            last_line = f.readline().decode().strip()
        if last_line:
            try:
                last = json.loads(last_line)
                prev_hash = last.get("hash", "GENESIS")
            except Exception:
                prev_hash = "GENESIS"
    record = {
        "ts": time.time(),
        "prev_hash": prev_hash,
        "payload": entry,
    }
    record["hash"] = _hash_record(record)
    with LEDGER_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, separators=(",",":")) + "\n")
    return record

def verify_chain() -> bool:
    """Verify entire chain linkage and hashes."""
    if not LEDGER_PATH.exists():
        return True
    prev = "GENESIS"
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            expected_hash = hashlib.sha256(json.dumps(
                {"ts": rec["ts"], "prev_hash": rec["prev_hash"], "payload": rec["payload"]},
                sort_keys=True, separators=(",",":")
            ).encode()).hexdigest()
            if rec.get("hash") != expected_hash or rec.get("prev_hash") != prev:
                return False
            prev = rec.get("hash")
    return True
