from owlready2 import *


# Load ontology from file
onto = get_ontology("file:///Users/frieder/Documents/GitHub/procedural-stories/story_ontology.owl").load()

# Reason
#sync_reasoner()
print(onto)
print(onto.Entity)


# serialize rdflib graph to json-ld (might be better for LLM comprehension)
# g.serialize(format='json-ld')