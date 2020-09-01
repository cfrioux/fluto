metabolite("S1",s).

% import S1
metabolite("S1",d).
reversible("R_importS1").
reaction("R_importS1",d).
prd("S1","1","R_importS1",d).
bounds("R_importS1","-99999","99999").


metabolite("I1",r).
% metabolite("I2",r).
metabolite("T",r).

reaction("R1",r).
bounds("R1","0","99999").
rct("S1","1","R1",r).
% rct("I2","1","R1",r).
prd("I1","1","R1",r).


reaction("R2",r).
bounds("R2","0","99999").
rct("I1","1","R2",r).
% prd("I2","1","R2",r).
prd("T","1","R2",r).

% export T
metabolite("T",t).
reaction("EX",t).
objective("EX",t).
bounds("EX","0","99999").
rct("T","1","EX",t).

#const export=1. 

