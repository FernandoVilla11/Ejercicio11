# generate_markov_data.py - Complete Sports Performance Data Generator
import json, random, uuid, datetime
from faker import Faker

fake = Faker()

# Core Sports Categories
sports = ["football", "basketball", "soccer", "tennis", "hockey"]
positions = ["forward", "midfielder", "defender", "goalkeeper", "guard", "center"]

# Markov Chain States
perf_states = ["peak", "good", "average", "declining", "injured"]
prev_states = ["peak", "good", "average", "declining"]
momentum_states = ["strong_favor", "slight_favor", "neutral", "slight_against", "strong_against"]
game_phases = ["opening", "early", "middle", "late", "critical"]

# Team & Strategy States
team_states = ["coordinated", "average", "disjointed"]
roles = ["leader", "supporting", "specialist", "substitute"]
strategies = ["aggressive", "defensive", "balanced", "adaptive"]
play_types = ["offensive", "defensive", "special", "transition"]

# Near Neighbor Search Categories
nn_sports = ["Basketball", "Soccer", "Tennis", "Running"]

# MapReduce & Processing Categories
processing_nodes = [f"node_{i}" for i in range(1, 12)]

def gen_record():
    ts = datetime.datetime.utcnow().isoformat() + "Z"
    speed = round(random.uniform(5,30), 2)
    accuracy = random.randint(50,100)
    stamina = random.randint(0,100)
    player_id = str(uuid.uuid4())
    current_sport = random.choice(sports)
    current_position = random.choice(positions)
    perf_state = random.choice(perf_states)
    
    return {
        # Core Identification
        "_id": player_id,
        "player": f"{fake.first_name()} {fake.last_name()}",
        "sport": current_sport,
        "position": current_position,
        
        # Markov Chain States (Unit 3)
        "performanceState": perf_state,
        "previousPerformanceState": random.choice(prev_states),
        "stateTransitionProb": round(random.uniform(0.0, 1.0), 3),
        "timeInPerformanceState": random.randint(5, 300),
        "expectedPerformanceDuration": random.randint(10, 180),
        
        # Enhanced Performance Data
        "performanceData": {
            "speed": f"{speed}",
            "accuracy": accuracy,
            "stamina": stamina,
            "consistency": round(random.uniform(0.0, 1.0), 2),
            "pressureHandling": round(random.uniform(0.0, 1.0), 2),
            "pointsScored": random.randint(0, 50),  # For MapReduce algorithms
            "gamesPlayed": random.randint(1, 82),   # For player counting
        },
        
        # Game Flow Analysis
        "gameFlowAnalysis": {
            "momentumState": random.choice(momentum_states),
            "momentumTransitionProb": round(random.uniform(0.0,1.0), 3),
            "scoringProbability": round(random.uniform(0.0,1.0), 3),
            "gamePhase": random.choice(game_phases)
        },
        
        # Team Dynamics
        "teamDynamics": {
            "teamState": random.choice(team_states),
            "roleInTeam": random.choice(roles),
            "teamChemistry": round(random.uniform(0.0,1.0), 2),
            "communicationEffectiveness": round(random.uniform(0.0,1.0), 2),
            "teamId": f"team_{random.randint(1, 30)}"  # For MapReduce joins
        },
        
        # Strategic Analysis
        "strategicAnalysis": {
            "optimalStrategy": random.choice(strategies),
            "strategyTransitionProb": round(random.uniform(0.0,1.0), 3),
            "counterStrategyRisk": round(random.uniform(0.0,1.0), 2),
            "adaptabilityIndex": round(random.uniform(0.0,1.0), 2)
        },
        
        # Performance Prediction
        "performancePrediction": {
            "nextGamePerformance": random.choice(["peak","good","average","declining"]),
            "predictionConfidence": round(random.uniform(0.0,1.0), 2),
            "expectedImprovement": round(random.uniform(-20.0,50.0), 1),
            "recoveryTime": random.randint(24,720)
        },
        
        # Injury Risk Analysis
        "injuryRiskAnalysis": {
            "currentRiskLevel": round(random.uniform(0.0,1.0), 2),
            "injuryTransitionProb": round(random.uniform(0.0,0.1), 4),
            "recoveryStateProb": round(random.uniform(0.0,1.0), 3),
            "fitnessDeclineRate": round(random.uniform(0.0,0.1), 4)
        },
        
        # Streaming Algorithms Fields (Unit 1)
        "playType": random.choice(play_types),
        "performancePeak": random.choice([True, False]),
        "stationaryPerformance": round(random.uniform(0.0,1.0), 3),
        "ergodicity": random.choice([True, False]),
        "mixingTime": random.randint(10,120),
        
        # MapReduce Fields (Unit 4)
        "mapReducePartition": random.randint(1, 22),
        "processingNode": random.choice(processing_nodes),
        "batchId": f"batch_{random.randint(1000, 9999)}",
        "aggregationKey": f"{perf_state}_{current_position}",
        
        # Near Neighbor Search Fields (Unit 6)
        "sportsSimilarity": {
            "performanceScores": [random.randint(60, 100) for _ in range(4)],
            "sport": random.choice(nn_sports),
            "experienceLevel": random.randint(1, 10),
            "improvementRate": round(random.uniform(0.0, 0.3), 2),
            "trainingResponse": round(random.uniform(0.5, 1.0), 2),
            "athleteSimilarityScore": round(random.uniform(0.4, 1.0), 2)
        },
        
        # Training & Development Metrics
        "trainingMetrics": {
            "weeklyTrainingHours": random.randint(10, 40),
            "skillDevelopmentRate": round(random.uniform(0.01, 0.15), 3),
            "fatigueLevel": round(random.uniform(0.0, 1.0), 2),
            "mentalReadiness": round(random.uniform(0.3, 1.0), 2)
        },
        
        # Cost Analysis (for MapReduce cost calculations)
        "resourceUsage": {
            "dataStorageMB": random.randint(50, 500),
            "processingTimeMS": random.randint(10, 1000),
            "networkBandwidthKbps": random.randint(100, 10000)
        },
        
        # Final timestamp
        "timestamp": ts
    }

if __name__ == "__main__":
    # Generate different datasets for different purposes
    datasets = {
        "synthetic_sports_complete_1000.json": 1000,  # Full dataset
        "synthetic_sports_training_500.json": 500,    # Training dataset
        "synthetic_sports_test_200.json": 200         # Test dataset
    }
    
    for filename, count in datasets.items():
        data = [gen_record() for _ in range(count)]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Generado {filename} con {count} registros")
    
    print("\nTodos los datasets generados exitosamente!")
    print("- Dataset completo: 1000 registros")
    print("- Dataset de entrenamiento: 500 registros") 
    print("- Dataset de prueba: 200 registros")
