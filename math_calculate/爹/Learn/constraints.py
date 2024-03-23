from boundary_conditions import ConstraintBase
class Constraints():
    #初始化，把几个函数塞到列表里面，然后又新建了一个列表
    def __init__(self):
        self._constraints = []
        super(Constraints, self).__init__()
        self._feature_group_constrain_values.append(self._constrain_values)
        self._feature_group_constrain_rates.append(self._constrain_rates)
        self._feature_group_finalize.append(self._finalize_constraints)

    #constrain函数，输入的是一个系统，类似consserate_rod，会得到输入系统在系统列表中的编号
    #然后新建一个_Constraint对象，将编号传给它的初始化方法，将这个对象保存到_constraints列表中，然后返回这个对象
    def constrain(self, system):
        sys_idx = self._get_sys_idx_if_valid(system)
        #create _Constraint object, cache it and return it

        #_constraint是一个_Constraint对象，_Constraint对象会保存系统的编号
        _constraint = _Constraint(sys_idx)
        #将_Constraint对象保存到_constraints列表中
        self._constraints.append(_constraint)
        return _constraint
    

    #这里的finalize_constraints函数
    #让_constraints列表中的每一个元素都调用一次id方法，然后调用一次__call__方法，将结果保存在_constraints列表中，替换原来的元素
    #然后对_constraints列表进行排序
    #然后调用_constrain_values和_constrain_rates函数，时间参数为0
    def _finalize_constraints(self):
        self._constraints[:] = [
            (constraint.id(), constraint(self._systems[constraint.id()]))
            for constraint in self._constraints
        ]

        self._constraints.sort(key = lambda x: x[0])
        
        self._constrain_values(time = 0.0)
        self._constrain_rates(time = 0.0)


    #这里的_constrain_values函数，其实就是调用_constraints列表中每一个元素的constraint_values方法
    #如果你问，_constraints列表中不是_Constraint对象吗？为什么可以调用constraint_values方法？他没有定义这个方法啊
    #这里的_constraint列表中的元素是一个元组，元组的第二个元素是__call__函数返回的
    #类似“OneEndFixedBC”之类的边界条件，是ConstraintBase的子类，而ConstraintBase是一个抽象类
    #并且有_constrain_values以及_constrain_rates的方法，所以可以调用constraint_values方法
    def _constrain_values(self, time, *args, **kwargs):
        for sys_id, constraint in self._constraints:
            constraint.constrain_values(self._systems[sys_id], time, *args, **kwargs)
    def _constrain_rates(self, time, *args, **kwargs):
        for sys_id, constraint in self._constraints:
            constraint.constrain_rates(self._systems[sys_id], time, *args, **kwargs)

class _Constraint:
    #初始化，将输入的系统的编号保存起来
    def __init__(self, sys_idx: int):
        self._sys_idx = sys_idx
        self._bc_cls = None
        self._args = ()
        self._kwargs = {}
    
    #这里的using函数，就是把输入的边界条件类和参数保存起来，然后返回自己
    def using(self, bc_cls, *args, **kwargs):
        assert issubclass(
            bc_cls, ConstraintBase
        ),"{} is not a valid constraint. Constraint must be drvien from ConstraintBase.".format(
            bc_cls
        )
        self._bc_cls = bc_cls
        self._args = args
        self._kwargs = kwargs
        return self
    
    def id(self):
        return self._sys_idx
    
    #这里的__call__函数，接受的输入是一个类似cosseratrod之类的系统
    #然后调用_bc_cls的初始化方法，将输入的系统的位置和方向传给它的初始化方法，将参数保存起来，这些参数是通过using函数传进来的
    #然后返回这个对象,是一个类似OneEndFixedBC之类的边界条件
    def __call__(self, rod, *args, **kwargs):
        #constructs a constraint after checks
        if not self._bc_cls:
            raise RuntimeError(
                "No boundary condition provided to contrain rod"
            )
        pos_indices = self._kwargs.get(
            "constrained_position_idx", None
        )
        print("constraints_81")
        print(self._kwargs)

        director_indices = self._kwargs.get(
            "constrained_director_idx", None
        )
        #If pos_indices is not None, construct list else empty list
        positions =(
            [rod.position_collection[..., idx].copy() for idx in pos_indices]
            if pos_indices
            else []
        )
        #If director_indices is not None, construct list else empty list
        directors = (
            [rod.director_collection[..., idx].copy() for idx in director_indices]
            if director_indices
            else []
        )

        try:
            print("constraints.py_101")
            print(positions)
            print(directors)
            print(self._args)
            print(self._kwargs)
            print(rod)
            print("这里应该还有 bug,因为 directors 和示例代码不同")
            bc = self._bc_cls(
                *positions, *directors, *self._args, _system=rod, **self._kwargs
            )
            return bc
        except(TypeError, ValueError):
            raise TypeError(
                "Unable to construct boundary condition with given arguments"
            )