#!/bin/sh
docker rmi biviosoftware/publicprize
docker build --tag=biviosoftware/publicprize .
