import numpy as np
from tqdm import tqdm
from symplectic_steppers import SymplecticStepperTag
from explicit_steppers import ExplicitStepperTag
def extend_stepper_interface(Stepper, System):
    from elastica_utils import extend_instance
    from elastica_systems import is_system_a_collection

    is_this_system_a_collection = is_system_a_collection(System)

    ConcreteStepper = Stepper

    if type(ConcreteStepper.Tag) == SymplecticStepperTag:
        from symplectic_steppers import (
            _SystemInstanceStepper,
            _SystemCollectionStepper,
            SymplecticStepperMethods as StepperMethodCollector,
        )
    
    elif type(ConcreteStepper.Tag) == ExplicitStepperTag:
        from explicit_steppers import (
            _SystemInstanceStepper,
            _SystemCollectionStepper,
            ExplicitStepperMethods as StepperMethodCollector,
        )
    
    stepper_methods = StepperMethodCollector(ConcreteStepper)
    do_step_method = (
        _SystemCollectionStepper.do_step
        if is_this_system_a_collection
        else _SystemInstanceStepper.do_step
    )

    return do_step_method, stepper_methods.step_methods()

def integrate(
        StatefulStepper,
        System,
        final_time:float,
        n_steps: int = 1000,
        restart_time: float = 0.0,
        progress_bar: bool = True,
        **kwargs
        ):
    assert final_time > 0.0, "Final time is negative"
    assert n_steps > 0, "Number of steps is negative"

    do_step, stages_and_updates = extend_stepper_interface(StatefulStepper, System)

    dt = np.float64(float(final_time) / n_steps)
    time = restart_time

    for i in tqdm(range(n_steps), disable = (not progress_bar)):
        time = do_step(StatefulStepper, stages_and_updates, System, time, dt)

    print("Final time of simulation is:", time)

    return time
