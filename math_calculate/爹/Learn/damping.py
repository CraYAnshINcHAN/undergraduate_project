from elastica_dissipation import DamperBase

class Damping:
    def __init__(self):
        self._dampers = []
        super(Damping, self).__init__()
        self._feature_group_constrain_rates.append(self._dampen_rates)
        self._feature_group_finalize.append(self._finalize_dampers)

    #活得系统的编号，新建一个_Damper对象，将编号传给它的初始化方法，将这个对象保存到_dampers列表中，然后返回这个对象
    def dampen(self, system):
        sys_idx = self._get_sys_idx_if_valid(system)

        _damper = _Damper(sys_idx)
        self._dampers.append(_damper)
        return _damper
    def _finalize_dampers(self):
        self._dampers[:] = [
            (damper.id(), damper(self._systems[damper.id()]))
            for damper in self._dampers
        ]
        
        self._dampers.sort(key = lambda x: x[0])

    def _dampen_rates(self, time, *args, **kwargs):
        for sys_id, damper in self._dampers:
            damper.dampen_rates(self._systems[sys_id], time, *args, **kwargs)

#这个类的作用是保存系统的编号，以及外力的类和参数
class _Damper:
    def __init__(self, sys_idx:int):
        self._sys_idx = sys_idx
        self._damper_cls = None
        self._args = ()
        self._kwargs = {}
    def using(self, damper_cls, *args, **kwargs):
        assert issubclass(
            damper_cls, DamperBase
        ), "{} is not a valid damper. Damper must be driven from DamperBase.".format(
            damper_cls
        )
        self._damper_cls = damper_cls
        self._args = args
        self._kwargs = kwargs
        return self
    
    def id(self):
        return self._sys_idx
    
    def __call__(self, rod, *args, **kwargs):
        if not self._damper_cls:
            raise RuntimeError("No damper class specified")
        try:
            damper = self._damper_cls(*self._args, _system = rod, **self._kwargs)
            return damper
        except (TypeError,IndexError):
            raise TypeError("unable to construct damping class")