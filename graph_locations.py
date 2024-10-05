from typing import List

import networkx as nx
import matplotlib.pyplot as plt

from generator.models import LocationData


def display_location_relationships(locations: List[LocationData]):
    # Create a graph
    G = nx.Graph()

    # Add nodes and edges
    for location in locations:
        G.add_node(location.name)  # Add each location as a node
        for related_location in location.relationships:
            # Create edges for relationships
            G.add_edge(location.name, related_location)

    # Draw the graph
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G)  # Positioning of the graph

    # Draw nodes, edges, and labels
    nx.draw(G, pos,
            with_labels=True,
            node_color='lightblue',
            node_size=2000,
            font_size=10,
            font_weight='bold',
            edge_color='gray')
    plt.title('Location Relationship Graph')
    plt.show()
