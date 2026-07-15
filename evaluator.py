import numpy as np 
#همانطور که از اسم تابع پیداست این تابع برای ارزیابی ماتریس OD ساخته شده
def evaluate_od(
        od_true,
        od_est,
        od_pairs
):
    true_values = np.array([od_true[origin, destination] for origin, destination in od_pairs])
    estimated_values = np.array([od_est[origin, destination] for origin, destination in od_pairs])

    errors = estimated_values - true_values
    mae = np.mean(np.abs(errors))
    rmse = np.sqrt(np.mean(errors ** 2))

    total_relative_error = np.sum(np.abs(errors)) / np.sum(true_values)
    return {
        "mae": mae,
        "rmse": rmse,
        "total_relative_error": total_relative_error
    }

def evaluate_link_counts(
    assignment_matrix,
    od_est_vector,
    observed_link_counts
):
    reproduced_link_counts =( assignment_matrix @ od_est_vector)

    errors =( reproduced_link_counts - observed_link_counts)

    reconstruction_error = np.linalg.norm(errors)
    reconstruction_rmse = np.sqrt(
        np.mean(errors ** 2)
    )

    return {
        "reconstruction_error": reconstruction_error,
        "reconstruction_rmse": reconstruction_rmse,
        "reproduced_link_counts": reproduced_link_counts
    }


if __name__ == "__main__":
    from generator import (
        load_config,
        generate_network,
        generate_od_true,
        create_assignment_matrix,
        generate_link_counts)
    
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

    od_metrics = evaluate_od(
        od_true,
        od_est,
        od_pairs
    )

    link_metrics = evaluate_link_counts(
        assignment_matrix,
        od_est_vector,
        link_counts
    )


    #testing the evaluation functions
    print("\nOD evaluation:")

    print("MAE:", round(od_metrics["mae"], 4))
    print("RMSE:", round(od_metrics["rmse"], 4))
    print(
        "Total relative error:",
        round(od_metrics["total_relative_error"], 4)
    )

    print("\nLink-count evaluation:")

    print(
        "Reconstruction error:",
        round(link_metrics["reconstruction_error"], 4)
    )

    print(
        "Reconstruction RMSE:",
        round(link_metrics["reconstruction_rmse"], 4)
    )