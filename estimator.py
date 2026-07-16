import numpy as np 
from scipy.optimize import minimize

def objective_function(od_vector,assignment_matrix,link_counts,lambda_value):
    estimated_link_counts = assignment_matrix @ od_vector

    link_count_error = np.sum((estimated_link_counts - link_counts) ** 2)

    regularization_error = (lambda_value * np.sum(od_vector ** 2))

    total_error= (link_count_error+ regularization_error)

    return total_error


def estimate_od(assignment_matrix,link_counts,lambda_value):
    number_of_od_pairs = assignment_matrix.shape[1]
    initial_od_vector = np.zeros(number_of_od_pairs)

    bounds= []
    for index in range(number_of_od_pairs):
        bounds.append((0, None))
        
    result = minimize(
        objective_function,
        initial_od_vector,
        args=(
            assignment_matrix,
            link_counts,
            lambda_value
        ),
        method="L-BFGS-B",# این همون الگوریتمی هست که من انتخاب کردم برای حل این مسيله(همون تابع حل کننده)
        bounds=bounds)

    if not result.success:
        raise RuntimeError("OD estimation failed: " + result.message)

    return result.x


def vector_to_od_matrix(od_vector, od_pairs, number_of_nodes):
    od_matrix = np.zeros(
        (number_of_nodes, number_of_nodes)
    )

    index = 0

    while index < len(od_pairs):
        pair = od_pairs[index]

        origin = pair[0]
        destination = pair[1]
        value = od_vector[index]

        od_matrix[origin, destination] = value

        index = index + 1

    return od_matrix

if __name__ == "__main__":
    from generator import (
        load_config,
        generate_network,
        generate_od_true,
        create_assignment_matrix,
        generate_link_counts
    )

    config=load_config()

    graph=generate_network(config)

    od_true= generate_od_true(config)

    assignment_matrix, edge_list, od_pairs, shortest_paths = (
        create_assignment_matrix(graph)
    )

    link_counts, true_link_counts, od_true_vector = (
        generate_link_counts(
            assignment_matrix,
            od_true,
            od_pairs,
            config
        )
    )

    lambda_value = config["estimator"]["lambda"]

    od_est_vector = estimate_od(
        assignment_matrix,
        link_counts,
        lambda_value
    )

    number_of_nodes = config["network"]["number_of_nodes"]

    od_est = vector_to_od_matrix(
        od_est_vector,
        od_pairs,
        number_of_nodes
    )

    estimated_link_counts = (
        assignment_matrix @ od_est_vector
    )
#testing od_est and estimated_link_counts
    # print("\nOD true:")
    # print(od_true)

    # print("\nOD estimated:")
    # print(np.round(od_est, 2))

    # print("\nObserved link counts:")
    # print(link_counts)

    # print("\nEstimated link counts:")
    # print(np.round(estimated_link_counts, 2))