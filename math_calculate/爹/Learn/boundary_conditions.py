import warnings
from typing import Optional

import numpy as np

from abc import ABC, abstractmethod

from numba import njit

from elastica_linalg import _batch_matvec, _batch_matrix_transpose
from elastica_rotations import _get_rotation_matrix
from elastica_typing import SystemType, RodType

class ConstraintBase(ABC):
    _system: SystemType
    _constrained_position_idx: np.ndarray
    _constrained_director_idx: np.ndarray

    def __init__(self, *args, **kwargs):
        """Initialize boundary conditions"""
        try:
            self._system = kwargs["_system"]
            self._constrained_position_idx = np.array(
                kwargs.get("constrained_position_idx", []), dtype = int
            )
            self._constrained_director_idx = np.array(
                kwargs.get("constrained_director_idx", []), dtype = int
            )
        except KeyError:
            raise ValueError(
                "ConstraintBase must be initialized with a system"
            )
        
        @property
        def system(self) -> SystemType: 
            return self._system
        
        @property
        def constrained_position_idx(self) -> Optional[np.ndarray]:
            return self._constrained_position_idx
        
        @property
        def constrained_director_idx(self) -> Optional[np.ndarray]:
            return self._constrained_director_idx
        
        @abstractmethod
        def constrain_values(self, system:SystemType, time:float):
            # TODO: in the future, remove rod and use self.system instead
            pass
        
        @abstractmethod
        def constrain_rates(self, system:SystemType, time:float):
            pass

class OneEndFixedBC(ConstraintBase):
    def __init__(self, fixed_position, fixed_directors, **kwargs):
        super().__init__(**kwargs)
        self.fixed_position_collection = np.array(fixed_position)
        self.fixed_director_collection = np.array(fixed_directors)

    def constrain_values(self, system:SystemType, time:float) -> None:
        self.compute_constrain_values(
            system.position_collection,
            self.fixed_position_collection,
            system.director_collection,
            self.fixed_director_collection,
        )
    
    def constrain_rates(self, system: SystemType, time:float) -> None:
        self.compute_constrain_rates(
            system.velocity_collection,
            system.omega_collection,
        )

    @staticmethod
    @njit(cache = True)
    def compute_constrain_values(
        position_collection,
        fixed_position_collection,
        director_collection,
        fixed_directors_collection,
    ):
        position_collection[..., 0] = fixed_position_collection
        director_collection[..., 0] = fixed_directors_collection

    @staticmethod
    @njit(cache = True)
    def compute_constrain_rates(
        velocity_collection,
        omega_collection,
    ):
        velocity_collection[..., 0] = 0.0
        omega_collection[..., 0] = 0.0