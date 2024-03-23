def is_system_a_collection(system):
    from base_system import BaseSystemCollection

    __sys__get__item = getattr(system, "__getitem__", None)
    return issubclass(system.__class__, BaseSystemCollection) or callable(__sys__get__item)