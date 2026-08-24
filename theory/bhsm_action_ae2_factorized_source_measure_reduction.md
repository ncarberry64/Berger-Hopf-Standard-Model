# AE2 factorized source-measure reduction

For one fixed factorized channel write `A=d/dtau+s(tau)`, `K=A* A`, `v=A u`, and `lambda=k^2`. The exact transfer system is

`u'=-s u+v`, `v'=s v-lambda u`.

At a zero resonance the natural factorized conormal is zero, so `u_0=exp(-S)` and `v_0=0`, with `S(t)=integral_0^t s`. Differentiating in the neutral spectral value `lambda` gives

`partial_lambda v|_0=-exp(S(t))*integral_0^t exp(-2S(r))dr`.

Thus `A u_k=O(k^2)` on every compact source support. Since the retained log-radius factor jet is multiplication by `-h s`, the first form response is

`D_h q[u_k]=2 Re integral (A u_k)^*(-h s u_k)=O(k^2)`.

If the sum of squared generalized-eigenstate normalization amplitudes is uniformly bounded in a threshold neighborhood for that channel, one-dimensional counting gives `|nu_h|([0,Lambda])=O(Lambda^(3/2))`. This is exactly the strict superlinearity needed by the stored E1 dyadic criterion. The constant-core witness is recovered algebraically, including coefficient `6.552579915052088`.

This closes the abstract factorized transfer-to-source-measure implication and reduces the realized infinite-end obligation to one source-contracted scalar supremum per channel. It does not claim that the unknown N12 maximal far end has that uniform bound. A finite regular event or canonical stop has compact resolvent; its zero atom has exactly zero first form weight and needs no continuous limiting-absorption theorem.

The next dependency is therefore to classify each realized factorized far end. Only infinite regular ends need a finite threshold generalized-eigenstate normalization sum on the retained compact source support. A strict Wronskian gap and a full operator-norm limiting-absorption theorem remain unnecessary.

`FULL_BHSM_COMPLETE=false`.
