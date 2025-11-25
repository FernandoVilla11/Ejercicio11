# dgim.py
import math, time

class DGIM:
    def __init__(self, window_size):
        self.window = window_size
        # buckets: list of (timestamp_of_rightmost_1, size), newer first
        self.buckets = []

    def _current_time(self):
        return int(time.time())

    def add_bit(self, bit, ts=None):
        if ts is None:
            ts = self._current_time()
        # shift: we won't maintain exact positions by index; we'll store event order index instead
        if bit:
            # create new bucket size 1 at current position
            self.buckets.insert(0, {'time': ts, 'size':1})
            # merge buckets of same size from left to right
            i = 0
            while i+2 < len(self.buckets):
                if self.buckets[i]['size'] == self.buckets[i+1]['size'] == self.buckets[i+2]['size']:
                    # merge top two (i+1 into i)
                    self.buckets[i+1]['size'] += self.buckets[i]['size']
                    self.buckets.pop(i)
                else:
                    i += 1
        # expire buckets older than window_time (if window is time-based). If window is count-based, you'd track indices.
        cutoff = ts - self.window
        # remove buckets whose rightmost timestamp < cutoff
        self.buckets = [b for b in self.buckets if b['time'] >= cutoff]

    def query(self, ts=None):
        if ts is None:
            ts = self._current_time()
        cutoff = ts - self.window
        total = 0
        last_bucket = None
        for b in self.buckets:
            if b['time'] < cutoff:
                # this bucket is partially outside window
                if last_bucket is None:
                    # approximate half of this bucket
                    total += b['size'] // 2
                break
            total += b['size']
            last_bucket = b
        return total
