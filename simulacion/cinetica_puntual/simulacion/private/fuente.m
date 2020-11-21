function [T , E] = fuente(tipo,nf,Ei,Q)

% FUENTE Define a la fuente de neutrones que será utilizada
%           [T , E] = fuente(tipo,nf,Ei,Q)
%  ENTRADAS:
%      Q : Valor de la fuente de neutrones
%     nf : Cantidad de neutrones emitidos por la fuente
%   tipo : Tipo de fuente. Puede ser:
%            'poisson' -> emisión con una distribución de poisson
%            'pulsada' -> todos las emisiones se hacen a t=0
%     Ei : Energía inicial de las partículas (por ahora no se utiliza)
%  SALIDAS:
%      T : Tiempo en el que sale cada neutrón
%      E : Energía con la que sale cada neutrón

if (nargin > 4)||(nargin<3)
    error('Número de parámetros de entrada incorrecto. No hace falta definir el Q de la fuente');
end

switch tipo
    case 'pulsada'
        if nargin==4, warning('El último parámetro sobra, será descartado'); end
        
        % Todas las partícuals nacen a t=0
        T(1:nf,1) = zeros(nf,1);
    case 'poisson'
        if nargin==3; error('Falta definir el valor de la fuente'); end
        % Muestreo una distribucion exponencial para definir el tiempos
        % entre does emisiones.
        % Después hago una suma acumulada para obtener los tiempos en los
        % que salen cada uno de los neutrones.
        T(1:nf,1) = cumsum(-(1/Q).*log(rand(nf,1)));
    otherwise
        error('Tipo de fuente incorrecto')
end

% Defino la energía de cada partícula
E(1:nf,1) = Ei.*ones(nf,1);           % A un grupo, es irrelevante

end

