% option data defaults
#const unreachable=1.

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


% minimize size of completion
#minimize{ 1@2,R : completion(R) }.

#show completion/1.
#show producible_target/1.
#show unreachable/1.
#show acc/1.
