import numpy as np
from numpy import zeros, empty
from numba import njit
import functools
#输入量为一个3*n的矩阵，输出量为一个3*(n-1)的矩阵，输出量的第i列为输入量的第i+1列减去第i列
@njit(cache=True)
def _difference(vector):
    blocksize = vector.shape[1] - 1
    output_vector = zeros((3, blocksize))

    for i in range(3):
        for k in range(blocksize):
            output_vector[i, k] += vector[i, k + 1] - vector[i, k]

    return output_vector
#输入一个n维向量，输出的是一个n-1维向量，输出的第i个元素为输入的第i个元素与第i+1个元素的平均值
@njit(cache=True)
def _average(vector):
    blocksize = vector.shape[0] - 1
    output_vector = empty((blocksize))

    for k in range(blocksize):
        output_vector[k] = 0.5 * (vector[k + 1] + vector[k])
        
    return output_vector