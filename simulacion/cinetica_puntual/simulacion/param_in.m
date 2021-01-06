
nf      = 2e6;             % Número de particulas de fuente
nbuf    = nf*2;            % Buffer para alojar nuevas partículas
nf2     = nf*50;           % Buffer para alojar tiempos
nf3     = nf*5;            % Buffer para alojar tiempos de detección

efi     = 4e-2             % Eficiencia del detector (R/F)
%-------- Definición de la fuente -----------------------------------------
E0      = 1;               % Energía inicial de la fuente
m       = 1;               % Masa de la partícula
V0      = sqrt(2.*E0./m);  % Velocidad inicial
V0      = 220000;
Q       = 1.0e+3; % Valor de la fuente de neutrones (si se usa una poissoniana)
tpo_fte = 'poisson';
%  tpo_fte = 'pulsada';

%-------- Parámetros físicos del medio ------------------------------------
% Sistema crítico con Sig_c=Sig_f=1 y nprod=2 (Asumiendo medio infinito)
Sig_f   = 0.01866953306808798;             % Sección eficáz macroscópica de fisión
Sig_t   = 0.04704545454545454;             % 5 dolares
Sig_d1  = Sig_f * efi;
Sig_c   = Sig_t - Sig_f - Sig_d1;          % Sección eficáz macroscópica de captura
prob_c  = Sig_c/Sig_t;
prob_f  = Sig_f/Sig_t;
prob_d1 = Sig_d1/Sig_t;
p_Sig   = [prob_c prob_f prob_d1];
cum_s   = cumsum(p_Sig);

% Probabilidad de que se produzcan n partículas en una fisión p(n)
% P_prod = [p(0) p(1) p(2) p(3) p(4) p(5) p(6) p(7)]
p_prod  = [0.032 0.17 0.34 0.30 0.13 0.027 0.0026 0.0002]; % Experimental
nu_prod = [0 1 2 3 4 5 6 7];
p_prod  = p_prod./sum(p_prod);      % Normalizo por las dudas
% p_prod = [0 0 1 0 0 0 0 0];      % Sólo se producen 2 partículas por fisión (Yule-Furry)
cum_p   = cumsum(p_prod);
nu_p    = p_prod*nu_prod';
% Diven factor (prompt)
D_p     = p_prod*(nu_prod.*(nu_prod-1))' / nu_p**2;

%-- Neutrones retardados
bet     = 700e-5;                   % Debe ser menor a 0.33(0.05 anda bien sec_temp)
nu_d    = bet*nu_p/(1-bet);
nu      = nu_p+nu_d;
lam_d   = 0.01;                    % Constante de decaimiento de n. ret.

