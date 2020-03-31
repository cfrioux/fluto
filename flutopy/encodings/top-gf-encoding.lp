% option data defaults
#const unreachable=1.
#const reachability=1.
#const fluxbalance=1.
#const edge_priority=2.
#const exp_priority=3.
#const topo_seeds=1.
#const boundary=1.
#const hinteresting=0.
#const overlaps=0.
#const cspace_opt=0.

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


% detect boundary seeds by itself
metabolite'(M,s) :- prd'(M,_,R,T), T!=r, #count{N:rct(N,W,R,T)}=0, boundary=1.
metabolite'(M,s) :- rct'(M,_,R,T), T!=r, #count{N:prd(N,W,R,T)}=0, reversible(R), boundary=1.

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

% choose completion
{ completion(R) : edge(R,M,N,r), not edge(R,M,N,d), scope(M,x), scope(N,x) } :- cspace_opt=0.

% completion space optimization (exploit pairwise repair equivalences)
{ completion(R)
     : edge(R,M,N,r), not edge(R,M,N,d), scope(M,x), scope(N,x), edge(_,_,M,T1), T1!=r;
  completion(R)
     : edge(R,M,N,r), not edge(R,M,N,d), scope(M,x), scope(N,x), edge(_,N,_,T2), T2!=r;
  completion(IR,OR)
     : edge(IR,_,M,r), edge(OR,M,_,r), not edge(IR,_,M,d), not edge(OR,M,_,d), scope(M,x), metabolite'(M,r) }
               :- cspace_opt=1.
completion(IR) :- completion(IR,OR), cspace_opt=1.
completion(OR) :- completion(IR,OR), cspace_opt=1.

% get interesting reactions backwards from targets to seeds
applicable_forward(R) :- reaction'(R,_), scope(M,x) : rct'(M,_,R,_) ; prd'(M2,_,R,_), not scope(M2,d),
                            hinteresting=1.
applicable_backward(R) :- reaction'(R,_), reversible(R), scope(M,x) : prd'(M,_,R,_) ; rct'(M2,_,R,_), not scope(M2,d),
                            hinteresting=1.

mproducible(M) :- metabolite'(M,t), scope(M,x),
                            hinteresting=1.
munproducible(M) :- metabolite'(M,t), not scope(M,x),
                            hinteresting=1.

interesting_metabolite(M) :- mproducible(M), not scope(M,d),
                            hinteresting=1.
interesting_metabolite(M) :- rct'(M,_,R,_), interesting_reaction_forward(R), not scope(M,d),
                            hinteresting=1.
% for reversible reactions
interesting_metabolite(M) :- prd'(M,_,R,_), interesting_reaction_backward(R), not scope(M,d),
                            hinteresting=1.

interesting_reaction_forward(R) :- applicable_forward(R), prd'(M,_,R,_), interesting_metabolite(M),
                            hinteresting=1.
% for reversible reactions
interesting_reaction_backward(R) :- applicable_backward(R), rct'(M,_,R,_), interesting_metabolite(M),
                            hinteresting=1.

interesting(R) :- interesting_reaction_forward(R), not edge(R,_,_,d),
                            hinteresting=1.
interesting(R) :- interesting_reaction_backward(R), not edge(R,_,_,d),
                            hinteresting=1.

% set heuristic on interesting reactions
#heuristic completion(R):interesting(R), hinteresting=1. [1,true]



%%%%%%%%%% REACHABILITY ENCODING %%%%%%%%%%%

% draft and choosen repair scope
scope(M,c) :- scope(M,d).
scope(M,c) :- edge(R,_,M,T), T!=r, scope(N,c):edge(R,N,_,T'), T'!=r, N!=M.
scope(M,c) :- completion(R), edge(R,_,M,r), scope(N,c):edge(R,N,_,r), N!=M.

% each target of scope need to be reached
:- metabolite'(M,t), not scope(M,c), reachability=1, unreachable=0.
:- metabolite'(M,t), scope(M,x), not scope(M,c), reachability=1, unreachable=1.
unreachable(M) :- metabolite'(M,t), not scope(M,x), unreachable=1, reachability=1.
#show unreachable/1.

%%%%%%%%%% FLUX BALANCED ENCODING %%%%%%%%%%%

% domain definition; default dom{(x,0,inf)}
&dom{L..U} = R :- bounds(R,L,U), fluxbalance=1.

% equalities for all metabolites
% export=0: consider no exports
&sum{  IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR')
   } = 0 :- metabolite'(M,_), not metabolite'(M,s), fluxbalance=1, export=0.
% export=1: exports via conditionals
&sum{  IS*IR   : prd'(M,IS,IR,T), T!=r;
     -OS*OR   : rct'(M,OS,OR,T), T!=r;
      IS'*IR' : prd'(M,IS',IR',r), completion(IR');
     -OS'*OR' : rct'(M,OS',OR',r), completion(OR');
     -1*M   : exp(M)
   } = 0 :- metabolite'(M,_), not metabolite'(M,s), fluxbalance=1, export=1.

% derive exports
exp(M) :- &sum{M} > 0, metabolite'(M,T), fluxbalance=1, export=1.
#show exp/1.

% goal condition: target > 0
&sum{ R } > 0 :- reaction'(R,t), fluxbalance=1.

% export=1: minimizing exports via ASP  priorize less exports (less than gaps)
#minimize{ 1@exp_priority,M:exp(M),fluxbalance=1 }.

% maximizing biomass maximize{W*ID : objective(ID,W)}
&maximize{ R : objective(R,t) } :- fluxbalance=1.

% minimize number of gaps
#minimize{ 1@edge_priority,R:completion(R) }.

#show completion/1.
%#show metabolite'/2.
%#show compound(M) : metabolite'(M,N), N!=s.
