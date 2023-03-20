import glob
import json
import logging
import os
import sys

from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes
from pyspark.conf import SparkConf
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
from pyspark.sql.types import (ArrayType, MapType, Row, StringType,
                               StructField, StructType)


def main():
    # --------------------------------
    # Assets
    # --------------------------------
    neo4j_cfg = {
        'uri': os.environ.get('NEO4J_URI'),
        'user': os.environ.get('NEO4J_USER'),
        "password": os.environ.get('NEO4J_PASSWORD')
    }

    graph = Graph(
        neo4j_cfg['uri'],
        auth=(neo4j_cfg['user'], neo4j_cfg['password'])
    )
    # --------------------------------
    # Dataframes
    # --------------------------------
    # Storage dictionaries
    # the dataframes dictionary is used to store the created dataframes
    # along the process
    dataframes = {
        'extracted': {},
        'transformed': {}
    }

    # --------------------------------
    # ETL main pipeline
    # --------------------------------
    # start Spark application and get Spark session
    spark = SparkSession.builder.appName("weave_challenge-job").getOrCreate()
    spark, sc = init_spark()
    
    # Extraction phase
    print("Extracting data from source")
    dataframes['extracted'] = extract_data(spark)
    print("Done!")

    # Transform phase
    print("Loading Protein data into neo4j")
    load_data(dataframes['extracted'], graph)
    print("Done!")

    # log the success and terminate Spark application
    print('weave_challenge-job has finished')
    spark.stop()
    return None


def extract_data(spark):
    """
    Extracts protein datasets from XML files in the 'data' directory using
    Apache Spark.

    Args:
        spark (pyspark.sql.SparkSession): An instance of SparkSession.

    Returns:
        (dict): A dictionary containing protein datasets extracted from XML
        files, where the keys are protein names and the values are Spark
        DataFrames containing the extracted data.
    """
    protein_datasets = glob.glob('data/*.xml')
    xml_file_path = 'data/Q9Y261.xml'
    extracted_datasets = {}
    for dataset_path in protein_datasets:
        protein_name = dataset_path.split('/')[-1].replace('.xml', '')
        extracted_datasets[protein_name] = (
            spark
            .read
            .format("xml")
            .option("rowTag", "entry")
            .load(xml_file_path)
        )

    return extracted_datasets


def load_data(extracted_dataframes, graph):
    """
    Loads protein data from Spark DataFrames into a graph database.

    Args:
        extracted_dataframes (dict): A dictionary containing protein datasets as
            Spark DataFrames, where the keys are protein IDs and the values are 
            Spark DataFrames containing the extracted data.

        graph (py2neo.Graph): A graph database object to which the protein data
            will be loaded.

    Returns:
        None
    """
    for protein_id, df in extracted_dataframes.items():
        _create_nodes(protein_id, df, graph)


# ==============================================================================
# sub-transform functions
# ==============================================================================
def _create_nodes(protein_id, df, graph):
    """
    Creates nodes in a graph database for the protein data in a Spark DataFrame.

    Args:
        protein_id (str): A string representing the ID of the protein.
        df (pyspark.sql.DataFrame): A Spark DataFrame containing the
            protein data.
        graph (py2neo.Graph): A graph database object to which the nodes will 
            be added.

    Returns:
        None

    Note:
        This function is intended to be used internally by the load_data
        function.
    """
    # Insert the nested data into the database
    root_node = Node('Protein', **{'id': protein_id})
    graph.create(root_node)
    for column in df.columns:
        rows = []
        rows = _get_field_data(df, column)
        for row in rows:
            _insert_node_with_children(graph, column, row, root_node)
            del row


def _insert_node_with_children(graph, node_name, row, parent_node=None):
    """
    Inserts a node with its children into a graph database.

    Args:
        graph (py2neo.Graph): A graph database object to which the nodes will
            be added.
        node_name (str): A string representing the name of the node to be
            created.
        row : A dictionary or list containing the data for the node and its
            children.
        parent_node (py2neo.Node): An optional parent node to which the new
            node will be connected.

    Returns:
        The newly created node.

    Note:
        This function is intended to be used internally by the load_data
        function.
    """
    # Flatten the nested data structure
    flattened_data = {}
    if isinstance(row, (dict, list)):
        for key, value in row.items():
            if isinstance(value, (dict, list)):
                continue
            flattened_data[key] = value
    else:
        flattened_data = {'name': row}
    if flattened_data == {}:
        flattened_data = {'name': node_name}

    # Create a new node with the flattened data
    node = Node(node_name.capitalize(), **flattened_data)

    # If a parent node is provided, create a relationship from the parent to the new node
    if parent_node:
        relationship = Relationship(parent_node, f"HAS_{node_name.upper()}", node)
        graph.create(relationship)

    # If the data dictionary contains nested dictionaries or arrays,
    # recursively insert the child nodes under the new node
    if isinstance(row, (dict, list)):
        for key, value in row.items():
            if not isinstance(value, (dict, list)):
                continue
            child_rows = value if isinstance(value, list) else [value]
            for child_row in child_rows:
                _insert_node_with_children(graph, key, child_row, node)

    # Return the new node
    return graph.create(node)


def _get_field_data(df, field):
    """
    Extracts the data from a field in a PySpark DataFrame.

    Args:
        df (pyspark.sql.DataFrame): A PySpark DataFrame containing the data to
            be extracted.
        field (str): Represents the name of the field to be extracted.

    Returns:
        (list): A list of dictionaries representing the extracted data.

    Note:
        This function is intended to be used internally by the
            _create_nodes function.
    """
    field_type = type(df.schema[field].dataType)
    if (field_type == ArrayType) or (field_type == StructType):
        if field_type == ArrayType:
            df = (
                df
                .select((explode(field).alias(field)))
            )
            array_field_type = type(df.schema[field].dataType)
            if array_field_type == StructType:
                df = (
                    df
                    .select(col(f'{field}.*'))
                )
        if field_type == StructType:
            df = (
                df
                .select(col(field))
            )
    else:
        df = df.select(col(field))
    return (
            df
            .toJSON()
            .map(json.loads)
            .collect()
    )


# ==============================================================================
# utils functions
# ==============================================================================
def init_spark():
    """
    Initializes a SparkSession and SparkContext.

    Returns:
        A tuple containing the SparkSession and SparkContext objects.
    """
    spark = SparkSession.builder\
        .appName("sarasa_10")\
        .getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("WARN")
    return (spark, sc)


# entry point for PySpark ETL application
if __name__ == "__main__":
    main()
