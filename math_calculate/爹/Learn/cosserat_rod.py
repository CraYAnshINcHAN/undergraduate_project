from knot_theory import KnotTheory
import logging
from typing import Optional, Tuple
import numpy as np
from numpy import finfo, float64
import numba
from numba import njit
from rod_base import RodBase
from elastica_utils import Tolerance
from elastica_linalg import _batch_cross, _batch_dot, _batch_norm, _batch_matvec
from elastica_rotations import _inv_rotate
from elastica_calculus import _difference, _average

position_difference_kernel = _difference
position_average = _average
def _compute_sigma_kappa_for_blockstructure(memory_block):
    #This funtion is a wrapper to call functions which computes shear stretch, strain and bending twist strain
    _compute_shear_stretch_strains(
        memory_block.position_collection,
        memory_block.volume,
        memory_block.lengths,
        memory_block.tangents,
        memory_block.radius,
        memory_block.rest_lengths,
        memory_block.rest_voronoi_lengths,
        memory_block.dilatation,
        memory_block.voronoi_dilatation,
        memory_block.director_collection,
        memory_block.sigma,
    )

    _compute_bending_twist_strains(
        memory_block.director_collection,
        memory_block.rest_voronoi_lengths,
        memory_block.kappa,
    )
class CosseratRod(RodBase, KnotTheory):
    """
    Cosserat Rod class. This is the preferred class for rods because it is derived from some
    of the essential base classes.

        Attributes
        ----------
        n_elems: int
            The number of elements of the rod.
        position_collection: numpy.ndarray
            2D (dim, n_nodes) array containing data with 'float' type.
            Array containing node position vectors.
        velocity_collection: numpy.ndarray
            2D (dim, n_nodes) array containing data with 'float' type.
            Array containing node velocity vectors.
        acceleration_collection: numpy.ndarray
            2D (dim, n_nodes) array containing data with 'float' type.
            Array containing node acceleration vectors.
        omega_collection: numpy.ndarray
            2D (dim, n_elems) array containing data with 'float' type.
            Array containing element angular velocity vectors.
        alpha_collection: numpy.ndarray
            2D (dim, n_elems) array containing data with 'float' type.
            Array contining element angular acceleration vectors.
        director_collection: numpy.ndarray
            3D (dim, dim, n_elems) array containing data with 'float' type.
            Array containing element director matrices.
        rest_lengths: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element lengths at rest configuration.
        density: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod elements densities.
        volume: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element volumes.
        mass: numpy.ndarray
            1D (n_nodes) array containing data with 'float' type.
            Rod node masses. Note that masses are stored on the nodes, not on elements.
        mass_second_moment_of_inertia: numpy.ndarray
            3D (dim, dim, n_elems) array containing data with 'float' type.
            Rod element mass second moment of interia.
        inv_mass_second_moment_of_inertia: numpy.ndarray
            3D (dim, dim, n_elems) array containing data with 'float' type.
            Rod element inverse mass moment of inertia.
        rest_voronoi_lengths: numpy.ndarray
            1D (n_voronoi) array containing data with 'float' type.
            Rod lengths on the voronoi domain at the rest configuration.
        internal_forces: numpy.ndarray
            2D (dim, n_nodes) array containing data with 'float' type.
            Rod node internal forces. Note that internal forces are stored on the node, not on elements.
        internal_torques: numpy.ndarray
            2D (dim, n_elems) array containing data with 'float' type.
            Rod element internal torques.
        external_forces: numpy.ndarray
            2D (dim, n_nodes) array containing data with 'float' type.
            External forces acting on rod nodes.
        external_torques: numpy.ndarray
            2D (dim, n_elems) array containing data with 'float' type.
            External torques acting on rod elements.
        lengths: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element lengths.
        tangents: numpy.ndarray
            2D (dim, n_elems) array containing data with 'float' type.
            Rod element tangent vectors.
        radius: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element radius.
        dilatation: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element dilatation.
        voronoi_dilatation: numpy.ndarray
            1D (n_voronoi) array containing data with 'float' type.
            Rod dilatation on voronoi domain.
        dilatation_rate: numpy.ndarray
            1D (n_elems) array containing data with 'float' type.
            Rod element dilatation rates.
    """

    def __init__(
        self,
        n_elements,
        position,
        velocity,
        omega,
        acceleration,
        angular_acceleration,
        directors,
        radius,
        mass_second_moment_of_inertia,
        inv_mass_second_moment_of_inertia,
        shear_matrix,
        bend_matrix,
        density,
        volume,
        mass,
        internal_forces,
        internal_torques,
        external_forces,
        external_torques,
        lengths,
        rest_lengths,
        tangents,
        dilatation,
        dilatation_rate,
        voronoi_dilatation,
        rest_voronoi_lengths,
        sigma,
        kappa,
        rest_sigma,
        rest_kappa,
        internal_stress,
        internal_couple,
        ring_rod_flag,
    ):
        self.n_elems = n_elements
        self.position_collection = position
        self.velocity_collection = velocity
        self.omega_collection = omega
        self.acceleration_collection = acceleration
        self.alpha_collection = angular_acceleration
        self.director_collection = directors
        self.radius = radius
        self.mass_second_moment_of_inertia = mass_second_moment_of_inertia
        self.inv_mass_second_moment_of_inertia = inv_mass_second_moment_of_inertia
        self.shear_matrix = shear_matrix
        self.bend_matrix = bend_matrix
        self.density = density
        self.volume = volume
        self.mass = mass
        self.internal_forces = internal_forces
        self.internal_torques = internal_torques
        self.external_forces = external_forces
        self.external_torques = external_torques
        self.lengths = lengths
        self.rest_lengths = rest_lengths
        self.tangents = tangents
        self.dilatation = dilatation
        self.dilatation_rate = dilatation_rate
        self.voronoi_dilatation = voronoi_dilatation
        self.rest_voronoi_lengths = rest_voronoi_lengths
        self.sigma = sigma
        self.kappa = kappa
        self.rest_sigma = rest_sigma
        self.rest_kappa = rest_kappa
        self.internal_stress = internal_stress
        self.internal_couple = internal_couple
        self.ring_rod_flag = ring_rod_flag

#计算出每一段的length，tangents，radius，dilatation, voronoi_length, voronoi_dilatation
#还计算的是剪切应变sigma，也就是把切向量转到了杆坐标系中，然后乘以dilatation，然后减去z_vector，这可以表示拉伸，sigma是在杆坐标系中的
        _compute_shear_stretch_strains(
            self.position_collection,
            self.volume,
            self.lengths,
            self.tangents,
            self.radius,
            self.rest_lengths,
            self.rest_voronoi_lengths,
            self.dilatation,
            self.voronoi_dilatation,
            self.director_collection,
            self.sigma,
        )

        # Compute bending twist strains
        ##先得到相邻两个杆变化对应的旋转矩阵，找到其轴角对应的向量，再用这个向量除以这段的长度。就得到了每一段对应的曲率向量kappa
        #这也是在Theory板块中有提到过
        _compute_bending_twist_strains(
            self.director_collection, self.rest_voronoi_lengths, self.kappa
        )

    @classmethod
    def straight_rod(
        cls,
        n_elements: int,
        start: np.ndarray,
        direction: np.ndarray,
        normal: np.ndarray,
        base_length: float,
        base_radius: float,
        density: float,
        *,
        nu: Optional[float] = None,
        youngs_modulus: float,
        **kwargs,
    ):
        """
        Cosserat rod constructor for straight-rod geometry.


        Notes
        -----
        Since we expect the Cosserat Rod to simulate soft rod, Poisson's ratio is set to 0.5 by default.
        It is possible to give additional argument "shear_modulus" or "poisson_ratio" to specify extra modulus.


        Parameters
        ----------
        n_elements : int
            Number of element. Must be greater than 3.
            Generally recommended to start with 40-50, and adjust the resolution.
        start : NDArray[3, float]
            Starting coordinate in 3D
        direction : NDArray[3, float]
            Direction of the rod in 3D
        normal : NDArray[3, float]
            Normal vector of the rod in 3D
        base_length : float
            Total length of the rod
        base_radius : float
            Uniform radius of the rod
        density : float
            Density of the rod
        nu : float
            Damping coefficient for Rayleigh damping
        youngs_modulus : float
            Young's modulus
        **kwargs : dict, optional
            The "position" and/or "directors" can be overrided by passing "position" and "directors" argument. Remember, the shape of the "position" is (3,n_elements+1) and the shape of the "directors" is (3,3,n_elements).

        Returns
        -------
        CosseratRod

        """

        if nu is not None:
            raise ValueError(
                # Remove the option to set internal nu inside, beyond v0.4.0
                "The option to set damping coefficient (nu) for the rod during rod\n"
                "initialisation is now deprecated. Instead, for adding damping to rods,\n"
                "please derive your simulation class from the add-on Damping mixin class.\n"
                "For reference see the class elastica.dissipation.AnalyticalLinearDamper(),\n"
                "and for usage check examples/axial_stretching.py"
            )
        # Straight rod is not ring rod set flag to false
        ring_rod_flag = False
        (
            n_elements,
            position,
            velocities,
            omegas,
            accelerations,
            angular_accelerations,
            directors,
            radius,
            mass_second_moment_of_inertia,
            inv_mass_second_moment_of_inertia,
            shear_matrix,
            bend_matrix,
            density,
            volume,
            mass,
            internal_forces,
            internal_torques,
            external_forces,
            external_torques,
            lengths,
            rest_lengths,
            tangents,
            dilatation,
            dilatation_rate,
            voronoi_dilatation,
            rest_voronoi_lengths,
            sigma,
            kappa,
            rest_sigma,
            rest_kappa,
            internal_stress,
            internal_couple,
        ) = allocate(
            n_elements,
            direction,
            normal,
            base_length,
            base_radius,
            density,
            youngs_modulus,
            rod_origin_position = start,
            ring_rod_flag = ring_rod_flag,
            **kwargs,
        )

        return cls(
            n_elements,
            position,
            velocities,
            omegas,
            accelerations,
            angular_accelerations,
            directors,
            radius,
            mass_second_moment_of_inertia,
            inv_mass_second_moment_of_inertia,
            shear_matrix,
            bend_matrix,
            density,
            volume,
            mass,
            internal_forces,
            internal_torques,
            external_forces,
            external_torques,
            lengths,
            rest_lengths,
            tangents,
            dilatation,
            dilatation_rate,
            voronoi_dilatation,
            rest_voronoi_lengths,
            sigma,
            kappa,
            rest_sigma,
            rest_kappa,
            internal_stress,
            internal_couple,
            ring_rod_flag,
        )

#本函数作用就是计算出每一段的长度，切向量，半径
@numba.njit(cache=True)
def _compute_geometry_from_state(
    position_collection, volume, lengths, tangents, radius
):
    #输入量为一个3*n的矩阵，输出量为一个3*(n-1)的矩阵，输出量的第i列为输入量的第i+1列减去第i列
    #在这里就是把position_collection的每一列的差值计算出来，然后计算出长度，然后计算出切向量，最后计算出半径
    position_diff = position_difference_kernel(position_collection)
    #计算每段长度给lengths
    lengths[:] = _batch_norm(position_diff) + 1e-10
    #计算每段切向量以及半径给tangents
    for k in range(lengths.shape[0]):
        tangents[0,k] = position_diff[0,k] / lengths[k]
        tangents[1,k] = position_diff[1,k] / lengths[k]
        tangents[2,k] = position_diff[2,k] / lengths[k]
        radius[k] = np.sqrt(volume[k]/lengths[k]/np.pi)

#计算出每一段的length，tangents，radius，dilatation, voronoi_length, voronoi_dilatation
@numba.njit(cache=True)
def _compute_all_dilatations(
    position_collection,
    volume,
    lengths,
    tangents,
    radius,
    dilatation,
    rest_lengths,
    rest_voronoi_lengths,
    voronoi_dilatation,
):

    #本函数作用就是计算出每一段的length，tangents，radius
    _compute_geometry_from_state(position_collection, volume, lengths, tangents, radius)
    #这里就是计算每一段的伸缩比,第一次计算的时候其实都是1
    for k in range(lengths.shape[0]):
        dilatation[k] = lengths[k] / (rest_lengths[k])

    ##输入一个n维向量，输出的是一个n-1维向量，输出的第i个元素为输入的第i个元素与第i+1个元素的平均值
    #在这里计算的就是两端的平均值赋给了voronoi_length
    #所以现在voronoi_length在我的理解下就是在内部节点给它赋予一段element，就是这个节点左右的element各取一半
    voronoi_length = position_average(lengths)

    for k in range(voronoi_length.shape[0]):
        voronoi_dilatation[k] = voronoi_length[k] / rest_voronoi_lengths[k]


#计算出每一段的length，tangents，radius，dilatation, voronoi_length, voronoi_dilatation
#还计算的是剪切应变sigma，也就是把切向量转到了杆坐标系中，然后乘以dilatation，然后减去z_vector，这可以表示拉伸，sigma是在杆坐标系中的
@numba.njit(cache=True)
def _compute_shear_stretch_strains(
    position_collection,
    volume,
    lengths,
    tangents,
    radius,
    rest_lengths,
    rest_voronoi_lengths,
    dilatation,
    voronoi_dilatation,
    director_collection,
    sigma,
):
    
#计算出每一段的length，tangents，radius，dilatation, voronoi_length, voronoi_dilatation

    _compute_all_dilatations(
        position_collection,
        volume,
        lengths,
        tangents,
        radius,
        dilatation,
        rest_lengths,
        rest_voronoi_lengths,
        voronoi_dilatation,
    )

    #这个有点像https://www.cosseratrods.org 中的Theory的那个\sigma但是有些问题，比如那里并不是减z_vector
    #这里director_collection是矩阵的旋转矩阵，应该是把切向向量转到了杆坐标系中，(0,0,1)就是d3，前面的就是et再把et转到了杆坐标系中
    
    #计算的是剪切应变sigma，也就是把切向量转到了杆坐标系中，然后乘以dilatation，然后减去z_vector，这可以表示拉伸+剪切

    z_vector = np.array([0.0,0.0,1.0]).reshape(3,-1)
    sigma[:] = dilatation * _batch_matvec(director_collection, tangents) - z_vector

#先得到相邻两个杆变化对应的旋转矩阵，找到其轴角对应的向量，再用这个向量除以这段的长度。就得到了每一段对应的曲率向量
@numba.njit(cache=True)
def _compute_bending_twist_strains(
    director_collection, rest_voronoi_length, kappa
):
    #这里_inv_rotate给出了相邻两个矩阵旋转矩阵的逆矩阵，通过轴角方式给出的，其中向量的模是旋转角度，向量的方向是旋转轴
    temp = _inv_rotate(director_collection)
    blocksize = rest_voronoi_length.shape[0]
    #这里kappa就是旋转轴除以剩余的长度，还没有特别明白，这是要结合cossearrod计算得到的内容来看的，先不急
    #我的猜测这个就是旋转角度除以弧长，近似为圆形轨迹，也就是多段常曲率预测

    #但是为啥没有返回值？也蛮奇怪的,应该就是直接改变了kappa的值，所以不需要返回值吧
    #这里的kappa是旋转角度除以弧长，也就是曲率向量（弧度），这个也是在杆坐标系中的
    for k in range(blocksize):
        kappa[0,k] = temp[0,k] / rest_voronoi_length[k]
        kappa[1,k] = temp[1,k] / rest_voronoi_length[k]
        kappa[2,k] = temp[2,k] / rest_voronoi_length[k]

class MaxDimension:
    @staticmethod
    def value():
        return 3

def _assert_shape(array: np.ndarray, expected_shape: Tuple[int], name: str):
    assert array.shape == expected_shape, (
        f"Expected shape {expected_shape} for {name}, "
        f"but got {array.shape} instead."
    )


def assert_allclose(actual, desired, rtol = 1e-7, atol = 0, equal_nan = True,
                    err_msg = '', verbose = True):
    __tracebackhide__ = True


def _position_validity_checker(position, start, n_elements):
    _assert_shape(position, (MaxDimension.value(), n_elements + 1), "position")

    #Check if the start and end of the rod are as expected
    assert_allclose(
        position[..., 0],
        start,
        atol = Tolerance.atol(),
        err_msg = str(
            "First entry of position" + "(" + str(position[..., 0]) + ")"
            "is different from" + "(" + str(start) + ")"
            )
        )
def _directors_validity_checker(directors, tangents, n_elements):
    pass


def _assert_dim(vector, max_dim: int, name:str):
    assert vector.ndim < max_dim, (
        f"Expected shape ({max_dim},) for {name}, "
        f"but got {vector.shape} instead."
    )

def allocate(
    n_elements,
    direction,
    normal,
    base_length,
    base_radius,
    density,
    youngs_modulus: float,
    *,
    rod_origin_position: np.ndarray,
    ring_rod_flag: bool,
    shear_modulus: Optional[float] = None,
    position: Optional[np.ndarray] = None,
    directors: Optional[np.ndarray] = None,
    rest_sigma: Optional[np.ndarray] = None,
    rest_kappa: Optional[np.ndarray] = None,
    **kwargs,
):
    log = logging.getLogger()
    assert n_elements > 2 if ring_rod_flag else n_elements > 1
    assert base_length > Tolerance.atol()
    assert np.sqrt(np.dot(normal, normal)) > Tolerance.atol()
    assert np.sqrt(np.dot(direction, direction)) > Tolerance.atol()

    #define the number of nodes and voronoi elements base on if rod is
    #straight and open or closed and ring shaped
    n_nodes = n_elements if ring_rod_flag else n_elements + 1
    n_voronoi_elements = n_elements if ring_rod_flag else n_elements - 1

    #check if position is provided
    if position is None:
        #set the position array
        position = np.zeros((MaxDimension.value(), n_nodes))
        if not ring_rod_flag:   #i.e. a straight open rod
            start = rod_origin_position
            end = start + direction * base_length
            for i in range(0,3):
                position[i, ...] = np.linspace(start[i], end[i], n_elements + 1)
                _position_validity_checker(position, start, n_elements)
        else:
            pass

    #compute rest length and tangents
    position_for_difference = (
        np.hstack((position, position[..., 0].reshape(3,1)))
        if ring_rod_flag
        else position
    )
    position_diff = position_for_difference[:, 1:] - position_for_difference[:, :-1]
    rest_lengths = _batch_norm(position_diff)
    print("cosserat_rod_528")
    print(rest_lengths)
    tangents = position_diff / rest_lengths
    normal = normal / np.sqrt(np.dot(normal, normal))
    if directors is None: #Generate a straight uniform rod
        #set the directors matrix
        directors = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements))
        #Construct directors using tangents and normal
        #这里就是把normal向量变成了一个矩阵，矩阵的每一列都是normal向量
        normal_collection = np.repeat(normal[:, np.newaxis], n_elements, axis = 1)
        #检查normal_collection与tangents是否垂直且纬度一致
        assert_allclose(
            _batch_dot(normal_collection, tangents),
            0,
            atol = Tolerance.atol(),
            err_msg = "Normal and tangent vectors are not orthogonal",
        )
        #directors[x,y,z] x:0,1,2分别代表normal，tangent， cross
        #y:0,1,2代表x，y，z(也就是x的三个向量在坐标系下的坐标)，z:0，1.....代表n_elements个元素
        directors[0, ...] = normal_collection
        directors[1, ...] = _batch_cross(tangents, normal_collection)
        directors[2, ...] = tangents
    _directors_validity_checker(directors, tangents, n_elements)
    #set radius array
    radius =  np.zeros((n_elements))
    #Check if the user input radius is valid
    radius_temp = np.array(base_radius)
    _assert_dim(radius_temp, 2, "radius")
    radius[:] = radius_temp
    assert np.all(radius > Tolerance.atol()), "Radius must be greater than zero"
    
    #set density arrary
    density_arrary = np.zeros((n_elements))
    #Check if the user input density is valid
    density_temp = np.array(density)
    _assert_dim(density_temp, 2, "density")
    density_arrary[:] = density_temp
    #check if the elements of density arrary are greater than tolerance
    assert np.all(density_arrary > Tolerance.atol()), "Density must be greater than zero" 

    #second moment of inertia（截面二次轴矩）
    A0 = np.pi * radius * radius
    I0_1 = A0 * A0 / (4.0 * np.pi)
    I0_2 = I0_1
    I0_3 = 2.0 * I0_1
    I0 = np.array([I0_1, I0_2, I0_3]).transpose()
    #mass second moment of inertia for disk cross section
    mass_second_moment_of_inertia = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements), np.float64)
    mass_second_moment_of_inertia_temp = np.einsum(
        "ij, i->ij", I0, density*rest_lengths
    )
    #这一步简单来说是这样的，mass_second_moment_of_inertia_temp是一个3*3*n_elements的矩阵，对于每一个n_elements，都有一个3*3的矩阵，
    #即刚度矩阵，而这个刚度矩阵对应的就是在ass_second_moment_of_inertia_temp中计算出来的每个n_elements对应的那一行作为对角元素所张成的矩阵
    for i in range(n_elements):
        np.fill_diagonal(
            mass_second_moment_of_inertia[..., i],
            mass_second_moment_of_inertia_temp[i, ...]
        )
    #sanity check of mass second moment of inertia
    pass
    #Inverse of second moment of inertia
    inv_mass_second_moment_of_inertia = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements))
    for i in range(n_elements):
        #check rank of mass second moment of inertia to see if it is invertible
        pass
        inv_mass_second_moment_of_inertia[..., i] = np.linalg.inv(mass_second_moment_of_inertia[..., i])
    #shear/stretch matrix
    if not shear_modulus:
        log.info(
            """Shear modulus not provided, using Young's modulus and Poisson's ratio to compute shear modulus.\n
            in such case, we assume possion_ratio = 0.5"""
        )
        shear_modulus = youngs_modulus / (2.0 * (1.0 + 0.5))

    alpha_c = 27.0/28.0
    shear_matrix = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements), np.float64)
    #x,y方向是抗剪刚度(kGA)，而z方向是抗拉刚度(EA)
    for i in range(n_elements):
        np.fill_diagonal(
            shear_matrix[..., i],
            [
                alpha_c * shear_modulus * A0[i],
                alpha_c * shear_modulus * A0[i],
                youngs_modulus * A0[i]
            ]
        )
    #Bend/Twist matrix
    #抗弯/抗扭矩阵
    bend_matrix = np.zeros((MaxDimension.value(), MaxDimension.value(), n_voronoi_elements + 1), np.float64)
    for i in range(n_elements):
        np.fill_diagonal(
            bend_matrix[..., i],
            [
                youngs_modulus * I0_1[i],
                youngs_modulus * I0_2[i],
                shear_modulus * I0_3[i]
            ]
        )
    #check Bend/Twist matrix
    for i in range(0, MaxDimension.value()):
        assert np.all(
            bend_matrix[i, i, :] > Tolerance.atol()
        ), "Bend matrix has to be greater than 0"

    #Compute bend matrix in Voronoi Domain
    #说简单点就是，我的微分方程设立对应的每个点是我的节点，节点是每一小段的两端而不是中心，我现在给出的matrix是每一小段的中心
    #所以我要把每一小段的中心的matrix转换成每一小段的两端的matrix
    #Voronoi图是一种将空间划分为多个区域的方法，每个区域包含一个生成点，且区域内的任何位置离它的生成点都比离其他生成点更近。
    #在这个例子中，你可以将每个节点看作是一个生成点，而每段杆可以看作是连接两个生成点的边。然后，你可以将每个节点的弯曲矩阵看作是该节点对应的Voronoi区域的属性。
    if ring_rod_flag:
        bend_matrix[..., -1] = bend_matrix[..., 0]
    rest_lengths_temp_for_voronoi = (
        np.hstack((rest_lengths, rest_lengths[0])) if ring_rod_flag else rest_lengths
    )
    bend_matrix = (
        bend_matrix[...,1:] * rest_lengths_temp_for_voronoi[1:] + bend_matrix[...,:-1] * rest_lengths_temp_for_voronoi[0:-1]
    ) / (rest_lengths_temp_for_voronoi[1:] + rest_lengths_temp_for_voronoi[:-1])
        
    #compute volume of elements
    volume = np.pi * radius * radius * rest_lengths

    #compute mass of elements,这里把每一段的质量分到了两个端点上
    mass = np.zeros(n_elements+1)
    if not ring_rod_flag:
        mass[: -1] += 0.5 * density * volume
        mass[1:] += 0.5 * density * volume
    else:
        mass[:] = density * volume
    if rest_sigma is None:
        rest_sigma = np.zeros((MaxDimension.value(), n_elements))
    if rest_kappa is None:
        rest_kappa = np.zeros((MaxDimension.value(), n_voronoi_elements))
    #compute rest voronoi lengths
    rest_voronoi_lengths = 0.5 * (rest_lengths[:-1] + rest_lengths[1:])

    #Allocate arrarys for Cosserat Rod equations
    velocities = np.zeros((MaxDimension.value(), n_nodes))
    omegas = np.zeros((MaxDimension.value(), n_elements))
    accelerations = 0.0 * velocities
    angular_accelerations = 0.0 * omegas

    internal_forces = 0.0 * accelerations
    internal_torques = 0.0 * angular_accelerations

    external_forces = 0.0 * accelerations
    external_torques = 0.0 * angular_accelerations

    lengths = np.zeros(n_elements)
    tangents = np.zeros((3, n_elements))

    dilatation = np.zeros((n_elements))
    voronoi_dilatation = np.zeros((n_voronoi_elements))
    dilatation_rate = np.zeros((n_elements))

    sigma = np.zeros((3, n_elements))
    kappa = np.zeros((3, n_voronoi_elements))
    
    internal_stress = np.zeros((3, n_elements))
    internal_couple = np.zeros((3, n_voronoi_elements))

    return(
        n_elements,
        position,
        velocities,
        omegas,
        accelerations,
        angular_accelerations,
        directors,
        radius,
        mass_second_moment_of_inertia,
        inv_mass_second_moment_of_inertia,
        shear_matrix,
        bend_matrix,
        density_arrary,
        volume,
        mass,
        internal_forces,
        internal_torques,
        external_forces,
        external_torques,
        lengths,
        rest_lengths,
        tangents,
        dilatation,
        dilatation_rate,
        voronoi_dilatation,
        rest_voronoi_lengths,
        sigma,
        kappa,
        rest_sigma,
        rest_kappa,
        internal_stress,
        internal_couple,
    )




# if __name__ == '__main__':
#     ring_rod_flag = False
#     n_elements = 50
#     #初始位置
#     start = np.zeros((3,))
#     #初始方向
#     direction = np.array([1.0, 0.0, 0.0])
#     #法线方向
#     normal = np.array([0.0, 0.0, 1.0])
#     #杆长
#     base_length = 6.0
#     #杆半径
#     base_radius = 0.15
#     #杆截面积
#     base_area = np.pi * base_radius ** 2
#     #杆材料密度
#     density = 5000
#     #杨氏模量
#     youngs_modulus = 1e6
#     #面积矩
#     I = (np.pi / 4) * base_radius ** 4
#     possion_ratio = 0.5
#     shear_modulus = youngs_modulus / (2 * (1 + possion_ratio))
#     rod_origin_position = start

#     oungs_modulus: float
#     nu_for_torques: Optional[float] = None
#     position: Optional[np.ndarray] = None
#     directors: Optional[np.ndarray] = None
#     rest_sigma: Optional[np.ndarray] = None
#     rest_kappa: Optional[np.ndarray] = None

#     #磁参数
#     magnetization_density = 1e5
#     magnetic_field_angle = 2 * np.pi / 3
#     magnetic_field = 1e-2
#     #将每个杆元素的磁化方向设置为一致
#     magnetization_direction = np.ones((n_elements)) * direction.reshape(3, 1)
#     log = logging.getLogger()
#     assert n_elements > 2 if ring_rod_flag else n_elements > 1
#     assert base_length > Tolerance.atol()
#     assert np.sqrt(np.dot(normal, normal)) > Tolerance.atol()
#     assert np.sqrt(np.dot(direction, direction)) > Tolerance.atol()

#     #define the number of nodes and voronoi elements base on if rod is
#     #straight and open or closed and ring shaped
#     n_nodes = n_elements if ring_rod_flag else n_elements + 1
#     n_voronoi_elements = n_elements if ring_rod_flag else n_elements - 1

#     #check if position is provided
#     if position is None:
#         #set the position array
#         position = np.zeros((MaxDimension.value(), n_nodes))
#         if not ring_rod_flag:   #i.e. a straight open rod
#             start = rod_origin_position
#             end = start + direction * base_length
#             for i in range(0,3):
#                 position[i, ...] = np.linspace(start[i], end[i], n_elements + 1)
#                 _position_validity_checker(position, start, n_elements)
#         else:
#             pass

#     #compute rest length and tangents
#     position_for_difference = (
#         np.hstack((position, position[..., 0].reshape(3,1)))
#         if ring_rod_flag
#         else position
#     )
#     position_diff = position_for_difference[:, 1:] - position_for_difference[:, :-1]
#     rest_lengths = _batch_norm(position_diff)
#     tangents = position_diff / rest_lengths
#     normal = normal / np.sqrt(np.dot(normal, normal))
#     if directors is None: #Generate a straight uniform rod
#         #set the directors matrix
#         directors = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements))
#         #Construct directors using tangents and normal
#         #这里就是把normal向量变成了一个矩阵，矩阵的每一列都是normal向量
#         normal_collection = np.repeat(normal[:, np.newaxis], n_elements, axis = 1)
#         #检查normal_collection与tangents是否垂直且纬度一致
#         assert_allclose(
#             _batch_dot(normal_collection, tangents),
#             0,
#             atol = Tolerance.atol(),
#             err_msg = "Normal and tangent vectors are not orthogonal",
#         )
#         #directors[x,y,z] x:0,1,2分别代表normal，tangent， cross，y:0,1,2代表x，y，z，z:0，1.....代表n_elements个元素
#         directors[0, ...] = normal_collection
#         directors[1, ...] = _batch_cross(tangents, normal_collection)
#         directors[2, ...] = tangents
#     _directors_validity_checker(directors, tangents, n_elements)
#     #set radius array
#     radius =  np.zeros((n_elements))
#     #Check if the user input radius is valid
#     radius_temp = np.array(base_radius)
#     _assert_dim(radius_temp, 2, "radius")
#     radius[:] = radius_temp
#     assert np.all(radius > Tolerance.atol()), "Radius must be greater than zero"
    
#     #set density arrary
#     density_arrary = np.zeros((n_elements))
#     #Check if the user input density is valid
#     density_temp = np.array(density)
#     _assert_dim(density_temp, 2, "density")
#     density_arrary[:] = density_temp
#     #check if the elements of density arrary are greater than tolerance
#     assert np.all(density_arrary > Tolerance.atol()), "Density must be greater than zero" 

#     #second moment of inertia（截面二次轴矩）
#     A0 = np.pi * radius * radius
#     I0_1 = A0 * A0 / (4.0 * np.pi)
#     I0_2 = I0_1
#     I0_3 = 2.0 * I0_1
#     I0 = np.array([I0_1, I0_2, I0_3]).transpose()
#     #mass second moment of inertia for disk cross section
#     mass_second_moment_of_inertia = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements), np.float64)
#     mass_second_moment_of_inertia_temp = np.einsum(
#         "ij, i->ij", I0, density*rest_lengths
#     )
#     #这一步简单来说是这样的，mass_second_moment_of_inertia_temp是一个3*3*n_elements的矩阵，对于每一个n_elements，都有一个3*3的矩阵，
#     #即刚度矩阵，而这个刚度矩阵对应的就是在ass_second_moment_of_inertia_temp中计算出来的每个n_elements对应的那一行作为对角元素所张成的矩阵
#     for i in range(n_elements):
#         np.fill_diagonal(
#             mass_second_moment_of_inertia[..., i],
#             mass_second_moment_of_inertia_temp[i, ...]
#         )
#     #sanity check of mass second moment of inertia
#     pass
#     #Inverse of second moment of inertia
#     inv_mass_second_moment_of_inertia = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements))
#     for i in range(n_elements):
#         #check rank of mass second moment of inertia to see if it is invertible
#         pass
#         inv_mass_second_moment_of_inertia[..., i] = np.linalg.inv(mass_second_moment_of_inertia[..., i])
#     #shear/stretch matrix
#     if not shear_modulus:
#         log.info(
#             """Shear modulus not provided, using Young's modulus and Poisson's ratio to compute shear modulus.\n
#             in such case, we assume possion_ratio = 0.5"""
#         )
#         shear_modulus = youngs_modulus / (2.0 * (1.0 + 0.5))

#     alpha_c = 27.0/28.0
#     shear_matrix = np.zeros((MaxDimension.value(), MaxDimension.value(), n_elements), np.float64)
#     #x,y方向是抗剪刚度(kGA)，而z方向是抗拉刚度(EA)
#     for i in range(n_elements):
#         np.fill_diagonal(
#             shear_matrix[..., i],
#             [
#                 alpha_c * shear_modulus * A0[i],
#                 alpha_c * shear_modulus * A0[i],
#                 youngs_modulus * A0[i]
#             ]
#         )
#     #Bend/Twist matrix
#     #抗弯/抗扭矩阵
#     bend_matrix = np.zeros((MaxDimension.value(), MaxDimension.value(), n_voronoi_elements + 1), np.float64)
#     for i in range(n_elements):
#         np.fill_diagonal(
#             bend_matrix[..., i],
#             [
#                 youngs_modulus * I0_1[i],
#                 youngs_modulus * I0_2[i],
#                 shear_modulus * I0_3[i]
#             ]
#         )
#     #check Bend/Twist matrix
#     for i in range(0, MaxDimension.value()):
#         assert np.all(
#             bend_matrix[i, i, :] > Tolerance.atol()
#         ), "Bend matrix has to be greater than 0"

#     #Compute bend matrix in Voronoi Domain
#     #说简单点就是，我的微分方程设立对应的每个点是我的节点，节点是每一小段的两端而不是中心，我现在给出的matrix是每一小段的中心
#     #所以我要把每一小段的中心的matrix转换成每一小段的两端的matrix
#     #Voronoi图是一种将空间划分为多个区域的方法，每个区域包含一个生成点，且区域内的任何位置离它的生成点都比离其他生成点更近。
#     #在这个例子中，你可以将每个节点看作是一个生成点，而每段杆可以看作是连接两个生成点的边。然后，你可以将每个节点的弯曲矩阵看作是该节点对应的Voronoi区域的属性。
#     if ring_rod_flag:
#         bend_matrix[..., -1] = bend_matrix[..., 0]
#     rest_lengths_temp_for_voronoi = (
#         np.hstack((rest_lengths, rest_lengths[0])) if ring_rod_flag else rest_lengths
#     )
#     bend_matrix = (
#         bend_matrix[...,1:] * rest_lengths_temp_for_voronoi[1:] + bend_matrix[...,:-1] * rest_lengths_temp_for_voronoi[0:-1]
#     ) / (rest_lengths_temp_for_voronoi[1:] + rest_lengths_temp_for_voronoi[:-1])
        
#     #compute volume of elements
#     volume = np.pi * radius * radius * rest_lengths

#     #compute mass of elements,这里把每一段的质量分到了两个端点上
#     mass = np.zeros(n_elements+1)
#     if not ring_rod_flag:
#         mass[: -1] += 0.5 * density * volume
#         mass[1:] += 0.5 * density * volume
#     else:
#         mass[:] = density * volume
#     if rest_sigma is None:
#         rest_sigma = np.zeros((MaxDimension.value(), n_elements))
#     if rest_kappa is None:
#         rest_kappa = np.zeros((MaxDimension.value(), n_voronoi_elements))
#     #compute rest voronoi lengths
#     rest_voronoi_lengths = 0.5 * (rest_lengths[:-1] + rest_lengths[1:])

#     #Allocate arrarys for Cosserat Rod equations
#     velocities = np.zeros((MaxDimension.value(), n_nodes))
#     omegas = np.zeros((MaxDimension.value(), n_elements))
#     accelerations = 0.0 * velocities
#     angular_accelerations = 0.0 * omegas

#     internal_forces = 0.0 * accelerations
#     internal_torques = 0.0 * angular_accelerations

#     external_forces = 0.0 * accelerations
#     external_torques = 0.0 * angular_accelerations

#     lengths = np.zeros(n_elements)
#     tangents = np.zeros((3, n_elements))

#     dilatation = np.zeros((n_elements))
#     voronoi_dilatation = np.zeros((n_voronoi_elements))
#     dilatation_rate = np.zeros((n_elements))

#     sigma = np.zeros((3, n_elements))
#     kappa = np.zeros((3, n_voronoi_elements))
    
#     internal_stress = np.zeros((3, n_elements))
#     internal_couple = np.zeros((3, n_voronoi_elements))

#     print(rest_lengths)


