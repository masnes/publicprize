#!/bin/sh
IMAGE=biviosoftware/publicprize-py3
docker rmi $IMAGE
docker build --tag=$IMAGE .
