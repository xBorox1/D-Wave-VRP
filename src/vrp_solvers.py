from qubo_helper import Qubo
from vrp_problem import VRPProblem
from vrp_solution import VRPSolution
from itertools import product
import DWaveSolvers
import networkx as nx
import numpy as np
from queue import Queue

# Abstract class for VRP solvers.
class VRPSolver:
    # Attributes : VRPProblem
    def __init__(self, problem):
        self.problem = problem

    def set_problem(self, problem):
        self.problem = problem

    # only_one_const - const in qubo making solution correct
    # order_const - multiplier for costs in qubo
    # It is recommended to set order_const = 1 and only_one_const
    # big enough to make solutions correct. Bigger than sum of all
    # costs should be enough.
    def solve(self, only_one_const, order_const, solver_type = 'cpu'):
        pass

# Solver solves VRP only by QUBO formulation.
class FullQuboSolver(VRPSolver):
    def solve(self, only_one_const, order_const, solver_type = 'cpu'):
        qubo = self.problem.get_full_qubo(only_one_const, order_const)
        sample = DWaveSolvers.solve_qubo(qubo, solver_type = solver_type)
        solution = VRPSolution(self.problem, sample)
        return solution

# Solver assumes that every vehicle serves approximately the same number of deliveries.
# Additional attribute : limit_radius - maximum difference between served number of deliveries
# and average number of deliveries that every vehicle should serve.
class AveragePartitionSolver(VRPSolver):
    def __init__(self, problem, limit_radius = 1):
        self.problem = problem
        self.limit_radius = limit_radius

    def solve(self, only_one_const, order_const, solver_type = 'cpu'):
        dests = len(self.problem.dests)
        vehicles = len(self.problem.capacities)

        avg = int(dests / vehicles)
        limit_radius = self.limit_radius

        limits = [(max(avg - limit_radius, 0), min(avg + limit_radius, dests)) for _ in range(vehicles)]
        max_limits = [r for (_, r) in limits]

        vrp_qubo = self.problem.get_qubo_with_both_limits(limits,
                only_one_const, order_const)

        sample = DWaveSolvers.solve_qubo(vrp_qubo, solver_type = solver_type)

        solution = VRPSolution(self.problem, sample, max_limits)
        return solution

# Solver uses DBScan to divide problem into subproblems that can be solved effectively by FullQuboSolver.
# Attributes : max_len - maximum number of deliveries in problems solved by FullQuboSolver.
# anti_noiser : True if dbscan should eliminate singleton clusters, False otherwise.
class DBScanSolver(VRPSolver):

    def __init__(self, problem, max_len = 10, anti_noiser = True):
        self.problem = problem
        self.anti_noiser = anti_noiser
        self.max_len = max_len
        self.max_weight = max(problem.capacities)
        self.max_dist = 2 * max(map(max, problem.costs))

    # Returns subset of dests with elements x that satisfies
    # costs[source][x] + costs[x][source] <= 2 * radius
    def _range_query(self, dests, costs, source, radius):
        result = list()
        for dest in dests:
            if (costs[source][dest] + costs[dest][source]) / 2 <= radius:
                result.append(dest)
        return result

    # Standard dbscan clustering dests.
    # Returns list of clusters.
    def _dbscan(self, dests, costs, radius, min_size):
        clusters_num = -1

        states = dict()
        # Undifined cluster.
        for d in dests:
            states[d] = -2

        for d in dests:
            neighbours = self._range_query(dests, costs, d, radius)
            if len(neighbours) < min_size:
                states[d] = -1

        for dest in dests:
            if states[dest] != -2:
                continue

            clusters_num += 1
            q = Queue()
            q.put(dest)

            while not q.empty():
                dest2 = q.get()
                states[dest2] = clusters_num
                neighbours = self._range_query(dests, costs, dest2, radius)
                for v in neighbours:
                    if states[v] == -2:
                        q.put(v)

        for dest in dests: 
            if states[dest] == -1:
                min_dist = self.max_dist
                best_neighbour = -1
                for d in dests:
                    if states[d] != -1:
                        if costs[d][dest] < min_dist:
                            best_neighbour = d
                            min_dist = costs[d][dest]
                if best_neighbour == -1:
                    clusters_num += 1
                    states[dest] = clusters_num
                else:
                    states[dest] = states[best_neighbour]

        clusters = list()
        for i in range(clusters_num + 1):
            clusters.append(list())
        for dest in dests:
            cl = states[dest]
            clusters[cl].append(dest)

        return clusters

    # Recursive dbscan. Returns list of clusters.
    # dests - set that need to be clustered.
    # costs - array with costs between dests.
    # min_radius, max_radius - lower and upper bound for radius parameter
    # in dbscan.
    # clusters_num - expected maximum number of clusters. It is not guaranteed that 
    # function won't return more clusters.
    # max_len - maximum size of a cluster. It is guaranteed that every cluster will
    # have at most max_len elements.
    # max_weight - maximum sum of deliveries' weights of a cluster. It is guaranteed that every cluster will
    # have at most max_weight sum of weights.
    def _recursive_dbscan(self, dests, costs, min_radius, max_radius,
                          clusters_num, max_len, max_weight):
        best_res = [[d] for d in dests]

        min_r = min_radius
        max_r = max_radius
        curr_r = max_r

        # Searching best radius with binary search.
        while min_r + 1 < max_r:
            curr_r = (min_r + max_r) / 2

            clusters = self._dbscan(dests, costs, curr_r, 1)

            if len(clusters) < clusters_num:
                max_r = curr_r
            else:
                min_r = curr_r
                if len(clusters) < len(best_res):
                    best_res = clusters

        # Recursive dbscan on clusters with too many elements. 
        for cluster in best_res:
            weight = 0
            for dest in cluster:
                weight += self.problem.weights[dest]
            if len(cluster) > max_len or weight > max_weight:
                best_res.remove(cluster)
                best_res += self._recursive_dbscan(cluster, costs, 0., self.max_dist, 2,
                                                   max_len, max_weight)

        # Removing singleton clusters while they are and there is more than clusters_num clusters.
        if self.anti_noiser:
            while len(best_res) > clusters_num:
                singleton = [0]
                for cluster in best_res:
                    if len(cluster) == 1:
                        singleton = cluster
                        break

                if singleton == [0]:
                    break

                best_res.remove(singleton)

                one = singleton[0]
                best_cluster = []
                best_dist = self.max_dist

                for cluster in best_res:
                    if len(cluster) == max_len or cluster == singleton:
                        continue

                    weight = 0
                    min_dist = self.max_dist

                    for dest in cluster:
                        weight += self.problem.weights[dest]
                        min_dist = min(min_dist, costs[dest][one])
                    if weight + self.problem.weights[one] <= max_weight:
                        if best_dist > min_dist:
                            best_dist = min_dist
                            best_cluster = cluster

                if best_cluster == []:
                    best_res.append(singleton)
                    break
                best_res.remove(best_cluster)
                best_res.append(best_cluster + singleton)

        return best_res

    def solve(self, only_one_const, order_const, solver_type = 'cpu'):
        problem = self.problem
        dests = problem.dests
        costs = problem.costs
        sources = [problem.source]
        capacities = problem.capacities
        weights = problem.weights
        vehicles = len(problem.capacities)

        if len(dests) == 0:
            return VRPSolution(problem, None, None, [[]])

        clusters = self._recursive_dbscan(dests, costs, 0., self.max_dist, vehicles,
                self.max_len, self.max_weight)

        # If we have as much small clusters as vehicles, we can solve TSP for every cluster.
        if len(clusters) == vehicles:
            result = list()
            for cluster in clusters:
                new_problem = VRPProblem(sources, costs, [capacities[0]], cluster, weights)
                solver = FullQuboSolver(new_problem)
                solution = solver.solve(only_one_const, order_const,
                                    solver_type = solver_type).solution[0]
                result.append(solution)
            return VRPSolution(problem, None, None, result)

        solutions = list()
        solutions.append(VRPSolution(problem, None, None, [[0]]))

        # Solving TSP for every cluster.
        for cluster in clusters:
            new_problem = VRPProblem(sources, costs, [capacities[0]], cluster, weights,
                                 first_source = False, last_source = False)
            solver = FullQuboSolver(new_problem)
            solution = solver.solve(only_one_const, order_const, solver_type = solver_type)
            solutions.append(solution)

        # Creating smaller instance of problem for DBScanSolver.
        clusters_num = len(clusters) + 1
        new_dests = [i for i in range(1, clusters_num)]
        new_costs = np.zeros((clusters_num, clusters_num), dtype=float)
        new_weights = np.zeros((clusters_num), dtype=int)

        for (i, j) in product(range(clusters_num), range(clusters_num)):
            if i == j:
                new_costs[i][j] = 0
                continue
            id1 = solutions[i].solution[0][-1]
            id2 = solutions[j].solution[0][0]
            new_costs[i][j] = costs[id1][id2]

        for i in range(clusters_num):
            for dest in solutions[i].solution[0]:
                new_weights[i] += weights[dest]

        new_problem = VRPProblem(sources, new_costs, capacities, new_dests, new_weights)
        solver = DBScanSolver(new_problem)
        compressed_solution = solver.solve(only_one_const, order_const, 
                            solver_type = solver_type).solution

        # Achieving full solution from solution of smaller version.
        uncompressed_solution = list()
        for vehicle_dests in compressed_solution:
            uncompressed = list()
            for dest in vehicle_dests:
                uncompressed += solutions[dest].solution[0]
            uncompressed_solution.append(uncompressed)

        return VRPSolution(problem, None, None, uncompressed_solution)

# Solver uses some solver to generate TSP Solution and tries to make VRP solution from it.
# Attributes : solver - VRPSolver object. DBScanSolver is recomended.
# random - number of permutations of vehicles that will be generate. 
class SolutionPartitioningSolver(VRPSolver):

    def __init__(self, problem, solver, random = 100):
        self.problem = problem
        self.solver = solver
        self.random = random
        self.inf = 2 * sum(map(sum, problem.costs))
    
    # Divides TSP solution to continous parts that will be correct VRP solution.
    def _divide_solution_greedy_dp(self, solution):
        problem = self.problem
        capacities = problem.capacities
        costs = problem.costs
        weights = problem.weights

        dests = len(solution)
        vehicles = len(capacities)
        div_costs = np.zeros(dests)
        for i in range(1, dests - 1):
            d1 = solution[i]
            d2 = solution[i+1]
            div_costs[i] = costs[d1][0] + costs[0][d2] - costs[d1][d2]

        dp = np.zeros((dests, vehicles + 1), dtype=float)
        prev_state = np.zeros((dests, vehicles + 1), dtype=int)

        for i in range(dests):
            if i != 0:
                dp[i][0] = self.inf
            for j in range(1, vehicles + 1):
                cap = capacities[j-1]
                pointer = i
                dp[i][j] = dp[i][j-1]
                prev_state[i][j] = i
                while pointer > 0 and cap >= weights[solution[pointer]]:
                    pointer -= 1
                    new_cost = div_costs[pointer] + dp[pointer][j-1]
                    if new_cost < dp[i][j]:
                        dp[i][j] = new_cost
                        prev_state[i][j] = pointer
                    cap -= weights[solution[pointer + 1]]

        new_solution = []
        pointer = dests - 1
        for j in reversed(range(1, vehicles + 1)):
            prev = prev_state[pointer][j]
            if prev != pointer:
                lis = solution[(prev + 1):(pointer + 1)]
                if prev != -1:
                    lis = [0] + lis
                if pointer != dests - 1:
                    lis = lis + [0]
                new_solution.append(lis)
            else:
                new_solution.append([])
            pointer = prev
        
        new_solution.reverse()
        return VRPSolution(problem, None, None, new_solution)

    # Creates random permutations of vehicles and using _divide_solution_greedy for
    # each of them. 
    # random - number of permutations.
    def _divide_solution_random(self, solution):
        random = self.random
        capacities = self.problem.capacities.copy()
        vehicles = len(capacities)

        new_solution = None
        best_cost = self.inf

        for i in range(random):
            perm = np.random.permutation(vehicles)
            inv = [list(perm).index(j) for j in range(vehicles)]
            self.problem.capacities = [capacities[j] for j in perm]

            new_sol = self._divide_solution_greedy_dp(solution)
            new_cost = new_sol.total_cost()

            if new_cost < best_cost and new_sol.check():
                best_cost = new_cost
                new_solution = new_sol
                new_solution.solution = [new_sol.solution[j] for j in inv]

            self.problem.capacities = capacities

        return new_solution

    def solve(self, only_one_const, order_const, solver_type = 'cpu'):
        problem = self.problem
        capacity = 0
        weights = problem.weights
        for w in weights:
            capacity += w

        # Creating new problem with one vehicle.
        sources = [0]
        dests = problem.dests
        costs = problem.costs
        new_capacities = [capacity]
        new_problem = VRPProblem(sources, costs, new_capacities, dests, weights)

        if len(dests) == 0:
            sol = [[] for _ in range(len(problem.capacities))]
            return VRPSolution(problem, None, None, sol)

        solver = self.solver
        solver.set_problem(new_problem)
        solution = solver.solve(only_one_const, order_const, solver_type = solver_type)

        sol = solution.solution[0]
        return self._divide_solution_random(sol)
