from rod_base import RodBase
from rigid_body import RigidBodyBase
from memory_block_rod import MemoryBlockCosseratRod
from memory_block_rigid_body import MemoryBlockRigidBody


def construct_memory_block_structures(systems):
    _memory_blocks = []
    temp_list_for_cosserat_rod_systems = []
    temp_list_for_rigid_body_systems = []
    temp_list_for_cosserat_rod_systems_idx = []
    temp_list_for_rigid_body_systems_idx = []


    for system_idx, sys_to_be_added in enumerate(systems):
#在这里，我们将系统分成两类，一类是cosserat rod系统，一类是rigid body系统
#然后将这两类系统分别保存到两对列表中，
        if issubclass(sys_to_be_added.__class__, RodBase):
            temp_list_for_cosserat_rod_systems.append(sys_to_be_added)
            temp_list_for_cosserat_rod_systems_idx.append(system_idx)
        elif issubclass(sys_to_be_added.__class__, RigidBodyBase):
            temp_list_for_rigid_body_systems.append(sys_to_be_added)
            temp_list_for_rigid_body_systems_idx.append(system_idx)
        else:
            raise TypeError(
                f"System must be a subclass of RodBase or RigidBodyBase"
            )
#这里我们把系统的列表以及保存系统索引的列表传给MemoryBlockCosseratRod中，新建了一个MemoryBlockCosseratRod对象
#然后将这个对象保存到_memory_blocks列表中，并返回
    if temp_list_for_cosserat_rod_systems:
        _memory_blocks.append(
            MemoryBlockCosseratRod(
                temp_list_for_cosserat_rod_systems, temp_list_for_cosserat_rod_systems_idx
            )
        )
    if temp_list_for_rigid_body_systems:
        _memory_blocks.append(
            MemoryBlockRigidBody(
                temp_list_for_rigid_body_systems, temp_list_for_rigid_body_systems_idx
            )
        )
    
    return _memory_blocks