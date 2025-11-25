# generate_data.py
import json, random, uuid, datetime
from faker import Faker

fake = Faker()
sports = ["football", "basketball", "soccer", "tennis"]

def gen_record():
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    return {
        "_id": str(uuid.uuid4()),
        "player": f"{fake.first_name()} {fake.last_name()}",
        "sport": random.choice(sports),
        "performanceData": {
            "speed": f"{random.uniform(5,30):.2f} m/s",
            "accuracy": f"{random.randint(50,100)}%",
            "stamina": f"{random.randint(0,100)}%"
        },
        "timestamp": ts
    }

if __name__ == "__main__":
    data = [gen_record() for _ in range(500)]
    with open("synthetic_sports_500.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("Generado synthetic_sports_500.json con 500 registros")
