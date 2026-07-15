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

def create_assignment_matrix(graph):#P matrix is created here
    edge_list = list(graph.edges)
    od_pairs = [(origin, destination) for origin in graph.nodes for destination in graph.nodes if origin != destination]
    number_of_edges = len(edge_list)
    number_of_od_pairs = len(od_pairs)

    assignment_matrix = np.zeros((number_of_edges, number_of_od_pairs), dtype=int)

    edge_index = {edge: index for index, edge in enumerate(edge_list)}
    shortest_paths = {}
    for column, (origin, destination) in enumerate(od_pairs):
        path = nx.shortest_path(
            graph,
            source=origin,
            target=destination,
            weight="cost"
        )

        shortest_paths[(origin, destination)] = path
        path_edges = list(zip(path[:-1], path[1:]))

        for edge in path_edges:
            row = edge_index[edge]
            assignment_matrix[row, column] = 1

    return assignment_matrix, edge_list, od_pairs, shortest_paths



def generate_link_counts(assignment_matrix , od_true, od_pairs, config):
    od_vector =np.array([od_true[origin, destination] for origin, destination in od_pairs])
    true_link_counts = assignment_matrix @ od_vector
    noise_level = config["od_generator"]["noise_level"]

    if noise_level>0:
        rng = np.random.default_rng(config["seed"] + 2)
        noise = rng.normal(
            loc=0,
            scale=noise_level * np.maximum(true_link_counts, 1)
        )
        observed_link_counts = np.rint(true_link_counts + noise).astype(int)
        observed_link_counts = np.maximum(observed_link_counts, 0)

    else:
        observed_link_counts = true_link_counts.copy()
    return observed_link_counts, true_link_counts, od_vector

if __name__ =="__main__":

    config = load_config()
    graph = generate_network(config)
    assignment_matrix, edge_list, od_pairs, shortest_paths = (
    create_assignment_matrix(graph))
    od_true = generate_od_true(config)

    assignment_matrix, edge_list, od_pairs, shortest_paths = (
        create_assignment_matrix(graph)
    )

    link_counts, true_link_counts, od_vector = generate_link_counts(
        assignment_matrix,
        od_true,
        od_pairs,
        config
    )


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
    # od_true = generate_od_true(config)

    # print("\nOD true:")
    # print(od_true)

#testing P matrix and shortest path 
    # print("\nShortest paths:")
    # for od_pair, path in shortest_paths.items():
    #     print(od_pair, ":", path)

    # print("\nAssignment matrix P:")
    # print(assignment_matrix)

    # print("\nP shape:")
    # print(assignment_matrix.shape)
#testing link counts
    print("\nOD true:")
    print(od_true)

    print("\nTrue link counts:")
    for edge, count in zip(edge_list, true_link_counts):
        print(edge, ":", count)

    print("\nObserved link counts:")
    for edge, count in zip(edge_list, link_counts):
        print(edge, ":", count)
