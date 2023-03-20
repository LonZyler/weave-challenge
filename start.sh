#!/bin/bash
# envs setup
dir_path="."
export AIRFLOW_PROJ_DIR=$(realpath "$dir_path")
export WORKER_PROJ_DIR="/weave/challenge"
export AIRFLOW_UID=1000\
export NEO4J_USER='neo4j'
export NEO4J_PASSWORD='password'

# Run solution
docker-compose -f docker/docker-compose.yml up