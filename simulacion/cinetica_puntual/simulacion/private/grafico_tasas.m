function [R_t, t] = grafico_tasas(T)


[C, t] = hist(T,300);
dt     = t(2)-t(1);
R_t    = C./dt;

figure
bar(t,R_t,'FaceColor',[0.0 0.0 0.6]);
xlabel('Tiempo');

end