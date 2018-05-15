% what is producible by draft

	dscope(M) :- product(M,R,_), dreaction(R,_),
				dscope(M2) : reactant(M2,R,_).
	dscope(M) :- reactant(M,R,_), dreaction(R,_), reversible(R,_),
				dscope(M2) : product(M2,R,_).
	dscope(M) :- seed(M).

% unproducible targets

    unproducible_target(M) :- target(M,_), not dscope(M).

    #show unproducible_target/1.
