%%%%       TOPOLOGICAL REACHABILITY ENCODINGS        %%%%
%%%%             à la Sagot & Acuña                  %%%%
sagot.

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
