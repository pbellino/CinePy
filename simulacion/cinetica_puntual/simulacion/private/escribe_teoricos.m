function escribe_teoricos(name)

teo = teoricos;

fid = fopen(name, 'w+');

for [val, key] = teo
    fprintf(fid, '%s: %f \n', key, val);
endfor

