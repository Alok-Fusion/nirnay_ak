import subprocess
import sys
import os
import time

def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root_dir, "backend")
    frontend_dir = os.path.join(root_dir, "frontend")

    print("=" * 60)
    print("           NIRNAY DECISION INTELLIGENCE PLATFORM            ")
    print("=" * 60)
    print("Starting FastAPI Backend (Port 8000)...")
    
    # Launch Backend
    backend_process = subprocess.Popen(
        [sys.executable, "run.py"],
        cwd=backend_dir,
        shell=True
    )
    
    # Wait for backend to initialize database tables
    time.sleep(2)

    print("\nStarting Vite React Frontend (Port 5173)...")
    # Launch Frontend
    frontend_process = subprocess.Popen(
        "npm run dev",
        cwd=frontend_dir,
        shell=True
    )

    print("\nNIRNAY Platform is booting up!")
    print("  -> Backend API: http://localhost:8000")
    print("  -> Backend API Docs: http://localhost:8000/docs")
    print("  -> Frontend UI: http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers.")
    print("=" * 60)

    try:
        while True:
            # Check if any process terminated unexpectedly
            if backend_process.poll() is not None:
                print("Backend server stopped unexpectedly.")
                break
            if frontend_process.poll() is not None:
                print("Frontend server stopped unexpectedly.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping NIRNAY server processes...")
    finally:
        # Kill both processes on exit
        backend_process.terminate()
        frontend_process.terminate()
        print("Servers stopped. Thank you for using NIRNAY.")

if __name__ == "__main__":
    main()
