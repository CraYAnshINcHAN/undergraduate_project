from rod_data_structures import _RodSymplecticStepperMixin

class _RigidRodSymplecticStepperMixin(_RodSymplecticStepperMixin):
    def __init__(self):
        super(_RigidRodSymplecticStepperMixin, self).__init__()
    
    def update_internal_forces_and_torques(self, *args, **kwargs):
        pass