import numpy as np 
from colorama import Fore,Style,init

from generator import load_config
from generator import generate_network
from generator import create_adjacency_matrix
from generator import generate_od_true
from generator import create_assignment_matrix
from generator import generate_link_counts


from estimator import estimate_od, vector_to_od_matrix
from estimator import vector_to_od_matrix


from evaluator import evaluate_od
from evaluator import evaluate_link_counts


from vrp import calculate_demands
from vrp import create_distance_matrix
from vrp import solve_vrp
from vrp import calculate_total_cost
from vrp import validate_routes

config = load_config()



graph = generate_network(config)
adjacency_matrix = create_adjacency_matrix(graph)
od_true = generate_od_true(config)

assignment_results = create_assignment_matrix(graph)
assignment_matrix = assignment_results[0]
edge_list = assignment_results[1]
od_pairs = assignment_results[2]
shortest_paths = assignment_results[3]

link_count_results = generate_link_counts(assignment_matrix, od_true, od_pairs, config)
observed_link_counts = link_count_results[0]
true_link_counts = link_count_results[1]
od_true_vector = link_count_results[2]

lambda_value = config["estimator"]["lambda"]
od_est_vector=estimate_od(assignment_matrix, observed_link_counts, lambda_value)

number_of_nodes = config["network"]["number_of_nodes"]
od_est = vector_to_od_matrix(od_est_vector, od_pairs, number_of_nodes)

od_metrics = evaluate_od(od_true, od_est, od_pairs)

link_metrics = evaluate_link_counts(assignment_matrix, od_est_vector, observed_link_counts)


depot= config["vrp"]["depot"]
number_of_vehicles = config["vrp"]["number_of_vehicles"]
vehicle_capacity = config["vrp"]["vehicle_capacity"]
distance_matrix = create_distance_matrix(graph)
estimate_demands = calculate_demands(od_est, depot)

true_demands = calculate_demands(od_true, depot)

estimated_routes = solve_vrp(estimate_demands,distance_matrix,depot,number_of_vehicles,vehicle_capacity)
estimated_total_cost = calculate_total_cost(estimated_routes)

true_routes = solve_vrp(true_demands,distance_matrix,depot,number_of_vehicles,vehicle_capacity)
true_total_cost = calculate_total_cost(true_routes)
cost_difference = (estimated_total_cost - true_total_cost)

estimated_validation = validate_routes(estimated_routes, estimate_demands, depot,vehicle_capacity)
estimated_routes_with_true_demands= validate_routes(estimated_routes, true_demands, depot, vehicle_capacity)
true_validation= validate_routes(true_routes,true_demands,depot,vehicle_capacity)

#View ////////
init(autoreset=True)

print(Fore.BLACK + "\nProgram Generated Data:\n")
print(Fore.GREEN + "\nAdjacency matrix:")
print(adjacency_matrix)

print(Fore.GREEN+ "\nOD true:")
print(od_true)

print(Fore.GREEN +"\nObserved link counts: ")
print(observed_link_counts)
print(Fore.BLACK + "=======================================\n")
print(Fore.BLACK + "\nEstimator Results:\n")
print(Fore.GREEN + "\nOD estimated:")
print(np.round(od_est, 2))
print(Fore.GREEN + "\nMAE:")
print(round(od_metrics["mae"], 4))
print(Fore.GREEN + "\nRMSE:")
print(round(od_metrics["rmse"], 4))
print(Fore.GREEN + "\nTotal relative error:")
print(round(od_metrics["total_relative_error"], 4))
print(Fore.GREEN+ "\nReconstruction error: ")
print(round(link_metrics["reconstruction_error"], 4))
print(Fore.GREEN + "\nReconstruction RMSE: ")
print(round(link_metrics["reconstruction_rmse"], 4))


print(Fore.BLACK + "=======================================\n")
print(Fore.BLACK + "\nEstimated OD routes")

vehicle_number = 1
for route_data in estimated_routes:
    print("\nVehicle:", vehicle_number)
    print("Route:", route_data["route"])
    print("Load:", round(route_data["load"], 2))
    print("Cost:", round(route_data["cost"], 2))

    vehicle_number = vehicle_number + 1

print("\nEstimated OD total cost:")
print(round(estimated_total_cost, 2))

print(Fore.BLACK + "========================================\n")

print(Fore.BLACK + "\nTrue OD routes")

vehicle_number = 1

for route_data in true_routes:
    print("\nVehicle:", vehicle_number)
    print("Route:", route_data["route"])
    print("Load:", round(route_data["load"], 2))
    print("Cost:", round(route_data["cost"], 2))

    vehicle_number = vehicle_number + 1

print(Fore.GREEN + "\nTrue OD total cost:")
print(round(true_total_cost, 2))

print(Fore.GREEN + "\nCost difference between estimated and true OD:")
print(round(cost_difference, 2))

print(Fore.BLACK + "========================================\n")
print(Fore.BLACK + "\n Validation:")
print(Fore.GREEN + "Estimated routes with estimated demands valid:")
print(estimated_validation["valid"])
print(Fore.GREEN + "Estimated routes with true demands valid:")
print(estimated_routes_with_true_demands["valid"])

for error in estimated_routes_with_true_demands["errors"]:
    print(Fore.RED + error)

print("\nTrue routes with true demands:")
print(true_validation["valid"])