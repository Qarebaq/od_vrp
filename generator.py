import json 
import random
import pathlib
import networkx as nx
import numpy as np


def load_config(config_path = "config.json"):#just importing config file here
    with open(config_path, "r") as file:
        config = json.load(file)
    return config

def generate_network(config):
    network_config = config["network"]


    number_of_nodes =network_config["number_of_nodes"]
    edge_probability = network_config["edge_probability"]
    minimum_cost = network_config["minimum_edge_cost"]
    maximum_cost = network_config["maximum_edge_cost"]

    rng = random.Random(config["seed"])

#این جا شروع کردم به ساختن گراف حتما حواست باشه
    graph = nx.DiGraph()
    graph.add_nodes_from(range(number_of_nodes))

    for node in range(number_of_nodes):
        next_node = (node + 1)%number_of_nodes
        cost = rng.randint(minimum_cost,maximum_cost)

        graph.add_edge(node,next_node,cost = cost)

    for source in range(number_of_nodes):
        for destination in range(number_of_nodes):
            if source == destination:
                continue
            if graph.has_edge(source , destination):
                continue
            

            if rng.random() <edge_probability:
                cost = rng.randint(minimum_cost , maximum_cost)
                graph.add_edge(source , destination ,cost = cost)
    return graph
        


def create_adjacency_matrix(graph):
    adjacency_matrix =nx.to_numpy_array(graph , weight="cost" , dtype=int)

    return adjacency_matrix




def generate_od_true(config):


    number_of_nodes = config["network"]["number_of_nodes"]
    minimum_trip_count = config["od_generator"]["minimum_trip_count"]
    maximum_trip_count = config["od_generator"]["maximum_trip_count"]

    rng = np.random.default_rng(config["seed"]+1 )

    od_true = rng.integers(low=minimum_trip_count, high=maximum_trip_count + 1, size=(number_of_nodes, number_of_nodes))
    np.fill_diagonal(od_true, 0)

    return od_true



if __name__ =="__main__":

    config = load_config()
    graph = generate_network(config)


    # print("Nodes:")
    # print(list(graph.nodes))
    # print("\nEdges: ")
    # for source, destination, data in graph.edges(data=True):
    #     print(source, "->" ,destination, "cost: " , data["cost"])
    

#for testing adjecency matrix
    # adjacency_matrix = create_adjacency_matrix(graph)

    # print("\nAdjacency matrix:")
    # print(adjacency_matrix)

#testing od_true
    od_true = generate_od_true(config)

    print("\nOD true:")
    print(od_true)