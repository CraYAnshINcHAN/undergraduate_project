from abc import ABC, abstractmethod
from numba import njit
from elastica_typing import SystemType, RodType
import numpy as np
from typing import Optional
class ConstraintBase(ABC):
    _system: SystemType
    _constrained_position_idx: np.ndarray
    _constrained_director_idx: np.ndarray
    def __init__(self, *args, **kwargs):
        #initialize boundary condition
        try:
            self._system = kwargs["system"]
            self._constrained_position_idx = np.arrary(
                kwargs.get("constrained_position_idx", []), dtype=int
            )
            self._constrained_velocity_idx = np.array(
                kwargs.get("constrained_director_idx", []), dtype=int
            )
        except KeyError:
            raise KeyError(
                "Please use simulator.constrain(...).using(...) to establish constraints"
            )
    @property
    def system(self) -> SystemType:
        """get system(rod or rigid body) reference"""
        return self._system
    @property
    def constrained_position_idx(self) -> Optional[np.ndarray]:
        """get position-indices passed to "using" """
        #TODO:This should be immutable somehow
        return self._constrained_position_idx
    @property
    def constrained_director_idx(self) -> Optional[np.ndarray]:
        """get position-indices passed to "using" """
        #TODO:This should be immutable somehow
        return self._constrained_director_idx
    
    @abstractmethod
    def constrain_values(self, system: SystemType, time: float)->None:
        """constrain values of the system"""
        pass
    @abstractmethod
    def constrain_rates(self, system: SystemType, time: float)->None:
        """constrain rates of the system"""
        pass

class OneEndFixedBC(ConstraintBase):
    def __init__(self, fixed_position, fixed_directors, **kwargs):
        super().__init__(**kwargs)
        self.fixed_position_collection = np.array(fixed_position)
        self.fixed_director_collection = np.array(fixed_directors)
    
    def constrain_values(self, system: SystemType, time: float) -> None:
        self.compute_constrain_values(
            system.position_collection,
            system.director_collection,
            self.fixed_position_collection,
            self.fixed_director_collection,
        )