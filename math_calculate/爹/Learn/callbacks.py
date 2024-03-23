from elastica_callback_functions import CallBackBaseClass

class CallBacks:
    def __init__(self):
        self._callback_list = []
        super(CallBacks, self).__init__()
        self._feature_group_callback.append(self._callback_execution)
        self._feature_group_finalize.append(self._finalize_callback)

    def collect_diagnostics(self, system):
        sys_idx = self._get_sys_idx_if_valid(system)
        _callbacks = _CallBack(sys_idx)
        self._callback_list.append(_callbacks)
        return _callbacks
    
    def _finalize_callback(self):
        self._callback_list[:] = [
            (callback.id(), callback(self._systems[callback.id()]))
            for callback in self._callback_list
        ]

        self._callback_list.sort(key=lambda x: x[0])

        self._callback_execution(time=0.0, current_step=0)
    
    def _callback_execution(self, time, current_step:int, *args, **kwargs):
        for sys_id, callback in self._callback_list:
            callback.make_callback(
                self._systems[sys_id], time, current_step, *args, **kwargs
            )

class _CallBack:
    def __init__(self, sys_idx: int):
        self._sys_idx = sys_idx
        self._callback_cls = None
        self._args = ()
        self._kwargs = {}

    def using(self, callback_cls, *args, **kwargs):
        assert issubclass(callback_cls, CallBackBaseClass
        ),"{} is not a valid callback class".format(
            callback_cls
        )
        self._callback_cls = callback_cls
        self._args = args
        self._kwargs = kwargs
        return self
    def id(self):
        return self._sys_idx
    
    def __call__(self, *args,**kwargs) -> CallBackBaseClass:
        if not self._callback_cls:
            raise RuntimeError("No callback class specified")
        try:
            return self._callback_cls(*self._args, **self._kwargs)
        
        except (TypeError,IndexError):
            raise TypeError(
                "Unable to construct callback class with args"
            )

    

    
