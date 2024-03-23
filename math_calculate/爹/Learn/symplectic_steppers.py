import numpy as np
from rod_data_structures import overload_operator_kinematic_numba, overload_operator_dynamic_numba


class SymplecticStepperTag:
    def __init__(self):
        pass
class PositionVerlet:
    Tag = SymplecticStepperTag()

    def __init__(self, dt):
        pass
    
    def _first_prefactor(self, dt):
        return 0.5 * dt
    
    def _first_kinematic_step(self, System, time: np.float64, dt: np.float64):
        prefac = self._first_prefactor(dt)

        overload_operator_kinematic_numba(
            System.n_nodes,
            prefac,
            System.kinematic_states.position_collection,
            System.kinematic_states.director_collection,
            System.velocity_collection,
            System.omega_collection,
        )

    def _first_dynamic_step(self, System, time: np.float64, dt: np.float64):
        
        overload_operator_dynamic_numba(
            System.dynamic_states.rate_collection,
            System.dynamic_rates(time,dt),
        )


