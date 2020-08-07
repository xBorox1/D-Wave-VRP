from qubo_helper import Qubo
from vrp_problem import VRPProblem
from vrp_solvers import *
from itertools import product
import DWaveSolvers
import networkx as nx
import numpy as np
from input import *

if __name__ == '__main__':

    for t in ['example1', 'example2', 'example3']:
        print("Test : ", t)

        TEST = '../tests/' + t + '.test'
        test = read_test(TEST)

        # Problem parameters
        sources = test['sources']
        costs = test['costs']
        capacities = test['capacities']
        dests = test['dests']
        weigths = test['weights']

        only_one_const = 10000000.
        order_const = 1.

        problem = VRPProblem(sources, costs, capacities, dests, weigths)
        #solver = SolutionPartitioningSolver(problem, DBScanSolver(problem, anti_noiser = False))
        solver = FullQuboSolver(problem)
        #solver = AveragePartitionSolver(problem, limit_radius = 1)

        result = solver.solve(only_one_const, order_const, solver_type = 'cpu')

        if result == None or result.check() == False:
            print("Solver hasn't find solution.\n")
            continue

        print("Solution : ", result.solution)
        print("Total cost : ", result.total_cost())
        print("Weights : ", result.all_weights())
        print("\n")
