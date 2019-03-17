% Programa para calcular a-Feynman con la t�cnica de agrupamiento de
% intervalos. Lee el archivo en binario grabado por la adquisici�n en
% LabView.

%% Lectura de los datos
clear all
archivo = '../../datos/nucleo_01';

fid1 = fopen([archivo '.D1.bin'],'r','b');
fid2 = fopen([archivo '.D2.bin'],'r','b');
%fid3 = fopen([archivo '.D3.bin'],'r','b');

for j=1:7,
    encab1{j} = fgets(fid1);
    encab2{j} = fgets(fid2);
%    encab3{j} = fgets(fid3);
end

aa1 = fread(fid1, inf,'uint32=>uint32');
aa2 = fread(fid2, inf,'uint32=>uint32');
%aa3 = fread(fid3, inf,'uint32=>uint32');

fclose(fid1);
fclose(fid2);
%fclose(fid3);

%indek = find(aa==0);plot(indek,'*')
len = min(length(aa1),length(aa2));
aa1 = aa1(2:len);
aa2 = aa2(2:len);
aa4 = aa1+aa2;

% aa(1:fix(end/2));  % Para med05_bc4_55.bin
% aa = aa(fix(end*0.6):end);
%% Resampleo de los datos
nre = 5;        % N�mero de intervalos que voy a resamplear
if nre > 1,
    njust = fix(length(aa1)/nre);
    c1    = reshape(aa1(1:nre*njust),nre,njust);
    c2    = reshape(aa2(1:nre*njust),nre,njust);
    c4    = reshape(aa4(1:nre*njust),nre,njust);
    aa1   = sum(c1,1,'native');
    aa2   = sum(c2,1,'native');
    aa4   = sum(c4,1,'native');
    clear c1 c2 c4
end


%% promedio y desviaci�n estandar del contaje
prom1  = mean(aa1);
estaa1 = std(double(aa1));
prom2  = mean(aa2);
estaa2 = std(double(aa2));
prom4  = mean(aa4);
estaa4 = std(double(aa4));

%% Intervalos termporales
dt0 = 50e-6*nre;

%% T�cnica de agrupamiento
mm    = 100;               % Cantidad de historias que voy a promediar
ktot  = fix(1000/nre);     % Cantidad m�xima de intervalos que voy a agrupar (depende del dt)
int   = fix(length(aa1)/mm);    % Cantidad de intervalos base que necesito para cada historia
Ytodo1 = zeros(mm,ktot);
Ytodo2 = zeros(mm,ktot);
Ytodo3 = zeros(mm,ktot);
Ytodo4 = zeros(mm,ktot);
for pp = 1:mm,             % El loop principal corre por cada historia

    a1 = aa1(fix(int*(pp-1))+1:fix(int*pp));
    a2 = aa2(fix(int*(pp-1))+1:fix(int*pp));
    a4 = aa4(fix(int*(pp-1))+1:fix(int*pp));

    Y1 = zeros(1,ktot);
    Y2 = zeros(1,ktot);
    Y3 = zeros(1,ktot);
    Y4 = zeros(1,ktot);
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
        b2  = sum(reshape(a2(1:rer*k),k,rer),1);
        b4  = sum(reshape(a4(1:rer*k),k,rer),1);

        co   = cov([b1(:),b2(:)]);
        Y1(k)=co(1,1)/mean(b1)-1;
        Y2(k)=co(2,2)/mean(b2)-1;
        Y3(k)=co(1,2)/sqrt(mean(b1)*mean(b2));
        Y4(k)=var(b4)/mean(b4)-1;
    
    end
    pp
    Ytodo1(pp,:) = Y1;   % Ytodo es una matriz que contiene a todas las historias
    Ytodo2(pp,:) = Y2;
    Ytodo3(pp,:) = Y3;
    Ytodo4(pp,:) = Y4;  

end
Yprom1 = mean(Ytodo1);
Yprom2 = mean(Ytodo2);
Yprom3 = mean(Ytodo3);
Yprom4 = mean(Ytodo4);
Yvar1  = var(Ytodo1);
Yvar2  = var(Ytodo2);
Yvar3  = var(Ytodo3);
Yvar4  = var(Ytodo4);
error('Lo finalizo aca')
%% Ajuste de la funci�n
load RA4
Leff = RA4.Leff;
beff = RA4.beff;
Form = RA4.Form;
Div  = RA4.Div;

dt  = (1:ktot)*dt0;

global N inic;
N  = int./(1:ktot)';     % La cantidad de puntos de cada serie (se pasa como global a func)
w1 = 1./sqrt(Yvar1./mm);      % Funci�n de peso para realizar el ajuste
w2 = 1./sqrt(Yvar2./mm);
w3 = 1./sqrt(Yvar3./mm);
w4 = 1./sqrt(Yvar4./mm);

inic = 1;               % Punto inicial del ajuste
aj   = 1;               % Fracci�n de datos que ser�n ajustados (l�mite superior)

xx  = dt(inic:end*aj);
y   = [Yprom1 ; Yprom2 ; Yprom3 ; Yprom4]';
yy  = y(:,inic:end*aj);
w   = [w1 ; w2 ; w3 ; w4];
ww  = w(:,inic:end*aj)';

conpeso = 1;            % 0 realiza el ajuste sin errores
                        % 1 realiza el ajuste ponderado con errores
prome = [prom1 ; prom2 ; sqrt(prom1*prom2); prom4];     
cps   = prome./dt(1);
for j=1:4
    ccps = cps(j);
    switch conpeso,
        case 0
            modelFun = @(p,x) func(p,x,N,inic,ccps);
            p0 = [0.25 100 -0.1 -0.1];
            [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
                regnolin(xx',yy(:,j),modelFun,p0);
            close;figure;plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
        case 1
            modelFunW = @(p,x) func(p,x,N,inic,ccps).*ww(:,j);
            yyw = yy(:,j).*ww(:,j);
            p0 = [20 300 0.00001 -1];
            [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
                regnolin(xx',yyw,modelFunW,p0);
            yp(:,j) = yp(:,j)./ww(:,j);
            close;figure; plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
    end

    doll(j)     = 1 - pd(2,j)*Leff;
    sdoll(j)    = sp(2,j)*Leff;
    tdead(j)    = - pd(3,j)*dt0/(2*prome(j));
    stdead(j)   = (dt0*sp(3,j)/2/prome(j))^2; %+ (pd(3)*dt0*estaa/2/prom/prom)^2;
    stdead(j)   = sqrt(stdead(j));
    eff(j)      = pd(1,j)*pd(2,j)^2*(Leff*beff)^2/(Div*Form);
    seff(j)     = sp(1,j)*(pd(2,j)^2)*(Leff*beff)^2/(Div*Form) + ...
        pd(1,j)*2*pd(2,j)*sp(2,j)*(Leff*beff)^2/(Div*Form);

    fprintf('\r\t Reactividad: (%7.3f +/- %7.3f) $ \r',doll(j),sdoll(j))
    fprintf('\r\t Tieimpo muerto: (%7.3E +/- %7.3E) seg. \r',tdead(j),stdead(j))
    fprintf('\r\t Eficiencia detector: (%7.5E +/- %7.5E) seg. \r',eff(j),seff(j))

end
% % % % 
% % % % for j=1:4
% % % %     switch conpeso,
% % % %         case 0
% % % %             modelFun = @(p,x) func(p,x);
% % % %             p0 = [0.25 100 -0.1 -0.1];
% % % %             [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
% % % %                 regnolin(xx',yy(:,j),modelFun,p0);
% % % %             close;figure;plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
% % % %         case 1
% % % %             modelFunW = @(p,x) func(p,x).*ww(:,j);
% % % %             yyw = yy(:,j).*ww(:,j);
% % % %             p0 = [20 300 0.00001 -1];
% % % %             [yp(:,j) pd(:,j) sp(:,j) cic(:,j) cio(:,j) R sd cova mse] = ...
% % % %                 regnolin(xx',yyw,modelFunW,p0);
% % % %             yp(:,j) = yp(:,j)./ww(:,j);
% % % %             close;figure; plot(xx,yy(:,j),'k.',xx,yp(:,j),'r');
% % % %     end
% % % % 
% % % % % % %     doll(j)     = 1 - pd(2,j)*0.0119;
% % % % % % %     sdoll(j)    = sp(2,j)*0.0119;
% % % % % % %     tdead(j)    = - pd(3,j)*dt0/(2*prome(j));
% % % % % % %     stdead(j)   = (dt0*sp(3,j)/2/prome(j))^2; %+ (pd(3)*dt0*estaa/2/prom/prom)^2;
% % % % % % %     stdead(j)   = sqrt(stdead(j));
% % % % % % %     eff(j)      = pd(1,j)*pd(2,j)^2*(0.0119*0.00802)^2/(0.7962*1.18);
% % % % % % %     seff(j)     = sp(1,j)*(pd(2,j)^2)*(0.0119*0.00802)^2/(0.7962*1.18) + ...
% % % % % % %         pd(1,j)*2*pd(2,j)*sp(2,j)*(0.0119*0.00802)^2/(0.7962*1.18);
% % % % 
% % % %     doll(j)     = 1 - pd(2,j)*Leff;
% % % %     sdoll(j)    = sp(2,j)*Leff;
% % % %     tdead(j)    = - pd(3,j)*dt0/(2*prome(j));
% % % %     stdead(j)   = (dt0*sp(3,j)/2/prome(j))^2; %+ (pd(3)*dt0*estaa/2/prom/prom)^2;
% % % %     stdead(j)   = sqrt(stdead(j));
% % % %     eff(j)      = pd(1,j)*pd(2,j)^2*(Leff*beff)^2/(Div*Form);
% % % %     seff(j)     = sp(1,j)*(pd(2,j)^2)*(Leff*beff)^2/(Div*Form) + ...
% % % %         pd(1,j)*2*pd(2,j)*sp(2,j)*(Leff*beff)^2/(Div*Form);
% % % % 
% % % %     fprintf('\r\t Reactividad: (%7.3f +/- %7.3f) $ \r',doll(j),sdoll(j))
% % % %     fprintf('\r\t Tieimpo muerto: (%7.3E +/- %7.3E) seg. \r',tdead(j),stdead(j))
% % % %     fprintf('\r\t Eficiencia detector: (%7.5E +/- %7.5E) seg. \r',eff(j),seff(j))
% % % % 
% % % % end
%% Para guardar y leer los resultados finales
%  ggg=zeros(1,length(N));ggg(1:4)=prome;
%  rr = [dt' y w' ggg'  N]; 
%  save([archivo '.fey'],'rr','-ASCII');


% fff=load([archivo '.fey']);
% plot(fff(:,1),fff(:,5))
ggg      = zeros(1,length(N));
ggg(1:4) = prome; 
rr       = [dt' y w' ggg'  N]; 
nomcom   = [archivo '.' num2str(mm) 'h.fey'];
if ~exist(nomcom)
    save([archivo '.' num2str(mm) 'h.fey'],'rr','-ASCII');
else
    'El archivo ya existe'
end