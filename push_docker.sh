#!/bin/bash

imname=$1

docker tag ${imname}:latest docker.mpifr-bonn.mpg.de:5000/${imname}:latest
docker push docker.mpifr-bonn.mpg.de:5000/${imname}:latest
