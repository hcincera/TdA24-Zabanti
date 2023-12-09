#!/bin/sh

docker build . -t tda-flask
docker run -it -p 8080:80 -v ${PWD}:/app tda-flask
