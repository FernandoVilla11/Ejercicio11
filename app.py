# app.py - Enhanced Real-Time Sports Performance Tracking System
import asyncio, json, logging, os
from typing import Dict, List, Optional
import redis
from fastapi import FastAPI, WebSocket, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from datetime import datetime, timedelta

# Import our custom algorithms
from bloom_filter_module import bf, mark_play_analyzed, check_play_analyzed
from count_min_sketch import CountMinSketch
from markov_module import OnlineMarkovModel
from knn_athlete_similarity import AthleteKNNAnalyzer
from mapreduce_algorithms import (
    PlayerPerformanceCounter, AverageScoreCalculator, 
    SportsReportGenerator, SportsSystemCostCalculator, SportsProcessingPerformance
)
from minwise_sampler import MinWiseSampler
from online_moments import RunningMoments
from ams_f2 import AMSF2
from dgim import DGIM
from monte_carlo_predict import simulate_score_probability

# Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app setup
app = FastAPI(
    title="Real-Time Sports Performance Tracking System",
    description="Advanced sports analytics with streaming algorithms, ML, and real-time processing",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class AthleteData(BaseModel):
    player: str
    sport: str
    performance_data: Dict
    timestamp: Optional[str] = None

class PredictionRequest(BaseModel):
    speed: float
    accuracy: float
    stamina: float
    simulation_count: Optional[int] = 1000

# Global instances
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
    r.ping()  # Test connection
    logger.info(f"✅ Redis connected at {REDIS_HOST}:{REDIS_PORT}")
except Exception as e:
    logger.error(f"❌ Redis connection failed: {e}")
    r = None

# WebSocket clients
clients = set()

# Analytics instances
cms = CountMinSketch(width=2000, depth=5)
markov = OnlineMarkovModel(["peak", "good", "average", "declining", "injured"])
knn_analyzer = AthleteKNNAnalyzer(n_neighbors=5)
minwise = MinWiseSampler(k=200)
dgim_global = DGIM(window_size=60*5)  # 5 minutes
ams_speed = AMSF2(k=10)

# MapReduce processors
player_counter = PlayerPerformanceCounter()
score_calculator = AverageScoreCalculator()
report_generator = SportsReportGenerator()
cost_calculator = SportsSystemCostCalculator()
performance_analyzer = SportsProcessingPerformance()

# Running statistics per player
player_moments = {}  # player_id -> {"speed": RunningMoments(), "accuracy": RunningMoments()}

# In-memory data storage for analytics
processed_athletes = []
analytics_cache = {
    "last_update": None,
    "player_rankings": [],
    "position_averages": {},
    "similarity_network": {},
    "markov_predictions": {},
    "cost_analysis": {}
}

# === WebSocket Endpoints ===

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    """Enhanced WebSocket endpoint with real-time analytics"""
    await ws.accept()
    clients.add(ws)
    logger.info(f"✅ WebSocket client connected. Total clients: {len(clients)}")
    
    try:
        # Send initial analytics data
        await ws.send_text(json.dumps({
            "type": "initial_data",
            "analytics": analytics_cache,
            "timestamp": datetime.now().isoformat()
        }))
        
        while True:
            # Keep connection alive and send periodic updates
            await asyncio.sleep(30)
            await ws.send_text(json.dumps({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat(),
                "clients_connected": len(clients)
            }))
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        clients.remove(ws)
        logger.info(f"WebSocket client disconnected. Total clients: {len(clients)}")

# === REST API Endpoints ===

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the main dashboard"""
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Dashboard not found. Please ensure index.html exists.</h1>")

@app.post("/api/athlete/process")
async def process_athlete_data(athlete_data: AthleteData, background_tasks: BackgroundTasks):
    """Process new athlete data through all algorithms"""
    try:
        # Convert Pydantic model to dict
        record = athlete_data.dict()
        record["timestamp"] = record.get("timestamp") or datetime.now().isoformat()
        record["_id"] = f"athlete_{len(processed_athletes)}"
        
        # Add to processed data
        processed_athletes.append(record)
        
        # Process in background
        background_tasks.add_task(process_athlete_record, record)
        
        return JSONResponse({
            "status": "success",
            "message": "Athlete data processed successfully",
            "athlete_id": record["_id"]
        })
        
    except Exception as e:
        logger.error(f"Error processing athlete data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get comprehensive analytics summary"""
    try:
        if not processed_athletes:
            return JSONResponse({"message": "No data processed yet"})
        
        # Update analytics cache
        await update_analytics_cache()
        
        return JSONResponse({
            "status": "success",
            "data": analytics_cache,
            "total_athletes": len(processed_athletes),
            "last_update": analytics_cache["last_update"]
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/prediction/monte_carlo")
async def monte_carlo_prediction(request: PredictionRequest):
    """Get Monte Carlo prediction for performance"""
    try:
        probability = simulate_score_probability(
            request.speed, 
            request.accuracy, 
            request.stamina, 
            request.simulation_count
        )
        
        return JSONResponse({
            "status": "success",
            "prediction": {
                "success_probability": round(probability, 4),
                "parameters": {
                    "speed": request.speed,
                    "accuracy": request.accuracy,
                    "stamina": request.stamina
                },
                "simulation_count": request.simulation_count
            }
        })
        
    except Exception as e:
        logger.error(f"Error in Monte Carlo prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/similarity/{athlete_id}")
async def get_similar_athletes(athlete_id: str, top_k: int = 5):
    """Find similar athletes using KNN"""
    try:
        # Find target athlete
        target_athlete = None
        for athlete in processed_athletes:
            if athlete["_id"] == athlete_id:
                target_athlete = athlete
                break
        
        if not target_athlete:
            raise HTTPException(status_code=404, detail="Athlete not found")
        
        # Train KNN if needed
        if len(processed_athletes) >= 2:
            knn_analyzer.fit(processed_athletes)
            similar = knn_analyzer.find_similar_athletes(target_athlete)
            return JSONResponse({
                "status": "success",
                "similar_athletes": similar[:top_k]
            })
        else:
            return JSONResponse({"message": "Need at least 2 athletes for similarity analysis"})
        
    except Exception as e:
        logger.error(f"Error finding similar athletes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mapreduce/results")
async def get_mapreduce_results():
    """Get MapReduce algorithm results"""
    try:
        if len(processed_athletes) < 10:
            return JSONResponse({"message": "Need at least 10 athletes for MapReduce analysis"})
        
        # Run MapReduce algorithms
        player_results = player_counter.run_job(processed_athletes)
        score_results = score_calculator.run_job(processed_athletes)
        cost_analysis = cost_calculator.calculate_player_costs(processed_athletes)
        
        return JSONResponse({
            "status": "success",
            "results": {
                "top_players": dict(list(player_results.items())[:10]),
                "position_averages": score_results,
                "cost_analysis": cost_analysis,
                "total_processed": len(processed_athletes)
            }
        })
        
    except Exception as e:
        logger.error(f"Error in MapReduce analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/streaming/stats")
async def get_streaming_stats():
    """Get streaming algorithm statistics"""
    try:
        # HyperLogLog cardinality (if Redis available)
        unique_plays = 0
        if r:
            try:
                unique_plays = r.pfcount("hll:plays")
            except:
                unique_plays = 0
        
        # Sample from MinWise
        minwise_sample = minwise.sample()
        
        # DGIM peak count
        dgim_peaks = dgim_global.query()
        
        # AMS F2 estimate
        ams_estimate = ams_speed.estimate_F2()
        
        return JSONResponse({
            "status": "success",
            "streaming_stats": {
                "unique_plays_hll": unique_plays,
                "minwise_sample_size": len(minwise_sample),
                "dgim_peaks_count": dgim_peaks,
                "ams_f2_estimate": round(ams_estimate, 2),
                "processed_records": len(processed_athletes)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting streaming stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# === Background Processing ===

async def process_athlete_record(record: Dict):
    """Process athlete record through all algorithms"""
    try:
        player_id = record.get("_id", "unknown")
        sport = record.get("sport", "unknown")
        play_type = record.get("playType", "offensive")
        
        # 1. Bloom Filter - check if play type analyzed
        play_key = f"{sport}:{play_type}"
        if not check_play_analyzed(play_key):
            mark_play_analyzed(play_key)
            logger.info(f"First time analyzing play type: {play_key}")
        
        # 2. HyperLogLog - add to unique plays (if Redis available)
        if r:
            try:
                r.pfadd("hll:plays", f"{sport}|{play_type}|{player_id}")
            except Exception as e:
                logger.warning(f"Redis HLL operation failed: {e}")
        
        # 3. Count-Min Sketch - update player frequency
        cms.add(player_id, 1)
        
        # 4. MinWise Sampling - consider performance peaks
        if record.get("performancePeak"):
            minwise.consider(json.dumps(record))
        
        # 5. Update player running moments
        if player_id not in player_moments:
            player_moments[player_id] = {
                "speed": RunningMoments(),
                "accuracy": RunningMoments()
            }
        
        perf_data = record.get("performanceData", {})
        speed = float(str(perf_data.get("speed", "0")).replace(" m/s", ""))
        accuracy = int(str(perf_data.get("accuracy", "0")).replace("%", ""))
        
        player_moments[player_id]["speed"].update(speed)
        player_moments[player_id]["accuracy"].update(accuracy)
        
        # 6. AMS F2 - update speed distribution
        speed_bin = int(speed)
        ams_speed.update(speed_bin, 1)
        
        # 7. DGIM - add performance peak bit
        dgim_global.add_bit(1 if record.get("performancePeak") else 0)
        
        # 8. Markov Chain - update state transitions
        prev_state = record.get("previousPerformanceState")
        current_state = record.get("performanceState")
        if prev_state and current_state:
            markov.observe_transition(prev_state, current_state)
        
        # 9. Broadcast update to WebSocket clients
        await broadcast_event({
            "type": "athlete_processed",
            "athlete_id": player_id,
            "player": record.get("player", "Unknown"),
            "sport": sport,
            "performance_state": current_state,
            "timestamp": record.get("timestamp")
        })
        
        logger.info(f"Processed athlete record: {player_id}")
        
    except Exception as e:
        logger.error(f"Error processing athlete record: {e}")

async def update_analytics_cache():
    """Update analytics cache with latest results"""
    try:
        if len(processed_athletes) < 5:
            return
        
        # MapReduce results
        player_results = player_counter.run_job(processed_athletes)
        score_results = score_calculator.run_job(processed_athletes)
        
        # Cost analysis
        cost_analysis = cost_calculator.calculate_player_costs(processed_athletes)
        
        # Markov predictions
        markov_stats = {
            "transition_matrix": markov.transition_prob_matrix_readable(),
            "stationary_distribution": markov.stationary_distribution(),
            "is_aperiodic": markov.is_aperiodic(),
            "mixing_time": markov.mixing_time_approx()
        }
        
        # Update cache
        analytics_cache.update({
            "last_update": datetime.now().isoformat(),
            "player_rankings": dict(list(player_results.items())[:10]),
            "position_averages": score_results,
            "cost_analysis": cost_analysis,
            "markov_predictions": markov_stats
        })
        
        logger.info("Analytics cache updated successfully")
        
    except Exception as e:
        logger.error(f"Error updating analytics cache: {e}")

async def broadcast_event(event: Dict):
    """Broadcast event to all WebSocket clients"""
    if not clients:
        return
    
    to_remove = []
    for ws in list(clients):
        try:
            await ws.send_text(json.dumps(event))
        except Exception as e:
            logger.warning(f"Failed to send to client: {e}")
            to_remove.append(ws)
    
    for ws in to_remove:
        clients.discard(ws)

async def redis_poller():
    """Poll Redis for new events"""
    if not r:
        logger.warning("Redis not available, skipping poller")
        return
    
    while True:
        try:
            item = r.brpop("events:timeline", timeout=5)
            if item:
                _, data = item
                event = json.loads(data)
                
                # Enrich event with analytics
                event["analytics"] = {
                    "processed_count": len(processed_athletes),
                    "unique_plays": r.pfcount("hll:plays") if r else 0,
                    "timestamp": datetime.now().isoformat()
                }
                
                await broadcast_event(event)
                
        except Exception as e:
            logger.error(f"Redis poller error: {e}")
            await asyncio.sleep(5)
        
        await asyncio.sleep(0.1)

# === Startup/Shutdown Events ===

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("🚀 Starting Real-Time Sports Performance Tracking System")
    
    # Start background tasks
    loop = asyncio.get_event_loop()
    loop.create_task(redis_poller())
    
    # Periodic analytics update
    async def periodic_analytics_update():
        while True:
            await asyncio.sleep(60)  # Update every minute
            await update_analytics_cache()
    
    loop.create_task(periodic_analytics_update())
    
    logger.info("✅ Application startup completed")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🔄 Shutting down application...")
    
    # Close Redis connection
    if r:
        try:
            r.close()
        except:
            pass
    
    logger.info("✅ Application shutdown completed")

# === Health Check ===

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    redis_status = "connected" if r else "disconnected"
    
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "redis_status": redis_status,
        "processed_athletes": len(processed_athletes),
        "connected_clients": len(clients)
    })

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
