#!/bin/bash

#echo "60 second sleep began."
#sleep 60
#echo "60 second sleep ended."

cd neo-sync-scripts
python neo4j-node-dataset-index.py 
#python neo4j-node-variable-index.py
#python neo4j-node-publication-index.py
python neo4j-node-keyword-index.py
python neo4j-node-platform-index.py
python neo4j-node-instrument-index.py
python neo4j-node-investigator-index.py
#python neo4j-edge-dataset-variable-index.py
#python neo4j-edge-dataset-publication-index.py
python neo4j-edge-dataset-keyword-index.py
python neo4j-edge-dataset-platform-index.py
python neo4j-edge-dataset-instrument-index.py
python neo4j-edge-dataset-investigator-index.py
python neo4j-gds-fastrp.py
#python neo4j-link-prediction-pipeline.py