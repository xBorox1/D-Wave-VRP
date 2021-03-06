# Copyright 2021 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import unittest
import os
import sys

project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class IntegrationTests(unittest.TestCase):
    """Run all example files with small problems to make sure there aren't any crashes."""
    def get_output(self, example_file):
        demo_file = os.path.join(project_dir, example_file)
        output = subprocess.check_output([sys.executable, demo_file])
        return str(output).upper()

    def test_solution_partitioning_solver(self):
        output = self.get_output('examples/SolutionPartitioningSolver.py')

        with self.subTest(msg="Verify if output contains a solution for every graph tested. \n"):
            num_solutions = output.count("SOLUTION : ")
            self.assertEqual(num_solutions, 3)
            self.assertNotIn("SOLVER HASN'T FIND SOLUTION.", output)
        with self.subTest(msg="Verify if output contains a total cost for every graph tested. \n"):
            num_total_costs = output.count("TOTAL COST : ")
            self.assertEqual(num_total_costs, 3)

    def test_solution_partitioning_solver_2(self):
        output = self.get_output('examples/SolutionPartitioningSolver2.py')

        with self.subTest(msg="Verify if output contains a solution for every graph tested. \n"):
            num_solutions = output.count("SOLUTION : ")
            self.assertEqual(num_solutions, 3)
            self.assertNotIn("SOLVER HASN'T FIND SOLUTION.", output)
        with self.subTest(msg="Verify if output contains a total cost for every graph tested. \n"):
            num_total_costs = output.count("TOTAL COST : ")
            self.assertEqual(num_total_costs, 3)
        with self.subTest(msg="Verify if output contains weights for every graph tested. \n"):
            num_weights = output.count("WEIGHTS : ")
            self.assertEqual(num_weights, 3)

    def test_average_partitioning_solver(self):
        output = self.get_output('examples/AveragePartitionSolver.py')

        with self.subTest(msg="Verify if output contains a solution for every graph tested. \n"):
            num_solutions = output.count("SOLUTION : ")
            self.assertEqual(num_solutions, 3)
            self.assertNotIn("SOLVER HASN'T FIND SOLUTION.", output)
        with self.subTest(msg="Verify if output contains a total cost for every graph tested. \n"):
            num_total_costs = output.count("TOTAL COST : ")
            self.assertEqual(num_total_costs, 3)

    def test_full_qubo_solver(self):
        output = self.get_output('examples/FullQuboSolver.py')

        with self.subTest(msg="Verify if output contains a solution for every graph tested. \n"):
            num_solutions = output.count("SOLUTION : ")
            self.assertEqual(num_solutions, 2)
            self.assertNotIn("SOLVER HASN'T FIND SOLUTION.", output)
        with self.subTest(msg="Verify if output contains a total cost for every graph tested. \n"):
            num_total_costs = output.count("TOTAL COST : ")
            self.assertEqual(num_total_costs, 2)

if __name__ == '__main__':
    unittest.main()
