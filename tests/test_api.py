# tests/test_api.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_scrape_endpoint():
    print("--- Testing /scrape endpoint ---")
    url = f"{BASE_URL}/scrape"
    payload = {
      "target_url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
      "content_selector": "#mw-content-text .mw-parser-output",
      "output_filename": "python_wiki_from_test.txt",
      "login": False
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print("✅ /scrape call successful!")
        print("Response:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"❌ /scrape call failed: {e}")
        print("Response Body:", e.response.text if e.response else "No response")


def test_ingest_endpoint():
    print("\n--- Testing /ingest endpoint ---")
    url = f"{BASE_URL}/ingest"
    # Make sure you have a sample PDF file at this path
    file_path = "tests/sample.pdf"
    
    try:
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, "application/pdf")}
            response = requests.post(url, files=files)
            response.raise_for_status()
            print("✅ /ingest call successful!")
            print("Response:", response.json())
    except FileNotFoundError:
        print(f"❌ Test file not found at {file_path}. Please create a sample.pdf.")
    except requests.exceptions.RequestException as e:
        print(f"❌ /ingest call failed: {e}")
        print("Response Body:", e.response.text if e.response else "No response")

if __name__ == "__main__":
    # IMPORTANT: You need a sample.pdf file in the 'tests' directory for this to work.
    # Download any simple PDF and save it as 'tests/sample.pdf'.
    import os
    if not os.path.exists("tests/sample.pdf"):
        print("🚨 Please add a file named 'sample.pdf' to the 'tests' directory before running.")
    else:
        test_ingest_endpoint()
    
    # test_scrape_endpoint() # You can uncomment this to test the scrape endpoint too