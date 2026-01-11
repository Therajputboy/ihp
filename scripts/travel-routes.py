import requests
from datetime import datetime
import json
import time


login = {
    "userid": "rohit_marker",
    "password": "password123"
}
# Login to the system
login_response = requests.post("http://localhost:8080/v2/app/user/login", json=login)
if login_response.status_code == 200:
    print("Login successful!")
else:
    print(f"Login failed: {login_response.status_code} - {login_response.text}")
cookies = login_response.cookies
cookie = cookies.get('cookie')

for i in range(100):
    time.sleep(20)  # Sleep for 1 second between requests to avoid overwhelming the server
    url = f"http://localhost:8080/v2/app/route/marking"
    coordinate = [{
        "lat": 12.9379265 + (i * 0.01),  # Increment latitude for each route
        "lng": 77.5694534 + (i * 0.01),  # Increment longitude for each route
        "timestamp": datetime.now().timestamp() * 1000,  # Convert to milliseconds
        "id": datetime.now().strftime("%Y%m%d%H%M%S") + "~" + str(i),
        "seq": str(i) + "~" +  str(1),
    },
    {
        "lat": 12.9379265   + (i * 0.02),  # Increment latitude for each route
        "lng": 77.5694534 + (i * 0.02),  # Increment longitude for each route
        "timestamp": datetime.now().timestamp() * 1000,  # Convert to milliseconds
        "id": datetime.now().strftime("%Y%m%d%H%M%S") + "~" + str(i),
        "seq": str(i) + "~" +  str(2),
    }]
    if i%5 == 0:
        coordinate[0].update(
            {"checkpoint": {
        "lat": 12.9379265 + (i * 0.01),  # Increment latitude for each checkpoint
        "lng": 77.5694534 + (i * 0.01),  # Increment longitude for each checkpoint
        "timestamp": datetime.now().timestamp() * 1000,  # Convert to milliseconds
        "id": datetime.now().strftime("%Y%m%d%H%M%S") + "~" + str(i)
    }}
    )
    payload = {
        "routeid": "58ce10dc71aa4a8190726bc00d89522e",
        "coordinates": json.dumps(coordinate),
        "status": "active",
    }
    if i == 99:
        payload["status"] = "completed"
    response = requests.post(url, data=payload, files={}, headers={"Cookie": f"cookie={cookie}"})
    print(f"Request for route {i} sent, status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Route {i}: {response.content}")
    else:
        print(f"Failed to retrieve route {i}: {response.content}")
        break
