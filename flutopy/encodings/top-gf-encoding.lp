% option data defaults
#const unreachable=1.
% handorf.
% no_fba.
% no_accumulation.

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

% detect boundary seeds defined via reactions in the model
metabolite'(M,s) :- prd'(M,_,R,T), T!=r, #count{N:rct(N,W,R,T)}=0.
metabolite'(M,s) :- rct'(M,_,R,T), T!=r, #count{N:prd(N,W,R,T)}=0, reversible(R).

% draft scope
dscope(M) :- seed(M).
dscope(M) :- metabolite'(M,s).
dscope(M) :- dscope(N):rct'(N,_,R,T'), T'!=r; reaction'(R,T), prd'(M,_,R,T), T!=r.
dscope(M) :- dscope(N):prd'(N,_,R,T'), T'!=r; reaction'(R,T), reversible(R), rct'(M,_,R,T), T!=r.

% potential scope (with all reactions)
pscope(M) :- dscope(M).
pscope(M) :- pscope(N):rct'(N,_,R,_); reaction'(R,T), prd'(M,_,R,_).
pscope(M) :- pscope(N):prd'(N,_,R,_); reaction'(R,T), reversible(R), rct'(M,_,R,_).


%%%%%%%%%% REACHABILITY ENCODINGS %%%%%%%%%%%
sagot :- not handorf.

%%%% à la Sagot & Acuña %%%%%%%%%%%

% choose completion
{ completion(R) : reaction'(R,r), not reaction'(R,d) } :- sagot.
% { completion(R) } :- present(M):rct'(M,_,R,r); reaction'(R,r), not reaction'(R,d), sagot.
% { completion(R) } :- present(M):prd'(M,_,R,r); reaction'(R,r), not reaction'(R,d), reversible(R), sagot.

reach(X) :- pscope(X), sagot.
reach(X) :- prd'(X,_,R,T), rct'(Y,_,R,T), reach(Y), sagot.
reach(X) :- rct'(X,_,R,T), prd'(Y,_,R,T), reach(Y), bounds(R,L,U), L<0, sagot.

% each metabolite might be present
present(M) :- dscope(M), sagot.
{ present(M) } :- metabolite'(M,T), reach(M), not dscope(M), sagot.

% a reaction is feasible if all reactants are present
feasible(R) :- present(M) : rct'(M,_,R,T); reaction'(R,T), T!=r, sagot.
feasible(R) :- present(M) : prd'(M,_,R,T); reaction'(R,T), T!=r, bounds(R,L,U), L<0, sagot.
feasible(R) :- present(M) : rct'(M,_,R,T); reaction'(R,T), completion(R), sagot.
feasible(R) :- present(M) : prd'(M,_,R,T); reaction'(R,T), completion(R), bounds(R,L,U), L<0, sagot.

producible(M) :- feasible(R), prd'(M,_,R,T), sagot.
producible(M) :- feasible(R), rct'(M,_,R,T), bounds(R,L,U), L<0, sagot.

% every present metabolite must be producible
:- present(M), not producible(M), not dscope(M), sagot.

% every target must be present
:- metabolite'(M,t), not present(M), unreachable=0, sagot.
unreachable(M) :- metabolite'(M,t), not present(M), sagot.
producible_target(M) :- metabolite'(M,t), present(M), sagot.
#minimize{ 1@4,M:unreachable(M), metabolite'(M,t),unreachable=1, sagot }.

%%%% à la Handorf & Ebenhöh 

% choose completion
% { completion(R) : reaction'(R,r), not reaction'(R,d), prd'(M,_,R,r), pscope(M) } :- handorf.
help(R) :- pscope(M):rct'(M,_,R,r); reaction'(R,r), not reaction'(R,d), prd'(M,_,R,r), pscope(M), handorf.
help(R) :- pscope(M):prd'(M,_,R,r); reaction'(R,r), not reaction'(R,d), rct'(M,_,R,r), pscope(M), reversible(R), handorf.
{ completion(R) : help(R) } :- handorf.


% draft and choosen repair scope
xscope(M) :- dscope(M), handorf.
xscope(M) :- xscope(N):rct'(N,_,R,T'), T'!=r; reaction'(R,T), prd'(M,_,R,T), T!=r, handorf.
xscope(M) :- xscope(N):prd'(N,_,R,T'), T'!=r; reaction'(R,T), reversible(R),rct'(M,_,R,T), T!=r, handorf.
xscope(M) :- xscope(N):rct'(N,_,R,r); completion(R), prd'(M,_,R,r), handorf.
xscope(M) :- xscope(N):prd'(N,_,R,r); completion(R), reversible(R),rct'(M,_,R,r), handorf.

% each target of scope need to be reached
:- metabolite'(M,t), not xscope(M), unreachable=0, handorf.
:- metabolite'(M,t), pscope(M), not xscope(M), unreachable=1, handorf.
unreachable(M) :- metabolite'(M,t), not pscope(M), unreachable=1, handorf.
producible_target(M) :- metabolite'(M,t), xscope(M), handorf.

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

% minimize size of completion
#minimize{ 1@2,R : completion(R) }.

#show completion/1.
#show producible_target/1.
#show unreachable/1.
#show acc/1.
