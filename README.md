# CVRP approach using quantum computing

Few quantum approaches for CVRP problems, based on D-Wave's quantum annealing. Older version of this code was base for publication https://link.springer.com/chapter/10.1007%2F978-3-030-50433-5_42. You can find more detailed description of solutions in it.

## Getting started

Firstly, you need to be able use D-Wave. If you are not, follow this https://docs.ocean.dwavesys.com/en/stable/overview/install.html.

## Input

There are two input formats. You can find examples in formats directory.

### Full input

It needs graph file and test file. In graph file you need to provide edges description : in each line should be two nodes' ids and cost. Cost is what you want to optimize, for example distance or time. In test file you need to provide information about sources, destinations and vehicles. If you want to solve vrp (without capacities), you only need to provide sources' and destinations' ids and number of vehicles. If you want to solve cvrp, you also need to provide destinations' weights and vehicles' capacities. 

If you have both files, you can use function 'read_full_test' (from input.py) to obtain VRPProblem object. Note that if you want to solve vrp, you need to set capacity parameter to False.

Using this format can take long time on big graphs with many sources and destinations, so if you want to use same problem many times, I recommend to use second format. You can use 'create_test' (from input.py) function to generate input in second format from this format.

### Normal input

It needs only test file. You need to provide information about sources, destinations, vehicles and costs of travelling between sources and destinations. If you want to solve vrp (without capacities), you only need to provide sources' and destinations' ids, number of vehicles and costs. If you want to solve cvrp, you also need to provide destinations' weights and vehicles' capacities.

Sources and destinations will be enumerated with natural numbers. If you have n sources and m destinations, sources will have numbers 0, 1, 2, ..., n - 1 and destinations will have numbers n, n + 1, n + 2, ..., n + m - 1. You need to provide (n + m) x (n + m) matrix with costs.   

If you have test file, you can use function 'read_test' (from input.py) to obtain VRPProblem object.

## Solvers

Once you have VRPProblem object, you need to choose a solver. All solvers have the same 'solve' interface. You just need to provide VRPProblem object, two constants and information if you want to solve problem on cpu or qpu. You can find more detailed description in vrp_solvers.py. You can find examples of using every solver in examples directory.

### FullQuboSolver

It solves vrp (and not cvrp) by formulating problem as QUBO and solving it with D-Waves solver. It's the weakest solver that works effectively on problems with max 30 destinations and few (1-3) vehicles. 

### AveragePartitionSolver

It is FullQuboSolver, but with additional constraint that each vehicle serves approximately the same number of destinations. There is additional attribute 'limit_radius', which is maximum absolute difference between number of destinations that vehicle serves and average number of destinations that each vehicle serves. For small values of limit_radius, solver works effectively on tests with max 50 destinations.

Note that if you have only one vehicle, this solver works exactly the same as FullQuboSolver.

### DBScanSolver

This solver uses more classical approaches. It solves problem by solving small instances of TSP problem with FullQuboSolver. 'max_len' attribute is maximum number of destinations in problems that will be solve by FullQuboSolver. It has also 'anti_noiser' parameter, which says solver if it needs to get rid of singleton clusters in dbscan. It is expected to that setting 'anti_noiser' False would work better if there is a lot of isolated destinations in a problem.

Note that default 'max_len' attribute is 10. It is so small that FullQuboSolver can find the best solution. Experiments shows that this value works effectively on tests with 250 destinations. But of course, I encourage to experiment with bigger values of this parameter on different tests.

Also, I want to optimize classical parts of this solver to make bigger experiments possible.

This solver is for vrp, but it is implemented some prototype of cvrp in it, which should work when all capacities are the same.

### SolutionPartitioningSolver

This is vrp and cvrp solver, which use another solver ('solver' attribute) to solve TSP, and then tries to divide solution to consecutive parts that will be served by vehicles. There is also 'random' attribute. Bigger value of it should give better solutions with bigger execution time.

Using this solver with DBScanSolver should give the best effect. On smaller tests, you can use it with FullQuboSolver, to reduce size of QUBO and achieve good solution for tests with number of destinations up to 50.

Note that using this solver with AveragePartitionSolver is exactly the same as using it with FullQuboSolver.

## Output

'solve' function of solver returns VRPSolution object, which has solution attribute, which is list of lists of vehicles' paths. First and last numbers of list are sources, and between them are continous destinations.

Note that independetly of used input format, sources and destinations will be enumerated. Numbers form 0 to (number of sources - 1) are sources and next numbers are destinations.
