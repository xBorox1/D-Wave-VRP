# File simplifies communication with DWave solvers. 

from dwave.system.samplers import DWaveSampler
from dwave.system.composites import EmbeddingComposite
from dwave_qbsolv import QBSolv
from hybrid.reference.kerberos import KerberosSampler
from dimod.reference.samplers import ExactSolver
import hybrid
import dimod
import neal

# Creates hybrid solver with hardcoded configuration.
def hybrid_solver():
    workflow = hybrid.Loop(
        hybrid.RacingBranches(
        hybrid.InterruptableTabuSampler(),
        hybrid.EnergyImpactDecomposer(size=30, rolling=True, rolling_history=0.75)
        | hybrid.QPUSubproblemAutoEmbeddingSampler()
        | hybrid.SplatComposer()) | hybrid.ArgMin(), convergence=1)
    return hybrid.HybridSampler(workflow)

# Gets cpu or qpu solver.
# For qpu hybrid solver is used. For cpu qbsolv.
def get_solver(solver_type):
    solver = None
    if solver_type == 'qpu':
        solver = hybrid_solver()
    if solver_type == 'cpu':
        solver = QBSolv()
    return solver

# Solves qubo on qpu. Returns list of solutions.
def solve_qubo(qubo, solver_type = 'cpu'):
    sampler = get_solver(solver_type)
    response = sampler.sample_qubo(qubo.dict)
    return list(response)[0]
    
