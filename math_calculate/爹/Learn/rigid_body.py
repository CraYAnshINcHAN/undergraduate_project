import numpy as np
from abc import ABC
from elastica_linalg import _batch_matvec, _batch_cross

class RigidBodyBase(ABC):
    def __init__(self):
        self.position_collection = NotImplementedError
        self.velocity_collection = NotImplementedError
        self.acceleration_collection = NotImplementedError
        self.omega_collection = NotImplementedError
        self.alpha_collection = NotImplementedError
        self.director_collection = NotImplementedError

        self.external_forces = NotImplementedError
        self.external_torques = NotImplementedError

        self.mass = NotImplementedError

        self.mass_second_moment_of_inertia = NotImplementedError
        self.inv_mass_second_moment_of_inertia = NotImplementedError