"""Run the processing worker outside FastAPI."""

from backend.app.orchestration.worker import run_worker_loop

if __name__ == "__main__":
    run_worker_loop()
