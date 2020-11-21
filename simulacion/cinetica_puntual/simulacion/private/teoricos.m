function teo = teoricos

run('param_in.m')

% Tiempo entre reproducciones
teo.Lambda = 1/(V0*nu*Sig_f);
% Vida media
teo.lambda = 1/(V0*(Sig_c+Sig_f+Sig_d1));
% k efectivo
teo.keff   = nu*Sig_f/(Sig_f+Sig_c+Sig_d1);
% Reactividad
teo.rho    = (teo.keff-1)/teo.keff;
% Alfa de los instant�neos
teo.alfa_p = (teo.rho-bet)/teo.Lambda;
% Alfa de los retardados
teo.alfa_d = -lam_d*teo.rho/(teo.rho-bet);
% Eficiencia del detector
teo.efi = Sig_d1/Sig_f;

% Soluci�n m�s exacta para los alfa
[teo.ap , teo.ad]  = raices(lam_d,teo.Lambda,teo.rho,bet);

% Si utilizo una fuente poissoniana, calculo valores estacionarios te�ricos
if strcmp(tpo_fte,'poisson')
    teo.N  = -teo.Lambda*Q/teo.rho;              % Densidad neutr�nica
    teo.Ra = teo.N*V0.*(Sig_c+Sig_f+Sig_d1);     % Tasa de absorciones
    teo.Rd = teo.N*V0.*Sig_d1;                   % Tasa de detecciones
    teo.Rf = teo.N*V0*Sig_f;                     % Tasa de fisiones
else
    teo.N  = nan;
    teo.Ra = nan;
    teo.Rd = nan;
    teo.Rf = nan;
end

end