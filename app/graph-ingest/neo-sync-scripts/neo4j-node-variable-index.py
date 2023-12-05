import os
from pathlib import Path, PurePath
import logging
from weaviate.util import generate_uuid5
import requests
from tqdm import tqdm
import json


from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, merge_nodes, create_relationships

# Get Neo4j client
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "neo4j"))

cwd = os.getcwd()
pd = Path(cwd).parents[0]


# Setting up logs
log_dir = os.path.join(cwd, "logs")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(os.path.join("logs", "neo4j_dataset_index_logs.log"))
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


def add_variable(batch: list, variable_data: dict, variable_id) -> str:
    keys = ["globalId", "shortName", "longName", "variableMeasurement"]
    data = []

    """
        Add Variable nodes to Neo4j
    """

    # assert(dataset_data["ShortName"]==dataset_data['CollectionCitations'][0]['SeriesName'])

    dataset_object = {
        "globalId": variable_id,
        "shortName": variable_data["dataFieldSdsName"],
        "longName": variable_data["dataFieldLongName"],
        "variableMeasurement": variable_data["dataFieldMeasurement"],
    }

    current_batch = [
        dataset_object["globalId"],
        dataset_object["shortName"],
        dataset_object["longName"],
        dataset_object["variableMeasurement"],
    ]
    batch.append(current_batch)

    return variable_id


keys = ["globalId", "shortName", "longName", "variableMeasurement"]
batch = []
for variable_dict in giovanni_list:
    # print(batch.shape)
    # variable_dict = giovanni_list[var]
    variable_name = variable_dict["dataFieldSdsName"]
    variable_id = generate_uuid5(variable_name)
    logger.debug(
        "func: main. Iterating over variables. Variable is: {}.".format(variable_name)
    )
    dataset_id = add_variable(
        batch=batch, variable_data=variable_dict, variable_id=variable_id
    )

merge_nodes(graph.auto(), batch, merge_key=("Variable", "globalId"), keys=keys)
graph.nodes.match("Variable").count()
