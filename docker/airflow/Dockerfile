FROM apache/airflow:2.5.2
USER root

RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;

ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

USER airflow

ADD docker/airflow/requirements.txt . 
RUN pip install -r requirements.txt 