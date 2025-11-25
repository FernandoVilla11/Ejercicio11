# ingest_redis.py
import json, hashlib
import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

def make_key(record):
    # key por jugador: hash del nombre + id corto
    h = hashlib.sha256(record["_id"].encode()).hexdigest()[:16]
    return f"player:{h}"

def ingest(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for rec in data:
        key = make_key(rec)
        # Guardamos stats como hash
        perf = rec["performanceData"]
        r.hset(key, mapping={
            "player": rec["player"],
            "sport": rec["sport"],
            "speed": perf["speed"].split()[0],
            "accuracy": perf["accuracy"].strip('%'),
            "stamina": perf["stamina"].strip('%'),
            "last_ts": rec["timestamp"]
        })
        # push al timeline general
        r.lpush("events:timeline", json.dumps({"key": key, "ts": rec["timestamp"]}))
    print("Ingesta completa")

if __name__ == "__main__":
    ingest("synthetic_sports_500.json")
