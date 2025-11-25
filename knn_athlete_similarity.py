# knn_athlete_similarity.py - Near Neighbor Search for Athlete Similarity
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import pandas as pd
import json
from typing import List, Dict, Tuple, Optional

class AthleteKNNAnalyzer:
    def __init__(self, n_neighbors=5, metric='euclidean'):
        """
        Initialize KNN analyzer for athlete similarity
        
        Args:
            n_neighbors: Number of similar athletes to find
            metric: Distance metric ('euclidean', 'cosine', 'manhattan')
        """
        self.n_neighbors = n_neighbors
        self.metric = metric
        self.knn = NearestNeighbors(n_neighbors=n_neighbors, metric=metric)
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.athletes_data = None
        self.feature_matrix = None
        self.athlete_ids = []
        
    def prepare_features(self, athletes_data: List[Dict]) -> np.ndarray:
        """
        Extract and prepare features for KNN analysis
        
        Args:
            athletes_data: List of athlete records
            
        Returns:
            Normalized feature matrix
        """
        features = []
        self.athlete_ids = []
        
        for athlete in athletes_data:
            # Basic performance features
            perf_data = athlete.get('performanceData', {})
            speed = float(str(perf_data.get('speed', '0')).replace(' m/s', ''))
            accuracy = int(str(perf_data.get('accuracy', '0')).replace('%', ''))
            stamina = int(str(perf_data.get('stamina', '0')).replace('%', ''))
            
            # Training metrics
            training = athlete.get('trainingMetrics', {})
            training_hours = training.get('weeklyTrainingHours', 0)
            skill_dev_rate = training.get('skillDevelopmentRate', 0)
            fatigue = training.get('fatigueLevel', 0)
            mental_readiness = training.get('mentalReadiness', 0)
            
            # Sports similarity scores
            sports_sim = athlete.get('sportsSimilarity', {})
            perf_scores = sports_sim.get('performanceScores', [0, 0, 0, 0])
            experience = sports_sim.get('experienceLevel', 0)
            improvement_rate = sports_sim.get('improvementRate', 0)
            training_response = sports_sim.get('trainingResponse', 0)
            
            # Injury risk factors
            injury_risk = athlete.get('injuryRiskAnalysis', {})
            risk_level = injury_risk.get('currentRiskLevel', 0)
            fitness_decline = injury_risk.get('fitnessDeclineRate', 0)
            
            feature_vector = [
                speed, accuracy, stamina,
                training_hours, skill_dev_rate, fatigue, mental_readiness,
                experience, improvement_rate, training_response,
                risk_level, fitness_decline
            ] + perf_scores
            
            features.append(feature_vector)
            self.athlete_ids.append(athlete['_id'])
        
        feature_matrix = np.array(features)
        return self.scaler.fit_transform(feature_matrix)
    
    def fit(self, athletes_data: List[Dict]):
        """
        Fit KNN model with athlete data
        
        Args:
            athletes_data: List of athlete records
        """
        self.athletes_data = athletes_data
        self.feature_matrix = self.prepare_features(athletes_data)
        self.knn.fit(self.feature_matrix)
    
    def find_similar_athletes(self, target_athlete: Dict, include_distances=True) -> List[Dict]:
        """
        Find athletes similar to target athlete
        
        Args:
            target_athlete: Athlete record to find similarities for
            include_distances: Whether to include similarity distances
            
        Returns:
            List of similar athletes with similarity scores
        """
        if self.feature_matrix is None:
            raise ValueError("Model must be fitted before finding similarities")
        
        # Extract features for target athlete
        target_features = self.prepare_single_athlete_features(target_athlete)
        target_features = self.scaler.transform([target_features])
        
        # Find nearest neighbors
        distances, indices = self.knn.kneighbors(target_features)
        
        similar_athletes = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            similar_athlete = self.athletes_data[idx].copy()
            if include_distances:
                similar_athlete['similarity_distance'] = float(distance)
                similar_athlete['similarity_rank'] = i + 1
            similar_athletes.append(similar_athlete)
        
        return similar_athletes
    
    def prepare_single_athlete_features(self, athlete: Dict) -> List[float]:
        """
        Extract features for a single athlete
        
        Args:
            athlete: Single athlete record
            
        Returns:
            Feature vector
        """
        perf_data = athlete.get('performanceData', {})
        speed = float(str(perf_data.get('speed', '0')).replace(' m/s', ''))
        accuracy = int(str(perf_data.get('accuracy', '0')).replace('%', ''))
        stamina = int(str(perf_data.get('stamina', '0')).replace('%', ''))
        
        training = athlete.get('trainingMetrics', {})
        training_hours = training.get('weeklyTrainingHours', 0)
        skill_dev_rate = training.get('skillDevelopmentRate', 0)
        fatigue = training.get('fatigueLevel', 0)
        mental_readiness = training.get('mentalReadiness', 0)
        
        sports_sim = athlete.get('sportsSimilarity', {})
        perf_scores = sports_sim.get('performanceScores', [0, 0, 0, 0])
        experience = sports_sim.get('experienceLevel', 0)
        improvement_rate = sports_sim.get('improvementRate', 0)
        training_response = sports_sim.get('trainingResponse', 0)
        
        injury_risk = athlete.get('injuryRiskAnalysis', {})
        risk_level = injury_risk.get('currentRiskLevel', 0)
        fitness_decline = injury_risk.get('fitnessDeclineRate', 0)
        
        return [
            speed, accuracy, stamina,
            training_hours, skill_dev_rate, fatigue, mental_readiness,
            experience, improvement_rate, training_response,
            risk_level, fitness_decline
        ] + perf_scores
    
    def get_sport_based_similarity(self, athletes_data: List[Dict], target_sport: str) -> List[Dict]:
        """
        Find similar athletes within the same sport category
        
        Args:
            athletes_data: List of athlete records
            target_sport: Sport to filter by
            
        Returns:
            Similar athletes in same sport
        """
        # Filter by sport
        sport_athletes = [a for a in athletes_data if a.get('sport') == target_sport]
        
        if len(sport_athletes) < 2:
            return sport_athletes
        
        # Create temporary KNN for this sport
        temp_knn = AthleteKNNAnalyzer(n_neighbors=min(self.n_neighbors, len(sport_athletes)-1))
        temp_knn.fit(sport_athletes)
        
        # Find similarities within sport
        results = []
        for athlete in sport_athletes:
            similar = temp_knn.find_similar_athletes(athlete)
            results.extend(similar)
        
        return results
    
    def cluster_athletes_by_performance(self, athletes_data: List[Dict], n_clusters=5) -> Dict[str, List[Dict]]:
        """
        Group athletes by performance similarity using KNN results
        
        Args:
            athletes_data: List of athlete records
            n_clusters: Number of performance clusters
            
        Returns:
            Dictionary mapping cluster names to athlete lists
        """
        from sklearn.cluster import KMeans
        
        feature_matrix = self.prepare_features(athletes_data)
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(feature_matrix)
        
        # Group athletes by cluster
        clusters = {}
        for i, athlete in enumerate(athletes_data):
            cluster_name = f"cluster_{cluster_labels[i]}"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            athlete_copy = athlete.copy()
            athlete_copy['performance_cluster'] = cluster_name
            clusters[cluster_name].append(athlete_copy)
        
        return clusters
    
    def recommend_training_partners(self, target_athlete: Dict, athletes_data: List[Dict]) -> List[Dict]:
        """
        Recommend training partners based on complementary skills
        
        Args:
            target_athlete: Athlete to find partners for
            athletes_data: Pool of potential partners
            
        Returns:
            Recommended training partners
        """
        # Find similar athletes
        similar = self.find_similar_athletes(target_athlete)
        
        # Filter for complementary skills (different strengths, similar weaknesses)
        target_perf = target_athlete.get('performanceData', {})
        target_speed = float(str(target_perf.get('speed', '0')).replace(' m/s', ''))
        target_accuracy = int(str(target_perf.get('accuracy', '0')).replace('%', ''))
        
        recommendations = []
        for athlete in similar:
            athlete_perf = athlete.get('performanceData', {})
            athlete_speed = float(str(athlete_perf.get('speed', '0')).replace(' m/s', ''))
            athlete_accuracy = int(str(athlete_perf.get('accuracy', '0')).replace('%', ''))
            
            # Look for complementary strengths
            speed_complement = abs(athlete_speed - target_speed) > 5  # Different speed levels
            accuracy_complement = abs(athlete_accuracy - target_accuracy) > 10  # Different accuracy
            
            if speed_complement or accuracy_complement:
                athlete['recommendation_reason'] = "Complementary skills"
                recommendations.append(athlete)
        
        return recommendations[:3]  # Top 3 recommendations


# Example usage and testing
if __name__ == "__main__":
    # Load sample data
    try:
        with open("synthetic_sports_complete_1000.json", "r", encoding="utf-8") as f:
            athletes_data = json.load(f)
        
        # Initialize KNN analyzer
        knn_analyzer = AthleteKNNAnalyzer(n_neighbors=5)
        knn_analyzer.fit(athletes_data)
        
        # Find similar athletes for first athlete
        target_athlete = athletes_data[0]
        similar_athletes = knn_analyzer.find_similar_athletes(target_athlete)
        
        print(f"Similar athletes to {target_athlete['player']}:")
        for athlete in similar_athletes[:3]:
            print(f"  - {athlete['player']} (distance: {athlete.get('similarity_distance', 0):.3f})")
        
        # Performance clustering
        clusters = knn_analyzer.cluster_athletes_by_performance(athletes_data[:100])
        print(f"\nPerformance clusters created: {len(clusters)}")
        for cluster_name, cluster_athletes in clusters.items():
            print(f"  {cluster_name}: {len(cluster_athletes)} athletes")
        
        # Training partner recommendations
        partners = knn_analyzer.recommend_training_partners(target_athlete, athletes_data)
        print(f"\nTraining partner recommendations for {target_athlete['player']}:")
        for partner in partners:
            print(f"  - {partner['player']} ({partner.get('recommendation_reason', 'Similar performance')})")
            
    except FileNotFoundError:
        print("Data file not found. Please generate data first using generate_markov_data.py")