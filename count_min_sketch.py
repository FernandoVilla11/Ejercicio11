# count_min_sketch.py
import math, mmh3, random

class CountMinSketch:
    def __init__(self, width=2000, depth=5, seed=42):
        self.width = width
        self.depth = depth
        self.tables = [[0]*width for _ in range(depth)]
        random.seed(seed)
        self.seeds = [random.randint(0, 2**31-1) for _ in range(depth)]
    def _hashes(self, key):
        for s in self.seeds:
            yield mmh3.hash(key, s) % self.width
    def add(self, key, count=1):
        for i, idx in enumerate(self._hashes(key)):
            self.tables[i][idx] += count
    def estimate(self, key):
        return min(self.tables[i][idx] for i, idx in enumerate(self._hashes(key)))

# Ejemplo de uso
if __name__ == "__main__":
    cms = CountMinSketch()
    cms.add("player:123", 1)
    cms.add("player:111", 5)
    print("Estimate player:123 ->", cms.estimate("player:123"))
    print("Estimate player:111 ->", cms.estimate("player:111"))
