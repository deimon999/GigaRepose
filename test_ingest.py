import requests
import json

# Test the re-ingest endpoint
url = "http://localhost:5000/ingest-all"

print("Testing /ingest-all endpoint...")
print(f"URL: {url}")
print("-" * 50)

try:
    response = requests.post(url, headers={"Content-Type": "application/json"})
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: Cannot connect to {url}")
    print(f"   Make sure the Flask server is running on port 5000")
    print(f"   Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    print(f"   Response text: {response.text if 'response' in locals() else 'N/A'}")
