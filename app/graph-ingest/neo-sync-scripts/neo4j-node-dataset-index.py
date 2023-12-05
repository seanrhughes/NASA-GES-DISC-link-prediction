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
graph = Graph("bolt://localhost:7687", auth=("neo4j", "linkprediction"))

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


def add_dataset(batch: list, dataset_data: dict, dataset_id) -> str:
    keys = ["globalId", "doi", "shortName", "longName", "daac", "abstract"]
    data = []

    """
        Add Dataset nodes to Neo4j
    """

    try:
        DOI = dataset_data["DOI"]["DOI"]
    except:
        DOI = "0000"

    try:
        DAAC = dataset_data["DAAC"]
    except:
        DAAC = "NA"

    # assert(dataset_data["ShortName"]==dataset_data['CollectionCitations'][0]['SeriesName'])

    dataset_object = {
        "globalID": dataset_id,
        "doi": DOI,
        "shortName": dataset_data["ShortName"],
        "longName": dataset_data["CollectionCitations"][0]["Title"],
        "daac": DAAC,
        "abstract": dataset_data["Abstract"].replace(
            "\n", ""
        ),  # remove newline character
    }

    current_batch = [
        dataset_object["globalID"],
        dataset_object["doi"],
        dataset_object["shortName"],
        dataset_object["longName"],
        dataset_object["daac"],
        dataset_object["abstract"],
    ]
    batch.append(current_batch)

    return dataset_id


keys = ["globalId", "doi", "shortName", "longName", "daac", "abstract"]
batch = []
for doc in collections_dict:
    dataset_dict = collections_dict[doc]
    logger.debug(
        "func: main. Iterating over collections. Collection is: {}.".format(
            dataset_dict["DOI"]
        )
    )
    dataset_id = add_dataset(batch=batch, dataset_data=dataset_dict, dataset_id=doc)

merge_nodes(graph.auto(), batch, merge_key=("Dataset", "globalId"), keys=keys)
graph.nodes.match("Dataset").count()
