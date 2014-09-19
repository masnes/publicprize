#!/bin/sh
IMAGE=biviosoftware/publicprize-uwsgi
docker rmi $IMAGE
docker build --tag=$IMAGE .
