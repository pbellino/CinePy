% Programa para calcular a-Feynman con la t�cnica de agrupamiento de
% intervalos. Lee el archivo en binario grabado por la adquisici�n en
% LabView.

%% Lectura de los datos
clear all
archivo = '../../datos/nucleo_01';

fid1 = fopen([archivo '.D1.bin'],'r','b');

for j=1:7,
    encab1{j} = fgets(fid1);
end

aa1 = fread(fid1, inf,'uint32=>uint32');

fclose(fid1);

%indek = find(aa==0);plot(indek,'*')
len = min([length(aa1)]);
aa1 = aa1(2:len);


% aa(1:fix(end/2));  % Para med05_bc4_55.bin
% aa = aa(fix(end*0.6):end);
%% Resampleo de los datos
nre = 5;        % N�mero de intervalos que voy a resamplear
if nre > 1,
    njust = fix(length(aa1)/nre);
    c1    = reshape(aa1(1:nre*njust),nre,njust);
    aa1   = sum(c1,1,'native');
    clear c1
end


%% promedio y desviaci�n estandar del contaje
prom1  = mean(aa1);
estaa1 = std(double(aa1));

%% Intervalos termporales
dt0 = 50e-6*nre;

%% T�cnica de agrupamiento
mm    = 100;               % Cantidad de historias que voy a promediar
ktot  = fix(1000/nre);     % Cantidad m�xima de intervalos que voy a agrupar (depende del dt)
int   = length(aa1)/mm;    % Cantidad de intervalos base que necesito para cada historia
int   = fix(length(aa1)/mm);    % Cantidad de intervalos base que necesito para cada histori
Ytodo1 = zeros(mm,ktot);

for pp = 1:mm,             % El loop principal corre por cada historia

    a1 = aa1(fix(int*(pp-1))+1:fix(int*pp));
    %if pp==30
    %a1(1:20)
    %error('sf')
    %end

    Y1 = zeros(1,ktot);
    for k=1:ktot,          % El loop secundario corre por cada intervalo agrupado
        
%         n = fix(length(a)/k);   % N�mero de bloques armados para cada k
%         b = zeros(1,n);
%         
%         for i=1:n,
%             b(i)=sum(a((i-1)*k+1:i*k));
%         end
        
        % Utilizando reshape funciona m�s r�pido (con pocos datos)
        rer = fix(length(a1)/k);
        b1  = sum(reshape(a1(1:rer*k),k,rer),1);
        %if (pp==70)&&(k==50),
        %  b1(1:20)
        %  co   = cov(b1,b1)
        %  mean(b1)
        %  co(1,1)/mean(b1)-1
        %  error('sfsfs')
        %end
        
     
        co   = cov(b1,b1);
        Y1(k)=co(1,1)/mean(b1)-1;
        
    end
    pp
    Ytodo1(pp,:) = Y1;   % Ytodo es una matriz que contiene a todas las historias
end
Yprom1 = mean(Ytodo1);
Yvar1  = var(Ytodo1);

%% Gr�ficos de las funciones

dt  = (1:ktot)*dt0;

plot(dt,Yprom1);


%% Ajuste de la funci�n

dt  = (1:ktot)*dt0;

global N inic;
N  = int./(1:ktot)';     % La cantidad de puntos de cada serie (se pasa como global a func)
w1 = 1./sqrt(Yvar1./mm);      % Funci�n de peso para realizar el ajuste
% w4 = 1./sqrt(Yvar4./mm);
% % % 
% % % inic = 1;               % Punto inicial del ajuste
% % % aj   = 1;               % Fracci�n de datos que ser�n ajustados (l�mite superior)
% % % 
% % % xx  = dt(inic:end*aj);
y   = [Yprom1]';
% % % yy  = y(:,inic:end*aj);
w   = [w1];
% % % ww  = w(:,inic:end*aj)';
% % % 
% % % conpeso = 1;            % 0 realiza el ajuste sin errores
% % %                         % 1 realiza el ajuste ponderado con errores
prome = [prom1];
% % % 
% % % for j=1:2
% % %     switch conpeso,
% % %         case 0
% % %             modelFun = @(p,x) func(p,x);
% % %             [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
% % %                 regnolin(xx',yy(:,j),modelFun,[0.25 200 -0.1 0.1]);
% % %             close;figure;plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
% % %         case 1
% % %             modelFunW = @(p,x) func(p,x).*ww(:,j);
% % %             yyw = yy(:,j).*ww(:,j);
% % %             [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
% % %                 regnolin(xx',yyw,modelFunW,[25 1000 -0.1 20]);
% % %             yp(:,j) = yp(:,j)./ww(:,j);
% % %             close;figure; plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
% % %     end
% % % 
% % %     doll(j)     = 1 - pd(2,j)*0.0119;
% % %     sdoll(j)    = sp(2,j)*0.0119;
% % %     tdead(j)    = - pd(3,j)*dt0/(2*prome(j));
% % %     stdead(j)   = (dt0*sp(3,j)/2/prome(j))^2; %+ (pd(3)*dt0*estaa/2/prom/prom)^2;
% % %     stdead(j)   = sqrt(stdead(j));
% % %     eff(j)      = pd(1,j)*pd(2,j)^2*(0.0119*0.00802)^2/(0.7962*1.18);
% % %     seff(j)     = sp(1,j)*(pd(2,j)^2)*(0.0119*0.00802)^2/(0.7962*1.18) + ...
% % %         pd(1,j)*2*pd(2,j)*sp(2,j)*(0.0119*0.00802)^2/(0.7962*1.18);
% % % 
% % % 
% % %     fprintf('\r\t Reactividad: (%7.3f +/- %7.3f) $ \r',doll(j),sdoll(j))
% % %     fprintf('\r\t Tieimpo muerto: (%7.3E +/- %7.3E) seg. \r',tdead(j),stdead(j))
% % %     fprintf('\r\t Eficiencia detector: (%7.5E +/- %7.5E) seg. \r',eff(j),seff(j))
% % % 
% % % end

%% Para guardar y leer los resultados finales
%  ggg=zeros(1,length(N));ggg(1:4)=prome; % si uso dos detectores con cov
% ggg=zeros(1,length(N));ggg(1:3)=prome; 
% rr = [dt' y w' ggg'  N]; 
%  save([archivo '.fey'],'rr','-ASCII');


% fff=load([archivo '.fey']);
% plot(fff(:,1),fff(:,5))
