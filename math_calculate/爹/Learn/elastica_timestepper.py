import numpy as np
from tqdm import tqdm
from symplectic_steppers import SymplecticStepperTag
from explicit_steppers import ExplicitStepperTag

def extend_stepper_interface(Stepper, System):
    from elastica_utils import extend_instance
    from elastica_systems import is_system_a_collection

    is_this_system_a_collection = is_system_a_collection(System)
    assert is_this_system_a_collection, "System is not a collection"

    ConcreteStepper = Stepper

    if type(ConcreteStepper.Tag) == SymplecticStepperTag:
        from symplectic_steppers import (
            _SystemCollectionStepper,
            SymplecticStepperMethods as StepperMethodCollector,
        )
    
    stepper_methods = StepperMethodCollector(ConcreteStepper)
    do_step_method = (
        _SystemCollectionStepper.do_step
    )

    #stepper_methods.step_methods是一个元组
    #这个元组的每一个元素中有三个元素，第一个元素是一个函数，第二个元素是一个函数，第三个元素是一个函数
    #对元组中的第一个元素，其中第一个元素是_prefactors，第二个元素，里面是更新各节点的位置和方向的函数，第三个元素是更新各节点的速度和角速度的函数
    #这个元组中的第二个元素，其中第一个元素是_prefactors，第二个元素，里面是更新各节点的位置和方向的函数，第三个元素是pass
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
    #StatefulStepper是timestepper,是PositionVerlet类的一个对象，有用于更新节点位置和方向的函数和用于更新节点速度和角速度的函数
    #System是magnetic_beam_sim。
    do_step, stages_and_updates = extend_stepper_interface(StatefulStepper, System)

    dt = np.float64(float(final_time) / n_steps)
    time = restart_time

    for i in tqdm(range(n_steps), disable = (not progress_bar)):
        time = do_step(StatefulStepper, stages_and_updates, System, time, dt)

    print("Final time of simulation is:", time)

    return time
