# monte_carlo_predict.py
import random

def simulate_score_probability(speed, accuracy, stamina, n=1000):
    # normalizar inputs (ejemplo simple)
    s = float(speed)  # m/s
    a = float(accuracy)  # 0-100
    st = float(stamina)  # 0-100

    # heurística: más speed+accuracy+stamina -> mayor chance
    base = (s/30)*0.4 + (a/100)*0.4 + (st/100)*0.2
    wins = 0
    for _ in range(n):
        # aleatoriedad por ruido del partido
        noise = random.gauss(0, 0.1)
        prob = min(max(base + noise, 0), 1)
        # evento "anotar / éxito"
        if random.random() < prob:
            wins += 1
    return wins / n

# Ejemplo
if __name__ == "__main__":
    p = simulate_score_probability(12.5, 78, 80, n=2000)
    print("Probabilidad estimada de éxito:", p)
