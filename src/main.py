from qubo_helper import Qubo
from tsp_problem import TSPProblem 
from vrp_problem import VRPProblem
from vrptw_problem import VRPTWProblem
from vrptw_solvers import *
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
        time_costs = test['time_costs']
        capacities = test['capacities']
        dests = test['dests']
        weigths = test['weights']
        time_windows = test['time_windows']

        only_one_const = 10000000.
        order_const = 1.
        capacity_const = 0. #not important in this example
        time_const = 0. #not important in this example

        problem = VRPProblem(sources, costs, time_costs, capacities, dests, weigths)
        solver = SolutionPartitioningSolver(problem, DBScanSolver(problem, anti_noiser = False))
        #solver = FullQuboSolver(problem)
        #solver = AveragePartitionSolver(problem)

        result = solver.solve(only_one_const, order_const, capacity_const,
                solver_type = 'cpu')

        if result == None or result.check() == False:
            print("Solver hasn't find solution.\n")
            continue

        print("Solution : ", result.solution)
        print("Total cost : ", result.total_cost())
        print("Weights : ", result.all_weights())
        print("\n")
