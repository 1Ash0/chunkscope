import requests
import json

def test_preview_api():
    BASE_URL = "http://127.0.0.1:8000"

    # Test Paragraph Chunking
    payload = {
        "text": "Paragraph 1.\n\nParagraph 2.\n\nParagraph 3.",
        "config": {
            "method": "paragraph",
            "chunk_size": 1000,
            "overlap": 0
        }
    }
    
    print("\nTesting Paragraph Chunking (size=1000)...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/preview/chunking", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Chunks: {len(data['chunks'])}")
        for i, chunk in enumerate(data['chunks']):
            print(f"  Chunk {i+1}: {chunk['text'][:50]}...")
    except Exception as e:
        print(f"Error: {e}")

    # Test Fixed Chunking
    payload["config"]["method"] = "fixed"
    payload["config"]["chunk_size"] = 10
    
    print("\nTesting Fixed Example...")
    try:
        response = requests.post(f"{BASE_URL}/api/v1/preview/chunking", json=payload)
        response.raise_for_status()
        data = response.json()
        print(f"Status: {response.status_code}")
        print(f"Chunks: {len(data['chunks'])}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_preview_api()
