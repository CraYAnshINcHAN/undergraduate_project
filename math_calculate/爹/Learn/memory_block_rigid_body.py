import numpy as np
from typing import Sequence, List

from rigid_body import RigidBodyBase
from rigidbody_data_structures import _RigidRodSymplecticStepperMixin

class MemoryBlockRigidBody(RigidBodyBase, _RigidRodSymplecticStepperMixin):
    def __init__(self, systems: Sequence, system_idx_list: List[int]):

        self.n_bodies = len(systems)
        self.n_elems = self.n_bodies
        self.n_nodes = self.n_elems
        self.system_idx_list = np.array(system_idx_list, dtype = np.int64)

        #Allocate block structure using system collection
        self.allocate_block_variables_scalars(systems)
        self.allocate_block_variables_vectors(systems)
        self.allocate_block_variables_matrix(systems)
        self.allocate_block_variables_for_symplectic_stepper(systems)

        #Initialize the mixin class for symplectic time-stepper
        _RigidRodSymplecticStepperMixin.__init__(self, systems)

    def allocate_block_variables_scalars(self, systems:Sequence):
        map_scalar_dofs_in_rigid_bodies = {
            "radius": 0,
            "length": 1,
            "density": 2,
            "volume": 3,
            "mass": 4,
        }
        self.scalar_dofs_in_rigid_bodies = np.zeros(
            (len(map_scalar_dofs_in_rigid_bodies), self.n_elems)
        )

        for k,v in map_scalar_dofs_in_rigid_bodies.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.scalar_dofs_in_rigid_bodies[v], (self.n_elems,)
            )
        
        for k,v in map_scalar_dofs_in_rigid_bodies.items():
            for system_idx, system in enumerate(systems):
                self.__dict__[k][..., system_idx : system_idx+1] = system.__dict__[k]
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., system_idx : system_idx+1]
                )
        
    def allocate_block_variables_vectors(self, systems:Sequence):
        map_vector_dofs_in_rigid_bodies = {
            "position_collection": 0,
            "external_forces": 1,
            "external_torques": 2,
        }
        self.vector_dofs_in_rigid_bodies = np.zeros(
            (len(map_vector_dofs_in_rigid_bodies), 3 * self.n_nodes)
        )

        for k,v in map_vector_dofs_in_rigid_bodies.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.vector_dofs_in_rigid_bodies[v], (3, self.n_nodes)
            )
        
        for k,v in map_vector_dofs_in_rigid_bodies.items():
            for system_idx, system in enumerate(systems):
                self.__dict__[k][..., system_idx : system_idx+1] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., system_idx : system_idx+1]
                )

    def allocate_block_variables_matrix(self, systems:Sequence):
        map_matrix_dofs_in_rigid_bodies = {
            "director_collections": 0,
            "mass_second_moment_of_intertia": 1,
            "inv_mass_second_moment_of_inertia": 2,
        }
        self.matrix_dofs_in_rigid_bodies = np.zeros(
            (len(map_matrix_dofs_in_rigid_bodies), 3 * 3 * self.n_nodes)
        )

        for k,v in map_matrix_dofs_in_rigid_bodies.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.matrix_dofs_in_rigid_bodies[v], (3, 3, self.n_nodes)
            )
        
        for k,v in map_matrix_dofs_in_rigid_bodies.items():
            for system_idx, system in enumerate(systems):
                self.__dict__[k][..., system_idx : system_idx+1] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., system_idx : system_idx+1]
                )
    
    def allocate_block_variables_for_symplectic_stepper(self, systems:Sequence):
        
        map_rate_collection = {
            "velocity_collection": 0,
            "omega_collection": 1,
            "acceleration_collection": 2,
            "alpha_collection": 3,
        }
        self.rate_collection = np.zeros(
            (len(map_rate_collection), 3 * self.n_elems)
        )

        for k,v in map_rate_collection.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.rate_collection[v], (3, self.n_elems)
            )
        
        self.v_w_collection = np.lib.stride_tricks.as_strided(self.rate_collection[0:2],(2,3*self.n_elems))
        self.dvdt_dwdt_collection = np.lib.stride_tricks.as_strided(self.rate_collection[2:-1],(2,3*self.n_elems))

        for k,v in map_rate_collection.items():
            for system_idx, system in enumerate(systems):
                self.__dict__[k][..., system_idx : system_idx+1] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., system_idx : system_idx+1]
                )


