function R = grafico_teorico(R_t,tR,teo_R,tpo_fte,nreac,teo)

if nargin <= 2
    error('Faltan datos de entrada')
end

if strcmp(tpo_fte,'pulsada')
    if nargin <= 3
        error('Faltan datos de entrada')
    end
end

switch tpo_fte
    case 'poisson'
        % % %----- Para una fuente poissoniana
        hold on
        R     = mean(R_t);
        R_teo = teo_R*ones(size(R_t));
        plot(tR,R_teo,'r','LineWidth',1.5);
        hold off
    case 'pulsada'
        %---------------------- Para un pulso
        %--- Una exponencial
        % f_teo = @(x) nd1*( ap*exp(-ap.*x) );
        %--- Dos exponenciales
        Ad = -(teo.rho/teo.Lambda + teo.ap)/(teo.ad-teo.ap);
        Ap = -(-teo.ad-teo.rho/teo.Lambda)/(teo.ad-teo.ap);
        % f_teo = @(x) nd1*(-ap*rho_teo*exp(-ap.*x) + ad*bet*exp(-ad.*x));
        f_teo = @(x) nreac*(teo.ap*Ap*exp(-teo.ap.*x) + teo.ad*Ad*exp(-teo.ad.*x));
        ve = 0:0.01:1000;
        hold on
        plot(ve,f_teo(ve),'r','LineWidth',1.5);
        hold off
        set(gca,'yscale','log');
        R = nan;
    otherwise
        error('Tipo de fuente incorrecta')
end

end