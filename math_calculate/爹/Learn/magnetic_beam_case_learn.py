import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgb
from collections import defaultdict
from base_system import *
from cosserat_rod import *
from magnetic_field import *
from constraints import *
from boundary_conditions import *
from forcing import *
from magnetic_forces import *
from callbacks import *
from damping import *
from elastica_dissipation import AnalyticalLinearDamper
from symplectic_steppers import PositionVerlet
SAVE_FIGURE = False
PLOT_FIGURE = True

class MageneticBeamSimulator(
    BaseSystemCollection, Constraints, Forcing, Damping, CallBacks
):
    pass

magnetic_beam_sim = MageneticBeamSimulator()

#setting up test params
#将杆分割成50个元素
n_elem = 50
#初始位置
start = np.zeros((3,))
#初始方向
direction = np.array([1.0, 0.0, 0.0])
#法线方向
normal = np.array([0.0, 0.0, 1.0])
#杆长
base_length = 6.0
#杆半径
base_radius = 0.15
#杆截面积
base_area = np.pi * base_radius ** 2
#杆材料密度
density = 5000
#杨氏模量
E = 1e6
#面积矩
I = (np.pi / 4) * base_radius ** 4
possion_ratio = 0.5
shear_modulus = E / (2 * (1 + possion_ratio))

#磁参数
magnetization_density = 1e5
magnetic_field_angle = 2 * np.pi / 3
magnetic_field = 1e-2
#将每个杆元素的磁化方向设置为一致
magnetization_direction = np.ones((n_elem)) * direction.reshape(3, 1)

#设置好了杆的参数，接下来就是把杆加入到系统中，主要设置的参数参考思维导图即可
magnetic_rod = CosseratRod.straight_rod(
    n_elem, start, direction, normal, base_length, base_radius, density, youngs_modulus=E, shear_modulus=shear_modulus,
)
#把杆加入到系统中
magnetic_beam_sim.append(magnetic_rod)

#Add boundary conditions, one end of rod is clamped
#这里先调用constrain函数，constrain函数会得到输入杆在系统中的编号，然后再把生成一个_Constraint对象
#将其保存到magnetic_beam_sim的_constraints列表中，将编号传给它的初始化方法，然后返回这个对象
#这个_Constraint对象会保存编号，然后再调用using函数，using函数会得到输入的边界条件类和参数，然后保存起来
#_Constraint函数会把输入的边界条件类和参数保存起来


#constrain函数，输入的是一个系统，类似consserate_rod，会得到输入系统在系统列表中的编号
#然后新建一个_Constraint对象，将编号传给它的初始化方法，将这个对象保存到_constraints列表中，然后返回这个对象

#所以这个函数做的就是把对英于magetic_rod的边界条件保存在了_constraints列表中的一个元素中，这个元素的类是_Constraint
#并且这个元素的_bc_cls中保存了边界条件的类型，即OneEndFixedBC，_kwargs中保存了边界条件的参数。
magnetic_beam_sim.constrain(magnetic_rod).using(
    OneEndFixedBC, constrained_position_idx = (0,), constrained_director_idx = (0,)
)   

# Set the constant magnetic field object，其中就是磁场的强度和方向
magnetic_field_amplitude = magnetic_field * np.array(
    [np.cos(magnetic_field_angle), np.sin(magnetic_field_angle), 0]
)

#这里的ConstantMagneticField是一个类，这个类的初始化函数中保存了磁场的强度和方向
#而我们给出的ram_interval，start_time，end_time是指磁场开始时间，结束时间以及磁场在ramp_interval时间内会逐渐增加到达end_time后又
#会在ramp_interval时间内逐渐减小
magnetic_field_object = ConstantMagneticField(
    magnetic_field_amplitude, ramp_interval = 500.0, start_time = 0.0, end_time = 100000
)


#Apply magnetic forces
#这里和上面思路很像，先用add_forcing_to函数，将magnetic_rod传入，由此会新建一个_ExternalForceTorque类的实例，把它保存在_ext_forces_torques列表中
#这个实例会保存系统的编号，然后再调用using函数，将输入的参数保存起来，其中_forcing_cls保存的是力的类型，即MagneticForces
#其余的都保存在了_kwargs中
magnetic_beam_sim.add_forcing_to(magnetic_rod).using(
    MagneticForces,
    external_magnetic_field = magnetic_field_object,
    magnetization_density = magnetization_density,
    magnetization_direction = magnetization_direction,
    rod_volume = magnetic_rod.volume,
    rod_director_collection = magnetic_rod.director_collection,
)

#Add callbacks
#CallBackBaseClass是一个基类，但是没有什么内容
#这里新建了一个MagneticBeamCallBack类，这个类继承自CallBackBaseClass

class MagneticBeamCallBack(CallBackBaseClass):
    def __init__(self, step_skip: int, callback_params: dict):
        CallBackBaseClass.__init__(self)
        self.every = step_skip
        self.callback_params = callback_params

    def make_callback(self, system, time, current_step: int):
        if current_step % self.every == 0:
            self.callback_params["time"].append(time)
            self.callback_params["step"].append(current_step)
            self.callback_params["velocity_norm"].append(
                np.linalg.norm(system.velocity_collection)
            )

#Add damping
dl = base_length / n_elem
dt = 0.05 * dl
damping_constant = 1.0
#这里和上面思路很像，先用dampen函数，将magnetic_rod传入，由此会新建一个_Damper类的实例，把它保存在_dampers列表中
#这个实例会保存系统的编号，然后再调用using函数，将输入的参数保存起来，其中_damper_cls保存的是阻尼的类型，即AnalyticalLinearDamper
#其余的都保存在了_kwargs中
magnetic_beam_sim.dampen(magnetic_rod).using(
    AnalyticalLinearDamper,
    damping_constant = damping_constant,
    time_step = dt,
    )

#Add call back for plotting time history of the rod
#defaultdict(list)表示创建一个默认字典，当访问的键不存在时，返回一个空列表（list）。然后，这个默认字典被赋值给变量post_processing_dict。
post_processing_dict = defaultdict(list)

#这里目前做的和上面的思路也比较像，
#先用collect_diagnostics函数，将magnetic_rod传入，由此会新建一个_MagneticBeamCallBack类的实例，把它保存在_callbacks列表中
#这个实例会保存系统的编号，然后再调用using函数，将输入的参数保存起来，其中_callback_cls保存的是回调的类型，即MagneticBeamCallBack
#其余的都保存在了_kwargs中
magnetic_beam_sim.collect_diagnostics(magnetic_rod).using(
    MagneticBeamCallBack, step_skip=500, callback_params=post_processing_dict
)

magnetic_beam_sim.finalize()
#2024-3-19已经跑通前面的代码，还差后面的部分没有怎么看，需要再自己看看
#主要内容现在分为两部分，把前半部分代码看懂，把后半部分写完并看懂，先打算把前半部分看懂

# timestepper = PositionVerlet()
# final_time = 1000.0
# total_steps = int(final_time / dt)

#integrate(timestepper, magnetic_beam_sim, final_time, total_steps)


#2024-3-17目前在完善cosserat_rod中的一些函数，有_compute_geometry_from_state，_compute_all_dilatations，_compute_shear_stretch_strains