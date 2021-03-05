# This example shows using SolutionPartitioningSolver with DBScanSolver.
# It makes solving cvrp possible with using DBScanSolver.

import sys
import os

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(project_dir, 'src'))

from vrp_solvers import SolutionPartitioningSolver, DBScanSolver
import DWaveSolvers
from input import *

if __name__ == '__main__':

    # Parameters for solve function.
    only_one_const = 10000000.
    order_const = 1.

    for t in ['example_medium4', 'example_medium5', 'example_medium6']:
        print("Test : ", t)

        # Reading problem from file.
        path = os.path.join(project_dir, 'tests/cvrp/' + t + '.test')
        problem = read_test(path, capacity = True)

        # Solving problem on SolutionPartitioningSolver.
        solver = SolutionPartitioningSolver(problem, DBScanSolver(problem, anti_noiser = True))
        solution = solver.solve(only_one_const, order_const, solver_type = 'cpu')

        # Checking if solution is correct.
        if solution == None or solution.check() == False:
            print("Solver hasn't find solution.\n")
            continue

        print("Solution : ", solution.solution) 
        print("Total cost : ", solution.total_cost())
        print("Weights : ", solution.all_weights())
        print("\n")
