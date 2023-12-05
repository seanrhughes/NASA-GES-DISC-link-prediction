import os
from pathlib import Path, PurePath
import logging
from weaviate.util import generate_uuid5
import requests
from tqdm import tqdm
import json


from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, merge_nodes, merge_relationships

# Get the NEO4J_AUTH from the environment variables
neo4j_auth = os.getenv("NEO4J_AUTH")

# NEO4J_AUTH is in the format "username/password", so we split it
username, password = neo4j_auth.split("/")

graph = Graph("bolt://neo4j:7687", auth=(username, password))


cwd = os.getcwd()
pd = Path(cwd).parents[0]


# Setting up logs
log_dir = os.path.join(cwd, "logs")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
    os.path.join("logs", "neo4j_dataset_variable_index_logs.log")
)
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)
log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(message)s")
file_handler.setFormatter(log_formatter)


# Path to data folder
data_path = os.path.join(pd, "data")

# Giovanni variables
giovanni_path = os.path.join(data_path, "aesir_dump.json")

with open(giovanni_path) as json_file:
    giovanni_list = json.load(json_file)["response"]["docs"]


def create_dataset_variable(batch, data_dict, graph=graph):

    variable_id = generate_uuid5(data_dict["dataFieldSdsName"])
    dataset_id = generate_uuid5(data_dict["dataProductId"])

    batch.append([dataset_id, {}, variable_id])

    return batch


batch = []
for gio_variable in giovanni_list:
    collection_name = gio_variable["dataProductShortName"]
    dataset_variable_edge_data = {}
    dataset_variable_edge_data["dataFieldSdsName"] = gio_variable["dataFieldSdsName"]
    dataset_variable_edge_data["dataProductId"] = gio_variable["dataProductId"].split(
        "."
    )[0]

    create_dataset_variable(
        batch=batch, data_dict=dataset_variable_edge_data, graph=graph
    )

#     variable_id = generate_uuid5(dataset_variable_edge_data["dataFieldSdsName"])
#     dataset_id = generate_uuid5(dataset_variable_edge_data["dataProductId"])

merge_relationships(
    graph.auto(),
    batch,
    "HAS_VARIABLE",
    start_node_key=("Dataset", "globalId"),
    end_node_key=("Variable", "globalId"),
)
merge_relationships(
    graph.auto(),
    batch,
    "OF_DATASET",
    start_node_key=("Variable", "globalId"),
    end_node_key=("Dataset", "globalId"),
)
