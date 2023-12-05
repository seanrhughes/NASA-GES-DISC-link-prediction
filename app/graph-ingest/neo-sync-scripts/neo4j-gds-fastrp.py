import os
from py2neo import Graph, Node, Relationship


# Get the NEO4J_AUTH from the environment variables
neo4j_auth = os.getenv("NEO4J_AUTH")


graph = Graph("bolt://localhost:7687", auth=("neo4j", "linkprediction"))



relationship_proj = '''
{
    relType: {
      type: '*',
      orientation: 'UNDIRECTED',
      properties: {}
    }
  }
'''
empty_brances = '''
{}
'''

projection_command = f'''
CALL gds.graph.project('in-memory-graph-1681323347597', "*",{relationship_proj}, {empty_brances});
'''

graph.run(projection_command)

config = '''
{
  relationshipWeightProperty: null,
  embeddingDimension: 10,
  normalizationStrength: 0.5,
  writeProperty: 'fastrp'
}
'''
generation_fastrp = f'''
CALL gds.fastRP.write("in-memory-graph-1681323347597", {config});
'''

graph.run(generation_fastrp)

drop_graph_command = f'''
CALL gds.graph.drop('in-memory-graph-1681323347597');
'''
graph.run(drop_graph_command)


