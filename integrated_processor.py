# integrated_processor.py - Complete Sports Analytics Processing Pipeline
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

# Import all our algorithms
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
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of processing an athlete record"""
    athlete_id: str
    processing_time: float
    algorithms_applied: List[str]
    predictions: Dict[str, Any]
    similarities: List[Dict]
    streaming_stats: Dict[str, Any]
    errors: List[str]

class IntegratedSportsProcessor:
    """
    Complete integrated processor that runs all algorithms
    on incoming sports performance data
    """
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.setup_algorithms()
        self.processed_count = 0
        self.processing_history = []
        self.athlete_database = []
        self.analytics_cache = {}
        
        logger.info("🚀 Integrated Sports Processor initialized")
    
    def setup_algorithms(self):
        """Initialize all algorithm instances"""
        # Streaming algorithms
        self.cms = CountMinSketch(
            width=self.config.CMS_WIDTH,
            depth=self.config.CMS_DEPTH
        )
        
        self.markov = OnlineMarkovModel(
            states=self.config.MARKOV_STATES,
            smoothing=self.config.MARKOV_SMOOTHING
        )
        
        self.knn_analyzer = AthleteKNNAnalyzer(
            n_neighbors=self.config.KNN_NEIGHBORS
        )
        
        self.minwise = MinWiseSampler(k=self.config.MINWISE_SAMPLE_SIZE)
        self.dgim = DGIM(window_size=self.config.DGIM_WINDOW_SIZE)
        self.ams_speed = AMSF2(k=self.config.AMS_K_VALUE)
        
        # MapReduce processors
        self.player_counter = PlayerPerformanceCounter()
        self.score_calculator = AverageScoreCalculator()
        self.report_generator = SportsReportGenerator()
        self.cost_calculator = SportsSystemCostCalculator()
        self.performance_analyzer = SportsProcessingPerformance()
        
        # Running statistics per player
        self.player_moments = {}
        
        logger.info("✅ All algorithms initialized successfully")
    
    async def process_athlete_stream(self, data_source: str) -> Dict[str, Any]:
        """
        Process a complete stream of athlete data from file or source
        
        Args:
            data_source: Path to JSON data file or data source identifier
            
        Returns:
            Complete processing results and analytics
        """
        start_time = datetime.now()
        
        try:
            # Load data
            if Path(data_source).exists():
                with open(data_source, 'r', encoding='utf-8') as f:
                    athletes_data = json.load(f)
                logger.info(f"📂 Loaded {len(athletes_data)} athletes from {data_source}")
            else:
                raise FileNotFoundError(f"Data source not found: {data_source}")
            
            # Process all athletes
            results = []
            for i, athlete in enumerate(athletes_data):
                result = await self.process_single_athlete(athlete)
                results.append(result)
                
                # Log progress every 100 athletes
                if (i + 1) % 100 == 0:
                    logger.info(f"📊 Processed {i + 1}/{len(athletes_data)} athletes")
            
            # Run comprehensive analytics
            analytics = await self.run_comprehensive_analytics()
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "processing_summary": {
                    "total_athletes": len(athletes_data),
                    "processing_time_seconds": processing_time,
                    "athletes_per_second": len(athletes_data) / processing_time,
                    "successful_processing": len([r for r in results if not r.errors]),
                    "failed_processing": len([r for r in results if r.errors]),
                },
                "individual_results": results,
                "comprehensive_analytics": analytics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error in stream processing: {e}")
            raise
    
    async def process_single_athlete(self, athlete_data: Dict) -> ProcessingResult:
        """
        Process a single athlete through all algorithms
        
        Args:
            athlete_data: Dictionary containing athlete information
            
        Returns:
            ProcessingResult with all analysis results
        """
        start_time = datetime.now()
        errors = []
        algorithms_applied = []
        predictions = {}
        similarities = []
        streaming_stats = {}
        
        athlete_id = athlete_data.get('_id', f'athlete_{self.processed_count}')
        
        try:
            # Add to database
            self.athlete_database.append(athlete_data)
            
            # 1. Bloom Filter Processing
            try:
                sport = athlete_data.get('sport', 'unknown')
                play_type = athlete_data.get('playType', 'offensive')
                play_key = f"{sport}:{play_type}"
                
                if not check_play_analyzed(play_key):
                    mark_play_analyzed(play_key)
                    logger.debug(f"🔍 First analysis of play type: {play_key}")
                
                algorithms_applied.append("bloom_filter")
            except Exception as e:
                errors.append(f"Bloom Filter error: {e}")
            
            # 2. Count-Min Sketch
            try:
                self.cms.add(athlete_id, 1)
                freq_estimate = self.cms.estimate(athlete_id)
                streaming_stats['cms_frequency'] = freq_estimate
                algorithms_applied.append("count_min_sketch")
            except Exception as e:
                errors.append(f"Count-Min Sketch error: {e}")
            
            # 3. MinWise Sampling
            try:
                if athlete_data.get('performancePeak'):
                    self.minwise.consider(json.dumps(athlete_data))
                streaming_stats['minwise_sample_size'] = len(self.minwise.sample())
                algorithms_applied.append("minwise_sampling")
            except Exception as e:
                errors.append(f"MinWise Sampling error: {e}")
            
            # 4. Running Moments
            try:
                if athlete_id not in self.player_moments:
                    self.player_moments[athlete_id] = {
                        "speed": RunningMoments(),
                        "accuracy": RunningMoments()
                    }
                
                perf_data = athlete_data.get('performanceData', {})
                speed = float(str(perf_data.get('speed', '0')).replace(' m/s', ''))
                accuracy = int(str(perf_data.get('accuracy', '0')).replace('%', ''))
                
                self.player_moments[athlete_id]["speed"].update(speed)
                self.player_moments[athlete_id]["accuracy"].update(accuracy)
                
                streaming_stats['running_moments'] = {
                    'speed_mean': self.player_moments[athlete_id]["speed"].get_mean(),
                    'speed_variance': self.player_moments[athlete_id]["speed"].get_variance(),
                    'accuracy_mean': self.player_moments[athlete_id]["accuracy"].get_mean(),
                    'accuracy_variance': self.player_moments[athlete_id]["accuracy"].get_variance()
                }
                algorithms_applied.append("running_moments")
            except Exception as e:
                errors.append(f"Running Moments error: {e}")
            
            # 5. AMS F2 Estimation
            try:
                speed_bin = int(speed) if 'speed' in locals() else 0
                self.ams_speed.update(speed_bin, 1)
                f2_estimate = self.ams_speed.estimate_F2()
                streaming_stats['ams_f2_estimate'] = f2_estimate
                algorithms_applied.append("ams_f2")
            except Exception as e:
                errors.append(f"AMS F2 error: {e}")
            
            # 6. DGIM Algorithm
            try:
                peak_bit = 1 if athlete_data.get('performancePeak') else 0
                self.dgim.add_bit(peak_bit)
                peak_count = self.dgim.query()
                streaming_stats['dgim_peak_count'] = peak_count
                algorithms_applied.append("dgim")
            except Exception as e:
                errors.append(f"DGIM error: {e}")
            
            # 7. Markov Chain Processing
            try:
                prev_state = athlete_data.get('previousPerformanceState')
                current_state = athlete_data.get('performanceState')
                
                if prev_state and current_state:
                    self.markov.observe_transition(prev_state, current_state)
                
                # Get predictions
                if current_state:
                    next_step_pred = self.markov.predict_distribution(current_state, steps=1)
                    predictions['markov_next_state'] = next_step_pred
                
                algorithms_applied.append("markov_chain")
            except Exception as e:
                errors.append(f"Markov Chain error: {e}")
            
            # 8. Monte Carlo Prediction
            try:
                if 'speed' in locals() and 'accuracy' in locals():
                    stamina = int(str(perf_data.get('stamina', '0')).replace('%', ''))
                    success_prob = simulate_score_probability(speed, accuracy, stamina, n=1000)
                    predictions['monte_carlo_success'] = success_prob
                
                algorithms_applied.append("monte_carlo")
            except Exception as e:
                errors.append(f"Monte Carlo error: {e}")
            
            # 9. KNN Similarity (if enough data)
            try:
                if len(self.athlete_database) >= 5:
                    self.knn_analyzer.fit(self.athlete_database)
                    similar_athletes = self.knn_analyzer.find_similar_athletes(
                        athlete_data, include_distances=True
                    )
                    similarities = similar_athletes[:3]  # Top 3 similar
                    
                algorithms_applied.append("knn_similarity")
            except Exception as e:
                errors.append(f"KNN Similarity error: {e}")
            
            self.processed_count += 1
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = ProcessingResult(
                athlete_id=athlete_id,
                processing_time=processing_time,
                algorithms_applied=algorithms_applied,
                predictions=predictions,
                similarities=similarities,
                streaming_stats=streaming_stats,
                errors=errors
            )
            
            self.processing_history.append(result)
            return result
            
        except Exception as e:
            logger.error(f"❌ Critical error processing athlete {athlete_id}: {e}")
            return ProcessingResult(
                athlete_id=athlete_id,
                processing_time=(datetime.now() - start_time).total_seconds(),
                algorithms_applied=algorithms_applied,
                predictions=predictions,
                similarities=similarities,
                streaming_stats=streaming_stats,
                errors=[f"Critical error: {e}"] + errors
            )
    
    async def run_comprehensive_analytics(self) -> Dict[str, Any]:
        """
        Run comprehensive analytics across all processed data
        
        Returns:
            Complete analytics results
        """
        logger.info("📊 Running comprehensive analytics...")
        
        analytics = {
            "timestamp": datetime.now().isoformat(),
            "total_processed": len(self.athlete_database)
        }
        
        try:
            # MapReduce Analytics
            if len(self.athlete_database) >= 10:
                analytics["mapreduce"] = {
                    "top_players": dict(list(
                        self.player_counter.run_job(self.athlete_database).items()
                    )[:10]),
                    "position_averages": self.score_calculator.run_job(self.athlete_database),
                    "cost_analysis": self.cost_calculator.calculate_player_costs(self.athlete_database)
                }
            
            # Markov Chain Analytics
            analytics["markov_analysis"] = {
                "transition_matrix": self.markov.transition_prob_matrix_readable(),
                "stationary_distribution": self.markov.stationary_distribution(),
                "is_aperiodic": self.markov.is_aperiodic(),
                "is_irreducible": self.markov.is_irreducible(),
                "mixing_time": self.markov.mixing_time_approx()
            }
            
            # Streaming Statistics Summary
            analytics["streaming_summary"] = {
                "minwise_sample_size": len(self.minwise.sample()),
                "ams_f2_final": self.ams_speed.estimate_F2(),
                "dgim_current_peaks": self.dgim.query(),
                "total_unique_athletes": len(self.player_moments)
            }
            
            # Performance Clustering (if enough data)
            if len(self.athlete_database) >= 20:
                clusters = self.knn_analyzer.cluster_athletes_by_performance(
                    self.athlete_database, n_clusters=5
                )
                analytics["performance_clusters"] = {
                    name: len(athletes) for name, athletes in clusters.items()
                }
            
            # Processing Performance Metrics
            processing_times = [r.processing_time for r in self.processing_history]
            if processing_times:
                analytics["processing_performance"] = {
                    "average_processing_time": sum(processing_times) / len(processing_times),
                    "min_processing_time": min(processing_times),
                    "max_processing_time": max(processing_times),
                    "total_algorithms_applied": sum(
                        len(r.algorithms_applied) for r in self.processing_history
                    )
                }
            
            # Error Analysis
            all_errors = []
            for result in self.processing_history:
                all_errors.extend(result.errors)
            
            analytics["error_analysis"] = {
                "total_errors": len(all_errors),
                "error_rate": len(all_errors) / max(len(self.processing_history), 1),
                "common_errors": self._analyze_common_errors(all_errors)
            }
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive analytics: {e}")
            analytics["analytics_error"] = str(e)
        
        # Cache analytics
        self.analytics_cache = analytics
        return analytics
    
    def _analyze_common_errors(self, errors: List[str]) -> Dict[str, int]:
        """Analyze and count common error types"""
        error_counts = {}
        for error in errors:
            # Extract error type (first part before colon)
            error_type = error.split(':')[0] if ':' in error else error
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        # Return top 5 most common errors
        return dict(sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5])
    
    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get current real-time statistics"""
        return {
            "processed_count": self.processed_count,
            "algorithms_running": len([
                'cms', 'markov', 'knn_analyzer', 'minwise', 'dgim', 'ams_speed'
            ]),
            "current_minwise_samples": len(self.minwise.sample()),
            "current_dgim_peaks": self.dgim.query(),
            "current_ams_estimate": self.ams_speed.estimate_F2(),
            "unique_athletes": len(self.player_moments),
            "markov_states_observed": len(self.markov.states),
            "last_update": datetime.now().isoformat()
        }
    
    def export_results(self, output_path: str) -> bool:
        """
        Export all processing results to file
        
        Args:
            output_path: Path to save results
            
        Returns:
            Success status
        """
        try:
            export_data = {
                "processing_summary": {
                    "total_processed": self.processed_count,
                    "export_timestamp": datetime.now().isoformat(),
                    "algorithms_used": [
                        "bloom_filter", "count_min_sketch", "minwise_sampling",
                        "running_moments", "ams_f2", "dgim", "markov_chain",
                        "monte_carlo", "knn_similarity"
                    ]
                },
                "processing_history": [
                    {
                        "athlete_id": r.athlete_id,
                        "processing_time": r.processing_time,
                        "algorithms_applied": r.algorithms_applied,
                        "predictions": r.predictions,
                        "similarities": len(r.similarities),
                        "streaming_stats": r.streaming_stats,
                        "error_count": len(r.errors)
                    }
                    for r in self.processing_history
                ],
                "final_analytics": self.analytics_cache
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Results exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error exporting results: {e}")
            return False

# Example usage and demonstration
async def main():
    """Demonstrate the complete integrated processor"""
    print("🚀 Starting Integrated Sports Performance Processor Demo")
    
    # Initialize processor
    processor = IntegratedSportsProcessor()
    
    # Check if data files exist
    data_files = [
        "synthetic_sports_complete_1000.json",
        "synthetic_sports_training_500.json",
        "synthetic_sports_test_200.json"
    ]
    
    available_file = None
    for file_path in data_files:
        if Path(file_path).exists():
            available_file = file_path
            break
    
    if not available_file:
        print("❌ No data files found. Please run generate_markov_data.py first.")
        return
    
    # Process the data stream
    print(f"📊 Processing data from {available_file}")
    results = await processor.process_athlete_stream(available_file)
    
    # Display summary
    summary = results["processing_summary"]
    print(f"\n✅ Processing Complete!")
    print(f"   📈 Athletes Processed: {summary['total_athletes']}")
    print(f"   ⏱️  Total Time: {summary['processing_time_seconds']:.2f}s")
    print(f"   🚀 Processing Rate: {summary['athletes_per_second']:.2f} athletes/sec")
    print(f"   ✅ Successful: {summary['successful_processing']}")
    print(f"   ❌ Failed: {summary['failed_processing']}")
    
    # Display analytics highlights
    analytics = results["comprehensive_analytics"]
    print(f"\n📊 Analytics Highlights:")
    
    if "markov_analysis" in analytics:
        markov = analytics["markov_analysis"]
        print(f"   🔗 Markov Chain: {len(markov.get('transition_matrix', {}))} states observed")
        print(f"   🎯 Is Aperiodic: {markov.get('is_aperiodic', False)}")
        print(f"   🔄 Mixing Time: {markov.get('mixing_time', 'N/A')} steps")
    
    if "streaming_summary" in analytics:
        streaming = analytics["streaming_summary"]
        print(f"   📊 MinWise Samples: {streaming.get('minwise_sample_size', 0)}")
        print(f"   📈 AMS-F2 Estimate: {streaming.get('ams_f2_final', 0):.2f}")
        print(f"   ⚡ DGIM Peaks: {streaming.get('dgim_current_peaks', 0)}")
    
    if "performance_clusters" in analytics:
        clusters = analytics["performance_clusters"]
        print(f"   🎯 Performance Clusters: {len(clusters)} clusters created")
    
    # Export results
    output_file = f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    if processor.export_results(output_file):
        print(f"   💾 Results exported to: {output_file}")
    
    print(f"\n🎉 Demo completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())