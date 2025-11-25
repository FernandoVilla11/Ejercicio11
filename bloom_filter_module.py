# bloom_filter_module.py
from pybloom_live import BloomFilter

# crear bloom (capacidad 10000, error 0.001)
bf = BloomFilter(capacity=10000, error_rate=0.001)

def mark_play_analyzed(play_key: str):
    bf.add(play_key)

def check_play_analyzed(play_key: str) -> bool:
    return play_key in bf
