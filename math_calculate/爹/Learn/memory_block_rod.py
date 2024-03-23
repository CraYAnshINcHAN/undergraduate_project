import numpy as np
from typing import Sequence
from memory_block_rod_base import(
    MemoryBlockRodBase,
    make_block_memory_metadata,
    make_block_memory_periodic_boundary_metadata,
)
from rod_data_structures import _RodSymplecticStepperMixin
from _reset_ghost_vector_or_scalar import _reset_scalar_ghost
from cosserat_rod import (
    CosseratRod,
    _compute_sigma_kappa_for_blockstructure
)
from elastica_synchronize_periodic_boundary import(
    _synchronize_periodic_boundary_of_vector_collection,
    _synchronize_periodic_boundary_of_scalar_collection,
    _synchronize_periodic_boundary_of_matrix_collection,
)

class MemoryBlockCosseratRod(
    MemoryBlockRodBase, CosseratRod, _RodSymplecticStepperMixin
):
    def __init__(self, systems: Sequence, system_idx_list):
        system_straight_rod = []
        system_ring_rod = []
        system_idx_list_ring_rod = []
        system_idx_list_straight_rod = []
        for k, system_to_be_added in enumerate(systems):
            if system_to_be_added.ring_rod_flag:
                system_ring_rod.append(system_to_be_added)
                system_idx_list_ring_rod.append(system_idx_list[k])
                self.ring_rod_flag = True
            else:
                #在system_straight_rod中加入系统
                #在system_idx_list_straight_rod中加入系统的索引
                system_straight_rod.append(system_to_be_added)
                system_idx_list_straight_rod.append(system_idx_list[k])
        
        #sorted systems
        systems = system_straight_rod + system_ring_rod
        self.system_idx_list = np.array(
            system_idx_list_straight_rod + system_idx_list_ring_rod
        )
        #获得每个系统的元素数量，然后将这些数量保存到数组中
        n_elems_straight_rods = np.array(
            [x.n_elems for x in system_straight_rod], dtype = np.int64
        )
        n_elems_ring_rods = np.array(
            [x.n_elems for x in system_ring_rod], dtype = np.int64
        )

        n_straight_rods = len(system_straight_rod)
        n_ring_rods = len(system_ring_rod)
        #
        self.n_elems_in_rods = np.hstack((n_elems_straight_rods, n_elems_ring_rods + 2))
        self.n_rods = len(systems)

        (
            self.n_elems,
            self.ghost_nodes_idx,
            self.ghost_elems_idx,
            self.ghost_voronoi_idx,
        ) = make_block_memory_metadata(self.n_elems_in_rods)
        self.n_nodes = self.n_elems + 1
        self.n_voronoi = self.n_elems - 1
        #这应该是每根杆开始节点的索引，第一根杆是0，第二根杆在第一根杆的幽灵节点的下一个节点,但是我们这边就一根杆所以就是0
        self.start_idx_in_rod_nodes = np.hstack(
            (0, self.ghost_nodes_idx + 1)
            )
        #这应该是每根杆结束节点的索引，第一根杆是幽灵节点,但是我们这里就一根杆，所以还是0
        self.end_idx_in_rod_nodes = np.hstack(
            (self.ghost_nodes_idx, self.n_nodes)
        )
        self.start_idx_in_rod_elems = np.hstack(
            (0, self.ghost_elems_idx[1::2] + 1)
        )
        #这些其实都没有变过，因为我们只有一根杆
        self.end_idx_in_rod_elems = np.hstack((self.ghost_elems_idx[::2], self.n_elems))
        self.start_idx_in_rod_voronoi = np.hstack((0, self.ghost_voronoi_idx[2::3] + 1))
        self.end_idx_in_rod_voronoi = np.hstack((self.ghost_voronoi_idx[::3], self.n_voronoi))

        #这只在出现了ringrod时才会用到，先不用管,结果都是空矩阵
        (
            _,
            self.periodic_boundary_nodes_idx,
            self.periodic_boundary_elems_idx,
            self.periodic_boundary_voronoi_idx,
        ) = make_block_memory_periodic_boundary_metadata(n_elems_ring_rods)

        if n_ring_rods !=0 :
            pass
        
        #下面四个函数就是给这个类新建一些属性并为其赋值，所新建的属性都是RodSystem中包含的属性
        #所赋的值就是system中的属性的值
        self.allocate_block_variables_in_nodes(systems)
        self.allocate_block_variables_in_elements(systems)
        self.allocate_block_variables_in_voronoi(systems)
        self.allocate_block_variables_for_symplectic_stepper(systems)

        _reset_scalar_ghost(self.mass, self.ghost_nodes_idx, 1.0)
        _reset_scalar_ghost(self.rest_lengths, self.ghost_elems_idx, 1.0)
        _reset_scalar_ghost(self.rest_voronoi_lengths, self.ghost_voronoi_idx, 1.0)

        _compute_sigma_kappa_for_blockstructure(self)

        if n_ring_rods!= 0:
            pass

        #Initialize the mixin class for symplectic time-stepper
        _RodSymplecticStepperMixin.__init__(self)

    def allocate_block_variables_in_nodes(self, systems: Sequence):
        map_scalar_dofs_in_rod_nodes = {"mass": 0}
        self.scalar_dofs_in_rod_nodes = np.zeros(
            (len(map_scalar_dofs_in_rod_nodes), self.n_nodes)
        )
        #__dict__是每个类都有的一个属性，是一个字典，里面保存了这个类的所有属性
        #这里属性的名字就是map_scalar_dofs_in_rod_nodes的键，属性的值就是map_scalar_dofs_in_rod_nodes的值
        #而这个循环的作用就是在这个类中新建了一些属性，这些属性的值是一个数组，这个数组的长度是self.n_nodes
        #而属性的名字就是map_scalar_dofs_in_rod_nodes的键，这样就在这个类中新建了一些属性

        for k,v in map_scalar_dofs_in_rod_nodes.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.scalar_dofs_in_rod_nodes[v], (self.n_nodes,)
            )
        
        #简单来说上一个循环是为了这个类创建一些属性，而这个循环就是为这些属性赋值
        #而所赋的值也就是system中的属性的值
        for k,v in map_scalar_dofs_in_rod_nodes.items():
            #enumerate会返回一个元组，元组的第一个元素是索引，第二个元素是值
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_nodes[system_idx]
                end_idx = self.end_idx_in_rod_nodes[system_idx]
                #这里的self.__dict__[k]是一个数组，所以可以用切片，这里的切片是把system.__dict__[k]的值复制到self.__dict__[k]中
                #也就是在self.__dict__[k]中的start_idx到end_idx的位置上复制system.__dict__[k]的值，这样就把每根杆的值都复制到了
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
                _synchronize_periodic_boundary_of_scalar_collection(
                    self.__dict__[k], self.periodic_boundary_nodes_idx
                )

        map_vector_dofs_in_rod_nodes = {
            "position_collection" : 0,
            "internal_forces" : 1,
            "external_forces" : 2,
        }

        self.vector_dofs_in_rod_nodes = np.zeros(
            (len(map_vector_dofs_in_rod_nodes), 3 * self.n_nodes)
        )
        for k,v in map_vector_dofs_in_rod_nodes.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.vector_dofs_in_rod_nodes[v], (3, self.n_nodes)
            )


        for k,v in map_vector_dofs_in_rod_nodes.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_nodes[system_idx]
                end_idx = self.end_idx_in_rod_nodes[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_vector_collection(
                self.__dict__[k], self.periodic_boundary_nodes_idx
            )
    
    def allocate_block_variables_in_elements(self, systems: Sequence):
        map_scalar_dofs_in_rod_elems = {
            "radius": 0,
            "volume": 1,
            "density": 2,
            "lengths": 3,
            "rest_lengths": 4,
            "dilatation": 5,
            "dilatation_rate": 6,
        }
        self.scalar_dofs_in_rod_elems = np.zeros(
            (len(map_scalar_dofs_in_rod_elems), self.n_elems)
        )
        for k,v in map_scalar_dofs_in_rod_elems.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.scalar_dofs_in_rod_elems[v], (self.n_elems,)
            )

        for k,v in map_scalar_dofs_in_rod_elems.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_elems[system_idx]
                end_idx = self.end_idx_in_rod_elems[system_idx]

                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )



            _synchronize_periodic_boundary_of_scalar_collection(
                self.__dict__[k], self.periodic_boundary_elems_idx
            )


        map_vector_dofs_in_rod_elems = {
            "tangents":0,
            "sigma":1,
            "rest_sigma":2,
            "internal_torques":3,
            "external_torques":4,
            "internal_stress":5,
        }
        self.vector_dofs_in_rod_elems = np.zeros(
            (len(map_vector_dofs_in_rod_elems), 3 * self.n_elems)
        )
        
        for k,v in map_vector_dofs_in_rod_elems.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.vector_dofs_in_rod_elems[v], (3, self.n_elems)
            )

        for k,v in map_vector_dofs_in_rod_elems.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_elems[system_idx]
                end_idx = self.end_idx_in_rod_elems[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_vector_collection(
                self.__dict__[k], self.periodic_boundary_elems_idx
            )

        map_matrix_dofs_in_rod_elems = {
            "director_collection": 0,
            "mass_second_moment_of_inertia": 1,
            "inv_mass_second_moment_of_inertia": 2,
            "shear_matrix": 3,
        }
        self.matrix_dofs_in_rod_elems = np.zeros(
            (len(map_matrix_dofs_in_rod_elems), 3 * 3 * self.n_elems)
        )
        for k,v in map_matrix_dofs_in_rod_elems.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.matrix_dofs_in_rod_elems[v], (3, 3, self.n_elems)
            )

        for k,v in map_matrix_dofs_in_rod_elems.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_elems[system_idx]
                end_idx = self.end_idx_in_rod_elems[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_matrix_collection(
                self.__dict__[k], self.periodic_boundary_elems_idx
            )
    
    def allocate_block_variables_in_voronoi(self, systems: Sequence):
        map_scalar_dofs_in_rod_voronoi = {
            "voronoi_dilatation": 0,
            "rest_voronoi_lengths": 1,
        }
        self.scalar_dofs_in_rod_voronoi = np.zeros(
            (len(map_scalar_dofs_in_rod_voronoi), self.n_voronoi)
        )
        for k,v in map_scalar_dofs_in_rod_voronoi.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.scalar_dofs_in_rod_voronoi[v], (self.n_voronoi,)
            )

        for k,v in map_scalar_dofs_in_rod_voronoi.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_voronoi[system_idx]
                end_idx = self.end_idx_in_rod_voronoi[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_scalar_collection(
                self.__dict__[k], self.periodic_boundary_voronoi_idx
            )

        map_vector_dofs_in_rod_voronoi = {
            "kappa": 0,
            "rest_kappa": 1,
            "internal_couple": 2,
        }
        self.vector_dofs_in_rod_voronoi = np.zeros(
            (len(map_vector_dofs_in_rod_voronoi), 3 * self.n_voronoi)
        )
        for k,v in map_vector_dofs_in_rod_voronoi.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.vector_dofs_in_rod_voronoi[v], (3, self.n_voronoi)
            )

        for k,v in map_vector_dofs_in_rod_voronoi.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_voronoi[system_idx]
                end_idx = self.end_idx_in_rod_voronoi[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_vector_collection(
                self.__dict__[k], self.periodic_boundary_voronoi_idx
            )
        
        map_matrix_dofs_in_rod_voronoi = {
            "bend_matrix": 0
        }
        self.matrix_dofs_in_rod_voronoi = np.zeros(
            (len(map_matrix_dofs_in_rod_voronoi), 3 * 3 * self.n_voronoi)
        )
        for k,v in map_matrix_dofs_in_rod_voronoi.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.matrix_dofs_in_rod_voronoi[v], (3, 3, self.n_voronoi)
            )
        for k,v in map_matrix_dofs_in_rod_voronoi.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_voronoi[system_idx]
                end_idx = self.end_idx_in_rod_voronoi[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_matrix_collection(
                self.__dict__[k], self.periodic_boundary_voronoi_idx
            )
    
    def allocate_block_variables_for_symplectic_stepper(self, systems: Sequence):
        map_rate_collection = {
            "velocity_collection": 0,
            "omega_collection": 1,
            "acceleration_collection": 2,
            "alpha_collection": 3,
        }
        self.rate_collection = np.zeros((len(map_rate_collection), 3 * self.n_nodes))
        for k,v in map_rate_collection.items():
            self.__dict__[k] = np.lib.stride_tricks.as_strided(
                self.rate_collection[v], (3, self.n_nodes)
            )
        #我觉得源代码这里有一部分重复的工作，不知道是不是我理解错了
            
        #For Dynamic state update of position verlet create references
        self.v_w_collection = np.lib.stride_tricks.as_strided(
            self.rate_collection[0:2], (2, 3 * self.n_nodes)
        )
        self.dvdt_dwdt_collection = np.lib.stride_tricks.as_strided(
            self.rate_collection[2:-1], (2, 3 * self.n_nodes)
        )

        map_rate_collection_dofs_in_rod_nodes = {
            "velocity_collection": 0,
            "acceleration_collection":1,
        }

        for k,v in map_rate_collection_dofs_in_rod_nodes.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_nodes[system_idx]
                end_idx = self.end_idx_in_rod_nodes[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_vector_collection(
                self.__dict__[k], self.periodic_boundary_nodes_idx
            )

        map_rate_collection_dofs_in_rod_elems = {
            "omega_collection": 0,
            "alpha_collection": 1,
        }
        for k,v in map_rate_collection_dofs_in_rod_elems.items():
            for system_idx, system in enumerate(systems):
                start_idx = self.start_idx_in_rod_elems[system_idx]
                end_idx = self.end_idx_in_rod_elems[system_idx]
                self.__dict__[k][..., start_idx:end_idx] = system.__dict__[k].copy()
                system.__dict__[k] = np.ndarray.view(
                    self.__dict__[k][..., start_idx:end_idx]
                )
            _synchronize_periodic_boundary_of_vector_collection(
                self.__dict__[k], self.periodic_boundary_elems_idx
            )



        