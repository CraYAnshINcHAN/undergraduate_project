from rod_base import RodBase
from rigid_body import RigidBodyBase

from typing import Type, Union

RodType = Type[RodBase]
SystemType = Union[RodType, Type[RigidBodyBase]]
