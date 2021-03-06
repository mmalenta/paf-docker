#!/bin/bash

imname=$1

docker tag ${imname}:latest docker.mpifr-bonn.mpg.de:5000/${imname}:latest
docker push docker.mpifr-bonn.mpg.de:5000/${imname}:latest

for node in {0..8}
do

    ssh pacifix${node} "docker pull docker.mpifr-bonn.mpg.de:5000/${imname}:latest; docker tag docker.mpifr-bonn.mpg.de:5000/${imname}:latest ${imname}:latest"

done
