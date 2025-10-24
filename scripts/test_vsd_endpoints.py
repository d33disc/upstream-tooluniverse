import json
import requests
from pathlib import Path

# Path to your candidates file
CANDIDATES_FILE = Path.home() / ".tooluniverse" / "vsd" / "catalog" / "vsd_catalog_candidates.json"

def test_first_n(n=10):
    with open(CANDIDATES_FILE, "r") as f:
        candidates = json.load(f)

    for i, cand in enumerate(candidates[:n], start=1):
        url = cand["endpoint"]
        label = cand.get("label", "unknown")
        print(f"\n[{i}] Testing: {label}")
        print(f"URL: {url}")

        try:
            r = requests.get(url, timeout=10)
            print("  Status:", r.status_code)
            if r.ok:
                # show first 200 chars of response for preview
                print("  Sample:", r.text[:200].replace("\n", " ") + "...")
        except Exception as e:
            print("  Error:", e)

if __name__ == "__main__":
    test_first_n(10)
