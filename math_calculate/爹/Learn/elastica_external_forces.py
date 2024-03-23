import numpy as np
from elastica_linalg import _batch_matvec
from elastica_typing import SystemType, RodType

from numba import njit

class NoForces:
    def __init__(self):
        pass

    def apply_forces(self, system: SystemType, time: np.float64 = 0.0):
        return
    
    def apply_torques(self, system: SystemType, time: np.float64 = 0.0):
        return