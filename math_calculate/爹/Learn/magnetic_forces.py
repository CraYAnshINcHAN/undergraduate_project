from elastica_external_forces import NoForces
from cosserat_rod import CosseratRod
from elastica_linalg import _batch_matvec, _batch_cross, _batch_norm
from magnetic_field import BaseMagneticField
import numpy as np
from typing import Union

class MagneticForces(NoForces):
    def __init__(
        self,
        external_magnetic_field: BaseMagneticField,
        magnetization_density: Union[float, np.ndarray],
        magnetization_direction: np.ndarray,
        rod_volume: np.ndarray, 
        rod_director_collection: np.ndarray,
    ):
        super(NoForces, self).__init__()
        self.external_magnetic_field = external_magnetic_field
        rod_n_elem = rod_volume.shape[0]

        #if fixed value, then expand to rod element size
        if magnetization_direction.shape == (3,) or magnetization_direction.shape == (3, rod_n_elem):
            magnetization_direction = magnetization_direction.reshape(3, -1) * np.ones(
                (rod_n_elem,)
            )
        else:
            raise ValueError("Magnetization direction should be either 3 or 3 x n_elems")
        
        #normalize for unit vectors
        magnetization_direction /= _batch_norm(magnetization_direction)
        #convert to local frame

        #这里我有点问题，这是从世界坐标系转到杆坐标系吗？感觉应该不是这样的，给我的感觉，这表现的是磁化方向随杆的旋转而旋转
        #但是这一块主要还是得看之后的计算给出的杆的坐标系的表达方式才能够明白
        magnetization_direction_in_material_frame = _batch_matvec(
            rod_director_collection, magnetization_direction
        )

        if not(
            isinstance(magnetization_density, float)
            or magnetization_density.shape == (rod_n_elem, )
        ):
            raise ValueError("Magnetization density should be either a float or an array")
        
        self.magnetization_collection = magnetization_density * rod_volume * magnetization_direction_in_material_frame
    
    def apply_torques(self, rod:CosseratRod, time:np.float64 = 0.0):
        rod.external_torques += _batch_cross(
            self.magnetization_collection,
            #convert external_magnetic_field to local frame
            _batch_matvec(
                rod.director_collection,
                self.external_magnetic_field.value(time = time).reshape(3,1)*np.ones((rod.n_elems, )),
            ),
        )



