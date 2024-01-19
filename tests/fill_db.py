#!/bin/python
import random, lorem, uuid, requests
from urllib.parse import urljoin

server_url = "http://localhost:8069"

def get_random_lecturer():
    l = {}
    l["title_before"] = random.choice(["Mgr.", "Ing.", "Bc.", "prof.", "doc.", None])
    l["first_name"] = random.choice(["Jiří", "Jan", "Petr", "Josef", "Pavel", "Martin", "Tomáš", "Jaroslav"])
    l["middle_name"] = random.choice(["Jiří", "Jan", "Petr", "Josef", "Pavel", "Martin", "Tomáš", "Jaroslav", None])
    l["last_name"] = random.choice(["Novák", "Svoboda", "Novotný", "Dvořák", "Černý", "Procházka", "Kučera", "Němec"])
    l["title_after"] = random.choice(["Ph.D.", "Dis.", None])
    l["picture_url"] = random.choice([None, "../static/jpg/p" + str(random.randint(1,5)) + ".jpg"])
    l["location"] = random.choice([None, "Praha", "Brno", "Plzeň", "Ostrava", "Pardubice", "Liberec", "Zlín"])
    l["claim"] = random.choice([None, lorem.sentence()])
    l["bio"] = random.choice([None, "<b>"+lorem.sentence()+"</b>"])
    l["tags"] = [(lambda x: {"name": x})(x) for x in random.sample(["Marketing", "Sales", "Human Resources", "Teacher", "Programmer", "Sysadmin"], random.randint(0, 5))]
    l["price_per_hour"] = random.randint(0, 1000)
    l["contact"] = {
        "telephone_numbers" : [(lambda: "+420 " + str(random.randint(111_111_111, 999_999_999)))() for x in range(random.randint(1,5))],
        "emails" : [(lambda: str(uuid.uuid4()) + "@example.com")() for x in range(random.randint(1,5))]
    }
    return l


s = requests.Session()
for i in range(20):
    l = get_random_lecturer()
    full_url = urljoin(server_url, "/api/lecturers")
    response = s.post(full_url, json=l)
    print("uuid: ", response.json()["uuid"])
