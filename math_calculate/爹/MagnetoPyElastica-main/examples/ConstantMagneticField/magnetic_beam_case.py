import numpy as np
from matplotlib import pyplot as plt
from matplotlib.colors import to_rgb
from elastica import *
from magneto_pyelastica import *


SAVE_FIGURE = True
PLOT_FIGURE = True

#这里继承了五个不同的类，分别有其不同的作用，之后用到了再来看
class MagneticBeamSimulator(
    BaseSystemCollection, Constraints, Forcing, Damping, CallBacks
):
    pass

#生成了一个仿真类
magnetic_beam_sim = MagneticBeamSimulator()

# setting up test params
#应该是将杆分为50段的含义
n_elem = 50
#也许是杆的起始位置？
start = np.zeros((3,))
#也许是杆的初始方向
direction = np.array([1.0, 0.0, 0.0])
#也许是杆的法向量
normal = np.array([0.0, 1.0, 0.0])
#杆的长度等一系列参数
base_length = 6.0
base_radius = 0.15
base_area = np.pi * base_radius**2
density = 5000
E = 1e6
I = np.pi / 4 * base_radius**4
poisson_ratio = 0.5
shear_modulus = E / (2 * poisson_ratio + 1.0)
base_radius = 0.15

# setting up magnetic properties
magnetization_density = 1e5
magnetic_field_angle = 2 * np.pi / 3
magnetic_field = 1e-2
#常磁场的方向，各点上都是（1 0 0）
magnetization_direction = np.ones((n_elem)) * direction.reshape(3, 1)

# Add rod to the simulator
#这里将信息传给了CosseratRod.straight_rod函数，这个函数是一个类方法(classmethod)，它会通过我们提供的参数计算出更多别的参数,并且return一个新的CosseratRod类
magnetic_rod = CosseratRod.straight_rod(
    n_elem,
    start,
    direction,
    normal,
    base_length,
    base_radius,
    density,
    youngs_modulus=E,
    shear_modulus=shear_modulus,
)
#将杆添加到仿真器中,具体是这样的，MagneticBeamSimulator所继承的BaseSystemCollection类中并没有append函数，但是这个类继承了MutableSequence
#这个类是一个抽象类，它的子类必须实现的方法有__getitem__、__setitem__、__delitem__、__len__、insert，而调用append方法时
#会调用MutableSequence类中的insert方法，将magnetic_rod添加到了一个列表中
magnetic_beam_sim.append(magnetic_rod)

# Add boundary conditions, one end of rod is clamped
#magnetic_beam_sim.constrain(magnetic_rod)返回的是一个_Constraint类的实例,并且会传给该实例rodsystem的索引
#之后调用了这个实例的using方法，这个方法的作用一个是检查我们给的第一个参数是不是给定的边界条件，第二、三个参数是给定的边界条件的参数
#整体来说这个方法是这样的，magnetic_beam_sim有一个_constraints列表，这个列表中存放的是_Constraint类的实例
#这个类的实例中存放的是我们给定的边界条件。我们先通过magnetic_beam_sim.constrain(magnetic_rod)返回一个_Constraint类的实例加入到列表中
#该实例又通过using方法加入了我们给定的边界条件
magnetic_beam_sim.constrain(magnetic_rod).using(
    OneEndFixedBC, constrained_position_idx=(0,), constrained_director_idx=(0,)
)

# Set the constant magnetic field object，常磁场条件下，磁场强度就是一个固定的向量。这个向量的方向是magnetic_field_angle，大小是magnetic_field 
magnetic_field_amplitude = magnetic_field * np.array(
    [np.cos(magnetic_field_angle), np.sin(magnetic_field_angle), 0]
)
#定义了一个磁场类，这个类继承了BaseMagneticField类，这个类中有一个value方法，这个方法返回的是磁场的值。这个磁场虽然说是常磁场
#但是是随时间变化的，从start_time到ramp_interval时间内，磁场的大小是线性增加的，之后不变，到end_time之后磁场的大小是线性减小的
magnetic_field_object = ConstantMagneticField(
    magnetic_field_amplitude, ramp_interval=500.0, start_time=0.0, end_time=100000
)

# Apply magnetic forces
#这个没有具体看实现，但是从目前这个地方来看，应该没有特别复杂的地方
magnetic_beam_sim.add_forcing_to(magnetic_rod).using(
    MagneticForces,
    external_magnetic_field=magnetic_field_object,
    magnetization_density=magnetization_density,
    magnetization_direction=magnetization_direction,
    rod_volume=magnetic_rod.volume,
    rod_director_collection=magnetic_rod.director_collection,
)

# Add callbacks
#CallBackBaseClass是一个抽象类，它的子类必须实现的方法有make_callback，这个方法的作用是在仿真过程中，每隔一段时间就调用一次
#这个方法的作用是收集仿真过程中的数据，记录时间、当前步以及速度大小。这个类的实例有两个属性，一个是every，一个是callback_params
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


# add damping
dl = base_length / n_elem
dt = 0.05 * dl
damping_constant = 1.0
#增加阻尼，也还没有仔细看。应该是和magnetic_beam_sim.constrain(magnetic_rod).using(）类似。但是这个time_step参数是什么意思？
magnetic_beam_sim.dampen(magnetic_rod).using(
    AnalyticalLinearDamper,
    damping_constant=damping_constant,
    time_step=dt,
)

# Add call back for plotting time history of the rod
post_processing_dict = defaultdict(list)
#也还没有仔细看。应该是和magnetic_beam_sim.constrain(magnetic_rod).using(）类似。但是这个time_step参数是什么意思？
magnetic_beam_sim.collect_diagnostics(magnetic_rod).using(
    MagneticBeamCallBack, step_skip=500, callback_params=post_processing_dict
)
#看着是一个仿真器的初始化，但是这个仿真器是怎么工作的还没有仔细看
magnetic_beam_sim.finalize()
timestepper = PositionVerlet()
final_time = 1000.0
total_steps = int(final_time / dt)
integrate(timestepper, magnetic_beam_sim, final_time, total_steps)

if PLOT_FIGURE:
    with plt.style.context("ggplot"):
        fig = plt.figure(figsize=(10, 8), frameon=True, dpi=150)
        ax = fig.add_subplot(111)
        ax.plot(
            magnetic_rod.position_collection[0, ...],
            magnetic_rod.position_collection[1, ...],
            lw=2,
            c=to_rgb("xkcd:bluish"),
        )
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        fig.show()

        fig = plt.figure(figsize=(10, 8), frameon=True, dpi=150)
        ax = fig.add_subplot(111)
        ax.semilogy(
            np.asarray(post_processing_dict["time"]),
            np.asarray(post_processing_dict["velocity_norm"]),
            lw=2,
            c=to_rgb("xkcd:bluish"),
        )
        ax.set_xlabel("t")
        ax.set_ylabel("|v|")
        fig.show()

        plt.show()  # block
    if SAVE_FIGURE:
        fig.savefig("Magnetic_beam_profile: N=" + str(magnetic_rod.n_elems) + ".png")
