# Developer Documentation

## 🏗️ Architecture Overview

### System Components

```
Frontend (index.html)
├── Chart.js visualizations
├── WebSocket client
├── Real-time updates
└── Interactive controls

Backend (FastAPI)
├── REST API endpoints
├── WebSocket handler  
├── Algorithm orchestration
└── Redis integration

Algorithm Layer
├── Streaming Algorithms
│   ├── Bloom Filter
│   ├── Count-Min Sketch
│   ├── HyperLogLog
│   ├── DGIM
│   └── AMS-F2
├── Machine Learning
│   ├── KNN Similarity
│   ├── Markov Chains
│   ├── Monte Carlo
│   └── Random Forest
└── MapReduce Pipeline
    ├── Player Counter
    ├── Score Aggregator
    └── Performance Analyzer
```

## 📊 Algorithm Implementation Details

### Streaming Algorithms

#### Bloom Filter (`bloom_filter_module.py`)
- **Purpose**: Fast membership testing for analyzed play types
- **Space Complexity**: O(m) where m is filter size
- **Time Complexity**: O(k) where k is number of hash functions
- **Use Case**: Check if play type has been previously analyzed

```python
# Usage example
bloom = BloomFilter(1000, 5)
bloom.add("basketball:offensive")
if bloom.check("football:defensive"):
    print("Play type potentially analyzed before")
```

#### Count-Min Sketch (`count_min_sketch.py`)
- **Purpose**: Approximate frequency counting of players
- **Space Complexity**: O(w × d) where w=width, d=depth
- **Time Complexity**: O(d) for updates and queries
- **Use Case**: Track how often each player appears in data

```python
# Usage example
cms = CountMinSketch(1000, 5)
cms.update("player_1")
frequency = cms.query("player_1")
```

#### HyperLogLog (`dgim.py` - includes HLL implementation)
- **Purpose**: Cardinality estimation of unique plays
- **Space Complexity**: O(log(log(n))) 
- **Error Rate**: ~1.04/√m where m is number of buckets
- **Use Case**: Estimate unique play combinations without storing all

#### DGIM Algorithm (`dgim.py`)
- **Purpose**: Count 1s in sliding window over data stream
- **Space Complexity**: O(log²(W)) where W is window size
- **Use Case**: Count peak performance instances in time window

#### AMS-F2 (`ams_f2.py`)
- **Purpose**: Second moment estimation (variance calculation)
- **Space Complexity**: O(1) per sketch
- **Use Case**: Estimate variance of athlete speeds without full data

### Machine Learning Algorithms

#### KNN Similarity (`knn_athlete_similarity.py`)
- **Purpose**: Find athletes with similar performance profiles
- **Algorithm**: Euclidean distance with k-nearest neighbors
- **Features**: Speed, accuracy, stamina normalization
- **Use Case**: Recommend training partners or benchmarks

```python
# Usage example
knn = KNNAthleteSimilarity()
knn.add_athlete("player1", [15.5, 0.75, 80])
similar = knn.find_similar("player2", [16.0, 0.72, 85], k=3)
```

#### Markov Chains (`markov_module.py`)
- **Purpose**: Model state transitions in athlete performance
- **States**: "improving", "stable", "declining"
- **Use Case**: Predict future performance trends

```python
# Usage example
markov = MarkovPerformanceModel()
markov.add_transition("stable", "improving")
next_state = markov.predict_next("stable")
```

#### Monte Carlo Simulation (`monte_carlo_predict.py`)
- **Purpose**: Probabilistic performance prediction
- **Method**: Random sampling with performance distributions
- **Use Case**: Calculate probability of achieving target performance

### MapReduce Implementation (`mapreduce_algorithms.py`)

#### Player Counter
- **Map Phase**: Extract (player, 1) pairs
- **Reduce Phase**: Sum counts per player
- **Use Case**: Find most active players

#### Score Aggregator  
- **Map Phase**: Extract (position, score) pairs
- **Reduce Phase**: Calculate average scores by position
- **Use Case**: Position-based performance analysis

#### Performance Analyzer
- **Map Phase**: Process athlete records
- **Reduce Phase**: Join player and team data
- **Use Case**: Comprehensive performance reports

## 🔧 API Reference

### REST Endpoints

#### Health Check
```http
GET /health
```
Response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-25T10:30:00",
  "redis_status": "connected",
  "processed_athletes": 150
}
```

#### Process Athlete
```http
POST /api/athlete/process
Content-Type: application/json

{
  "player": "John Doe",
  "sport": "football", 
  "performance_data": {
    "speed": "15.5",
    "accuracy": 75,
    "stamina": 80
  }
}
```

#### Analytics Summary
```http
GET /api/analytics/summary
```
Response includes:
- Total athletes processed
- Unique play estimations (HyperLogLog)
- Peak performance counts (DGIM)
- Speed variance estimates (AMS-F2)

#### Streaming Stats
```http
GET /api/streaming/stats  
```
Returns current state of all streaming algorithms

#### Monte Carlo Prediction
```http
POST /api/prediction/monte_carlo
Content-Type: application/json

{
  "speed": 15.5,
  "accuracy": 75, 
  "stamina": 80,
  "simulation_count": 1000
}
```

#### KNN Similar Athletes
```http
GET /api/similarity/{athlete_id}?k=5
```

### WebSocket Events

#### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

#### Event Types
- `initial_data`: Sent on connection with current stats
- `athlete_processed`: New athlete data processed
- `heartbeat`: Keep-alive every 30 seconds

## 🗂️ Data Models

### Athlete Record
```python
{
  "player": str,           # Player name
  "sport": str,            # Sport type (basketball, football, etc.)
  "performance_data": {
    "speed": float,        # Speed measurement  
    "accuracy": float,     # Accuracy percentage (0-100)
    "stamina": int,        # Stamina level (0-100)
    "position": str        # Player position
  },
  "timestamp": datetime    # Processing timestamp
}
```

### Analytics Summary Response
```python
{
  "total_athletes": int,
  "unique_plays_hll": int,        # HyperLogLog estimate
  "peak_performance_dgim": int,   # DGIM count
  "speed_variance_ams": float,    # AMS-F2 estimate
  "bloom_filter_size": int,
  "countmin_total_queries": int,
  "markov_states": dict,
  "processing_time_ms": float
}
```

## 🧪 Testing

### Unit Tests
```bash
# Test individual algorithms
python -m pytest tests/test_bloom_filter.py
python -m pytest tests/test_count_min_sketch.py
python -m pytest tests/test_markov.py
```

### Integration Tests
```bash
# Test API endpoints
python -m pytest tests/test_api.py

# Test WebSocket
python -m pytest tests/test_websocket.py
```

### Performance Tests
```bash
# Benchmark algorithms
python tests/benchmark_algorithms.py
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production with Gunicorn
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app --bind 0.0.0.0:8000
```

### Docker Deployment
```bash
docker build -t sports-analytics .
docker run -p 8000:8000 sports-analytics
```

### Docker Compose (with Redis)
```bash
docker-compose up -d
```

## 📊 Performance Metrics

### Throughput Benchmarks
- **Athlete Processing**: ~1,000 records/second
- **WebSocket Messages**: ~500 messages/second  
- **API Response Time**: <50ms average
- **Memory Usage**: ~200MB for full system

### Algorithm Performance
- **Bloom Filter**: O(1) amortized lookup
- **Count-Min Sketch**: O(1) amortized update/query
- **HyperLogLog**: O(1) add, O(m) merge
- **KNN Search**: O(n log k) where n=dataset size, k=neighbors

## 🔧 Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Server Configuration  
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Algorithm Parameters
BLOOM_FILTER_SIZE=10000
BLOOM_HASH_FUNCTIONS=5
COUNTMIN_WIDTH=1000
COUNTMIN_DEPTH=5
HLL_PRECISION=12
```

### Config File (`config.py`)
```python
class Config:
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    BLOOM_SIZE = int(os.getenv('BLOOM_FILTER_SIZE', 10000))
    # ... more configuration options
```

## 🤝 Contributing

### Development Setup
1. Fork repository
2. Create feature branch: `git checkout -b feature/new-algorithm`  
3. Install dev dependencies: `pip install -r requirements-dev.txt`
4. Run tests: `pytest`
5. Submit pull request

### Code Standards
- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Maintain test coverage >90%

### Adding New Algorithms
1. Create module in appropriate directory
2. Implement base interface (if applicable)
3. Add tests in `tests/` directory
4. Update documentation
5. Register in `integrated_processor.py`

## 📞 Support

- 📧 Email: support@sports-analytics.com
- 🐛 Issues: GitHub Issues tab
- 📖 Documentation: `/docs` endpoint when server running
- 💬 Discussions: GitHub Discussions tab