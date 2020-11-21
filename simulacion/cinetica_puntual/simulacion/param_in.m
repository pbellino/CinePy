
nf      = 1e6;          % N�mero de particulas de fuente
nbuf    = nf*2;            % Buffer para alojar nuevas part�culas

%-------- Definici�n de la fuente -----------------------------------------
E0      = 1;               % Energ�a inicial de la fuente
m       = 1;               % Masa de la part�cula
V0      = sqrt(2.*E0./m);  % Velocidad inicial
Q       = 1; % Valor de la fuente de neutrones (si se usa una poissoniana)
tpo_fte = 'poisson';
%  tpo_fte = 'pulsada';

%-------- Par�metros f�sicos del medio ------------------------------------
% Sistema cr�tico con Sig_c=Sig_f=1 y nprod=2 (Asumiendo medio infinito)
Sig_c   = 0.2;                  % Secci�n efic�z macrosc�pica de captura
Sig_f   = 0.2;                  % Secci�n efic�z macrosc�pica de fisi�n
Sig_d1  = 0.4;
Sig_t   = Sig_c + Sig_f + Sig_d1;  % Secci�n efic�z macrosc�pica total
prob_c  = Sig_c/Sig_t;
prob_f  = Sig_f/Sig_t;
prob_d1 = Sig_d1/Sig_t;
p_Sig   = [prob_c prob_f prob_d1];
cum_s   = cumsum(p_Sig);

% Probabilidad de que se produzcan n part�culas en una fisi�n p(n)
% P_prod = [p(0) p(1) p(2) p(3) p(4) p(5) p(6) p(7)]
p_prod  = [0.032 0.17 0.34 0.30 0.13 0.027 0.0026 0.0002]; % Experimental
p_prod  = p_prod./sum(p_prod);      % Normalizo por las dudas
% p_prod = [0 0 1 0 0 0 0 0];      % S�lo se producen 2 part�culas por fisi�n (Yule-Furry)
cum_p   = cumsum(p_prod);
nu_p    = p_prod*(0:7)';

%-- Neutrones retardados
bet     = 0.05;   % Debe ser menor a 0.33(0.05 anda bien sec_temp)
nu_d    = bet*nu_p/(1-bet);
nu      = nu_p+nu_d;
lam_d   = 0.01;                     % Constante de decaimiento de n. ret.

