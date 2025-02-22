import os
import shutil
import subprocess
import sys

def clean_previous_builds():
    """Clean up previous build artifacts"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # Use the Python executable from the virtual environment
    python_exec = os.path.join('.venv', 'Scripts', 'python.exe')
    
    # Build command
    cmd = [python_exec, '-m', 'PyInstaller', '--clean', 'LogoCraft.spec']
    
    try:
        subprocess.run(cmd, check=True)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to build executable")
        print(f"Command '{' '.join(cmd)}' returned non-zero exit status {e.returncode}")
        return False

def main():
    """Main build script"""
    try:
        # Clean previous builds
        print("Cleaning previous builds...")
        clean_previous_builds()
        
        # Build executable
        if not build_executable():
            print("Build failed! Please check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
