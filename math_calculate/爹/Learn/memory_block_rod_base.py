import numpy as np
#create block-structure class for collection of Cosserat rod systems.
#这里面做的是多根杆的问题，我们其实只需要做单根杆的问题，但是思路是一样的，先学会
def make_block_memory_metadata(n_elems_in_rods):
    #节点数量
    n_nodes_in_rods = n_elems_in_rods + 1
    #内部的节点的数量
    n_voronoi_in_rods = n_elems_in_rods - 1

    n_rods = n_elems_in_rods.shape[0]

    #gap between two rods have one ghost node
    #n_nodes_with_ghosts = np.sum(n_nodes_in_rods) + (n_rods - 1)
    #gap between two rods have two ghost elements : come out to n_nodes_with_ghosts - 1
    #加上幽灵节点的数量，因为这里并没有多根杆，所以也就没有幽灵节点
    n_elems_with_ghosts = np.sum(n_elems_in_rods) + 2*(n_rods - 1)

    #To be nulled
    #这里意思就是，给每个ghost node 一个编号，这个编号是从0开始的，然后每个ghost node的编号是前面的节点的数量。
    #举例来说，第一根杆有10个节点，那么第一个ghost node的编号就是10，第二根杆有20个节点，
    #那么第二个ghost node的编号就是10(第一根杆)+20(第二根杆)+1（第一个ghost节点）=31
    ghost_nodes_idx = np.zeros((n_rods -1,), dtype = np.int64)
    ghost_nodes_idx[:] = n_nodes_in_rods[:-1]
    ghost_nodes_idx = np.cumsum(ghost_nodes_idx)
    ghost_nodes_idx += np.arange(0, n_rods - 1, dtype = np.int64)

    ghost_elems_idx = np.zeros((2 * (n_rods - 1),), dtype = np.int64)
    #将 n_elems_in_rods 数组除了最后一个元素外的所有元素赋值给 ghost_elems_idx 数组的偶数索引位置（0，2，4，6，...）。
    #在 Python 中，切片语法 ::2 表示选择从头到尾，步长为 2 的所有元素，也就是所有偶数索引的元素。
    #整体而言，折合上一步做的事情一样，对于单根杆，没有ghost element
    ghost_elems_idx[::2] = n_elems_in_rods[:-1]
    ghost_elems_idx[1::2] = 1
    ghost_elems_idx = np.cumsum(ghost_elems_idx)
    ghost_elems_idx += np.repeat(np.arange(0, n_rods - 1, dtype = np.int64), 2)

    #现在对ghost_voronoi节点进行编号,其中，每两根杆之间有三个ghost_voronoi节点，再对其进行编号
    #编号的逻辑和上面的ghost_nodes_idx一样
    ghost_voronoi_idx = np.zeros(3 * (n_rods - 1), dtype = np.int64)
    ghost_voronoi_idx[::3] = n_voronoi_in_rods[:-1]
    ghost_voronoi_idx[1::3] = 1
    ghost_voronoi_idx[2::3] = 1
    ghost_voronoi_idx = np.cumsum(ghost_voronoi_idx)
    ghost_voronoi_idx += np.repeat(np.arange(0, n_rods - 1, dtype = np.int64), 3)

    return n_elems_with_ghosts, ghost_nodes_idx, ghost_elems_idx, ghost_voronoi_idx

#这段代码我还不是很明白，虽然从目前的理解上来说，之后并不需要使用这个函数，但是还是希望可以理解
#对于periodic_boundary_node_idx，看上去是在每个杆前面加了一个ghost node，然后在每个杆后面加了两根个ghost node
#前面的ghost node对应的参考节点是每根杆最后一个节点，后面的两个ghost node对应的参考节点是每根杆的第一个节点以及第二个节点
#这个函数的目的是什么？是为了计算周期性边界条件的吗？
#但是也可以发现，这个就好像把每根杆的第一个节点和最后一个节点连接起来了，这样就形成了一个环
def make_block_memory_periodic_boundary_metadata(n_elems_in_rods):
    #This function takes the number of elements of ring rods and compute the periodic boundary node,
    #element and voronoi index

    n_elem = n_elems_in_rods.copy()
    n_rods = n_elems_in_rods.shape[0]

    periodic_boundary_node_idx = np.zeros((2, 3 * n_rods), dtype = np.int64)
    #count ghost nodes, first rod does not have a ghost node at the start, so exclude first rod
    #这里设置了索引[3,6,...]的元素为1，其他的元素仍为0
    periodic_boundary_node_idx[0, 0::3][1:] = 1 
    
    periodic_boundary_node_idx[0, 1::3] = 1 + n_elem

    periodic_boundary_node_idx[0, 2::3] = 1
    periodic_boundary_node_idx[0,:] = np.cumsum(periodic_boundary_node_idx[0,:])
    periodic_boundary_node_idx[0,:] += np.repeat(np.arange(0, n_rods, dtype = np.int64), 3)

    periodic_boundary_node_idx[1, 0::3]=periodic_boundary_node_idx[0, 1::3] - 1
    periodic_boundary_node_idx[1, 1::3]=periodic_boundary_node_idx[0, 0::3] + 1
    periodic_boundary_node_idx[1, 2::3]=periodic_boundary_node_idx[0, 0::3] + 2

    periodic_boundary_elems_idx = np.zeros((2, 2 * n_rods), dtype = np.int64)
    periodic_boundary_elems_idx[0, 0::2][1:] = 2
    periodic_boundary_elems_idx[0, 1::2] = 1 + n_elem
    periodic_boundary_elems_idx[0,:] = np.cumsum(periodic_boundary_elems_idx[0,:])
    periodic_boundary_elems_idx[0,:] += np.repeat(np.arange(0, n_rods, dtype = np.int64), 2)

    periodic_boundary_elems_idx[1, 0::2] = periodic_boundary_elems_idx[0, 1::2] - 1
    periodic_boundary_elems_idx[1, 1::2] = periodic_boundary_elems_idx[0, 0::2] + 1

    periodic_boundary_voronoi_idx = np.zeros((2, n_rods), dtype = np.int64) 
    periodic_boundary_voronoi_idx[0, 0::1][1:] = 3
    periodic_boundary_voronoi_idx[0, 1:] += n_elem[:-1]
    periodic_boundary_voronoi_idx[0,:] = np.cumsum(periodic_boundary_voronoi_idx[0,:])

    periodic_boundary_voronoi_idx[0, :] += np.repeat(
        np.arange(0, n_rods, dtype = np.int64), 1
    )
    periodic_boundary_voronoi_idx[1, :] = periodic_boundary_voronoi_idx[0, :] + n_elem[:]

    n_elem += 2
    return(
        n_elem,
        periodic_boundary_node_idx,
        periodic_boundary_elems_idx,
        periodic_boundary_voronoi_idx
    )

class MemoryBlockRodBase:
    def __init__(self):
        pass

# if __name__ == "__main__":

#     n_elems_in_rods = np.array([3,4,5,6])
#     make_block_memory_periodic_doundary_metadata(n_elems_in_rods)


