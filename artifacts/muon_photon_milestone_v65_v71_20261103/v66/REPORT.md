# v66: eight-source radial Gauss return with its boundary remainder

The known classical source component now has an explicit radial return on
the saved initializer, using the original eight angular photon directions,
four radial profiles and 48-point quadrature plus its wall evaluation.
The nonzero radial connection is retained. Its first transport correction,
the inherited-flux transfer, the bulk-current kernel and the boundary Higgs
range map are constructed, with all 189 local-coordinate derivatives streamed.
No complete physical current, entering trace or event domain is assigned.

This is a local mathematical/coefficient milestone. It remains distinct from
a physical reconnection event or a magnetic-moment prediction. V65 and the
published v64 commit are unchanged; this work is local and is not pushed.

## 1. Owned source and radial equations

Write the canonical electric momentum as a density in the original material
coordinates. The interior Gauss equation and its linearization are

    D_rho Pi^rho + D_i Pi^i + rho_bulk = 0,
    (partial_rho+ad A_rho) delta Pi^rho = -F,
    F = D_i delta Pi^i + [delta A_m,Pi^m] + delta rho_bulk
        + the actual coordinate/domain pullback terms.

The sum over m includes rho. Independent native/relative, matter and source
correlations belong in delta rho_bulk with their original signs and matching.
They are not assigned zero. Boundary Higgs momentum is not an interior source.

For the specifically evaluated **direct field-velocity columns**, the existing
Maxwell Legendre map supplies

    delta dot A_i = B_p(rho) s_H omega_i,A,
    delta Pi^i = MAXWELL_TO_CAP e(rho) B_p(rho) s_H omega_i,A.

Here A=1,...,8 and p=0,...,3. These are coefficient directions of the original
variables, not chosen source amplitudes, particle states or physical photon
modes. The field values and geometry are fixed for this partial derivative;
their changes and native response are additional terms in the complete photon
variation. No new radial profile is introduced.

The source direction has `s_H=sqrt(16/3) q(H)`. On this angular-constant
initializer, the ordinary coexact divergence vanishes and the known load is

    K_pA(rho) = MAXWELL_TO_CAP e B_p G_A,
    G_A = sum_i [A_i,s_H] omega_i,A,
    s_H^T G_A = 0.

The A_i includes `M_i(lambda-1)` exactly once. The saved full wall field and
all original radial field samples/derivatives are checked independently.
The reference action subtraction has no independent-field-velocity variation;
it is not added a second time. Full native overlap subtraction remains once.

## 2. Explicit connection and controlled transport

The owned radial connection has the finite expression

    A_rho(rho) = x^alpha sum_(m=0)^3 c_m x^m,
    x=rho/(pi/2), alpha=(sqrt(45)-3)/2.

It is recovered from the existing four normalized Jacobi profiles and the
original gauge coefficients. Neither its SU(2) part nor its larger central
component is replaced by zero. The central component has exactly zero
adjoint action; that algebraic fact is also tested in its derivative columns.

Define A(rho)=ad A_rho(rho), with the owned unit-Tr16 bracket. Then

    partial_b U(b,a) = -A(b) U(b,a),  U(a,a)=I,
    J(b,a) = integral_a^b A(rho) d rho,
    U1(b,a) = I-J(b,a).

J is integrated analytically, power by power. No radial interpolation or new
quadrature is used for this connection. Skew adjointness makes the exact U an
isometry in the internal norm on a regular radial patch. This proves a local
transport property, not a complete physical Cauchy/domain theorem.

An upward-rounded coefficient bound gives

    integral_0^wall ||ad A_rho|| <= 5.27776750766740e-12.

For this frozen fractional-polynomial representation, the omitted ordered
transport terms satisfy

    ||U-U1|| <= a^2/[2(1-a)], a=5.27776750766740e-12 < 1.

This bound follows from the ordered-integral series without commuting radial
matrices or subtracting nearly equal floating exponentials. Decimal upward
rounding is used for the finite coefficient bound. It does not certify the
unknown physical coefficients or the integration error of the separate force
quadrature. Agreement with the saved radial basis remains a method check.

## 3. Affine return: inherited flux and bulk current remain

For the actual allowed entering face rho_in, the complete local relation is

    P_wall = U(wall,rho_in) P_in - integral U(wall,rho) F(rho) d rho.

The inherited P_in is not set to zero or fitted. Its allowed domain and its
coupled preparation must be supplied by the common event/Cauchy construction.
The stored endpoint matrix U1(wall,0) is a cap-coordinate operator value, not
a selection of physical pole flux. If the actual domain reaches a regular
pole, its finite-energy/trace condition must restrict P_in there; arbitrary
pole flux is not declared admissible. An actual inner port uses its own
entering face. Neither is replaced by an invented terminal condition.

The stored 49 kernel values also act on the remaining bulk current and
connection/background terms. This is the same source operator as the known
load, not a new independent closure. Their physical contractions remain open.

For K_pA only, the existing 48 quadrature weights give

    R0 = -sum_n w_n K_n,
    R1 = +sum_n w_n J(wall,rho_n) K_n,
    R_known = R0+R1.

The sign follows the original Gauss equation. These columns are a **particular
component of an affine response**, not a solution obtained by choosing all
other physical sources to vanish. The normal-flux transfer and independent
bulk-current terms must still be added.

Because `s_H^T R0=0` algebraically, the small surviving photon contraction is
evaluated as `s_H^T R1`, without subtracting large terms. It is nonzero:

| Saved-coefficient result | Value |
| --- | ---: |
| Norm of known normal return | 15.66425078928752 |
| Norm of its photon-projected first transport correction | **5.622569530130817e-14** |
| Largest bound from omitted transport orders in a projected column entry | **1.367454676288709e-22** |

The last line applies to the frozen connection model and fixed quadrature
source sum. It is not a quadrature-error certificate, a physical uncertainty,
or a reason to discard a term by comparing it with the physical guard.
The source sum, connection coefficients and geometry are initializer data.
Actual current and released work have not been evaluated.

Finite arithmetic/source representation also leaves a raw zeroth-order photon
contraction with largest entry 4.44e-15, despite the analytic coexact/invariant
cancellation. The raw zeroth and total contractions are saved separately from
the symmetry-reduced first transport component. This drift is larger than the
omitted-order bound and is **not** covered by it. The boundary range check uses
the raw return on both sides. The quoted small component must not be read as
a complete projection certified to 1e-22 accuracy.

## 4. Boundary matching and total coefficient response

For the parent outer face, the original gauge Green identity contributes
`b_Gamma delta Pi=-P_wall`. The boundary equation remains

    -P_wall + B(H)^T delta p_H + (delta B)^T p_H
              + rho_Gamma,rest + other retained/released conormals = 0.

Every term is pulled to the same common trace domain. No sharp indicator is
used to split an arbitrary weak conormal. Event, normal, clock and moving-edge
terms remain in the complete row; the local radial result does not construct
their unresolved physical extension.

Using v25's already-proved `T=B(B^T B)^+`, the new known component has

    delta p_H,known = T R_known,
    -R_known+B^T delta p_H,known = -q (q^T R_known).

The charged part is therefore absorbed by an explicitly computed Higgs
momentum range component. The neutral part remains and must be matched by
the complete inherited/native/released load. No radial Higgs momentum is
chosen: the general solution retains its null component along H. A nonzero
known remainder is not proof of inconsistency, since the complete equation
has not yet been evaluated.

First derivatives are saved in all 189 local coordinates, including the
electric density, mechanical lambda, independent connection, Higgs direction,
normal transport and Higgs range-map variation. They are streamed rather
than allocating a full node-by-coordinate source tensor. For the complete
physical total response, also retain

    delta U(b,a) = -integral_a^b U(b,s) ad(delta A_rho(s)) U(s,a) d s
                  + endpoint/domain motion,
    delta[U P_in] = (delta U)P_in + U delta P_in,
    delta(integral U F) = integral[(delta U)F+U delta F]
                         + moving-endpoint/readout terms.

These identities preserve independent entering and ordered source data.
The computed coefficient derivatives are not those unknown physical data.
Their noncommuting placements are retained; no native mixed term or the
separately varied Dirac-bar factors are altered by this classical calculation.

## 5. What is now executable and what is next

Executable now: the continuous analytic first-order radial transport kernel
with its conditional remainder, its inherited-flux transfer, its application
to 32 existing angular/radial velocity columns at the original 48 nodes, and
the corresponding boundary range elimination and 189 derivatives.
The largest method consistency defect is 6.19e-13, below the unchanged
2e-11 method tolerance. It is not the full physical residual.

The earliest remaining consumed quantity is the same-domain combination of
inherited normal flux, complete bulk-current return and retained/released
boundary load in the surviving electromagnetic row. These are prescribed
by the adopted preparation and native/relative action, not adjustable data.
The new kernel can now consume their projected values directly. The smallest
next step is to apply its dual photon covector to the action-owned bulk
current and entering trace, retaining the actual partial-envelope graph.
If only initializer values are available, their scope must remain conditional.
No new state, dissipation law, boundary selection rule or broad solve is
needed merely to formulate this remaining application.

The fixed preparation, original 2e-10 physical guard and admitted t=2^-9
temporal baseline are unchanged. No full physical state, reconnection,
released-energy partition, muon anomaly or total uncertainty is claimed.
Existing matched sectors and overlap are not recounted as new contributions.

## Reproduction and execution boundary

The checkpoint includes the frozen source inputs/excerpts, producer, focused
tests and isolated runner. Use the supplied runner under the inspected Dads
Python314 roots; it disables site/.pth startup, custom PYTHONPATH, plugin
autoload and repository conftest, and guards import destinations. This is a
bounded invocation, not a security certification of the whole computer.

```text
C:\Python314\python.exe -I -S isolated_muon_radial_runner_20261103.py produce --artifact . --out replay --receipt replay_invocation.json
C:\Python314\python.exe -I -S isolated_muon_radial_runner_20261103.py tests --artifact . --out replay_tests.xml --receipt replay_tests_invocation.json
```

The standalone replay and archive hashes are recorded in the final checkpoint
receipt. No old heat/history campaign, new resolution, reviewer or extra
worker is used, and no new changes are pushed.
