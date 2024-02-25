# Tour de App - Žabanti

Webová aplikace pro soutěž Tour de App

## Lokální spuštění

### Python

#### Prerekvizity
- Python 3
- pipenv (`pip install --user pipenv`)
- pyenv (`pip install --user pyenv`)

#### Spuštění

Windows
````
flask --app app\app.py init-db
flask --app app\app.py run
````

##### Linux / macOS
###### start.sh

Pro zjednodušení práce používáme skript start.sh

standardní spuštění:
````
./start.sh
````

spuštění v dockeru:
````
./start.sh docker
````

spuštění v dockeru s portem 8069:
````
./start.sh dev
````
pipenv shell
````
./start.sh sh
````

lokální testování:
````
./start.sh test
````

naplnění databáze běžící aplikace:
````
./start.sh fill_db
````

vyprázdnění databáze běžící aplikace:
````
./start.sh fill_db
````

spuštění za použití systémových balíčků:
````
./start.sh --use-system-packages
````