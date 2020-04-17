%%%%%%%%%% FLUX BALANCED ENCODING %%%%%%%%%%%
fluxbalance :- not no_fba.

% domain definition; default dom{(x,0,inf)}
&dom{L..U} = R :- bounds(R,L,U), fluxbalance.

% equalities for all metabolites either with accumulation allowed or not
allow_accumulation :- fluxbalance, not no_accumulation.

% no accumulation of metabolites allowed
&sum{ IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR')
    } = 0 :- metabolite'(M,_), not metabolite'(M,s), fluxbalance, no_accumulation.

% accumulation of metabolites allowed

% derive accumulating metabolites
acc(M) :- &sum{M} > 0, metabolite'(M,T), fluxbalance, allow_accumulation.

&sum{ IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR');
     -1*M   : acc(M)
    } = 0 :- metabolite'(M,_), not metabolite'(M,s), fluxbalance, allow_accumulation.


% goal condition: target flux > 0
&sum{ R } > 0 :- reaction'(R,t), fluxbalance.

% minimizing accumulating metabolites priorize less accumulation (less than gaps)
#minimize{ 1@3,M : acc(M), fluxbalance, allow_accumulation }.

% maximizing biomass maximize{W*ID : objective(ID,W)}
&maximize{ R : objective(R,t) } :- fluxbalance.