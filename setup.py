#!/usr/bin/env python3
"""
DataMender Setup Script
Setup and installation script for DataMender.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("Error: DataMender requires Python 3.8 or higher")
        print(f"Current version: {sys.version}")
        return False
    return True


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def create_executable_script():
    """Create executable script for DataMender."""
    script_content = f'''#!/usr/bin/env python3
"""DataMender executable script"""
import sys
import os

# Add DataMender directory to path
datamender_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, datamender_dir)

from datamender_cli import main

if __name__ == "__main__":
    sys.exit(main())
'''
    
    script_path = Path("datamender")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    # Make executable on Unix systems
    if os.name != 'nt':
        os.chmod(script_path, 0o755)
    
    print(f"✓ Created executable script: {script_path}")
    return True


def run_tests():
    """Run basic tests to verify installation."""
    print("Running basic tests...")
    
    try:
        # Test imports
        sys.path.insert(0, "src")
        from src.data_processor import DataProcessor
        from src.data_cleaner import DataCleaner
        
        # Test basic functionality
        processor = DataProcessor()
        cleaner = DataCleaner()
        
        print("✓ Core modules imported successfully")
        print("✓ Basic functionality test passed")
        return True
    except Exception as e:
        print(f"Error in tests: {e}")
        return False


def create_sample_data():
    """Create sample data files for testing."""
    print("Creating sample data files...")
    
    # Create samples directory
    samples_dir = Path("samples")
    samples_dir.mkdir(exist_ok=True)
    
    # Sample CSV data
    csv_content = '''Name,Email,Age,City,Date Joined
John Doe,john@example.com,25,New York,2023-01-15
jane smith,JANE@EXAMPLE.COM,30, Chicago ,01/20/2023
John Doe,john@example.com,25,New York,2023-01-15
Bob Johnson,,35,Los Angeles,2023/02/10
Alice Brown,alice@example.com,28,   Seattle,15-03-2023
'''
    
    with open(samples_dir / "sample_messy.csv", "w") as f:
        f.write(csv_content)
    
    # Sample JSON data
    json_content = '''[
    {"name": "John Doe", "email": "john@example.com", "age": 25, "city": "New York", "date_joined": "2023-01-15"},
    {"name": "jane smith", "email": "JANE@EXAMPLE.COM", "age": 30, "city": " Chicago ", "date_joined": "01/20/2023"},
    {"name": "John Doe", "email": "john@example.com", "age": 25, "city": "New York", "date_joined": "2023-01-15"},
    {"name": "Bob Johnson", "email": "", "age": 35, "city": "Los Angeles", "date_joined": "2023/02/10"},
    {"name": "Alice Brown", "email": "alice@example.com", "age": 28, "city": "   Seattle", "date_joined": "15-03-2023"}
]'''
    
    with open(samples_dir / "sample_messy.json", "w") as f:
        f.write(json_content)
    
    print(f"✓ Sample data files created in {samples_dir}/")
    return True


def main():
    """Main setup function."""
    print("DataMender Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Install dependencies
    if not install_dependencies():
        return 1
    
    # Create executable script
    if not create_executable_script():
        return 1
    
    # Run tests
    if not run_tests():
        print("Warning: Tests failed, but installation may still work")
    
    # Create sample data
    create_sample_data()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nUsage:")
    print("  CLI: python datamender_cli.py input.csv -o output.csv --remove-duplicates")
    print("  GUI: python datamender_cli.py --gui")
    print("  Executable: ./datamender input.csv -o output.csv --remove-duplicates")
    print("\nSample files created in samples/ directory for testing.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())