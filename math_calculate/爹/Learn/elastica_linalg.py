import numpy as np
from numba import njit
from numpy import sqrt
import functools
from itertools import permutations
from elastica_utils import perm_parity

#批量矩阵向量乘法，结果的每一列都是一个3*3(i*j)的矩阵和一个3*1(j*1)的向量相乘
#更具体来说，我一共给了k个矩阵和k个向量，每个矩阵都是3*3的，每个向量都是3*1的
#得到一个3*k的矩阵，每一列都是一个3*1的向量，对应的就是每个矩阵和每个向量相乘的结果
@njit(cache = True)
def _batch_matvec(matrix_collection, vector_collection):
    blocksize = vector_collection.shape[1]
    output_vector = np.zeros((3,blocksize))
    for i in range(3):
        for j in range(3):
            for k in range(blocksize):
                output_vector[i,k] += (
                    matrix_collection[i,j,k] * vector_collection[j,k]
                )
    return output_vector
#和上面差不多，只不过这里是向量和向量叉乘
@njit(cache=True)
def _batch_cross(first_vector_collection, second_vector_collection):
    blocksize = first_vector_collection.shape[1]
    output_vector = np.zeros((3, blocksize))
    for k in range(blocksize):
        output_vector[0, k] = (
            first_vector_collection[1, k] * second_vector_collection[2, k]
            - first_vector_collection[2, k] * second_vector_collection[1, k]
        )

        output_vector[1, k] = (
            first_vector_collection[2, k] * second_vector_collection[0, k]
            - first_vector_collection[0, k] * second_vector_collection[2, k]
        )

        output_vector[2, k] = (
            first_vector_collection[0, k] * second_vector_collection[1, k]
            - first_vector_collection[1, k] * second_vector_collection[0, k]
        )
    return output_vector

@njit(cache=True)
def _batch_matrix_transpose(input_matrix):
    output_matrix = np.empty(input_matrix.shape)
    for i in range(input_matrix.shape[0]):
        for j in range(input_matrix.shape[1]):
            output_matrix[j, i] = input_matrix[i, j]
    return output_matrix

@njit(cache=True)
def _batch_norm(vector):
    blocksize = vector.shape[1]
    output_vector = np.empty(blocksize)

    for k in range(blocksize):
        output_vector[k] = sqrt(
            vector[0, k] * vector[0, k] + vector[1, k] * vector[1, k] + vector[2, k] * vector[2, k]
        )

    return output_vector

@njit(cache=True)
def _batch_dot(first_vector, second_vector):
    blocksize = first_vector.shape[1]
    output_vector = np.zeros((blocksize,))
    for i in range(3):
        for k in range(blocksize):
            output_vector[k] += first_vector[i, k] * second_vector[i, k]

    return output_vector

@njit(cache=True)
def _batch_matmul(first_matrix_collection, second_matrix_collection):
    blocksize = first_matrix_collection.shape[2]
    output_matrix = np.empty((3, 3, blocksize))
    for i in range(3):
        for j in range(3):
            for m in range(3):
                for k in range(blocksize):
                    output_matrix[i, m, k] += (
                        first_matrix_collection[i, j, k] * second_matrix_collection[j, m, k]
                    )

    return output_matrix