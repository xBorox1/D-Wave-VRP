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

