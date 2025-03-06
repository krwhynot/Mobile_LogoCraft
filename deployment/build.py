"""
Build script for creating the Mobile LogoCraft executable using PyInstaller.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def clean_previous_builds():
    """Clean up previous build artifacts."""
    dirs_to_clean = ['build', 'dist']
    print("Cleaning previous build artifacts...")
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"  Removing {dir_name}...")
            try:
                shutil.rmtree(dir_path)
                print(f"  ✓ Removed {dir_name}")
            except Exception as e:
                print(f"  ✗ Error removing {dir_name}: {e}")
                return False
    
    print("Clean-up completed successfully.")
    return True

def ensure_resources():
    """Ensure all required resources exist before building."""
    print("Checking required resources...")
    
    # Check for required files
    required_files = [
        '../assets/icons/HungerRush_Icon.ico',
        'file_version_info.txt',
        'LogoCraft.spec'
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ Missing required file: {file_path}")
            return False
        print(f"  ✓ Found required file: {path.name}")
    
    # Ensure logs directory exists
    logs_dir = Path('../logs')
    if not logs_dir.exists():
        print(f"  Creating logs directory...")
        logs_dir.mkdir(exist_ok=True)
    
    print("All required resources are available.")
    return True

def build_executable():
    """Build the executable using PyInstaller."""
    print("Building executable...")
    
    # Use the Python executable from the virtual environment
    if sys.platform == 'win32':
        python_exec = os.path.join('..', '.venv', 'Scripts', 'python.exe')
    else:
        python_exec = os.path.join('..', '.venv', 'bin', 'python')
    
    if not Path(python_exec).exists():
        print(f"  ✗ Virtual environment not found at expected location: {python_exec}")
        return False
    
    # Build command
    cmd = [python_exec, '-m', 'PyInstaller', '--clean', 'LogoCraft.spec']
    
    print(f"Executing: {' '.join(cmd)}")
    try:
        process = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        # Print the output for debugging
        if process.stdout:
            print("==== Build Output ====")
            print(process.stdout)
        
        if process.stderr:
            print("==== Build Errors/Warnings ====")
            print(process.stderr)
        
        print("✓ Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: Failed to build executable")
        print(f"  Command '{' '.join(cmd)}' returned non-zero exit status {e.returncode}")
        
        if e.stdout:
            print("==== Build Output ====")
            print(e.stdout)
        
        if e.stderr:
            print("==== Build Errors ====")
            print(e.stderr)
        
        return False

def main():
    """Main build script."""
    try:
        print("=" * 60)
        print("  Mobile LogoCraft Build Process")
        print("=" * 60)
        
        # Clean previous builds
        if not clean_previous_builds():
            print("Build failed: Unable to clean previous builds.")
            sys.exit(1)
        
        # Ensure all resources exist
        if not ensure_resources():
            print("Build failed: Missing required resources.")
            sys.exit(1)
        
        # Build executable
        if not build_executable():
            print("Build failed: Error during PyInstaller execution.")
            sys.exit(1)
        
        print("=" * 60)
        print("  Build completed successfully!")
        print("  The executable can be found in the 'dist' directory.")
        print("=" * 60)
            
    except Exception as e:
        print(f"An unhandled error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
