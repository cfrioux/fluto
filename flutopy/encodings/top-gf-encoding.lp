% option data defaults
#const unreachable=1.
#const reachability=1.
#const fluxbalance=1.
#const edge_priority=2.
#const exp_priority=3.
#const boundary=1.

%%%%%%%%%% GENERAL ENCODING %%%%%%%%%%%

% avoid duplicate metabolites and repair reactions that are already in the draft
metabolite'(M,s) :- metabolite(M,s).
metabolite'(M,t) :- metabolite(M,t).
metabolite'(M,d) :- metabolite(M,d), not metabolite(M,s), not metabolite(M,t).
metabolite'(M,r) :- metabolite(M,r), not metabolite(M,s), not metabolite(M,t), not metabolite(M,d).
reaction'(R,T) :- reaction(R,T), T!=r.
reaction'(R,r) :- reaction(R,r), not reaction(R,d), not reaction(R,t).
rct'(M,W,R,T) :- rct(M,W,R,T), T!=r.
rct'(M,W,R,r) :- rct(M,W,R,r), not rct(M,W,R,d), not rct(M,W,R,t).
prd'(M,W,R,T) :- prd(M,W,R,T), T!=r.
prd'(M,W,R,r) :- prd(M,W,R,r), not prd(M,W,R,d), not prd(M,W,R,t).

% detect boundary seeds by itself
metabolite'(M,s) :- prd'(M,_,R,T), T!=r, #count{N:rct(N,W,R,T)}=0, boundary=1.
metabolite'(M,s) :- rct'(M,_,R,T), T!=r, #count{N:prd(N,W,R,T)}=0, reversible(R), boundary=1.

% draft scope
scope(M,d) :- seed(M).
scope(M,d) :- metabolite'(M,s).
scope(M,d) :- scope(N,d):rct'(N,_,R,T'), T'!=r; reaction'(R,T), prd'(M,_,R,T), T!=r.
scope(M,d) :- scope(N,d):prd'(N,_,R,T'), T'!=r; reaction'(R,T), reversible(R), rct'(M,_,R,T), T!=r.
% extended (all) scope
scope(M,x) :- scope(M,d).
scope(M,x) :- scope(N,x):rct'(N,_,R,_); reaction'(R,T), prd'(M,_,R,_).
scope(M,x) :- scope(N,x):prd'(N,_,R,_); reaction'(R,T), reversible(R), rct'(M,_,R,_).

% choose completion
{ completion(R) : reaction'(R,r), not reaction'(R,d), prd'(M,_,R,r), scope(M,x) }.

%%%%%%%%%% REACHABILITY ENCODING %%%%%%%%%%%

% draft and choosen repair scope
scope(M,c) :- scope(M,d).
scope(M,c) :- scope(N,c):rct'(N,_,R,T'), T'!=r; reaction'(R,T), prd'(M,_,R,T), T!=r.
scope(M,c) :- scope(N,c):prd'(N,_,R,T'), T'!=r; reaction'(R,T), reversible(R),rct'(M,_,R,T), T!=r.
scope(M,c) :- scope(N,c):rct'(N,_,R,r); completion(R), prd'(M,_,R,r).
scope(M,c) :- scope(N,c):prd'(N,_,R,r); completion(R), reversible(R),rct'(M,_,R,r).

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
