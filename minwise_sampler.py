# minwise_sampler.py
import heapq, hashlib

class MinWiseSampler:
    def __init__(self, k=200):
        self.k = k
        # max-heap of (-hash, item) so we can pop largest hash to maintain k smallest hashes
        self.heap = []

    def _hash_item(self, item_str):
        h = hashlib.sha256(item_str.encode('utf-8')).hexdigest()
        # convert to int
        return int(h, 16)

    def consider(self, item):
        hval = self._hash_item(item)
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, (-hval, item))
        else:
            # if new hash smaller than current max, replace
            if hval < -self.heap[0][0]:
                heapq.heapreplace(self.heap, (-hval, item))

    def sample(self):
        return [item for _, item in self.heap]
