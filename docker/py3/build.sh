#!/bin/sh
docker rmi biviosoftware/py3
docker build --tag=biviosoftware/py3 .
