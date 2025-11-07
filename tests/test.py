import requests
import json

API_KEY = ""
ZONE_ID = ""
DOMAIN = ""

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

payload = [
    {
        "name": f"test.{DOMAIN}",
        "type": "TXT",
        "content": "\"https://ejemplo.com\"",
        "ttl": 3600
    }
]

url = f"https://api.hosting.ionos.com/dns/v1/zones/{ZONE_ID}/records"
resp = requests.post(url, headers=headers, json=payload)

print("Status:", resp.status_code)
print(json.dumps(resp.json(), indent=2))
