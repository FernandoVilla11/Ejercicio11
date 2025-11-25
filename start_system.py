# start_system.py - System Startup Script
"""
Real-Time Sports Performance Tracking System Startup Script

This script provides an easy way to start and test the complete system.
"""

import asyncio
import sys
import os
import subprocess
import time
import json
from pathlib import Path
from typing import Optional

def print_banner():
    """Print system banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║    🏆 Real-Time Sports Performance Tracking System 🏆            ║
    ║                                                                  ║
    ║    Advanced Analytics • Machine Learning • Real-Time Processing ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'redis', 'numpy', 'pandas', 
        'scikit-learn', 'faker', 'websockets', 'plotly'
    ]
    
    missing = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("📦 Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing, "--quiet"
            ])
            print("✅ All packages installed successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages. Please install manually:")
            print(f"   pip install {' '.join(missing)}")
            return False
    else:
        print("✅ All dependencies satisfied!")
    
    return True

def check_redis():
    """Check if Redis is available"""
    print("🔍 Checking Redis connection...")
    
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        print("📋 Redis installation options:")
        print("   1. Windows: Use Docker - docker run -d -p 6379:6379 redis:alpine")
        print("   2. Linux: sudo apt-get install redis-server")
        print("   3. macOS: brew install redis")
        return False

def check_data_files():
    """Check if data files exist, generate if needed"""
    print("🔍 Checking data files...")
    
    data_files = [
        "synthetic_sports_complete_1000.json",
        "synthetic_sports_training_500.json", 
        "synthetic_sports_test_200.json"
    ]
    
    missing_files = [f for f in data_files if not Path(f).exists()]
    
    if missing_files:
        print(f"📊 Generating missing data files: {', '.join(missing_files)}")
        try:
            subprocess.check_call([sys.executable, "generate_markov_data.jl"])
            print("✅ Data files generated successfully!")
        except subprocess.CalledProcessError:
            print("❌ Failed to generate data files")
            return False
    else:
        print("✅ All data files present!")
    
    return True

def run_system_tests():
    """Run basic system tests"""
    print("🧪 Running system tests...")
    
    try:
        # Test integrated processor
        from integrated_processor import IntegratedSportsProcessor
        
        processor = IntegratedSportsProcessor()
        real_time_stats = processor.get_real_time_stats()
        
        print(f"   ✅ Integrated Processor: {real_time_stats['algorithms_running']} algorithms ready")
        
        # Test individual algorithms
        from bloom_filter_module import bf
        from count_min_sketch import CountMinSketch
        from markov_module import OnlineMarkovModel
        
        # Quick algorithm tests
        cms = CountMinSketch()
        cms.add("test", 1)
        estimate = cms.estimate("test")
        
        markov = OnlineMarkovModel(["state1", "state2"])
        markov.observe_transition("state1", "state2")
        
        print("   ✅ Core algorithms functional")
        print("✅ All system tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def start_server(port: int = 8000, host: str = "0.0.0.0"):
    """Start the FastAPI server"""
    print(f"🚀 Starting server at http://{host}:{port}")
    print("📊 Dashboard will be available at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    print("\n🔄 Press Ctrl+C to stop the server")
    
    try:
        import uvicorn
        uvicorn.run("app:app", host=host, port=port, reload=True, log_level="info")
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Server error: {e}")

def run_demo():
    """Run the integrated processor demo"""
    print("🎬 Running system demonstration...")
    
    try:
        from integrated_processor import main
        asyncio.run(main())
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def show_menu():
    """Show interactive menu"""
    menu = """
    🎯 What would you like to do?
    
    1. 🚀 Start Web Server (Full System)
    2. 🎬 Run Processing Demo
    3. 🧪 Run System Tests Only
    4. 📊 Generate Sample Data
    5. 📖 Show System Information
    6. 🚪 Exit
    
    """
    print(menu)
    
    while True:
        try:
            choice = input("Enter your choice (1-6): ").strip()
            return int(choice)
        except ValueError:
            print("❌ Please enter a valid number (1-6)")

def show_system_info():
    """Show system information"""
    print("\n📖 System Information:")
    print("=" * 50)
    
    # File structure
    files = [
        ("app.py", "Main FastAPI application"),
        ("integrated_processor.py", "Complete processing pipeline"),
        ("config.py", "System configuration"),
        ("requirements.txt", "Python dependencies"),
        ("index.html", "Web dashboard"),
        ("README.md", "Complete documentation")
    ]
    
    print("📁 Core Files:")
    for filename, description in files:
        status = "✅" if Path(filename).exists() else "❌"
        print(f"   {status} {filename}: {description}")
    
    # Algorithms
    algorithms = [
        "Bloom Filter", "Count-Min Sketch", "HyperLogLog", "DGIM", "AMS-F2",
        "MinWise Sampling", "KNN Similarity", "Markov Chains", "Monte Carlo",
        "MapReduce Processing", "Random Forest", "Online Moments"
    ]
    
    print(f"\n🤖 Implemented Algorithms ({len(algorithms)}):")
    for i, algo in enumerate(algorithms, 1):
        print(f"   {i:2d}. {algo}")
    
    # APIs
    print("\n🌐 Available APIs:")
    apis = [
        "GET  /                      - Dashboard",
        "GET  /health               - System health",
        "POST /api/athlete/process  - Process athlete",
        "GET  /api/analytics/summary - Analytics results",
        "POST /api/prediction/monte_carlo - Monte Carlo prediction",
        "GET  /api/similarity/{id}  - Find similar athletes",
        "GET  /api/mapreduce/results - MapReduce analytics",
        "GET  /api/streaming/stats  - Streaming statistics",
        "WS   /ws                   - Real-time updates"
    ]
    
    for api in apis:
        print(f"   {api}")
    
    print("\n📊 Data Processing:")
    print("   • Real-time streaming algorithms")
    print("   • Machine learning predictions") 
    print("   • MapReduce distributed processing")
    print("   • WebSocket live updates")
    print("   • Interactive dashboard")

def main():
    """Main startup function"""
    print_banner()
    
    # System checks
    checks_passed = True
    
    if not check_dependencies():
        checks_passed = False
    
    if not check_redis():
        print("⚠️  System will run without Redis (some features limited)")
    
    if not check_data_files():
        checks_passed = False
    
    if not checks_passed:
        print("\n❌ System checks failed. Please resolve issues above.")
        return
    
    if not run_system_tests():
        print("\n⚠️  Some system tests failed, but continuing...")
    
    # Interactive menu
    while True:
        choice = show_menu()
        
        if choice == 1:
            start_server()
            break
        elif choice == 2:
            run_demo()
        elif choice == 3:
            run_system_tests()
        elif choice == 4:
            subprocess.run([sys.executable, "generate_markov_data.jl"])
        elif choice == 5:
            show_system_info()
        elif choice == 6:
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice, please try again.")
        
        input("\n⏸️  Press Enter to continue...")

if __name__ == "__main__":
    main()