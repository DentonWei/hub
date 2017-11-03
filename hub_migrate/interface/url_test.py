import json
import requests


data = {"id": 14}
r = requests.post("http://localhost:8000/hub_migrate/index.html/copy/", data=json.dumps(data))
print(json.loads(r.text))
