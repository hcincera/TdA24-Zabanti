#!/bin/python
import random, lorem, uuid, requests
from urllib.parse import urljoin

server_url = "http://localhost:8069"

s = requests.Session()
full_url = urljoin(server_url, "/api/lecturers")
response = s.get(full_url)
print("total lecturers:", len(response.json()))
for lecturer in response.json():
    print("deleting:", lecturer["uuid"], end=" ")
    response = s.delete(urljoin(server_url, "/api/lecturers/"+lecturer["uuid"]))
    print(response.status_code)

