% option data defaults
#const edge_priority=2.
#const exp_priority=3.
#const topo_seeds=1.
#const overlaps=0.

%%%%%%%%%% GENERAL ENCODING %%%%%%%%%%%

% overlaps=0 avoid overlaps of draft and repair
metabolite'(M,s) :- metabolite(M,s), overlaps=0.
metabolite'(M,t) :- metabolite(M,t), overlaps=0.
metabolite'(M,d) :- metabolite(M,d), not metabolite(M,s), not metabolite(M,t), overlaps=0.
metabolite'(M,r) :- metabolite(M,r), not metabolite(M,s), not metabolite(M,t), not metabolite(M,d), overlaps=0.
reaction'(R,T) :- reaction(R,T), T!=r, overlaps=0.
reaction'(R,r) :- reaction(R,r), not reaction(R,d), not reaction(R,t), overlaps=0.
rct'(M,W,R,T) :- rct(M,W,R,T), T!=r, overlaps=0.
rct'(M,W,R,r) :- rct(M,W,R,r), not rct(M,W,R,d), not rct(M,W,R,t), overlaps=0.
prd'(M,W,R,T) :- prd(M,W,R,T), T!=r, overlaps=0.
prd'(M,W,R,r) :- prd(M,W,R,r), not prd(M,W,R,d), not prd(M,W,R,t), overlaps=0.

% overlaps=1 dont avoid overlaps
metabolite'(M,T) :- metabolite(M,T), overlaps=1.
reaction'(R,T) :- reaction(R,T), overlaps=1.
rct'(M,W,R,T) :- rct(M,W,R,T), overlaps=1.
prd'(M,W,R,T) :- prd(M,W,R,T), overlaps=1.

% edges
edge(R,M,N,T) :- reaction'(R,T), rct'(M,_,R,T), prd'(N,_,R,T).
edge(R,M,N,T) :- reaction'(R,T), rct'(N,_,R,T), prd'(M,_,R,T), reversible(R).

% draft scope
scope(M,d) :- seed(M), topo_seeds=1.
scope(M,d) :- metabolite'(M,s).
scope(M,d) :- edge(R,_,M,T), T!=r, scope(N,d):edge(R,N,_,T'), N!=M, T'!=r.


%%%%%%%%%% REACHABILITY ENCODING  Sagot Acuna %%%%%%%%%%%

% choose completion
{ completion(R) : edge(R,M,N,r), not edge(R,M,N,d) }.

reach(X) :- scope(X,d).
reach(X) :- prd'(X,_,R,T), rct'(Y,_,R,T), reach(Y).
reach(X) :- rct'(X,_,R,T), prd'(Y,_,R,T), reach(Y), bounds(R,L,U), L<0.

% each metabolite might be available
available(M) :- scope(M,d).
{ available(M) } :- metabolite'(M,T), reach(M).

% a reaction is applicable if all reactants are available
applicable(R) :- available(M) : rct'(M,_,R,T); reaction'(R,T), T!=r.
applicable(R) :- available(M) : prd'(M,_,R,T); reaction'(R,T), T!=r, bounds(R,L,U), L<0.
applicable(R) :- available(M) : rct'(M,_,R,T); reaction'(R,T), completion(R).
applicable(R) :- available(M) : prd'(M,_,R,T); reaction'(R,T), completion(R), bounds(R,L,U), L<0.

produced(M) :- applicable(R), prd'(M,_,R,T).
produced(M) :- applicable(R), rct'(M,_,R,T), bounds(R,L,U), L<0.

:- available(M), not produced(M).

% every target must be available
:- metabolite'(M,t), not available(M).


%%%%%%%%%% FLUX BALANCED ENCODING %%%%%%%%%%%

% domain definition; default dom{(x,0,inf)}
&dom{L..U} = R :- bounds(R,L,U).

% equalities for all metabolites
% export=0: consider no exports
&sum{  IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR')
   } = 0 :- metabolite'(M,_), not metabolite'(M,s),  export=0.
% export=1: exports via conditionals
&sum{  IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR');
     -1*M   : exp(M)
   } = 0 :- metabolite'(M,_), not metabolite'(M,s), export=1.

% derive exports
exp(M) :- &sum{M} > 0, metabolite'(M,T), export=1.
#show exp/1.

% goal condition: target > 0
&sum{ R } > 0 :- reaction'(R,t).

% export=1: minimizing exports via ASP  priorize less exports (less than gaps)
#minimize{ 1@exp_priority,M:exp(M) }.

% maximizing biomass maximize{W*ID : objective(ID,W)}
&maximize{ R : objective(R,t) }.

% minimize number of gaps
#minimize{ 1@edge_priority,R:completion(R) }.

#show completion/1.
%#show metabolite'/2.
%#show compound(M) : metabolite'(M,N), N!=s.
