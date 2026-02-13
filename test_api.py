import requests
import sys

try:
    response = requests.get("http://localhost:8000/api/v1/presets")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code != 200:
        sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
