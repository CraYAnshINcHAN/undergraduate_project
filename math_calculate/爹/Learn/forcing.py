class Forcing:
    def __init__(self):
        self._ext_forces_torques = []
        super(Forcing, self).__init__()
        self._feature_group_synchronize.append(self._call_ext_forces_torques)
        self._feature_group_finalize.append(self._finalize_forcing)

    def add_forcing_to(self, system):
        
        sys_idx = self._get_sys_idx_if_valid(system)

        #_ExternalForceTorque类的作用是保存系统的编号，以及外力的类和参数
        _ext_force_torque = _ExternalForceTorque(sys_idx)
        #将_ExternalForceTorque对象保存到_ext_forces_torques列表中
        self._ext_forces_torques.append(_ext_force_torque)

        return _ext_force_torque

    def _finalize_forcing(self):
        self._ext_forces_torques[:] = [
            (ext_force_torque.id(), ext_force_torque())
            for ext_force_torque in self._ext_forces_torques
        ]

        self._ext_forces_torques.sort(key=lambda x: x[0])

        #先不考虑这个函数，它是表示摩擦力的
        # friction_plane_index = []
        # for idx, ext_force_torque in enumerate(self._ext_forces_torques):
        #     if isinstance(ext_force_torque[1], AnisotropicFrictionPlane):
        #         friction_plane_index.append(idx)

        # for index in friction_plane_index:
        #     self._ext_forces_torques.append(self._ext_forces_torques.pop(index))

    def _call_ext_forces_torques(self, time, *args, **kwargs):
        for sys_id, ext_force_torque in self._ext_forces_torques:
            #apply_forces和apply_torques是在elastica_external_forces.py中定义的
            ext_force_torque.apply_forces(self._systems[sys_id], time, *args, **kwargs)
            ext_force_torque.apply_torques(self._systems[sys_id], time, *args, **kwargs)

#这个类的作用是保存系统的编号，以及外力的类和参数
class _ExternalForceTorque:
    def __init__(self, sys_idx: int):
        self._sys_idx = sys_idx
        self._forcing_cls = None
        self._args = ()
        self._kwargs = {}
    
    def using(self, forcing_cls, *args, **kwargs):
        
        from elastica_external_forces import NoForces
        assert issubclass(
            forcing_cls, NoForces
        ),"{} is not a valid forcing. Forcing must be drvien from ForcingBase.".format(
            forcing_cls
        )
        self._forcing_cls = forcing_cls
        self._args = args
        self._kwargs = kwargs
        return self
    
    def id(self):
        return self._sys_idx
    
    def __call__(self, *args, **kwargs):
        if not self._forcing_cls:
            raise RuntimeError("No forcing class specified")
        try:
            print("forcing.py_67")
            print(self._args)
            return self._forcing_cls(*self._args, **self._kwargs)
        except (TypeError,IndexError):
            raise TypeError("unable to construct forcing class")
    

    