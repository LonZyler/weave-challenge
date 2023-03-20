#!/bin/bash

# Build images
docker build -t weave/airflow -f docker/airflow/Dockerfile .
docker build -t weave/spark -f docker/spark/Dockerfile .