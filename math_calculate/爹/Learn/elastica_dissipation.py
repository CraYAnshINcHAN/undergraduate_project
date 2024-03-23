from elastica_typing import RodType, SystemType
from abc import ABC, abstractmethod

from numba import njit

import numpy as np

class DamperBase(ABC):
    _system: SystemType

    def __init__(self, *args, **kwargs):
        try:
            self._system = kwargs["_system"]
        except KeyError:
            raise KeyError("DamperBase must be initialized with a system")
    
    @property
    def system(self):
        return self._system
    
    @abstractmethod
    def dampen_rates(self, system:SystemType, time:float):
        # TODO
        pass

class AnalyticalLinearDamper(DamperBase):
    def __init__(self, damping_constant, time_step, **kwargs):
        super().__init__(**kwargs)
        # compute the damping coefficient for translational velocity
        nodal_mass = self._system.mass
        self.translational_damping_coefficient = np.exp(-damping_constant*time_step)

        if self._system.ring_rod_flag:
            element_mass = nodal_mass
        else:
            element_mass = 0.5 * (nodal_mass[1:] + nodal_mass[:-1])
            element_mass[0] += 0.5 * nodal_mass[0]
            element_mass[-1] += 0.5 * nodal_mass[-1]
        self.rotational_damping_coefficient = np.exp(
            -damping_constant * time_step * element_mass * np.diagonal(self._system.inv_mass_second_moment_of_inertia).T
        )

    def dampen_rates(self, rod:RodType, time:float):
        rod.velocity_collection[:] = (
            rod.velocity_collection * self.translational_damping_coefficient
        )

        rod.omega_collection[:] = (
            rod.omega_collection * np.power(self.rotational_damping_coefficient, rod.dilatation)
        )