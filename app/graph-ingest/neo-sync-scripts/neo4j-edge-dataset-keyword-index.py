import os
from pathlib import Path, PurePath
import logging
from weaviate.util import generate_uuid5
import requests
from tqdm import tqdm
import json


from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, merge_nodes, merge_relationships

# Get Neo4j client
graph = Graph("bolt://localhost:7687", auth=("neo4j", "linkprediction"))


cwd = os.getcwd()
pd = Path(cwd).parents[0]


# Setting up logs
log_dir = os.path.join(cwd, "logs")
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(
    os.path.join("logs", "neo4j_dataset_keyword_index_logs.log")
)
file_handler.setLevel(logging.WARNING)
logger.addHandler(file_handler)
log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(message)s")
file_handler.setFormatter(log_formatter)


# Path to data folder
data_path = os.path.join(pd, "data")

# Path to Dataset/Collection jsons
collection_jsons_path = os.path.join(data_path, "PROD_20230409")

collections_dict = {}
collection_jsons_list = [
    os.path.join(collection_jsons_path, file)
    for file in os.listdir(collection_jsons_path)
    if file.endswith(".json")
]


def create_dataset_variable(batch, data_dict, graph=graph):

    keyword_id = data_dict["keyword_id"]
    dataset_id = data_dict["dataset_id"]

    batch.append([dataset_id, {}, keyword_id])

    return batch


batch = []
for file in collection_jsons_list:
    with open(file) as json_file:
        data = json.load(json_file)
        dataset_id = generate_uuid5(data["ShortName"])
        for item in data["ScienceKeywords"]:
            for keyword in item:
                level = keyword
                name = item[keyword].lower()
#                 keyword_id = generate_uuid5(item[keyword])
#                 data_dict = {"keyword_id": keyword_id, "dataset_id": dataset_id}
#                 create_dataset_variable(batch=batch, data_dict=data_dict, graph=graph)
                if(level=='Category'):
                    # print(level, name)
                    pass
                else:
                    keyword_id = generate_uuid5(item[keyword])
                    data_dict = {"keyword_id": keyword_id, "dataset_id": dataset_id}
                    create_dataset_variable(batch=batch, data_dict=data_dict, graph=graph)


merge_relationships(
    graph.auto(),
    batch,
    "HAS_KEYWORD",
    start_node_key=("Dataset", "globalId"),
    end_node_key=("Keyword", "globalId"),
)
merge_relationships(
    graph.auto(),
    batch,
    "OF_DATASET",
    start_node_key=("Keyword", "globalId"),
    end_node_key=("Dataset", "globalId"),
)
