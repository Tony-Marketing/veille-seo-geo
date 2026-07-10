"""Run the processing scheduler outside FastAPI."""

from backend.app.orchestration.scheduler import run_scheduler_loop

if __name__ == "__main__":
    run_scheduler_loop()
