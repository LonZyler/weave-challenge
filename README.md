# Weave Challenge
The challenge for this project is to create a data pipeline that will ingest a UniProt XML file (data/Q9Y261.xml) and store the data in a Neo4j graph database.

## Task
The XML file Q9Y261.xml located in the data directory contains information about a protein. The task is to create a data pipeline that will ingest the XML file and store as much information as possible in a Neo4j graph database.

### Project's output sample
![image](https://user-images.githubusercontent.com/20272456/226253892-8c3ecebb-f22b-4c17-abef-b14a1885ea1b.png)


## Getting Started

To use this project, you will need to have Docker and Docker Compose installed on your system. Once you have installed Docker and Docker Compose, follow the instructions below to get started with the project.

1.  Clone the repository to your local machine.
    
2.  Navigate to the project directory.
    
3.  Run the following command to build the Docker images for Airflow and Spark:
    
    `sh build_images.sh` 
    
4.  Start the Docker containers by running the following command:
    
    `sh start.sh` 
    
5.  Once the containers are up and running, open a browser and navigate to [http://localhost:8080](http://localhost:8080/) to access the Airflow web UI.
    -  The login credentials for Airflow are username: "airflow" and the password is "airflow".
    
6.  In the Airflow UI, enable the "challenge_dag" DAG to run the XML data ingestion and validation process.
    
7.  The XML data files that need to be ingested and validated can be placed in the "data" directory.
    
8.  Once the XML data has been processed successfully, you can view the graph representation of the data in Neo4j by going to http://localhost:7474/ in your browser. 
    -  The login credentials for Neo4j are username: "neo4j" and the password is "password".   

## Project Tree
```
.
├── README.md
├── apps
│   └── xml-ingest.py
├── assets
│   └── xmlSchema.xml
├── build_images.sh
├── dags
│   └── challenge_dag.py
├── data
│   └── Q9Y261.xml
├── docker
│   ├── airflow
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── docker-compose.yml
│   ├── spark
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── start-spark.sh
│   └── spark-docker-compose.yml
└── start.sh
``` 

## Prerequisites

You will need to have Docker and Docker Compose installed on your system to use this project.

## Built With

-   [Apache Spark](https://spark.apache.org/) - Open source big data processing framework.
-   [Apache Airflow](https://airflow.apache.org/) - Open source workflow management platform.
-   [Docker](https://www.docker.com/) - Containerization platform.
-   [Neo4j](https://neo4j.com/) - Graph database platform.
