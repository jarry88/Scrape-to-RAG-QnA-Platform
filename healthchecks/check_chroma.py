# healthchecks/check_chroma.py
import sys
import urllib.request

try:
    # Use Python's built-in urllib to make the request. No external deps needed.
    with urllib.request.urlopen("http://localhost:8000/api/v1/heartbeat", timeout=5) as response:
        if response.status == 200:
            print("ChromaDB is healthy.")
            sys.exit(0)  # Exit with a success code
        else:
            print(f"ChromaDB returned status code {response.status}")
            sys.exit(1)  # Exit with a failure code
except Exception as e:
    print(f"Healthcheck failed: {e}")
    sys.exit(1)  # Exit with a failure code