import os
from pathlib import Path, PurePath
import logging
from weaviate.util import generate_uuid5
import requests
from tqdm import tqdm
import json


from py2neo import Graph, Node, Relationship
from py2neo.bulk import create_nodes, merge_nodes, create_relationships

# Get the NEO4J_AUTH from the environment variables
neo4j_auth = os.getenv("NEO4J_AUTH")

# NEO4J_AUTH is in the format "username/password", so we split it

graph = Graph("bolt://localhost:7687", auth=("neo4j", "linkprediction"))


cwd = os.getcwd()
pd = Path(cwd).parents[0]


# Setting up logs
# log_dir = os.path.join(cwd, "logs")
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler(os.path.join("logs", "neo4j_dataset_index_logs.log"))
# file_handler.setLevel(logging.WARNING)
# logger.addHandler(file_handler)
# log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(message)s")
# file_handler.setFormatter(log_formatter)


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


for file in collection_jsons_list:
    with open(file) as json_file:
        data = json.load(json_file)
        globalID = generate_uuid5(data["ShortName"])
        collections_dict[globalID] = data


def add_keyword(batch: list, keyword_data: dict, keyword_id) -> str:
    keys = ["globalId", "name", "level"]
    data = []

    name = keyword_data["name"].lower()
    level = keyword_data["level"]

    keyword_object = {
        "globalId": keyword_id,
        "name": name,
        "level": level,
    }

    current_batch = [
        keyword_object["globalId"],
        keyword_object["name"],
        keyword_object["level"],
    ]
    batch.append(current_batch)

    return keyword_id


aggregate_keywords = {}
for file in collection_jsons_list:
    with open(file) as json_file:
        data = json.load(json_file)
        for item in data["ScienceKeywords"]:
            for keyword in item:
                level = keyword
                name = item[keyword].lower()
                keyword_id = generate_uuid5(item[keyword])
                aggregate_keywords[keyword_id] = {
                    "globalId": keyword_id,
                    "name": name,
                    "level": level,
                }


keys = ["globalId", "name", "level"]
batch = []

for keyword in aggregate_keywords:
    keyword_id = add_keyword(
        batch=batch, keyword_data=aggregate_keywords[keyword], keyword_id=keyword
    )


merge_nodes(graph.auto(), batch, merge_key=("Keyword", "globalId"), keys=keys)
graph.nodes.match("Keyword").count()
