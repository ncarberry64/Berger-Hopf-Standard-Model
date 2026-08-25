# N12 finite-endpoint forward--adjoint KKT system

Status: `NO_SELECTOR_FORWARD_ADJOINT_KKT_SYSTEM_DERIVED_EVALUATION_OPEN`.

The AE2 reset is a relation, not a selector.  Therefore an adjoint force
evaluation at one fixed reset parameter cannot by itself define the physical
same-action saddle.  On a nonempty regular finite event or canonical-stop
stratum, the action-native unknown is the coupled tuple

`(xi,T,Y(t),P[Y,T],p(t))`,

where `xi` is a physical reset-quotient parameter.  The exact equations are

`Y(0)=R_AE2(xi)`, `Y'=V_AE2(Y)`,

the first retained transverse event or canonical-stop graph, the action-owned
operator realization `P[Y,T]`, the heat-minus-zeta operator cotangent, and

`-p'=DV(Y)^dagger p+q_Y`, `p(T)=Pi_T^dagger g_T`,

with `Pi_T=I-V tensor De/(De V)` at an event.  The final stationarity equation
is

`N_phys^dagger(D_xi R_AE2^dagger p(0)+q_xi,direct)=0`.

In raw coordinates this is equivalent to the bordered reset-constraint KKT
system after quotienting only the exact gauge and whole-system time
generators.  Common scale remains physical.

There are two equivalent implementations: certify a parametric finite-stratum
oracle and root its adjoint covector, or solve the forward state, operator,
adjoint, endpoint, and quotient stationarity equations simultaneously.  The
latter is a boundary-value formulation of the same action, not a new endpoint
condition or a reset selector.

Evaluating the first-order residual uses the retained `D3 L`.  Certifying a
Newton/KKT correction on a nonzero-force branch requires the already-retained
`D4 L`, second operator jet, and reset curvature.  That geometry KKT Jacobian
is still distinct from the later pair-plus-contact source Hessian.

No finite endpoint solution is claimed here.  The two certified chords remain
a base core without an endpoint, chord 3 remains unauthorized, Gate 7 is
active, and frozen predictions are unchanged.
