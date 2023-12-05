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
# log_dir = os.path.join(cwd, "logs")
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# file_handler = logging.FileHandler(os.path.join("logs", "neo4j_dataset_index_logs.log"))
# file_handler.setLevel(logging.WARNING)
# logger.addHandler(file_handler)
# log_formatter = logging.Formatter("%(asctime)s|%(name)s|%(message)s")
# file_handler.setFormatter(log_formatter)


# Path to data folder
data_path = Path(pd).joinpath("data")


# Publications path
publications_file_path = Path(data_path).joinpath("ges_disc_ads_self.json")

# with open(publications_file_path, "rb") as f:
#     publication_dicts = pickle.load(f)

with open(publications_file_path, "rb") as outfile:
    publication_dicts = json.load(outfile)


def add_publication(batch: list, publication_data: dict, publication_id) -> str:
    keys = ["globalId", "title", "doi", "abstract", "year", "authors"]
    data = []

    """
        Add Publications nodes to Neo4j
    """

    # assert(dataset_data["ShortName"]==dataset_data['CollectionCitations'][0]['SeriesName'])

    publication_object = {
        "globalId": publication_id,
        "title": publication_data["title"],
        "doi": publication_data["doi"],
        "abstract": publication_data["abstract"].replace(
            "\n", ""
        ),  # remove newline character
        "year": publication_data["year"],
        # "citationCount": publication_data['citationCount'],
        "authors": publication_data["authors"],
        # "keywords": publication_data['keywords'],
    }

    current_batch = [
        publication_object["globalId"],
        publication_object["title"],
        publication_object["doi"],
        publication_object["abstract"],
        publication_object["year"],
        publication_object["authors"],
    ]
    batch.append(current_batch)

    return publication_id


keys = ["globalId", "title", "doi", "abstract", "year", "authors"]
batch = []
for pub_doi in publication_dicts:

    try:
        publication_id = generate_uuid5(pub_doi)
        current_publication = {
            "globalId": publication_id,
            "title": publication_dicts[pub_doi]["Title"],
            "doi": publication_dicts[pub_doi]["DOI"],
            "abstract": publication_dicts[pub_doi]["zotero"]["abstractNote"],
            "year": int(publication_dicts[pub_doi]["Year"]),
            #'citationCount':publication_dicts[pub_doi]['DOI'],
            "authors": [
                (f"{author['firstName']} {author['lastName']}")
                for author in publication_dicts[pub_doi]["zotero"]["creators"]
            ],
            #'keywords':publication_dicts[pub_doi]['DOI'],
        }
        publication_id = add_publication(
            batch=batch,
            publication_data=current_publication,
            publication_id=current_publication["globalId"],
        )
    except KeyError as error:
        print(f"Publication with DOI {pub_doi} had the following KeyError: {error}")


merge_nodes(graph.auto(), batch, merge_key=("Publication", "globalId"), keys=keys)
print(f'Total indexed publication in Neo4j: {graph.nodes.match("Publication").count()}')
