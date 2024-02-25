#!/bin/sh

if [ "$1" = "docker" ] ; then
	docker build . -t tda-flask
	docker run -it -p 8080:80 -v ${PWD}:/app tda-flask
	exit
fi

if [ "$1" = "dev" ] ; then
	docker build . -t tda-flask
	docker run -it -p 8069:80 -v ${PWD}:/app tda-flask
	exit
fi

if [ -f /.dockerenv ] ; then
	export PORT=80
	python3 -m flask --app app/app.py init-db
	python3 -m flask --app app/app.py run --host=0.0.0.0 --port=$PORT
	
else
	export PORT=8069
fi

if [ "$1" = "sh" ] ; then
	pipenv install
	pipenv shell
	exit
fi

if [ "$1" = "test" ] ; then
	pipenv install
	pipenv run pytest
	exit
fi

if [ "$1" = "fill_db" ] ; then
	pipenv install
	pipenv run python tests/fill_db.py
	exit
fi

if [ "$1" = "clean_db" ] ; then
	pipenv install
	pipenv run python tests/clean_db.py
	exit
fi

if [ "$1" = "--use-system-packages" ] ; then
	python3 -m flask --app app/app.py init-db
	python3 -m flask --app app/app.py run --host=0.0.0.0 --port=$PORT
	exit
fi

pipenv install
pipenv run ./start.sh --use-system-packages