 function r = is_octave ()
%%  subfunction that checks if we are in octave
%  Usada para corregir incompatibilidades entre octave y matlab
  persistent x;
   if (isempty (x))
     x = exist ('OCTAVE_VERSION', 'builtin');
   end
   r = x;
 end
