#!/bin/bash


for i in {0..8} ; do
ssh pacifix${i} df -h /dev/shm
done
