%%%%       TOPOLOGICAL REACHABILITY ENCODINGS        %%%%
%%%%            à la Handorf & Ebenhöh               %%%%
handorf.

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
