from numpy import finfo, float64

class Tolerance:
    @staticmethod
    def atol():
        return finfo(float64).eps * 1e4
    @staticmethod
    def rtol():
        return finfo(float64).eps * 1e11
#对两个数列，求其排列的奇偶性，若是偶排列，返回1，若是奇排列，返回-1
#若都是偶/奇排列，说明两个数列可以通过有限次的交换得到，否则不行
def perm_parity(first):
    parity = 1
    for i in range(0,len(first)-1):
        if first[i] != i:
            parity *= -1
            mn = min(range(i, len(first)), key=first.__getitem__)
            first[i], first[mn] = first[mn], first[i]
    return parity
#这里是B样条曲线的计算，具体的数学原理可以参考这篇文章https://zhuanlan.zhihu.com/p/431240916
def _bspline(t_coeff, l_centerline=1.0):
    pass

def _bspline():
    pass

def extend_instance(obj, cls):
    base_cls = obj.__class__
    base_cls_name = base_cls.__name__
    obj.__class__ = type(base_cls_name, (cls,base_cls),{})

