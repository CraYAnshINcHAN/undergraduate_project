% 磁铁中心位置p_m、磁矩M_m.
% 导丝尖部位置p_t=[x_t;y_t;z_t]
% 导丝初始方向o_t，磁矩大小M_t，m先绕y轴旋转theta_t，再绕X轴转角phi_t。对应旋转矩阵R_t
% _v表示向量
% 真空磁导率mu_0
%磁场强度B=B(x_t,y_t,z_t)
syms theta_t phi_t x_t y_t z_t
mu_0 = 4*pi*10^(-7);

p_m = [1;1;1];
M_m = [1;1;1];

p_t = [x_t;y_t;z_t];
M_t = 1;
o_t = [0;0;1];
R_t_y = [cos(theta_t),0,sin(theta_t);0,1,0;-sin(theta_t),0,cos(theta_t)];       
R_t_x = [1,0,0;0,cos(phi_t),-sin(phi_t);0,sin(phi_t),cos(phi_t)];
R_t = R_t_x*R_t_y;
M_t_v = R_t*o_t*M_t;

I = eye(3);

p = p_t - p_m;
B_m = mu_0./(4*pi*(transpose(p)*p.^1.5)*((3*p*transpose(p)./(transpose(p)*p))-I))*M_m;

x_t = 2;
y_t= 2;
z_t = 2;

B_m = subs(B_m);

T = cross(M_t_v,B_m);






