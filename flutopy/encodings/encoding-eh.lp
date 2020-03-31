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

% extended (all) scope
scope(M,x) :- scope(M,d).
scope(M,x) :- edge(R,_,M,_), scope(N,x):edge(R,N,_,_), N!=M.


%%%%%%%%%% REACHABILITY ENCODING  Ebenhöh Handorf %%%%%%%%%%%

% choose completion
{ completion(R) : edge(R,M,N,r), not edge(R,M,N,d), scope(M,x), scope(N,x) }.

% draft and choosen repair scope
scope(M,c) :- scope(M,d).
scope(M,c) :-                edge(R,_,M,T), T!=r, scope(N,c):edge(R,N,_,T'), T'!=r, N!=M.
scope(M,c) :- completion(R), edge(R,_,M,r), scope(N,c):edge(R,N,_,r), N!=M.

% each reachable target of scope need to be reached
:- metabolite'(M,t), scope(M,x), not scope(M,c).
unreachable(M) :- metabolite'(M,t), not scope(M,x).
#show unreachable/1.

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
