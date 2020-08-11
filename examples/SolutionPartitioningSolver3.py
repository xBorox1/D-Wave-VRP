# This example shows using SolutionPartitioningSolver with DBScanSolver.
# It makes solving cvrp possible with using DBScanSolver.

import sys
sys.path.insert(1, '../src')

from vrp_solvers import SolutionPartitioningSolver, DBScanSolver
import DWaveSolvers
from input import *

if __name__ == '__main__':

    graph_path = '../graphs/medium.csv'

    # Parameters for solve function.
    only_one_const = 10000000.
    order_const = 1.

    for t in ['example_medium1', 'example_medium2', 'example_medium3']:
        print("Test : ", t)

        # Reading problem from file.
        path = '../tests/cvrp/' + t + '.test'
        problem = read_full_test(path, graph_path, capacity = True)

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
