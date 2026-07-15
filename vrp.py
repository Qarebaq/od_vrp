import numpy as np 

def calculate_demonds(od_matrix,depot):
    demands = np.sum(od_matrix, axis=0)#اینجا این یعنی ستون های ملتریس جمع بشن با هم حتما حواست باشه بعدا سوتی ندی
    demands[depot] = 0
    return demands


if __name__ == "__main__":
    from generator import (load_config, generate_network, generate_od_true, create_assignment_matrix, generate_link_counts)

    from estimator import (estimate_od, vector_to_od_matrix)
    config = load_config()
    graph = generate_network(config)
    od_true = generate_od_true(config)
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

    depot = config["vrp"]["depot"]
    demands = calculate_demonds(od_est,depot)


    #testing calculate_demonds
    # print("\nOD estimated:")
    # print(np.round(od_est, 2))

    # print("\nDestination demands:")

    # for node, demand in enumerate(demands):
    #     print(
    #         "Node",
    #         node,
    #         "demand:",
    #         round(demand, 2)
    #     )