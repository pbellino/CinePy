function [T , E] = fuente(tipo,nf,Ei,Q)

% FUENTE Define a la fuente de neutrones que ser� utilizada
%           [T , E] = fuente(tipo,nf,Ei,Q)
%  ENTRADAS:
%      Q : Valor de la fuente de neutrones
%     nf : Cantidad de neutrones emitidos por la fuente
%   tipo : Tipo de fuente. Puede ser:
%            'poisson' -> emisi�n con una distribuci�n de poisson
%            'pulsada' -> todos las emisiones se hacen a t=0
%     Ei : Energ�a inicial de las part�culas (por ahora no se utiliza)
%  SALIDAS:
%      T : Tiempo en el que sale cada neutr�n
%      E : Energ�a con la que sale cada neutr�n

if (nargin > 4)||(nargin<3)
    error('N�mero de par�metros de entrada incorrecto. No hace falta definir el Q de la fuente');
end

switch tipo
    case 'pulsada'
        if nargin==4, warning('El �ltimo par�metro sobra, ser� descartado'); end
        
        % Todas las part�cuals nacen a t=0
        T(1:nf,1) = zeros(nf,1);
    case 'poisson'
        if nargin==3; error('Falta definir el valor de la fuente'); end
        % Muestreo una distribucion exponencial para definir el tiempos
        % entre does emisiones.
        % Despu�s hago una suma acumulada para obtener los tiempos en los
        % que salen cada uno de los neutrones.
        T(1:nf,1) = cumsum(-(1/Q).*log(rand(nf,1)));
    otherwise
        error('Tipo de fuente incorrecto')
end

% Defino la energ�a de cada part�cula
E(1:nf,1) = Ei.*ones(nf,1);           % A un grupo, es irrelevante

end

