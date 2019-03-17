function [yp p sep cic cio R sd cov mse] = regnolin(x,y,modelo,p0)

% REGNOLIN hace un ajuste no lineal utilizando el algoritmo de
% Levenberg-Marquardt (funciones nlinfit de MATLAB). 
%       [yp p sdp ci R sd] = regnolin(x,y,@modelo,p0)
% ENTRADAS:
%       x es la variable independiente
%       y es la variable dependiente
%       modelo es la función que se utilizará como modelo 
%            Debe crearse un archivo que la contenga (modelo.m) cuya 
%            estructura será:
%                          yhat = modelo(beta,X)
%            donde beta son los coeficientes y X la variable independiente
%       p0 son los parámetros iniciales del ajuste
% SALIDAS:
%       yp es la curva obtenida en el ajuste
%       p son los parámetros obtenidos
%       sep son los errores estandar de los parámetros
%       cic es el intervalo de confianza (95%) de la curva
%       cio es el intervalo de confianza (95%) de cada medición
%       R es el coeficiente de la regresión
%       sd es la desviación estandar del ajuste
%
%  Hay opciones que se deben cambiar directamente de la función
%  (tolerancia, iteraciones, etc). Para ello ver "statset".
%
%  Pablo Bellino 24.01.2008 
%  Versión 0.1
%--------------------------
%  Para hacer un ajuste pesado, se ingresa directamente y.*sqrt(w)
%  y se modifica la función modelo @modelo.*sqrt(w). Luego, la salida
%  queda yp./sqrt(w). Fue comprobado que de esta manera los resultados son
%  iguales a los que da el Origin 8.0, con el ajuste no lineal y utilizando
%  la función "reduced chi-squared".
%  No se pudo lograr que el R coincidiera con el del Origin cuando se hace
%  un ajuste ponderado.
%   
%  Pablo Bellino 22.03.2008
%  Version 0.2

% Comprueba que estén todas las entradas
if (nargin < 4),error('Están faltando argumentos para el ajuste');end

N  = length(x);

% Comprueba que x e y sean del mismo tamaño
if (length(y) ~= N),error('x e y deben ser del mismo tamaño');end

% Ajuste no lineal
% p: parámetros | r: residuos | j: Jacobiano
options = statset('Display','iter','MaxIter',100,'TolFun',1e-10);
[p r j cov mse] = nlinfit(x,y,modelo,p0,options);

%La versión R2008a los toma como complejos (la anterior no)
p=real(p);r=real(r);j=real(j);

% Errores de los parámetros
% Da los intervalos con 95% de confianza en los parámetros
% pci = nlparci(p,r,j);
pci = nlparci(p,r,'cov',cov); %parece que es lo adecuado, aunque da lo mismo

% Predicción de la curva y de los intervalos de confianza
% yp: es la curva predicha por el ajuste yp = func(p,x)
% ci: es el ancho mitad (delta) del intervalo de confianza
% [yp-ci,yp+ci] es el intervalo con 95% de confianza (no simultaneo)

 alfa      = 0.05; % para calcular los intervalos de confianza
%  [yp, cic] = nlpredci(modelo,x,p,r,j,alfa,'off','curve');
%  [yp, cio] = nlpredci(modelo,x,p,r,j,alfa,'off','observation');
[yp, cic] = nlpredci(modelo,x,p,r,'cov',cov,'alpha',alfa,'predopt','curve','simopt','off');
[yp, cio] = nlpredci(modelo,x,p,r,'cov',cov,'alpha',alfa,'predopt','observation','simopt','off');
 
%% Un poco de estadística------------------------
% Desviación estandar (con 2 parámetros a calcular)
% Es equivalente a la salida mse de nlinfit (sd^2 = mse)
sse = sum((y-yp).^2);
sd  = sqrt(sse/(N-length(p)));
%%-----------------------------------------------

%% Error estadístico de los parámetros
% Debe haber algo que lo haga automático, pero no sé
%  tt  = tinv(1-alfa/2,length(y)-length(p));
%  sep = (pci(:,2)-pci(:,1)) ./ (2*tt); % error estandar
 
% Da lo mismo que utilizando la matríz de covarianza (22-03-2010)
sep = sqrt(diag(cov));
 
%% R del fiteo
 corrmat = corrcoef(y,yp);
 R       = corrmat(1,2);
 
% Gráficos de las curvas
figure;
plot(x,y,'.black');
hold on;
% grafica con el intervalo de confianza de la curva
plot(x,yp,'r',x,yp-cic,'b',x,yp+cic,'b');
% grafica el intervalo de confianza de cada medición
plot(x,yp-cio,'g',x,yp+cio,'g');
hold off;

% Muestra en pantalla los resultados
for i=1:length(p),
    fprintf('\r\t p(%i): \t %7.5f +/- %7.5f [%7.5f %7.5f] \r',i,p(i),sep(i),pci(i,1),pci(i,2))
end
fprintf('\r\t Desviación estandar: %7.5f \r',sd)
fprintf('\t Valor R del ajuste:  %7.5f \r', R)


