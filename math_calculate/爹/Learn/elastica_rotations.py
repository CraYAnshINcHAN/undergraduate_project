import functools

import numpy as np
from numpy import sqrt
from numpy import arccos
from numpy import sin
from numpy import cos
from numpy import sqrt

from elastica_linalg import _batch_matmul
from numba import njit

#这里是根据轴角计算旋转矩阵，相关的很多资料在这篇文章https://zhuanlan.zhihu.com/p/45404840
@njit(cache=True)
def _get_rotation_matrix(scale:float, axis_collection):
    blocksize = axis_collection.shape[1]
    rot_mat = np.matrix((3,3,blocksize))

    for k in range(blocksize):
        v0 = axis_collection[0,k]
        v1 = axis_collection[1,k]
        v2 = axis_collection[2,k]

        theta = sqrt(v0*v0 + v1*v1 + v2*v2)

        v0 /= theta +1e-14
        v1 /= theta +1e-14
        v2 /= theta +1e-14

        theta *= scale

        u_prefix = sin(theta)
        u_sq_prefix = 1.0 - cos(theta)

        rot_mat[0, 0, k] = 1.0 - u_sq_prefix * (v1*v1 + v2*v2)
        rot_mat[1, 1, k] = 1.0 - u_sq_prefix * (v0*v0 + v2*v2)
        rot_mat[2, 2, k] = 1.0 - u_sq_prefix * (v0*v0 + v1*v1)

        rot_mat[0, 1, k] = u_prefix * v2 + u_sq_prefix * v0 * v1
        rot_mat[1, 0, k] = -u_prefix * v2 + u_sq_prefix * v0 * v1
        rot_mat[0, 2, k] = -u_prefix * v1 + u_sq_prefix * v0 * v2
        rot_mat[2, 0, k] = u_prefix * v1 + u_sq_prefix * v0 * v2
        rot_mat[1, 2, k] = u_prefix * v0 + u_sq_prefix * v1 * v2
        rot_mat[2, 1, k] = -u_prefix * v0 + u_sq_prefix * v1 * v2

    return rot_mat

#这个主要是通过罗德里格斯公式计算旋转矩阵变化率，输出的是相邻两个矩阵之间变化的旋转轴以及旋转角度
@njit(cache=True)
def _inv_rotate(director_collection):
    blocksize = director_collection.shape[2] - 1
    vector_collection = np.empty((3,blocksize))

    for k in range(blocksize):
        #这里每个向量表现的是相邻两个旋转矩阵变化对应的旋转轴，具体内容参考https://blog.csdn.net/Sandy_WYM_/article/details/84309000
        #我还没有特别仔细看，但是相邻两个旋转矩阵之间的变化应该是R = R_(i+1)*R_i^T,从而使得R*R_i = R_(i+1)
        #然后再根据给出的资料中的内容，将旋转矩阵变化率转化为旋转轴以及旋转角度
        #但是具体的推导我还没有完成，需要之后代码框架看完再细致推导各个步骤
        vector_collection[0, k] = (
            director_collection[2, 0 ,k+1] * director_collection[1, 0, k]
            + director_collection[2, 1, k+1] * director_collection[1, 1, k]
            + director_collection[2, 2, k+1] * director_collection[1, 2, k]
        )-(
            director_collection[1, 0, k+1] * director_collection[2, 0, k]
            + director_collection[1, 1, k+1] * director_collection[2, 1, k]
            + director_collection[1, 2, k+1] * director_collection[2, 2, k]
        )

        vector_collection[1, k] = (
            director_collection[0, 0, k+1] * director_collection[2, 0, k]
            + director_collection[0, 1, k+1] * director_collection[2, 1, k]
            + director_collection[0, 2, k+1] * director_collection[2, 2, k]
        )-(
            director_collection[2, 0, k+1] * director_collection[0, 0, k]
            + director_collection[2, 1, k+1] * director_collection[0, 1, k]
            + director_collection[2, 2, k+1] * director_collection[0, 2, k]
        )

        vector_collection[2, k] = (
            director_collection[1, 0, k+1] * director_collection[0, 0, k]
            + director_collection[1, 1, k+1] * director_collection[0, 1, k]
            + director_collection[1, 2, k+1] * director_collection[0, 2, k]
        )-(
            director_collection[0, 0, k+1] * director_collection[1, 0, k]
            + director_collection[0, 1, k+1] * director_collection[1, 1, k]
            + director_collection[0, 2, k+1] * director_collection[1, 2, k]
        )

        trace = (
            (
                director_collection[0, 0, k+1] * director_collection[0, 0, k]
                + director_collection[0, 1, k+1] * director_collection[0, 1, k]
                + director_collection[0, 2, k+1] * director_collection[0, 2, k]
            )+(
                director_collection[1, 0, k+1] * director_collection[1, 0, k]
                + director_collection[1, 1, k+1] * director_collection[1, 1, k]
                + director_collection[1, 2, k+1] * director_collection[1, 2, k]
            )+(
                director_collection[2, 0, k+1] * director_collection[2, 0, k]
                + director_collection[2, 1, k+1] * director_collection[2, 1, k]
                + director_collection[2, 2, k+1] * director_collection[2, 2, k]
            )
        )

        theta =arccos(0.5 * trace - 0.5 - 1e-10)

        vector_collection[0, k] *= -0.5 * theta / sin(theta + 1e-14)
        vector_collection[1, k] *= -0.5 * theta / sin(theta + 1e-14)
        vector_collection[2, k] *= -0.5 * theta / sin(theta + 1e-14)

    return vector_collection

@njit(cache=True)
def _rotate(director_collection, scale: float, axis_collection):
    return _batch_matmul(
        _get_rotation_matrix(scale, axis_collection), director_collection
    )
