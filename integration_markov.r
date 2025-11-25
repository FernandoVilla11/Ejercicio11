# integration_markov.py (fragmento)
from markov_module import OnlineMarkovModel
# define states
states = ["peak","good","average","declining","injured"]
markov = OnlineMarkovModel(states)

def process_record_markov(rec):
    prev = rec.get("previousPerformanceState")
    cur = rec.get("performanceState")
    if prev and cur:
        markov.observe_transition(prev, cur)
    # periódicamente (cada N eventos o cada T segundos) recomputar y exponer:
    P = markov.transition_prob_matrix_readable()
    stationary = markov.stationary_distribution()
    aperiodic = markov.is_aperiodic()
    irreducible = markov.is_irreducible()
    mixing = markov.mixing_time_approx(tol=1e-3, max_steps=200)
    # exponer a Redis / API:
    # r.hset("markov:player:GLOBAL", mapping={"P":json.dumps(P), "pi":json.dumps(stationary), ...})
    # o emitir via websocket a dashboard
