# mapreduce_algorithms.py - MapReduce Implementation for Sports Analytics
import json
from collections import defaultdict
from typing import List, Dict, Tuple, Iterator, Any
import statistics
import time

class MapReduceEngine:
    """
    Simple MapReduce implementation for sports analytics
    """
    
    def __init__(self):
        self.intermediate_data = defaultdict(list)
        self.results = {}
    
    def emit(self, key: str, value: Any):
        """Emit key-value pair to intermediate storage"""
        self.intermediate_data[key].append(value)
    
    def clear_intermediate(self):
        """Clear intermediate data for new job"""
        self.intermediate_data.clear()
        self.results.clear()

class PlayerPerformanceCounter(MapReduceEngine):
    """
    Algorithm 1: Player Performance Counter (Basic Counting)
    Counts total games per player to find most active players
    """
    
    def map_function(self, record: Dict) -> Iterator[Tuple[str, int]]:
        """
        Map Function: Read sports performance data, emit (player_id, game_count)
        """
        player_id = record.get('_id', 'unknown')
        games_played = record.get('performanceData', {}).get('gamesPlayed', 1)
        yield (player_id, games_played)
    
    def reduce_function(self, key: str, values: List[int]) -> int:
        """
        Reduce Function: Count total games per player
        """
        return sum(values)
    
    def run_job(self, data: List[Dict]) -> Dict[str, int]:
        """Run complete MapReduce job for player counting"""
        self.clear_intermediate()
        
        # Map phase
        for record in data:
            for key, value in self.map_function(record):
                self.emit(key, value)
        
        # Reduce phase
        results = {}
        for key, values in self.intermediate_data.items():
            results[key] = self.reduce_function(key, values)
        
        # Sort by games played (descending)
        self.results = dict(sorted(results.items(), key=lambda x: x[1], reverse=True))
        return self.results
    
    def get_most_active_players(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top N most active players"""
        return list(self.results.items())[:top_n]

class AverageScoreCalculator(MapReduceEngine):
    """
    Algorithm 2: Average Score Calculator (Simple Aggregation)
    Calculates average points per player position
    """
    
    def map_function(self, record: Dict) -> Iterator[Tuple[str, int]]:
        """
        Map Function: Read game statistics, emit (player_position, points_scored)
        """
        position = record.get('position', 'unknown')
        points_scored = record.get('performanceData', {}).get('pointsScored', 0)
        yield (position, points_scored)
    
    def reduce_function(self, key: str, values: List[int]) -> Dict[str, float]:
        """
        Reduce Function: Calculate average points per player position
        """
        if not values:
            return {"average": 0.0, "count": 0, "total": 0}
        
        total_points = sum(values)
        count = len(values)
        average = total_points / count
        
        return {
            "average": round(average, 2),
            "count": count,
            "total": total_points,
            "max": max(values),
            "min": min(values)
        }
    
    def run_job(self, data: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Run complete MapReduce job for average score calculation"""
        self.clear_intermediate()
        
        # Map phase
        for record in data:
            for key, value in self.map_function(record):
                self.emit(key, value)
        
        # Reduce phase
        results = {}
        for key, values in self.intermediate_data.items():
            results[key] = self.reduce_function(key, values)
        
        # Sort by average score (descending)
        self.results = dict(sorted(results.items(), 
                                 key=lambda x: x[1]["average"], reverse=True))
        return self.results

class SportsReportGenerator(MapReduceEngine):
    """
    Algorithm 3: Sports Report Generator (Basic Join)
    Combines player statistics with team information
    """
    
    def map_function(self, record: Dict) -> Iterator[Tuple[str, Dict]]:
        """
        Map Function: Read player data and team data, emit (player_id, data_with_type)
        """
        player_id = record.get('_id', 'unknown')
        
        # Emit player performance data
        perf_data = {
            "type": "player_stats",
            "player_name": record.get('player', 'Unknown'),
            "sport": record.get('sport', 'Unknown'),
            "position": record.get('position', 'Unknown'),
            "performance_data": record.get('performanceData', {}),
            "performance_state": record.get('performanceState', 'Unknown')
        }
        yield (player_id, perf_data)
        
        # Emit team data
        team_data = {
            "type": "team_info",
            "team_id": record.get('teamDynamics', {}).get('teamId', 'unknown'),
            "team_state": record.get('teamDynamics', {}).get('teamState', 'Unknown'),
            "role_in_team": record.get('teamDynamics', {}).get('roleInTeam', 'Unknown'),
            "team_chemistry": record.get('teamDynamics', {}).get('teamChemistry', 0)
        }
        yield (player_id, team_data)
    
    def reduce_function(self, key: str, values: List[Dict]) -> Dict:
        """
        Reduce Function: Combine player statistics with team information
        """
        player_stats = None
        team_info = None
        
        for value in values:
            if value["type"] == "player_stats":
                player_stats = value
            elif value["type"] == "team_info":
                team_info = value
        
        # Create combined report
        report = {
            "player_id": key,
            "player_name": player_stats.get("player_name", "Unknown") if player_stats else "Unknown",
            "sport": player_stats.get("sport", "Unknown") if player_stats else "Unknown",
            "position": player_stats.get("position", "Unknown") if player_stats else "Unknown",
            "performance_state": player_stats.get("performance_state", "Unknown") if player_stats else "Unknown",
            "team_id": team_info.get("team_id", "Unknown") if team_info else "Unknown",
            "team_state": team_info.get("team_state", "Unknown") if team_info else "Unknown",
            "role_in_team": team_info.get("role_in_team", "Unknown") if team_info else "Unknown",
            "team_chemistry": team_info.get("team_chemistry", 0) if team_info else 0,
            "performance_metrics": player_stats.get("performance_data", {}) if player_stats else {}
        }
        
        return report
    
    def run_job(self, data: List[Dict]) -> Dict[str, Dict]:
        """Run complete MapReduce job for sports report generation"""
        self.clear_intermediate()
        
        # Map phase
        for record in data:
            for key, value in self.map_function(record):
                self.emit(key, value)
        
        # Reduce phase
        results = {}
        for key, values in self.intermediate_data.items():
            results[key] = self.reduce_function(key, values)
        
        self.results = results
        return self.results

class SportsSystemCostCalculator:
    """
    Algorithm 4: Sports System Costs
    Calculate costs of tracking different numbers of players
    """
    
    def __init__(self):
        # Cost parameters (per unit)
        self.storage_cost_per_mb = 0.001  # $0.001 per MB per month
        self.processing_cost_per_ms = 0.0001  # $0.0001 per millisecond
        self.bandwidth_cost_per_kbps = 0.01  # $0.01 per Kbps per hour
        
    def calculate_player_costs(self, data: List[Dict]) -> Dict[str, Any]:
        """Calculate costs for tracking players"""
        total_storage = 0
        total_processing = 0
        total_bandwidth = 0
        player_count = len(data)
        
        for record in data:
            resource_usage = record.get('resourceUsage', {})
            total_storage += resource_usage.get('dataStorageMB', 0)
            total_processing += resource_usage.get('processingTimeMS', 0)
            total_bandwidth += resource_usage.get('networkBandwidthKbps', 0)
        
        # Calculate costs
        storage_cost = total_storage * self.storage_cost_per_mb
        processing_cost = total_processing * self.processing_cost_per_ms
        bandwidth_cost = total_bandwidth * self.bandwidth_cost_per_kbps
        total_cost = storage_cost + processing_cost + bandwidth_cost
        
        return {
            "player_count": player_count,
            "storage_cost": round(storage_cost, 2),
            "processing_cost": round(processing_cost, 2),
            "bandwidth_cost": round(bandwidth_cost, 2),
            "total_cost": round(total_cost, 2),
            "cost_per_player": round(total_cost / max(player_count, 1), 4),
            "resource_totals": {
                "storage_mb": total_storage,
                "processing_ms": total_processing,
                "bandwidth_kbps": total_bandwidth
            }
        }
    
    def compare_league_costs(self, leagues_data: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """Compare costs across different leagues"""
        league_costs = {}
        
        for league_name, league_data in leagues_data.items():
            league_costs[league_name] = self.calculate_player_costs(league_data)
        
        return league_costs

class SportsProcessingPerformance:
    """
    Algorithm 5: Sports Processing Performance
    Test performance analysis with different cluster sizes
    """
    
    def __init__(self):
        self.performance_metrics = {}
    
    def test_cluster_performance(self, data: List[Dict], cluster_sizes: List[int]) -> Dict[str, Dict]:
        """Test performance with different cluster sizes"""
        results = {}
        
        for cluster_size in cluster_sizes:
            start_time = time.time()
            
            # Simulate processing with different cluster sizes
            chunk_size = len(data) // cluster_size
            processing_time = 0
            
            for i in range(cluster_size):
                chunk_start = i * chunk_size
                chunk_end = min((i + 1) * chunk_size, len(data))
                chunk_data = data[chunk_start:chunk_end]
                
                # Simulate processing each chunk
                chunk_processing_start = time.time()
                self._process_chunk(chunk_data)
                chunk_processing_time = time.time() - chunk_processing_start
                processing_time += chunk_processing_time
            
            total_time = time.time() - start_time
            
            results[f"cluster_size_{cluster_size}"] = {
                "cluster_size": cluster_size,
                "total_processing_time": round(total_time, 3),
                "average_chunk_time": round(processing_time / cluster_size, 3),
                "records_per_second": round(len(data) / total_time, 2),
                "efficiency": round(1.0 / (cluster_size * total_time), 4)
            }
        
        return results
    
    def _process_chunk(self, chunk_data: List[Dict]):
        """Simulate processing a data chunk"""
        # Simulate some computation
        total = 0
        for record in chunk_data:
            perf_data = record.get('performanceData', {})
            speed = float(str(perf_data.get('speed', '0')).replace(' m/s', ''))
            accuracy = int(str(perf_data.get('accuracy', '0')).replace('%', ''))
            total += speed + accuracy
        return total
    
    def compare_seasonal_performance(self, regular_season_data: List[Dict], 
                                   playoff_data: List[Dict]) -> Dict[str, Any]:
        """Compare processing performance between regular season and playoffs"""
        regular_start = time.time()
        self._process_chunk(regular_season_data)
        regular_time = time.time() - regular_start
        
        playoff_start = time.time()
        self._process_chunk(playoff_data)
        playoff_time = time.time() - playoff_start
        
        return {
            "regular_season": {
                "records": len(regular_season_data),
                "processing_time": round(regular_time, 3),
                "records_per_second": round(len(regular_season_data) / regular_time, 2)
            },
            "playoffs": {
                "records": len(playoff_data),
                "processing_time": round(playoff_time, 3),
                "records_per_second": round(len(playoff_data) / playoff_time, 2)
            },
            "performance_ratio": round(playoff_time / max(regular_time, 0.001), 2)
        }


# Example usage and testing
if __name__ == "__main__":
    # Load sample data
    try:
        with open("synthetic_sports_complete_1000.json", "r", encoding="utf-8") as f:
            sports_data = json.load(f)
        
        print("=== MapReduce Sports Analytics Demo ===\n")
        
        # Algorithm 1: Player Performance Counter
        print("1. Player Performance Counter (Most Active Players)")
        player_counter = PlayerPerformanceCounter()
        player_results = player_counter.run_job(sports_data)
        top_players = player_counter.get_most_active_players(5)
        
        print(f"Top 5 Most Active Players:")
        for i, (player_id, games) in enumerate(top_players, 1):
            player_name = next((p['player'] for p in sports_data if p['_id'] == player_id), 'Unknown')
            print(f"  {i}. {player_name}: {games} games")
        
        # Algorithm 2: Average Score Calculator
        print(f"\n2. Average Score Calculator (Points by Position)")
        score_calculator = AverageScoreCalculator()
        score_results = score_calculator.run_job(sports_data)
        
        for position, stats in score_results.items():
            print(f"  {position}: {stats['average']} avg points ({stats['count']} players)")
        
        # Algorithm 3: Sports Report Generator
        print(f"\n3. Sports Report Generator (Sample Report)")
        report_generator = SportsReportGenerator()
        reports = report_generator.run_job(sports_data[:10])  # Sample of 10 players
        
        sample_report = list(reports.values())[0]
        print(f"  Sample Player Report:")
        print(f"    Player: {sample_report['player_name']}")
        print(f"    Sport: {sample_report['sport']} ({sample_report['position']})")
        print(f"    Team: {sample_report['team_id']} (Chemistry: {sample_report['team_chemistry']})")
        print(f"    Performance State: {sample_report['performance_state']}")
        
        # Algorithm 4: System Cost Calculator
        print(f"\n4. Sports System Cost Analysis")
        cost_calculator = SportsSystemCostCalculator()
        cost_analysis = cost_calculator.calculate_player_costs(sports_data)
        
        print(f"  Total Players: {cost_analysis['player_count']}")
        print(f"  Total Cost: ${cost_analysis['total_cost']}")
        print(f"  Cost per Player: ${cost_analysis['cost_per_player']}")
        print(f"  Storage Cost: ${cost_analysis['storage_cost']}")
        print(f"  Processing Cost: ${cost_analysis['processing_cost']}")
        
        # Algorithm 5: Processing Performance
        print(f"\n5. Processing Performance Analysis")
        performance_analyzer = SportsProcessingPerformance()
        cluster_performance = performance_analyzer.test_cluster_performance(
            sports_data[:100], [1, 2, 4, 8]
        )
        
        print(f"  Cluster Performance Comparison:")
        for cluster_name, metrics in cluster_performance.items():
            print(f"    {cluster_name}: {metrics['records_per_second']} records/sec " + 
                  f"({metrics['total_processing_time']}s total)")
            
    except FileNotFoundError:
        print("Data file not found. Please generate data first using generate_markov_data.py")