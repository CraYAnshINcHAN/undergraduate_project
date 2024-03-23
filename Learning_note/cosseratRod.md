由于本科毕设需要用到CosseratRod模型做软磁材料的分析，因而写了这份文档作为学习笔记。  
# 前置知识
## 旋转群$SO(3)$
参考资料：https://zhuanlan.zhihu.com/p/137884920  
### $SO(3)的定义$
在三维空间$R^3$中定义一组旋转群组$SO(3)$,表示能在合成算子的作用下绕原点旋转。  
旋转群的定义：$SO(3):\{r:R^3 \rightarrow R^3 | \forall v,w \in R^3, ||r(v)||=||v||,r(v)\times r(w) = r(v\times w)\}$  
e.g. 三维旋转矩阵、四元数均是$SO(3)$  

### $旋转矩阵与SO(3)$
当旋转算子r时三维旋转矩阵$R\in R^{3\times 3}$， 很容易验证$R$满足旋转群的定义  
我们由此得到了向量在三维空间旋转的数学工具，之后进一步想要将其与向量的空间旋转及其旋转速度联系起来

已知$R^TR = I = RR^T$  
$\frac{d}{dt}(R^TR) = \dot R^TR+R^T\dot R = 0$  
$\dot R^TR = -R^T\dot R$  
我们看出$\dot R^TR是一个反对称矩阵$  
因此我们可以用一个反对称矩阵描述矩阵的旋转偏移  
$3\times 3的反对称矩阵的几何为so(3),也叫做SO(3)的李代数$为如下形式  
$[\omega]_{\times} = \begin{bmatrix} 0 & -\omega_z & \omega_y \\ \omega_z & 0 & -\omega_x \\ -\omega_y & \omega_x & 0 \end{bmatrix}$  
因此一定存在一个$\omega$,使得$R^T\dot R = [\omega]_{\times}$  
由此通过李代数将向量和旋转矩阵联系起来了，通过[·]将一个$R^3的向量转化为了so(3)$

之后我们想要再从$so(3)到SO(3)$  
$\dot R=R[w]_{\times}$两边求积分，有$R = e^{|v|_{\times}}$(这里看到资料中没有详细说明v和w的关系，不确定对不对，所以又去看了一篇更为仔细的李群李代数文章)  
从一维常微分来说$R = e^{[w]_{\times}t}$
## 李群李代数进一步讲解
### 群(group)
群：一种集合加上一种运算的代数结构。集合记为：A，运算记为·，群记为$G=(A,·)$  
满足以下条件：  
1.封闭性：$\forall a_1,a_2\in A,a_1·a_2\in A$  
2.结合律：$\forall a_1,a_2,a_3 \in A, (a_1·a_2)·a_3 = a_1·(a_2·a_3)$  
3.幺元：$\exist a_0 \in A, s.t. \forall a\in A,a_0·a = a·a_0$
4.逆：$\forall a\in A, \exist a^{-1}\in A, s.t. a·a^{-1}=a_0$

### 李群
定义：李群就是具有连续（光滑）性质的群。  
e.g. 整数的加法不是连续的，不是李群，而SO(3)是连续的，是李群。





