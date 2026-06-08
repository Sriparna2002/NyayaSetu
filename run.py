import subprocess
import time
import sys
import os

def main():
    # Set current directory to script location
    project_dir = os.path.dirname(os.path.abspath(__file__))
    if project_dir:
        os.chdir(project_dir)

    print("\n" + "="*65)
    print("  LegalJustice: Starting Compact Dual-Services (Django + Streamlit)")
    print("="*65 + "\n")

    # 1. Apply Django migrations automatically
    print("[1/3] Preparing Django database migrations...")
    try:
        # Run migrations using the active Python executable
        subprocess.run([sys.executable, "manage.py", "makemigrations"], check=True)
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        print("[OK] Database tables configured and migrated.\n")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Database migration failed: {e}")
        print("Attempting to run services anyway...\n")

    # 2. Start Django Web Server in the background
    print("[2/3] Launching Django Web Server on http://127.0.0.1:8000/...")
    
    # Save Django server logs to a file to keep the console clean
    log_file = open("django_server.log", "w", encoding="utf-8")
    
    try:
        django_process = subprocess.Popen(
            [sys.executable, "manage.py", "runserver"],
            stdout=log_file,
            stderr=log_file
        )
    except Exception as e:
        print(f"[ERROR] Failed to start Django server: {e}")
        log_file.close()
        sys.exit(1)

    # Allow Django a moment to boot
    time.sleep(3)
    
    # Verify if Django started successfully
    if django_process.poll() is not None:
        print("[ERROR] Django server failed to start. Check 'django_server.log' for details.")
        log_file.close()
        sys.exit(1)
        
    print("[OK] Django server is running in background. Logs: 'django_server.log'")
    
    # Open the Django Legal Web Portal homepage in the default browser
    import webbrowser
    print("Opening Django Legal Web Portal in your browser...")
    webbrowser.open("http://127.0.0.1:8000/")

    # 3. Start Streamlit Case Assistant in the foreground (blocking)
    print("\n[3/3] Launching Streamlit Case Assistant on http://localhost:8501/...")
    print("="*65)
    print(" PRESS Ctrl+C IN THIS COMMAND PROMPT TO TERMINATE BOTH SERVICES ")
    print("="*65 + "\n")

    try:
        # Run Streamlit in the foreground, using active python module call
        subprocess.run([sys.executable, "-m", "streamlit", "run", "chatpdf1.py"])
    except KeyboardInterrupt:
        print("\n\n[!] Termination requested by user...")
    finally:
        # Gracefully shutdown Django server
        print("Shutting down Django web server...")
        django_process.terminate()
        try:
            django_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            django_process.kill()
        
        log_file.close()
        print("[OK] All services stopped. Goodbye!")

if __name__ == "__main__":
    main()