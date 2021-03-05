# This example shows using AveragePartitionSolver on small vrp tests.
# limit_radius attribute is 1/10 of number of destinations here.

import sys
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_dir, 'src'))

from vrp_solvers import AveragePartitionSolver
import DWaveSolvers
from input import *

if __name__ == '__main__':

    graph_path = os.path.join(project_dir, 'graphs/small.csv')

    # Parameters for solve function.
    only_one_const = 10000000.
    order_const = 1.

    for t in ['small_graph1', 'small_graph2', 'small_graph3']:
        print("Test : ", t)

        # Reading problem from file.
        path = os.path.join(project_dir, 'tests/vrp/' + t + '.test')
        problem = read_full_test(path, graph_path ,capacity = False)
        limit_radius = int(len(problem.dests) / 10) # set limit_radius parameter

        # Solving problem on AveragePartitionSolver.
        solver = AveragePartitionSolver(problem, limit_radius)
        solution = solver.solve(only_one_const, order_const, solver_type = 'cpu')

        # Checking if solution is correct.
        if solution == None or solution.check() == False:
            print("Solver hasn't find solution.\n")
            continue

        print("Solution : ", solution.solution) 
        print("Total cost : ", solution.total_cost())
        print("\n")
