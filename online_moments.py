# online_moments.py
import math

class RunningMoments:
    def __init__(self):
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.M3 = 0.0
        self.M4 = 0.0

    def update(self, x):
        n1 = self.n
        self.n += 1
        delta = x - self.mean
        delta_n = delta / self.n
        delta_n2 = delta_n * delta_n
        term1 = delta * delta_n * n1

        self.mean += delta_n
        self.M4 += term1 * delta_n2 * (self.n*self.n - 3*self.n + 3) + 6*delta_n2*self.M2 - 4*delta_n*self.M3
        self.M3 += term1 * delta_n * (self.n - 2) - 3*delta_n*self.M2
        self.M2 += term1

    def get_mean(self):
        return self.mean if self.n else 0.0
    def get_variance(self):
        return (self.M2 / (self.n - 1)) if self.n > 1 else 0.0
    def get_skewness(self):
        if self.n < 3: return 0.0
        return (math.sqrt(self.n) * self.M3) / (self.M2 ** 1.5)
    def get_kurtosis(self):
        if self.n < 4: return 0.0
        return (self.n * self.M4) / (self.M2 * self.M2) - 3.0
