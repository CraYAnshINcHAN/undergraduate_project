from numba import njit
from elastica_boundary_conditions import ConstraintBase

#这三个函数就是让输入的向量，标量，矩阵的某些部分的值相等
@njit(cache=True)
def _synchronize_periodic_boundary_of_vector_collection(input, periodic_idx):
    for i in range(3):
        for k in range(periodic_idx.shape[1]):
            input[i, periodic_idx[0, k]] = input[i, periodic_idx[1, k]]

@njit(cache=True)
def _synchronize_periodic_boundary_of_scalar_collection(input, periodic_idx):
    for k in range(periodic_idx.shape[1]):
        input[periodic_idx[0, k]] = input[periodic_idx[1, k]]

@njit(cache=True)
def _synchronize_periodic_boundary_of_matrix_collection(input, periodic_idx):
    for i in range(3):
        for j in range(3):
            for k in range(periodic_idx.shape[1]):
                input[i, j, periodic_idx[0, k]] = input[i, j, periodic_idx[1, k]]

class _ConstrainPeriodicBoundaries(ConstraintBase):

    def __init__(self, **kwargs):
        super.__init__(**kwargs)
    
    def constrain_values(self, rod, time):
        _synchronize_periodic_boundary_of_vector_collection(
            rod.position_collection, rod.periodic_boundary_nodes_idx
        )
        _synchronize_periodic_boundary_of_matrix_collection(
            rod.director_collection, rod.periodic_boundary_elems_idx
        )
    def constrain_rates(self, rod, time):
        _synchronize_periodic_boundary_of_vector_collection(
            rod.velocity_collection, rod.periodic_boundary_nodes_idx
        )
        _synchronize_periodic_boundary_of_matrix_collection(
            rod.omega_collection, rod.periodic_boundary_elems_idx
        )