%较为困难的部分：微分方程的建立
syms alpha(s) beta(s) gamma(s) Px(s) Py(s) Pz(s) Fx(s) Fy(s) Fz(s) Tx(s) Ty(s) Tz(s)

Rx = [1 0 0; 0 cos(alpha) -sin(alpha); 0 sin(alpha) cos(alpha)];
Ry = [cos(beta) 0 sin(beta); 0 1 0; -sin(beta) 0 cos(beta)];
Rz = [cos(gamma) -sin(gamma) 0; sin(gamma) cos(gamma) 0; 0 0 1];
R = Rx*Ry*Rz;
P = [Px; Py; Pz];
F = [Fx; Fy; Fz];
u0 = eye(3);
v = [0; 0; 1];

Es = 160 * 10^9;%Elasitic Modulus of Silicon Tube
Gs = 66 * 10^9;
ds_out = 1 * 10^(-3);
ds_in = 0.5 * 10^(-3);
Isx = pi() * Es / 64 * (ds_out^4 - ds_in^4);
Isy = Isx;
Isz = 2*Isx;

%先忽略内部注入的东西
%Ep = 15.3 * 10^6;%Elastic Modulus of PDMS
%Gp

Kbt = diag([Es*Isx; Es*Isy; Gs*Isz]);
Kse = zeros(3);

function ode = myODE(s,y)
    Rx = [1 0 0; 0 cos(y(1)) -sin(y(1)); 0 sin(y(1)) cos(y(1))];
end


%较为简单的部分：磁场的建立