#!/bin/sh
IMAGE=biviosoftware/publicprize-pg
docker rmi $IMAGE
docker build --tag=$IMAGE .
