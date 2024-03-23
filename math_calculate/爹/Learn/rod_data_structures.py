import numpy as np
from numba import njit
from elastica_rotations import _get_rotation_matrix
from elastica_linalg import _batch_matmul

#不知道这个是干嘛的，但是这个是一个辛积分器的mixin类
#这个类的作用是将辛积分器的实现与实际的加法、乘法等公式分开
#之后用到其中内容的时候再来看就好啦
class _RodSymplecticStepperMixin:
    def __init__(self):
        self.kinematic_state = _KinematicState(
            self.position_collection, self.director_collection
        )
        self.dynamic_state = _DynamicState(
            self.v_w_collection,
            self.dvdt_dwdt_collection,
            self.velocity_collection,
            self.omega_collection,
        )

        self.kinematic_rates = self.dynamic_state.kinematic_rates

    def update_internal_forces_and_torques(self, time, *args, **kwargs):
        self.compute_internal_forces_and_torques(time)

    def dynamic_rates(self, time, prefac, *args, **kwargs):
        self.update_accletations(time)
        return self.dynamic_state.dynamic_rates(time, prefac, *args, **kwargs)
    
    def reset_external_forces_and_torques(self, time, *args, **kwargs):
        self.zeroed_out_external_forces_and_torques.fill(0.0)

class _KinematicState:
    #用于辛积分器的状态储存器，其中状态以（x,Q）保存
    def __init__(self, position_collection_view, direction_collection_view):
        self.postion_collection = position_collection_view
        self.direction_collection = direction_collection_view

class _DynamicState:
    #用于辛积分器的状态储存器，其中状态以(v,w,dv/dt,dw/dt)保存
    #将数据包装为状态对象，将积分器的实现与实际的加法、乘法等公式分开
    def __init__(
            self,
            v_w_collection,
            dvdt_dw_dt_collection,
            velocity_collection,
            omega_collection,
    ):
        super(_DynamicState, self).__init__()
        self.rate_collection = v_w_collection
        self.dvdt_dw_dt_collection = dvdt_dw_dt_collection
        self.velocity_collection = velocity_collection
        self.omega_collection = omega_collection

    def kinematic_rates(self, time, *args, **kwargs):
        return self.velocity_collection, self.omega_collection
    
    def dynamic_rates(self, time, prefac, *args, **kwargs):
        return prefac * self.dvdt_dw_dt_collection
    
@njit(cache=True)
def overload_operator_kinematic_numba(
    n_nodes,
    prefac,
    position_collection,
    director_collection,
    velocity_collection,
    omega_collection,
):
    for i in range(3):
        for k in range(n_nodes):
            position_collection[i, k] += prefac * velocity_collection[i, k]
    rotation_matrix = _get_rotation_matrix(1.0, prefac * omega_collection)
    director_collection[:] = _batch_matmul(rotation_matrix, director_collection)

    return

@njit(cache=True)
def overload_operator_dynamic_numba(rate_collection, scaled_second_deriv_array):
    blocksize = scaled_second_deriv_array.shape[1]

    for i in range(2):
        for k in range(blocksize):
            rate_collection[i,k] += scaled_second_deriv_array[i,k]
    
    return
