#!/bin/bash

for i in $(seq 1 100)
do
   echo "Starting generation $i"
   poetry run python reinforcement_learning.py
   echo "Finished generation $i"
done