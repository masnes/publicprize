#!/bin/sh
x="$(docker ps -a -q)"
test "$x" && docker rm -f $x
x="$(docker images -f "dangling=true" -q)"
test "$x" && docker rmi $x
