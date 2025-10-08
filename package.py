#!/usr/bin/env python3
"""
DataMender Packaging Script
Creates distribution packages for DataMender.
"""

import os
import sys
import subprocess
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def create_package_info():
    """Create package information."""
    version = "1.0.0"
    build_date = datetime.now().strftime("%Y-%m-%d")
    
    return {
        "name": "DataMender",
        "version": version,
        "description": "Cross-platform data cleaning tool for CSV and JSON files",
        "build_date": build_date,
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}",
        "author": "DataMender Team",
        "license": "MIT"
    }


def create_standalone_package():
    """Create standalone package (no PyInstaller needed)."""
    info = create_package_info()
    
    print(f"Creating standalone package for {info['name']} v{info['version']}...")
    
    # Create package directory
    package_name = f"DataMender-v{info['version']}-standalone"
    package_dir = Path(package_name)
    
    if package_dir.exists():
        shutil.rmtree(package_dir)
    
    package_dir.mkdir()
    
    # Copy source files
    print("Copying source files...")
    
    # Main files
    files_to_copy = [
        "README.md",
        "ROADMAP.md",
        "requirements.txt",
        "setup.py",
        "datamender_cli.py",
        "datamender"  # executable script
    ]
    
    for file in files_to_copy:
        if Path(file).exists():
            shutil.copy2(file, package_dir)
    
    # Copy src directory
    shutil.copytree("src", package_dir / "src")
    
    # Copy samples directory
    shutil.copytree("samples", package_dir / "samples")
    
    # Create package info file
    info_content = f"""DataMender Package Information
====================================

Name: {info['name']}
Version: {info['version']}
Description: {info['description']}
Build Date: {info['build_date']}
Python Version: {info['python_version']}+
Author: {info['author']}
License: {info['license']}

Installation:
1. Extract this package
2. Run: python setup.py
3. Use: python datamender_cli.py --help

System Requirements:
- Python {info['python_version']} or higher
- pandas (installed automatically)
- numpy (installed automatically)
- tkinter (included with Python)

Files Included:
- datamender_cli.py: Command-line interface
- src/: Core DataMender modules
- samples/: Sample data files for testing
- README.md: Documentation
- requirements.txt: Python dependencies
- setup.py: Installation script

Quick Start:
python datamender_cli.py samples/sample_messy.csv -o output.csv --remove-duplicates --trim-whitespace
"""
    
    with open(package_dir / "PACKAGE_INFO.txt", "w") as f:
        f.write(info_content)
    
    # Create run scripts for different platforms
    
    # Windows batch file
    windows_script = """@echo off
REM DataMender Windows Launcher
python datamender_cli.py %*
"""
    with open(package_dir / "datamender.bat", "w") as f:
        f.write(windows_script)
    
    # Linux/Mac shell script
    unix_script = """#!/bin/bash
# DataMender Unix Launcher
python3 datamender_cli.py "$@"
"""
    with open(package_dir / "datamender.sh", "w") as f:
        f.write(unix_script)
    
    # Make Unix script executable
    os.chmod(package_dir / "datamender.sh", 0o755)
    
    print(f"✓ Package created in {package_dir}/")
    return package_dir


def create_zip_archive(package_dir):
    """Create ZIP archive of the package."""
    zip_name = f"{package_dir.name}.zip"
    
    print(f"Creating ZIP archive: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in package_dir.rglob('*'):
            if file_path.is_file():
                # Calculate relative path
                relative_path = file_path.relative_to(package_dir.parent)
                zipf.write(file_path, relative_path)
    
    print(f"✓ ZIP archive created: {zip_name}")
    return zip_name


def create_pyinstaller_executable():
    """Create executable using PyInstaller (optional)."""
    try:
        import PyInstaller
        print("PyInstaller found, creating executable...")
        
        # PyInstaller command
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name", "datamender",
            "--add-data", "src:src",
            "datamender_cli.py"
        ]
        
        subprocess.run(cmd, check=True)
        print("✓ Executable created with PyInstaller")
        return True
        
    except ImportError:
        print("PyInstaller not available, skipping executable creation")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        return False


def main():
    """Main packaging function."""
    print("DataMender Packaging Tool")
    print("=" * 50)
    
    # Create standalone package
    package_dir = create_standalone_package()
    
    # Create ZIP archive
    zip_file = create_zip_archive(package_dir)
    
    # Try to create executable
    create_pyinstaller_executable()
    
    # Summary
    print("\n" + "=" * 50)
    print("Packaging completed successfully!")
    print(f"\nDeliverable files:")
    print(f"  📦 {zip_file} - Standalone package")
    print(f"  📁 {package_dir}/ - Extracted package")
    
    if Path("dist/datamender").exists() or Path("dist/datamender.exe").exists():
        print(f"  🚀 dist/ - Executable files")
    
    print(f"\nPackage is ready for distribution!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())