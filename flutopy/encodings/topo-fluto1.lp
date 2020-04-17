%%%%       TOPOLOGICAL REACHABILITY ENCODINGS        %%%%
%%%%            à la Frioux & Schellenberg           %%%%

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

%%%%%%%%%% REACHABILITY ENCODING %%%%%%%%%%%

% draft and choosen repair scope
scope(M,c) :- scope(M,d).
scope(M,c) :- edge(R,_,M,T), T!=r, scope(N,c):edge(R,N,_,T'), T'!=r, N!=M.
scope(M,c) :- completion(R), edge(R,_,M,r), scope(N,c):edge(R,N,_,r), N!=M.

% each target of scope need to be reached
:- metabolite'(M,t), not scope(M,c), reachability=1, unreachable=0.
:- metabolite'(M,t), scope(M,x), not scope(M,c), reachability=1, unreachable=1.
unreachable(M) :- metabolite'(M,t), not scope(M,x), unreachable=1, reachability=1.
