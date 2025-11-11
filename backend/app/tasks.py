# backend/app/tasks.py
import subprocess
import os
from celery import Celery

# Configure Celery
# The broker is the Redis service. The backend stores results (optional).
celery_app = Celery(
    'tasks',
    broker='redis://redis:6379/0',
    backend='redis://redis:6379/0'
)

@celery_app.task
def run_scraper_task(target_url: str, content_selector: str, output_filename: str, login: bool):
    """
    A Celery task to run the scrape_website.py script as a subprocess.
    """
    command = [
        "/usr/local/bin/python", "/scripts/scrape_website.py",
        "--target-url", target_url,
        "--content-selector", content_selector,
        "--output-filename", output_filename,
    ]
    if login:
        command.append("--login")

    # We need the environment variables for the subprocess
    env = {
        "SCRAPER_USERNAME": os.getenv("SCRAPER_USERNAME", ""),
        "SCRAPER_PASSWORD": os.getenv("SCRAPER_PASSWORD", ""),
    }
    
    try:
        # Run the script as a separate process
        result = subprocess.run(command, capture_output=True, text=True, check=True, env=env)
        print("Scraper script stdout:", result.stdout)
        return {"status": "success", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        print("Scraper script stderr:", e.stderr)
        raise Exception(f"Scraper script failed: {e.stderr}")