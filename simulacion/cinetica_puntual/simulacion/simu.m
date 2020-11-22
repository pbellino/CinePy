function simu


%% -------------  Entrada de datos ----------------------------------------
run('param_in')

if nu_d > 1
    % Por la forma en que pongo los tiempos de los neutrones retardados
    % la cantidad de neutrones retardados no debe superar a la cantidad
    % de fisiones que se producen.
    beta_lim =1/(nu_p+1);
    error('Reducir el beta para que nu_d<1\n Esto se cumple si beta< %.4f',beta_lim);
end
% --------------- Fin entrada de datos ------------------------------------

%% Inicializo las variables que voy a utilizar

E_vjo = nan(nbuf,1);
T_vjo = nan(nbuf,1);
E_nvo = E_vjo;
T_nvo = T_vjo;

% Fijo semmilla de números pseudoaleatorios  para reproducir resultados
SEED = 1;
rand ("state", SEED);

%% ------------------ FUENTE DE NEUTRONES ---------------------------------
% Defino y cargo los valores de la fuente de neutrones

% Si es una fuente poissoniana, puedo predecir hasta dónde estaré simuladno
% Lo hago para evitar muestrear un tiemop muy grande, lo que me tardaría
% mucho tiempo en procesar con los métodos de ruido.

% if strcmp(tpo_fte,'poisson')
%     disp(['Tiempo final (promedio) = ' num2str(nf/Q)]);
%     a = input('¿Sigue la ejecución? s/n [s]','s');
%     if a=='n', return; end
% end

% Cargo los valores de la fuente
[T_fte, E_fte] = fuente(tpo_fte,nf,E0,Q);
% Guardo los valores en los vectores principales
T_vjo(1:nf,:) = T_fte;
E_vjo(1:nf,:) = E_fte;

% ------------------- FIN FUENTE DE NEUTRONES -----------------------------
%% Inicializo contadores
nc  = 0;		% Número de capturas
nfi = 0;		% Número de fisiones
nd1 = 0;		% Número de detecciones en d1

ite = 200;		% Vector para ir guardando los contadores (asumo un máximo de 200)
ntot  = nan(ite,1);	% Cantidad total de neutrones
aite  = nan(ite,1);	% Cantidad de absorciones
fite  = nan(ite,1);	% Cantidad de fisiones
d1ite = nan(ite,1);	% Cantidad de detecciones

% Para guardar los tiempos, construyo vectores más grandes porque no sé cuán largos van a ser
nf2 = nf*8;		% Número tentativo
% Tiempos en donde se produce cada interacción
Ta  = nan(nf2,1);	% Absorción
Tf  = nan(nf2,1);	% Fisión
Td1 = nan(nf2,1);	% Detección
% Tiempos entre que nace el neutrón y realiza alguna reacción
DTfa  = nan(nf2,1);	% Absorción
DTff  = nan(nf2,1);	% Fisión
DTfd1 = nan(nf2,1);	% Detección

%%----------------- COMIENZO DE LA SIMULACIÓN -----------------------------
j = 1;
while ~all(isnan(E_vjo))

    nonan   = ~isnan(E_vjo);    % Lugares donde hay partículas
    ntot(j) = sum(nonan);       % Cantidad de partículas
    
    %% ----- Sorteo la distancia de interacción de la partícula -----------
    % Calculo distancia recorrida y acualizo el tiempo global
    S = -log(rand(ntot(j),1))./Sig_t;     % Tramo actual del recorrido
    T_nvo(nonan) = T_vjo(nonan) + S./V0;  % Tiempo de cada partícula 
    % ---------------------------------------------------------------------
    
    %% -----------------Sorteo el tipo de interacción----------------------
    % Se fija qué tipo de interaccción se producirá
    rul  = rand(nbuf,1);
    % Descarto
    rul(isnan(E_vjo)) = nan; % Elimino los lugares donde no había partículas
    % Asigno interacción a cada partícula
    indc  = find(     rul <= cum_s(1));            % Absorción
    indf  = find(cum_s(1) < rul & rul<=cum_s(2));  % Fisión
    indd1 = find(cum_s(2) < rul & rul<=cum_s(3));  % Detección en el det 1
    % ---------------------------------------------------------------------
    
    %% --------------------- ABSORCIONES ----------------------------------
    % Las absorciones serán las capturas + detecciones + fisiones
    % --- 1) CAPTURAS
    nc = nc + length(indc); % Cuento la cantidad de absorciones    
    %
    % No me interesa el tiempo de las capturas. Se guarda el de las
    % absorciones que tienen en cuenta capturas + detecciones + fisiones.
    % Esto tiene más sentido si se le agrega sctattering o escapes.
    vec_abs = [indc ; indf ; indd1];   % Junto a los tres procesos
    n_abs   = length(vec_abs);         % Cantidad de absorciones
    % Registro el tiempo de cada absorción y el Dt
    if ~isempty([indc;indf])
         Ta(find(isnan(Ta),n_abs),1) = T_nvo(vec_abs,1);
         DTfa(find(isnan(DTfa),n_abs),1) = (T_nvo(vec_abs,1)- T_vjo(vec_abs,1))./(prob_c+prob_f+prob_d1);
    end
    % Destruye las partículas capturadas
    E_nvo(indc,1) = nan;
    T_nvo(indc,1) = nan;  
    
    % --- 2) DETECCIONES
    nd1 = nd1+ length(indd1);  % Cantidad de detecciones
    if ~isempty(indd1)
         Td1(find(isnan(Td1),length(indd1)),1) = T_nvo(indd1,1);
         DTfd1(find(isnan(DTfd1),length(indd1)),1) = (T_nvo(indd1,1)- T_vjo(indd1,1))./prob_d1;
    end
    % Destruye las partículas detectadas
    E_nvo(indd1,1) = nan;
    T_nvo(indd1,1) = nan;
    % ----------------------- FIIN ABSORCIONES-----------------------------
    
    %% ----------------------- FISIONES -----------------------------------
    %
    nfi = nfi + length(indf);        % Cantidad de fisiones    
    %
    % NEUTRONES INSTANTÁNEOS
    %          
    % Sorteo la cantidad de neutrones instantáneos producidos por fisión
    rul = rand(length(indf),1);
    % Asigno la cantidad producida en cada fisión
    nprod = nan(length(indf),1);  % Neutr. inst. producidos por fisión
    nprod(                 rul <= cum_p(1)) = 0 ;
    nprod(cum_p(1) < rul & rul <= cum_p(2)) = 1; 
    nprod(cum_p(2) < rul & rul <= cum_p(3)) = 2; 
    nprod(cum_p(3) < rul & rul <= cum_p(4)) = 3; 
    nprod(cum_p(4) < rul & rul <= cum_p(5)) = 4; 
    nprod(cum_p(5) < rul & rul <= cum_p(6)) = 5; 
    nprod(cum_p(6) < rul & rul <= cum_p(7)) = 6;
    nprod(cum_p(7) < rul & rul <= cum_p(8)) = 7;
    nuev  = sum(nprod);   % Total de neutrones instantáneos producidos
    
    % Ubico los nuevos neutrones instantáneos producidos y les asigno el
    % tiempo y la energía correspondiente
    % Busco qué fisiones produjeron al menos uno, al menos dos, etc.
    % neutrones instantáneos
    indmp1 = find(nprod >= 1); mp(1)=length(indmp1);
    indmp2 = find(nprod >= 2); mp(2)=length(indmp2);
    indmp3 = find(nprod >= 3); mp(3)=length(indmp3);
    indmp4 = find(nprod >= 4); mp(4)=length(indmp4);
    indmp5 = find(nprod >= 5); mp(5)=length(indmp5);
    indmp6 = find(nprod >= 6); mp(6)=length(indmp6);
    indmp7 = find(nprod >= 7); mp(7)=length(indmp7);
    acmp = cumsum(mp);
    
    % Ubico las nuevas partículas en los lugares donde había nan's
    if nuev~=0  % Si hay nuevas partículas
        % Busco lugares con NaN para poner las nuevas partículas
        lib = find(isnan(E_vjo),nuev,'first');
        if nuev <= length(lib)    % Si me alcanza el buffer
            % Asigno los tiempos acuales a las nuevas partículas
            T_nvo(lib(1:acmp(1)),:)         = T_nvo(indf(indmp1),:);
            T_nvo(lib(acmp(1)+1:acmp(2)),:) = T_nvo(indf(indmp2),:);
            T_nvo(lib(acmp(2)+1:acmp(3)),:) = T_nvo(indf(indmp3),:);
            T_nvo(lib(acmp(3)+1:acmp(4)),:) = T_nvo(indf(indmp4),:);
            T_nvo(lib(acmp(4)+1:acmp(5)),:) = T_nvo(indf(indmp5),:);
            T_nvo(lib(acmp(5)+1:acmp(6)),:) = T_nvo(indf(indmp6),:);
            T_nvo(lib(acmp(6)+1:end),:)     = T_nvo(indf(indmp7),:);
            % Las creo con la misma energía
            E_nvo(lib,:) = E0.*ones(nuev,1);
        else
            disp('No se pueden ubicar a las nuevas partículas (instantáneas) creadas');
            error('Aumentar el tamaño del buffer');
        end
    end
    % 
    % NEUTRONES INSTANTÁNEOS
    % 
    % Toda esta sección es válida sólo si (nu_d=<1). Lo hice así porque es
    % más sencillo ubicar a los neutrones producidos. Se debe cambiar en
    % caso de querer generalizarlo.
    % Voy a asumir que por cada fisión se puede producir A LO SUMO un
    % neutrón retardado (por eso nu_d=<1).
    %
    % - Sorteo qué fisiones producirán un neutrón retardado
    rul    = rand(length(indf),1);  
    indf_d = indf(rul<=nu_d);   % Índices de fisiones que pruducen n. ret.
    nuev_d = length(indf_d);    % Neutrones retardados producidos
    
    % Ubico las nuevas neutrones retardados en los lugares donde había nan's
    if nuev_d~=0  % Si hay neutrones retardados
        % Busco lugares con NaN para poner las nuevas partículas
        lib_d = find(isnan(E_vjo),nuev+nuev_d,'first');
        lib_d(1:nuev)=[];   % Elimino los lugares que ocupé con los inst. (MEJORAR)
        if nuev_d<=length(lib_d)    % Si me alcanza el buffer para las creadas
            % El tiempo de emisión de la partícula distribuido exponencialmente
            T_nvo(lib_d,1) = T_nvo(indf_d,1) + (-1/lam_d).*log(rand(nuev_d,1));
            % Con energía fija
            E_nvo(lib_d,:) = E0.*ones(nuev_d,1);
        else
            disp('No se pueden ubicar a las nuevas partículas (retardadas) creadas');
            error('Aumentar el tamaño del buffer');
        end
    end
  

    % Guarda el tiempo en que se produjeron las fisiones
    if ~isempty(indf)
        Tf(find(isnan(Tf),length(indf)),1)  = T_nvo(indf,1);%./pf;
        DTff(find(isnan(Tf),length(indf)),1) = (T_nvo(indf,1)-T_vjo(indf,1))./prob_f;
    end
    % Destruye las partículas que fisionaron
    T_nvo(indf,:) = nan;
    E_nvo(indf,1) = nan;
    
    % ----------------------- FIN FISIONES --------------------------------
    
    %% Actualizo las energías y los tiempos de todas las partículas
    E_vjo = E_nvo;
    T_vjo = T_nvo;
       
    %% Información sobre los tipos de reacciones que se producen
    % fprintf('\tEn la iteracion ACTUAL\n');
    % fprintf('Capturas: %i\n',length(indc));
    % fprintf('Fisiones: %i\n',length(indf));
    % fprintf('Detecciones: %i\n',length(indd1));
    % fprintf('Generados-> Inst: %i \t Ret: %i \t Tot: %i \n',nuev,nuev_d,nuev+nuev_d);
    % fprintf('\tEn TOTAL\n');
    % fprintf('Absorciones: %i\n',nc);
    % fprintf('Fisiones: %i\n',nfi);
    % fprintf('Detecciones: %i\n',nd1);
    
    % Guarda información sobre las partículas en cada iteración
    aite(j)  = length(indc);
    fite(j)  = length(indf);
    d1ite(j) = length(indd1);
    j = j+1;
end

clear S E_nvo E_vjo T_nvo T_vjo indf indf_d indmp1 indmp2 indmp3 indmp4 indmp5
clear indmp6 indmp7 indp0 indp1 indp2 indp3 indp4 indp5 indp6 indp7 acmp indd1 indc
clear mp nonan vec_abs p_Sig p_prod lib lib_d cum_p cum_s

%--------- Saco los nan de todos los tiempos
DTff(isnan(DTff))   = [];
DTfa(isnan(DTfa))   = [];
DTfd1(isnan(DTfd1)) = [];
Tf(isnan(Tf))       = [];
Ta(isnan(Ta))       = [];
Td1(isnan(Td1))     = [];

% -------------------- FIN DE LA SIMULACIÓN -------------------------------

%% Verificación de la simulación
% Toda esta parte consiste en verificar los resultados que obtuve con la
% simulación. Es válido para un grupo de energía y para un reactor
% homogeneo


% Calculo alguno de los parámetros cinéticos más relevantes, tomando
% valores medios de los tiempos característicos simulados
Lambda  = mean(DTff)./nu;       % Tiempo entre reproducciones
lambda  = mean(DTfa);           % Vida media
keff    = lambda/Lambda;        % k efectivo
rho     = (keff-1)/keff;        % Reactividad
alfa    = (rho-bet)/Lambda;     % Alfa de los instantáneos
alfa_d  = -lam_d*rho/(rho-bet); % Alfa de los retardados
% Valores teóricos (válidos para un grupo de energías y reactor homogeneo)
teo = teoricos;

%% Grafico y calculo algunos resultados

%---- Absorciones

[Ra_t , tRa] = grafico_tasas(Ta);
ylabel('Tasa de absorciones');

Ra = grafico_teorico(Ra_t,tRa,teo.Ra,tpo_fte,nc+nd1+nfi,teo);

%---- Detecciones

[Rd_t , tRd] = grafico_tasas(Td1);
ylabel('Tasa de detecciones');

Rd = grafico_teorico(Rd_t,tRd,teo.Rd,tpo_fte,nd1,teo);

%---- Fisiones

[Rf_t, tRf] = grafico_tasas(Tf);

Rf = grafico_teorico(Rf_t,tRf,teo.Rf,tpo_fte,nfi,teo);
ylabel('Tasa de fisiones');

efi = Rd/Rf; % Eficiencia absoluta del detector

%% Muestro en pantalla algunas comparaciones
% Es relevante en el caso de estar con una fuente poissoniana (estacionaria)
% Se lo contrario los valores no van a ser estacionarios.

fprintf('Vida media (lambda)    --> Simulado: %.4f   Teorico: %.4f\n',lambda,teo.lambda);
fprintf('Reproduciones (Lambda) --> Simulado: %.4f   Teorico: %.4f\n',Lambda,teo.Lambda);
fprintf('k efectivo (keff)      --> Simulado: %.4f   Teorico: %.4f\n',keff,teo.keff);
fprintf('Reactividad (rho)      --> Simulado: %.4f  Teorico: %.4f\n',rho,teo.rho);
fprintf('Eficiencia detector    --> Simulado: %.4f   Teorico: %.4f\n',efi,teo.efi);
fprintf('Tasa de fisiones       --> Simulado: %.4f   Teorico: %.4f\n',Rf,teo.Rf); 
fprintf('Tasa de detecciones    --> Simulado: %.4f   Teorico: %.4f\n',Rd,teo.Rd); 
fprintf('Tasa de absorciones    --> Simulado: %.4f   Teorico: %.4f\n',Ra,teo.Ra);  
fprintf('Cocientes\t T.fis: %.4f \t T.Det: %.4f \t T.Abs: %.4f \n',teo.Rf/Rf,teo.Rd/Rd,teo.Ra/Ra);
fprintf('beta                   --> Teorico: %.4f\n',bet);  

fprintf('Alfa ret   --> Simulado: %.4f   Teorico: %.4f   Teorico_exacto: %.4f\n', alfa_d,teo.alfa_d, teo.ad);  
fprintf('Alfa inst  --> Simulado: %.4f   Teorico: %.4f   Teorico exacto: %.4f\n', alfa, teo.alfa_p, teo.ap);  

%% Aplico los distintos métodos de ruido neutrónico
% Sólo utilizo la variable local Td1. Tal vez alguna otra, pero sin
% importancia.

%%--- Para a-Rossi
% Nro = sort(Td1);
% Nro = Nro(1:end-10);
% arossi

%%--- Para a-feynman
% p=1;
% [N t] = sintetizar(sort(Td1),p);
% figure;
% plot(t,N);
% N=N(1:end-3000);
% figure;
% afeynman

%% Guardo todas las variables para controlar el código. En verdad sólo
% necesito guardar la variable temporal del detector (Td1)
% save variables
Td1 = sort(Td1);
save -z times.D1.gz Td1       % Si quiero guardar sólo Td1 (gzip)
% save -ascii times.D1.dat Td1  % Si quiero guardar sólo Td1 (ascii)

