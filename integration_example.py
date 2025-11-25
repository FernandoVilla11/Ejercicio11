# integration_example.py (fragmento)
import json
import redis
from bloom_filter_module import bf, mark_play_analyzed, check_play_analyzed
from minwise_sampler import MinWiseSampler
from online_moments import RunningMoments
from ams_f2 import AMSF2
from dgim import DGIM

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

# instancias globales (o por worker)
minwise = MinWiseSampler(k=200)
dgim_global = DGIM(window_size=60*5)  # contar picos en últimos 5 minutos
# moments por jugador: dict player_id -> RunningMoments for speed & accuracy
moments = {}
ams_speed = AMSF2(k=10)

def process_event(rec):
    # keys
    play_key = f"{rec['sport']}:{rec['playType']}"
    player_key = rec.get('_id')  # o computed hashed key
    # 1) Bloom: chequear si ya analizamos este tipo-play
    if not check_play_analyzed(play_key):
        mark_play_analyzed(play_key)
        # puedes realizar computos extra la primera vez que aparece ese playType

    # 2) HyperLogLog (Redis)
    r.pfadd("hll:plays", f"{rec['sport']}|{rec['playType']}|{rec['_id']}")

    # 3) MinWise: considerar solo si performancePeak o evento clave
    if rec.get('performancePeak'):
        minwise.consider(json.dumps(rec))

    # 4) Update moments per player
    pid = rec['player']
    if pid not in moments:
        moments[pid] = {"speed": RunningMoments(), "accuracy": RunningMoments()}
    moments[pid]["speed"].update(float(rec["performanceData"]["speed"]))
    moments[pid]["accuracy"].update(float(rec["performanceData"]["accuracy"]))

    # 5) AMS sketch: discretiza speed por bin y actualizar
    speed_bin = int(float(rec["performanceData"]["speed"]))  # ejemplo: bin por m/s
    ams_speed.update(speed_bin, 1)

    # 6) DGIM: actualizar conteo de picos
    dgim_global.add_bit(1 if rec.get("performancePeak") else 0)

    # 7) Actualizar Count-Min Sketch, Redis Hash, etc (ya lo tenías)
    # r.hset(...) ...
