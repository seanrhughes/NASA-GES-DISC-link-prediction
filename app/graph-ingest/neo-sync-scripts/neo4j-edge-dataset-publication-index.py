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
graph = Graph("bolt://neo4j:7687", auth=("neo4j", "neo4j"))


cwd = os.getcwd()
pd = Path(cwd).parents[0]


# Setting up logs
# log_dir = os.path.join(cwd, "logs")
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler(
#     os.path.join("logs", "neo4j_dataset_variable_index_logs.log")
# )
# file_handler.setLevel(logging.WARNING)
# logger.addHandler(file_handler)
# log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(message)s")
# file_handler.setFormatter(log_formatter)


# Path to data folder
data_path = Path(pd).joinpath("data")
publications_file_path = Path(data_path).joinpath("ges_disc_ads_self.json")

with open(publications_file_path, "rb") as outfile:
    publication_dicts = json.load(outfile)


def create_dataset_publication(batch, data_dict, graph=graph):

    publication_id = generate_uuid5(data_dict["publicaton_doi"])
    dataset_id = generate_uuid5(data_dict["dataset_name"])

    batch.append([dataset_id, {}, publication_id])

    return batch


batch = []
for pub_doi in publication_dicts:
    # publication_id = generate_uuid5(pub_doi)
    for dataset_citation in publication_dicts[pub_doi]["Cited-References"]:
        if dataset_citation["LP Agency"] == "GES DISC":

            dataset_name = dataset_citation["Shortname"]
            #                dataset_id = generate_uuid5(dataset_name)
            #                 _ = add_references_dataset_publication(
            #                     batch=batch, dataset_id=dataset_id, publication_id=publication_id
            #                 )

            dataset_publication_edge_data = {
                "publicaton_doi": pub_doi,
                "dataset_name": dataset_name,
            }

            create_dataset_publication(
                batch=batch, data_dict=dataset_publication_edge_data, graph=graph
            )

        else:
            pass


merge_relationships(
    graph.auto(),
    batch,
    "HAS_PUBLICATION",
    start_node_key=("Dataset", "globalId"),
    end_node_key=("Publication", "globalId"),
)
merge_relationships(
    graph.auto(),
    batch,
    "OF_DATASET",
    start_node_key=("Publication", "globalId"),
    end_node_key=("Dataset", "globalId"),
)
