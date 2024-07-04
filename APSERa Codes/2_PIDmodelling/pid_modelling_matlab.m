s = tf('s');
w_n = 0.01280928128794394; 
damp_f = 0.8909081606856718; 

kp = 5;
ki = 0.5;
kd = 0.2;

P = (w_n ^ 2)/((((s^2)*kd) + (s*kp) + ki)*(s+ (2*w_n*damp_f)));

%figure
%step(P)
%hold on

kp = 5;
ki = 0.5;
kd = 0.2;
C = pid(kp,ki,kd);
T = feedback(C*P,1);

t = 0:0.01:4000;
step(T,t)

%hold off
%legend('Without Kp','With Kp')

pidTuner(P,C)
