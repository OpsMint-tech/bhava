import requests
import json

def test_business_search():
    url = "http://localhost:8000/api/v1/agent/business-search"
    payload = {"interest": "Tata Consultancy Services"}
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print("Response:")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_business_search()
