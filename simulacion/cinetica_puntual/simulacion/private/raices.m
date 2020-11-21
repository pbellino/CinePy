function [ap , ad]=raices(lam_d,Lambda,rho,beta)

alfa = (beta-rho)/Lambda;

ap = 0.5*(alfa+lam_d) + 0.5*sqrt((alfa+lam_d)^2 + 4*rho*lam_d/Lambda);
ad = 0.5*(alfa+lam_d) - 0.5*sqrt((alfa+lam_d)^2 + 4*rho*lam_d/Lambda);