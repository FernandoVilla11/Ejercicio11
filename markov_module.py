# markov_module.py
import numpy as np
from collections import defaultdict
import math

class OnlineMarkovModel:
    def __init__(self, states, smoothing=1e-3):
        """
        states: list of state names e.g. ["peak","good","average","declining","injured"]
        smoothing: additive smoothing to avoid zeros
        """
        self.states = list(states)
        self.idx = {s:i for i,s in enumerate(self.states)}
        self.n = len(self.states)
        # counts[i][j] = transitions observed i -> j
        self.counts = np.zeros((self.n, self.n), dtype=float)
        self.smoothing = smoothing
        # maintain stationary distribution cache
        self._cached_P = None

    def observe_transition(self, from_state, to_state, weight=1.0):
        if from_state not in self.idx or to_state not in self.idx:
            return
        i = self.idx[from_state]
        j = self.idx[to_state]
        self.counts[i,j] += weight
        self._cached_P = None

    def transition_matrix(self):
        # returns row-stochastic matrix P (rows sum to 1)
        if self._cached_P is not None:
            return self._cached_P
        C = self.counts + self.smoothing
        row_sums = C.sum(axis=1, keepdims=True)
        # avoid division by zero
        row_sums[row_sums==0] = 1.0
        P = C / row_sums
        self._cached_P = P
        return P

    def predict_distribution(self, current_state, steps=1):
        if current_state not in self.idx:
            return None
        P = self.transition_matrix()
        v = np.zeros(self.n)
        v[self.idx[current_state]] = 1.0
        # fast exponentiation via repeated multiplication (steps usually small)
        for _ in range(steps):
            v = v.dot(P)
        return {self.states[i]: float(v[i]) for i in range(self.n)}

    def stationary_distribution(self, tol=1e-9, max_iter=10000):
        P = self.transition_matrix()
        # power method: start uniform distribution
        v = np.ones(self.n) / self.n
        for it in range(max_iter):
            v_new = v.dot(P)
            if np.linalg.norm(v_new - v, ord=1) < tol:
                return {self.states[i]: float(v_new[i]) for i in range(self.n)}
            v = v_new
        return {self.states[i]: float(v[i]) for i in range(self.n)}

    def is_aperiodic(self):
        # practical check: if any self-loop probability > 0 => aperiodic
        P = self.transition_matrix()
        if any(P[i,i] > 1e-12 for i in range(self.n)):
            return True
        # otherwise we do a weak test: check gcd of lengths up to some power
        # compute reachable sets for powers of P: if for some n, diagonal positive for all states -> aperiodic
        max_power = 10
        A = (P > 1e-12).astype(int)
        M = A.copy()
        for power in range(1, max_power+1):
            diag = np.diag(M)
            if all(diag > 0):
                return True
            M = (M.dot(A) > 0).astype(int)
        return False

    def is_irreducible(self):
        # connectivity on directed graph where there's edge i->j if count>0
        A = (self.counts > 0).astype(int)
        # floyd-warshall reachability OR BFS from first node
        reachable = set()
        stack = [0]
        visited = set(stack)
        while stack:
            u = stack.pop()
            reachable.add(u)
            for v in range(self.n):
                if A[u,v] and v not in visited:
                    visited.add(v)
                    stack.append(v)
        return len(reachable) == self.n

    def mixing_time_approx(self, tol=1e-3, max_steps=1000):
        # approximate mixing time: smallest t s.t. for any initial state distribution, distance to stationary < tol
        # approximate by checking worst-case starting basis vectors
        pi = np.array(list(self.stationary_distribution().values()))
        P = self.transition_matrix()
        worst = 0
        for s in range(self.n):
            v = np.zeros(self.n); v[s]=1.0
            for t in range(1, max_steps+1):
                v = v.dot(P)
                tvd = 0.5 * np.sum(np.abs(v - pi))
                if tvd < tol:
                    worst = max(worst, t)
                    break
            else:
                # didn't mix within max_steps
                worst = max(worst, max_steps)
        return worst

    def transition_prob_matrix_readable(self):
        P = self.transition_matrix()
        out = {}
        for i,s in enumerate(self.states):
            out[s] = {self.states[j]: float(P[i,j]) for j in range(self.n)}
        return out
