"""Local development startup script."""
import subprocess
import sys


def start_local():
    """Start application for local development."""
    print("Starting NexCell AI Receptionist Backend...")
    
    # TODO: Implement local startup
    # 1. Setup database
    # 2. Start FastAPI server
    # 3. Start any background workers
    
    subprocess.run([
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
    ])


if __name__ == "__main__":
    start_local()
