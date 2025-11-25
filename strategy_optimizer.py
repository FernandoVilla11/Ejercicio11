# strategy_optimizer.py (apéndice)
import copy
import numpy as np

def tweak_transition_for_action(P, states, action):
    # P: np.array row-stochastic
    Q = P.copy()
    # ejemplo heurístico:
    # - if action == "rest": decrease prob of transition to 'injured' and increase to 'good' by small factor
    if action == "rest":
        if 'injured' in states and 'good' in states:
            i_inj = states.index('injured')
            i_good = states.index('good')
            # for all rows, move epsilon mass from injured column to good column proportionally
            eps = 0.05
            delta = np.minimum(Q[:,i_inj], eps)
            Q[:,i_inj] -= delta
            Q[:,i_good] += delta
            # renormalize rows
            Q = Q / Q.sum(axis=1, keepdims=True)
    if action == "substitute":
        # approximation: immediate jump to 'average' or 'good' depending
        # implement as making current state's row have 0 prob except to 'average'
        pass
    # puedes añadir más acciones y reglas
    return Q

def evaluate_action_long_term(P_orig, states, action, reward_per_state):
    Q = tweak_transition_for_action(P_orig.copy(), states, action)
    # compute stationary dist for Q (power method)
    n = len(states)
    v = np.ones(n)/n
    for _ in range(1000):
        v_new = v.dot(Q)
        if np.linalg.norm(v_new - v, ord=1) < 1e-9:
            v = v_new; break
        v = v_new
    expected_reward = float(v.dot(np.array([reward_per_state[s] for s in states])))
    return expected_reward, v
