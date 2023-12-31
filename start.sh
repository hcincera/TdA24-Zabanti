#!/bin/sh

if [ "$1" == "docker" ]; then
	docker build . -t tda-flask
	docker run -it -p 8080:80 -v ${PWD}:/app tda-flask
	exit
fi

if [ -f /.dockerenv ]; then
    export PORT=80
else
    export PORT=8080
fi

python3 -m flask --app app/app.py init-db
python3 -m flask --app app/app.py run --host=0.0.0.0 --port=$PORT
