# ams_f2.py
import random, hashlib

class AMSF2:
    def __init__(self, k=10):
        self.k = k
        self.sign_hashes = [random.randint(1, 2**31-1) for _ in range(k)]
        self.Z = [0]*k

    def _sign(self, x, seed):
        key = f"{x}:{seed}".encode('utf-8')
        h = int(hashlib.sha256(key).hexdigest(),16)
        return 1 if h % 2 == 0 else -1

    def update(self, item, value=1):
        # item: discretized bin (e.g., int(speed_bin))
        for i in range(self.k):
            s = self._sign(item, self.sign_hashes[i])
            self.Z[i] += s * value

    def estimate_F2(self):
        vals = [z*z for z in self.Z]
        return sum(vals)/len(vals)
