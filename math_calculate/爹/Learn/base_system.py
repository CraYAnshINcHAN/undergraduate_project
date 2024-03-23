from collections.abc import MutableSequence
from typing import Iterable, Callable, AnyStr
from rod_base import RodBase
from rigid_body import RigidBodyBase
from memory_block import construct_memory_block_structures
from elastica_synchronize_periodic_boundary import _ConstrainPeriodicBoundaries

class BaseSystemCollection(MutableSequence):
    def __init__(self):
        #Collection of functions. Each group is executed as a collection at the different steps.
        #Each component (Forcing, Connection, etc.) registers the executable(callable) functions
        #in the group that needs to be executed. These should be initialized before mixin.
        self._feature_group_synchronize: Iterable[Callable[[float], None]] = []
        self._feature_group_constrain_values: Iterable[Callable[[float], None]] = []
        self._feature_group_constrain_rates: Iterable[Callable[[float], None]] = []
        self._feature_group_callback: Iterable[
            Callable[[float, int, AnyStr], None]
            ] = []
        self._feature_group_finalize: Iterable[Callable] = []
        super(BaseSystemCollection, self).__init__()
        self.allowed_sys_types = (RodBase, RigidBodyBase)
        self._systems = []
        self._finalize_flag = False

    def _check_type(self, sys_to_be_added: AnyStr):
        if not issubclass(sys_to_be_added.__class__, self.allowed_sys_types):
            raise TypeError(
                f"System must be a subclass of {self.allowed_sys_types}"
            )
        return True
    def __len__(self):
        return len(self._systems)
    def __getitem__(self, idx):
        return self._systems[idx]
    def __delitem__(self, idx):
        del self._systems[idx]
    def __setitem__(self, idx, system):
        self._check_type(system)
        self._systems[idx] = system
    def insert(self, idx, system):
        self._check_type(system)
        self._systems.insert(idx, system)
    #先判断输入是否为整数，如果是整数，就输出是否超过了目前系统的数量
    #若输入不是整数，则判断输入是否在系统列表中，如果不在则报错，如果在则输出系统的索引
    def _get_sys_idx_if_valid(self, sys_to_be_added):
        from numpy import int_ as npint

        n_systems = len(self._systems)
        if isinstance(sys_to_be_added,(int, npint)):
            assert(
                -n_systems <= sys_to_be_added < n_systems
            ), "Rod index {} exceeds number of registered rodtems".formant(
                sys_to_be_added
            )
        elif self._check_type(sys_to_be_added):
            try:
                sys_idx = self._systems.index(sys_to_be_added)
            except ValueError:(
                "Rod {} was not found, did you append it to the system?".format(
                    sys_to_be_added
                )
            )
        return sys_idx
    
    def finalize(self):
        assert self._finalize_flag is not True, "System already finalized"

        #construct memory block
        #这个会返回一个列表
        #列表中每一项是一个MemoryBlockCosseratRod类，或者MemoryBlockRigidBody类
        #而这个类中会保存一些系统本身的信息，还有开始节点、结束节点以及幽灵节点等信息，以及每段的质量等具体。但是不算复杂，没有新计算的东西
        self._memory_blocks = construct_memory_block_structures(self._systems)

        for i in range(len(self._memory_blocks)):
            self.append(self._memory_blocks[i])
            if hasattr(self._memory_blocks[i], "ring_rod_flag"):
                memory_block_idx = self._get_sys_idx_if_valid(self._memory_blocks[i])
                self.constrain(self._systems[memory_block_idx]).using(
                    _ConstrainPeriodicBoundaries,
                )

        for finalize in self._feature_group_finalize:
            finalize()

        self._feature_group_finalize.clear()
        self._feature_group_finalize = None
        self._finalize_flag = True

    def synchronize(self, time: float):
        for synchronize in self._feature_group_synchronize:
            synchronize(time)
        
    def constrain_values(self, time: float):
        for constrain_values in self._feature_group_constrain_values:
            constrain_values(time)

    def constrain_rates(self, time: float):
        for constrain_rates in self._feature_group_constrain_rates:
            constrain_rates(time)

    def apply_callbacks(self, time: float, current_step: int):
        for callback in self._feature_group_callback:
            callback(time, current_step)