import numpy as np 
import networkx as nx

def calculate_demands(od_matrix,depot):
    demands = np.sum(od_matrix, axis=0)#اینجا این یعنی ستون های ملتریس جمع بشن با هم حتما حواست باشه بعدا سوتی ندی
    demands[depot] = 0
    return demands


def create_distance_matrix(graph):
    node_list = sorted(graph.nodes)

    distance_matrix = nx.floyd_warshall_numpy(
        graph,
        nodelist=node_list,
        weight="cost"
    )
    return np.asarray(distance_matrix)


def calculate_route_cost(
    route,
    distance_matrix
):
    cost = 0

    for current_node, next_node in zip(
        route[:-1],
        route[1:]
    ):
        cost += distance_matrix[
            current_node,
            next_node
        ]

    return cost



def solve_vrp(
    demands,
    distance_matrix,
    depot,
    number_of_vehicles,
    vehicle_capacity
):
    customers = {
        node
        for node in range(len(demands))
        if node != depot and demands[node] > 0
    }

    total_capacity = (
        number_of_vehicles * vehicle_capacity
    )

    if np.sum(demands) > total_capacity:
        raise ValueError(
            "Total demand is greater than fleet capacity."
        )

    if np.max(demands) > vehicle_capacity:
        raise ValueError(
            "A customer's demand is greater than vehicle capacity."
        )

    routes = []

    for _ in range(number_of_vehicles):
        route = [depot]
        current_node = depot
        current_load = 0

        while customers:
            feasible_customers = [
                customer
                for customer in customers
                if (
                    current_load + demands[customer]
                    <= vehicle_capacity
                )
            ]

            if not feasible_customers:
                break

            next_customer = min(
                feasible_customers,
                key=lambda customer: distance_matrix[
                    current_node,
                    customer
                ]
            )

            route.append(next_customer)

            current_load += demands[next_customer]
            current_node = next_customer

            customers.remove(next_customer)

        route.append(depot)

        routes.append({
            "route": route,
            "load": current_load,
            "cost": calculate_route_cost(
                route,
                distance_matrix
            )
        })

    if customers:
        raise ValueError(
            "The available vehicles could not serve all customers."
        )

    return routes
def calculate_total_cost(routes):
    total_cost = sum(
        route_data["cost"]
        for route_data in routes
    )

    return total_cost

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
    demands = calculate_demands(od_est,depot)

    distance_matrix = create_distance_matrix(graph)


    #testing calculate_demands
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


    #testing create_distance_matrix
    # print("\nDistance matrix:")
    # print(distance_matrix)

#testing calculate_route_cost

    # number_of_vehicles = config["vrp"]["number_of_vehicles"]
    # vehicle_capacity = config["vrp"]["vehicle_capacity"]

    # routes = solve_vrp(
    #     demands,
    #     distance_matrix,
    #     depot,
    #     number_of_vehicles,
    #     vehicle_capacity
    # )

    # print("\nVRP routes:")

    # total_cost = 0

    # for vehicle_index, route_data in enumerate(
    #     routes,
    #     start=1
    # ):
    #     print(
    #         "Vehicle",
    #         vehicle_index,
    #         "route:",
    #         route_data["route"],
    #         "load:",
    #         round(route_data["load"], 2),
    #         "cost:",
    #         round(route_data["cost"], 2)
    #     )

    #     total_cost += route_data["cost"]

    # print("\nTotal fleet cost:", round(total_cost, 2))
    #testing calculate_total_cost
    # number_of_vehicles = config["vrp"]["number_of_vehicles"]
    # vehicle_capacity = config["vrp"]["vehicle_capacity"]
    # estimated_demands = calculate_demands(
    #     od_est,
    #     depot
    # )

    # estimated_routes = solve_vrp(
    #     estimated_demands,
    #     distance_matrix,
    #     depot,
    #     number_of_vehicles,
    #     vehicle_capacity
    # )

    # estimated_total_cost = calculate_total_cost(
    #     estimated_routes
    # )
    # true_demands = calculate_demands(
    #     od_true,
    #     depot
    # )

    # true_routes = solve_vrp(
    #     true_demands,
    #     distance_matrix,
    #     depot,
    #     number_of_vehicles,
    #     vehicle_capacity
    # )

    # true_total_cost = calculate_total_cost(
    #     true_routes
    # )

    # print("\nRoutes based on estimated OD:")

    # for vehicle_index, route_data in enumerate(
    #     estimated_routes,
    #     start=1
    # ):
    #     print(
    #         "Vehicle",
    #         vehicle_index,
    #         "route:",
    #         route_data["route"],
    #         "load:",
    #         round(route_data["load"], 2),
    #         "cost:",
    #         round(route_data["cost"], 2)
    #     )

    # print(
    #     "Estimated-OD total cost:",
    #     round(estimated_total_cost, 2)
    # )

    # print("\nRoutes based on true OD:")

    # for vehicle_index, route_data in enumerate(
    #     true_routes,
    #     start=1
    # ):
    #     print(
    #         "Vehicle",
    #         vehicle_index,
    #         "route:",
    #         route_data["route"],
    #         "load:",
    #         round(route_data["load"], 2),
    #         "cost:",
    #         round(route_data["cost"], 2)
    #     )
    # print(
    #     "True-OD total cost:",
    #     round(true_total_cost, 2)
    # )
    # cost_difference = (
    #     estimated_total_cost
    #     - true_total_cost
    # )
    # print(
    #     "\nCost difference:",
    #     round(cost_difference, 2)
    # )