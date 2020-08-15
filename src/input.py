import networkx as nx
import csv
import math
from itertools import product
from vrp_problem import VRPProblem
import numpy as np

# Creates directed graph from file.
# Format : id1|id2|cost
def create_graph_from_csv(path):
    g = nx.DiGraph(directed=True)

    with open(path, mode='r') as e_infile:
        reader = csv.reader(e_infile)
        next(reader)
        for row in reader:
            id1 = int(row[0])
            id2 = int(row[1])
            cost = float(row[2])
            g.add_edge(id1, id2, cost=cost)

    return g

# Creates VRPProblem from test file and graph file.
# path - path to test file
# graph_path - path to graph file
# capacity - True if vehicles have capacities, False otherwise
def read_full_test(path, graph_path, capacity = True):
    graph = create_graph_from_csv(graph_path)
    in_file = open(path, 'r')
    
    nodes_id = list()

    # Reading magazines.
    next(in_file)
    nodes_id = [int(s) for s in in_file.readline().split() if s.isdigit()]
    magazines_num = len(nodes_id)

    # Reading destinations.
    dests_num = int(in_file.readline())
    nodes_num = dests_num + magazines_num

    weights = np.zeros((nodes_num), dtype=int)
    for i in range(dests_num):
        order = in_file.readline().split()
        
        dest = int(order[0])
        nodes_id.append(dest)

        if capacity:
            weight = int(order[1])
            weights[i + magazines_num] = weight

    # Reading vehicles.
    vehicles = int(in_file.readline())
    capacities = np.ones((vehicles), dtype=int)

    if capacity:
        capacities = [int(s) for s in in_file.readline().split() if s.isdigit()]

    # Generating costs matrix.
    costs = np.zeros((nodes_num, nodes_num), dtype=int)
    for i in range(nodes_num):
        source = nodes_id[i]
        _, paths = nx.single_source_dijkstra(graph, source, weight = 'cost')
        for j in range(nodes_num):
            d = nodes_id[j]
            path = paths[d]
        
            prev = source
            for node in path[1:]:
                edge = graph.get_edge_data(prev, node)
                costs[i][j] += edge['cost']
                prev = node

    in_file.close()

    sources = [i for i in range(magazines_num)]
    dests =  [i for i in range(magazines_num, nodes_num)]

    return VRPProblem(sources, costs, capacities, dests, weights) 

# Creates VRPProblem from test file.
# path - path to test file
# capacity - True if vehicles have capacities, False otherwise
def read_test(path, capacity = True):
    in_file = open(path, 'r')
    
    magazines_num = int(in_file.readline())
    dests_num = int(in_file.readline())
    nodes_num = magazines_num + dests_num

    # Reading weights of destinations.
    weights = np.zeros((nodes_num), dtype=int)
    if capacity:
        w = [int(s) for s in in_file.readline().split() if s.isdigit()]
        for i in range(dests_num):
            weights[i + magazines_num] = w[i]

    # Reading costs.
    costs = np.zeros((nodes_num, nodes_num), dtype=int)
    for i in range(nodes_num):
        costs[i] = [int(s) for s in in_file.readline().split() if s.isdigit()]

    # Reading vehicles.
    vehicles = int(in_file.readline())
    capacities = np.ones((vehicles), dtype=int)
    if capacity:
        capacities = [int(s) for s in in_file.readline().split() if s.isdigit()]

    in_file.close()

    sources = [i for i in range(magazines_num)]
    dests =  [i for i in range(magazines_num, nodes_num)]

    return VRPProblem(sources, costs, capacities, dests, weights) 

# Creates one-file test from format with graph.
# in_path - test input file
# graph_path - graph input file
# out_path - output
# capacity - True if vehicles have capacities, False otherwise
def create_test(in_path, graph_path, out_path, capacity = True):
    test = read_full_test(in_path, graph_path, capacity)
    out_file = open(out_path, 'w+')

    # Number of magazines.
    out_file.write(str(len(test.sources)) + '\n')

    # Number of destinations..
    out_file.write(str(len(test.dests)) + '\n')

    # Weights of destinations.
    if capacity:
        for dest in test.dests:
            out_file.write(str(test.weights[dest])  + ' ')
        out_file.write('\n')

    # Costs.
    n = len(test.sources) + len(test.dests)
    for i in range(n):
        for j in range(n):
            out_file.write(str(test.costs[i][j]) + ' ')
        out_file.write('\n')

    # Vehicles.
    out_file.write(str(len(test.capacities)) + '\n')
    if capacity:
        for i in range(len(test.capacities)):
            out_file.write(str(test.capacities[i]) + ' ')
        out_file.write('\n')

    out_file.close()
