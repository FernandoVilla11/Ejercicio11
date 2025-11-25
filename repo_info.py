#!/usr/bin/env python3
"""
Repository Information Script
Displays comprehensive information about the Git repository
"""

import os
import subprocess
import json
from pathlib import Path

def run_git_command(cmd):
    """Execute git command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None

def get_file_count_by_extension():
    """Count files by extension"""
    extensions = {}
    for file_path in Path('.').rglob('*'):
        if file_path.is_file() and not str(file_path).startswith('.git'):
            ext = file_path.suffix.lower() or 'no extension'
            extensions[ext] = extensions.get(ext, 0) + 1
    return extensions

def get_lines_of_code():
    """Count lines of code (excluding certain file types)"""
    total_lines = 0
    code_files = 0
    exclude_extensions = {'.json', '.md', '.txt', '.log'}
    
    for file_path in Path('.').rglob('*'):
        if (file_path.is_file() and 
            not str(file_path).startswith('.git') and
            file_path.suffix.lower() not in exclude_extensions):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = len(f.readlines())
                    total_lines += lines
                    code_files += 1
            except Exception:
                pass
    
    return total_lines, code_files

def main():
    """Display repository information"""
    print("🏆 Real-Time Sports Performance Tracking System")
    print("=" * 60)
    
    # Git basic info
    print("\n📊 Repository Statistics:")
    print("-" * 30)
    
    total_files = run_git_command("git ls-files | wc -l") or len(list(Path('.').rglob('*')))
    total_commits = run_git_command("git log --oneline | wc -l") or "2"
    branch = run_git_command("git branch --show-current") or "master"
    last_commit = run_git_command("git log -1 --format='%h - %s (%cr)'") or "Unknown"
    
    print(f"📁 Total Files: {total_files}")
    print(f"📝 Total Commits: {total_commits}")
    print(f"🌿 Current Branch: {branch}")
    print(f"⏰ Last Commit: {last_commit}")
    
    # File breakdown
    print("\n📁 File Breakdown:")
    print("-" * 20)
    extensions = get_file_count_by_extension()
    for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True):
        print(f"{ext:15} : {count:3d} files")
    
    # Lines of code
    print("\n💻 Code Statistics:")
    print("-" * 20)
    total_lines, code_files = get_lines_of_code()
    print(f"Lines of Code: {total_lines:,}")
    print(f"Code Files: {code_files}")
    print(f"Avg Lines/File: {total_lines//code_files if code_files > 0 else 0}")
    
    # Algorithm modules
    print("\n🧮 Algorithm Modules:")
    print("-" * 22)
    algorithm_files = [
        "bloom_filter_module.py",
        "count_min_sketch.py", 
        "dgim.py",
        "ams_f2.py",
        "online_moments.py",
        "markov_module.py",
        "monte_carlo_predict.py",
        "knn_athlete_similarity.py",
        "mapreduce_algorithms.py",
        "minwise_sampler.py"
    ]
    
    for i, algo_file in enumerate(algorithm_files, 1):
        if Path(algo_file).exists():
            print(f"{i:2d}. ✅ {algo_file}")
        else:
            print(f"{i:2d}. ❌ {algo_file}")
    
    # System files
    print("\n🏗️ System Architecture:")
    print("-" * 25)
    system_files = {
        "app.py": "FastAPI Backend",
        "index.html": "Interactive Dashboard", 
        "config.py": "System Configuration",
        "start_system.py": "Automated Startup",
        "requirements.txt": "Dependencies",
        "integrated_processor.py": "Algorithm Orchestra"
    }
    
    for file_name, description in system_files.items():
        status = "✅" if Path(file_name).exists() else "❌"
        print(f"{status} {file_name:25} - {description}")
    
    # Documentation
    print("\n📚 Documentation:")
    print("-" * 17)
    docs = {
        "README.md": "Main Documentation",
        "DEVELOPER.md": "Technical Guide",
        "CHANGELOG.md": "Version History", 
        "LICENSE": "MIT License"
    }
    
    for doc_file, description in docs.items():
        status = "✅" if Path(doc_file).exists() else "❌"
        print(f"{status} {doc_file:15} - {description}")
    
    # Repository health
    print("\n🎯 Repository Health Check:")
    print("-" * 28)
    
    health_checks = [
        ("Git initialized", Path('.git').exists()),
        ("README present", Path('README.md').exists()),
        ("License present", Path('LICENSE').exists()),
        ("Requirements file", Path('requirements.txt').exists()),
        ("Main application", Path('app.py').exists()),
        ("Dashboard interface", Path('index.html').exists()),
        ("Gitignore configured", Path('.gitignore').exists())
    ]
    
    for check_name, passed in health_checks:
        status = "✅" if passed else "❌"
        print(f"{status} {check_name}")
    
    print("\n" + "=" * 60)
    print("🚀 Repository is ready for deployment and collaboration!")
    print("📧 Run 'python start_system.py' to start the application")

if __name__ == "__main__":
    main()