# Configuration settings
import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    
    # Algorithm parameters
    BLOOM_FILTER_CAPACITY = int(os.getenv("BLOOM_FILTER_CAPACITY", 10000))
    BLOOM_FILTER_ERROR_RATE = float(os.getenv("BLOOM_FILTER_ERROR_RATE", 0.001))
    
    CMS_WIDTH = int(os.getenv("CMS_WIDTH", 2000))
    CMS_DEPTH = int(os.getenv("CMS_DEPTH", 5))
    
    KNN_NEIGHBORS = int(os.getenv("KNN_NEIGHBORS", 5))
    
    MINWISE_SAMPLE_SIZE = int(os.getenv("MINWISE_SAMPLE_SIZE", 200))
    
    DGIM_WINDOW_SIZE = int(os.getenv("DGIM_WINDOW_SIZE", 300))  # 5 minutes in seconds
    
    AMS_K_VALUE = int(os.getenv("AMS_K_VALUE", 10))
    
    # Markov chain settings
    MARKOV_STATES = [
        "peak", "good", "average", "declining", "injured"
    ]
    MARKOV_SMOOTHING = float(os.getenv("MARKOV_SMOOTHING", 1e-3))
    
    # Performance settings
    MAX_WEBSOCKET_CLIENTS = int(os.getenv("MAX_WEBSOCKET_CLIENTS", 100))
    ANALYTICS_UPDATE_INTERVAL = int(os.getenv("ANALYTICS_UPDATE_INTERVAL", 60))  # seconds
    
    # Data generation settings
    SPORTS = ["football", "basketball", "soccer", "tennis", "hockey"]
    POSITIONS = ["forward", "midfielder", "defender", "goalkeeper", "guard", "center"]
    
    @classmethod
    def get_redis_config(cls) -> Dict[str, Any]:
        """Get Redis configuration as dictionary"""
        config = {
            "host": cls.REDIS_HOST,
            "port": cls.REDIS_PORT,
            "db": cls.REDIS_DB,
            "decode_responses": True
        }
        
        if cls.REDIS_PASSWORD:
            config["password"] = cls.REDIS_PASSWORD
            
        return config
    
    @classmethod
    def get_server_config(cls) -> Dict[str, Any]:
        """Get server configuration as dictionary"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": cls.DEBUG,
            "log_level": "debug" if cls.DEBUG else "info"
        }
    
    @classmethod
    def validate_config(cls) -> bool:
        """Validate configuration settings"""
        try:
            assert cls.PORT > 0 and cls.PORT < 65536, "Invalid port number"
            assert cls.REDIS_PORT > 0 and cls.REDIS_PORT < 65536, "Invalid Redis port"
            assert cls.BLOOM_FILTER_ERROR_RATE > 0 and cls.BLOOM_FILTER_ERROR_RATE < 1, "Invalid Bloom filter error rate"
            assert cls.KNN_NEIGHBORS > 0, "KNN neighbors must be positive"
            assert cls.MINWISE_SAMPLE_SIZE > 0, "MinWise sample size must be positive"
            return True
        except AssertionError as e:
            print(f"Configuration validation error: {e}")
            return False

# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    REDIS_HOST = "localhost"

class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    REDIS_HOST = os.getenv("REDIS_HOST", "redis-server")

class TestingConfig(Config):
    """Testing environment configuration"""
    DEBUG = True
    REDIS_DB = 1  # Use separate DB for testing

# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    elif env == "testing":
        return TestingConfig()
    else:
        return DevelopmentConfig()