from itertools import product

# Simple class that helps creating qubo dict for DWave solvers.
class Qubo:
    def __init__(self):
        self.dict = dict()

    # Creates new field in dict.
    def create_field(self, field):
        self.dict[field] = 0

    # Creates new field in dict if it doesn't exist.
    def create_not_exist_field(self, field):
        if field in self.dict:
            return
        self.create_field(field)

    # Adds constraint to qubo that exactly one of given variables should be equal to 1.
    # Const parameter defines 'weight' of that constraint.
    def add_only_one_constraint(self, variables, const):
        for var in variables:
            self.create_not_exist_field((var, var))
            self.dict[(var, var)] -= 2 * const
        for field in product(variables, variables):
            self.create_not_exist_field(field)
            self.dict[field] += const

    # Adds field to dict with given value.
    def add(self, field, value):
        self.create_not_exist_field(field)
        self.dict[field] += value

    # Merges qubo with another qubo. Consts parameters define 'weight' of each qubo.
    def merge_with(self, qubo, const1, const2):
        for field in self.dict:
            self.dict[field] *= const1
        for field in qubo.dict:
            self.create_not_exist_field(field)
            self.dict[field] += qubo.dict[field] * const2

    # Returns qubos dict which can be used in communication with DWave.
    def get_dict(self):
        return self.dict
