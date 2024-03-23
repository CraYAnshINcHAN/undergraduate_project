import sys
import numpy as np
from rod_base import RodBase
if sys.version_info.minor >= 8:
    #typing Protocol was introduced in Python 3.8
    from typing import Protocol
elif sys.version_info.minor < 8:
    from typing_extensions import Protocol
from typing import Union
    
class KnotTheoryCompatibleProtocol(Protocol):
    #show required properties to use KnotTheory mixin
    @property
    def position_collection(self) -> np.ndarray:
        ...
    @property
    def director_collection(self) -> np.ndarray:
        ...
    @property
    def radius(self) -> np.ndarray:
        ...
    @property
    def base_length(self)->np.ndarray:
        ...

class KnotTheory:
    #表示类型可以是两个类型中的任意一个
    MIXIN_PROTOCOL = Union[RodBase, KnotTheoryCompatibleProtocol]
    def compute_twist(self:MIXIN_PROTOCOL):
        total_twist, local_twist = compute_twist(
            self.position_collection[None, ...],
            self.director_collection[None, ...],
        )

def compute_twist(center_line, normal_collection):
    pass