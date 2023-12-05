import os
from py2neo import Graph, Node, Relationship

# Get the NEO4J_AUTH from the environment variables
neo4j_auth = os.getenv("NEO4J_AUTH")

# NEO4J_AUTH is in the format "username/password", so we split it
graph = Graph("bolt://localhost:7687", auth=("neo4j", "linkpredict"))

#drop pipeline if it exists so we can rerun, comment out if needed
drop_pipeline = f'''
CALL gds.beta.pipeline.drop('pipe')
)'''

graph.run(drop_pipeline)

#create pipeline
create_pipeline = f'''
CALL gds.beta.pipeline.linkPrediction.create(
  pipelineName: String
)'''

graph.run(create_pipeline)
