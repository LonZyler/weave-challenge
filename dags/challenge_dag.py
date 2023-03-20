import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.docker_operator import DockerOperator
from docker.types import Mount

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 19),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


with DAG(
    'data-engineering-coding-challenge',
    default_args=default_args,
    schedule_interval="30 * * * *",
    catchup=False
) as dag:

    t1 = BashOperator(
        task_id='print_current_date',
        bash_command='ls /opt/airflow/apps'
    )
    t2 = DockerOperator(
        task_id='pyspark_job.xml-protein_digest_neo4j',
        image='weave/spark',
        api_version='auto',
        container_name='weave-spark',
        auto_remove=True,
        mounts=[
            Mount(
                source=f"{os.environ.get('AIRFLOW_PROJ_DIR')}/apps",
                target=f"{os.environ.get('WORKER_PROJ_DIR')}/apps",
                type="bind"
            ),
            Mount(
                source=f"{os.environ.get('AIRFLOW_PROJ_DIR')}/data",
                target=f"{os.environ.get('WORKER_PROJ_DIR')}/data",
                type="bind"
            ),
        ],
        environment={
            'NEO4J_URI': os.environ.get('NEO4J_URI'),
            'NEO4J_USER': os.environ.get('NEO4J_USER'),
            'NEO4J_PASSWORD': os.environ.get('NEO4J_PASSWORD')
        },
        command=[
            'bash',
            '-c',
            f"cd {os.environ.get('WORKER_PROJ_DIR')} && spark-submit --packages com.databricks:spark-xml_2.12:0.16.0 apps/xml-ingest.py"
        ],
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
    )
    t3 = BashOperator(
        task_id='finish_job',
        bash_command='echo "Goodbye! :D"'
    )

t1 >> t2 >> t3