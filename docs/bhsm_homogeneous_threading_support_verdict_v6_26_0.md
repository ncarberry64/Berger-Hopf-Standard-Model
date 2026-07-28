# BHSM v6.26.0 homogeneous threading and support verdict

## Result

The local, action-normalized particular threading response is derived on the
action-selected closed-dS4 background.  It remains

\[
 B_{\rm part}(t,u)
 =-\tau{\pi\chi_1\over16}tq(u).
\]

However, variation with respect to the longitudinal scalar potential gives
only the divergence of the radial momentum constraint.  If

\[
 W(t,u)=B(t,u)+\tau{\pi\chi_1\over16}tq(u),
\]

the scalar-potential action equation is

\[
 \Box_4W=0,
\]

whereas the unprojected momentum constraint requires

\[
 D_\mu W=0.
\]

For a spatially homogeneous field the action equation admits

\[
 W_h(u)=C_0+C_1\int^u{du'\over a_4(u')^3}.
\]

The momentum constraint removes the \(C_1\) mode.  The inherited
\(C_\Sigma=0\) axiom fixes the time-independent spatial \(\ell=0\)
integration constant \(C_0\); its declared v6.18 round-\(S^3\) domain does
not fix the Lorentzian \(C_1\) mode.  Selecting retarded, advanced, Feynman,
Euclidean, initial, or final data would add an unstored state/domain
condition.

The earliest-stop support verdict is therefore

```text
BHSM_SUPPORT_DOMAIN_DECISION_BLOCKED_BY_UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE
```

Neither fixed-support compatibility nor dynamical-embedding necessity is
issued.

## Frozen action and conventions

The retained action is

\[
 S_{\rm total}
 =S_{{\rm P1},+}+S_{{\rm P1},-}
 +S_{{\rm GHY},+}+S_{{\rm GHY},-}
 +S_{\rm B1}+S_{\rm match}+S_\sigma .
\]

The P1 and GHY sectors use

\[
 S_{\rm P1}
 =\int\sqrt{-g}\left[
 {\kappa_1\over2}R_5-{\kappa_0\over2}
 -{Z_5\over2}(\nabla\sigma)^2-U_5(\sigma)\right],
\]

\[
 S_{\rm GHY}
 =\kappa_1\int_{\rm B1}\sqrt{-h}\,K
\]

on each cap.  There are two P1 caps, two capwise GHY terms, one common
intrinsic B1, and one exact matcher

\[
 S_{\rm match}=\int_{\rm B1}\sqrt{-h}\,
 \Lambda^{\mu\nu}(h_{\mu\nu}-\iota^*g_{\mu\nu}).
\]

No matcher coefficient, endpoint potential, tension, corner term, embedding
term, or Lorentzian state prescription is added.

The M4 signature is \((-+++)\), with

\[
 K_{\mu\nu}
 ={1\over2N}\left(
 \partial_t\gamma_{\mu\nu}
 -D_\mu N_\nu-D_\nu N_\mu\right),
\qquad
 Q_{\mu\nu}=K_{\mu\nu}-K\gamma_{\mu\nu}.
\]

## Action-selected closed-dS4 background

The normalized M4 branch is

\[
 ds_4^2=-du^2+a_4(u)^2d\Omega_3^2,
\]

\[
 a_4(u)=X_c^{-1/2}
 \cosh\!\left[\sqrt{X_c}(u-u_0)\right],
\qquad X_c=2.
\]

Writing \(H_4=\dot a_4/a_4\),

\[
 H_4=\sqrt{X_c}\tanh[\sqrt{X_c}(u-u_0)],
\qquad
 \dot H_4+H_4^2=X_c.
\]

The required connection components are

\[
 \Gamma^u{}_{ij}=H_4h_{ij},\qquad
 \Gamma^i{}_{uj}=H_4\delta^i_j,\qquad
 \Gamma^u{}_{uu}=0.
\]

No step evaluates the verdict only at the turning point \(u=u_0\).

For any homogeneous scalar \(f(u)\),

\[
 D_uD_uf=\ddot f,\qquad
 D_iD_jf=-H_4h_{ij}\dot f,
\]

\[
 \Box_4f=-\ddot f-3H_4\dot f.
\]

Thus spatial homogeneity is not four-dimensional constancy.

## Fixed-manifold shift

Let

\[
 c=\tau{\pi\chi_1\over16}.
\]

The fixed-manifold map gives

\[
 B_{\rm part}=-ctq,\qquad
 N_u=D_uB_{\rm part}=-ct\dot q.
\]

Its second derivatives are

\[
 D_uD_uB_{\rm part}=-ct\ddot q,
\]

\[
 D_iD_jB_{\rm part}=ctH_4h_{ij}\dot q,
\]

\[
 \Box_4B_{\rm part}
 =ct(\ddot q+3H_4\dot q).
\]

The coordinate-map shift contribution to the extrinsic curvature is, at
general \(t\),

\[
 \delta K_{\mu\nu}^{(B)}
 =\alpha(t)D_\mu D_\nu q,
\qquad
 \alpha(t)=\tau{\chi_1\over4}t.
\]

At B1,

\[
 \delta K_{uu}^{(B)}
 ={\tau\chi_1\over4}\ddot q,
\]

\[
 \delta K_{ij}^{(B)}
 =-{\tau\chi_1\over4}H_4h_{ij}\dot q,
\]

\[
 \delta K^{(B)}
 ={\tau\chi_1\over4}\Box_4q.
\]

The corresponding one-cap \(Q\) pieces are

\[
 \delta Q_{uu}^{(B)}
 =-{3\tau\chi_1\over4}H_4\dot q,
\]

\[
 \delta Q_{ij}^{(B)}
 ={\tau\chi_1\over4}
 (\ddot q+2H_4\dot q)h_{ij},
\qquad
 \delta Q_{ui}^{(B)}=0.
\]

These are valid direct threading contributions.  They are not promoted to a
complete junction response because the source-free \(W_h\) mode changes
\(\delta Q_{\mu\nu}\).

## Action equation and momentum constraint

The P1 shift Hessian inherited from v6.16 has the local density

\[
 {\,\kappa_1\over2}N\sqrt{|\gamma|}\,N^{-2}
 \left[
 (D_\mu D_\nu W)^2-(\Box_4W)^2
 \right].
\]

On the Einstein M4 background
\({\rm Ric}_{\mu\nu}=3X_c h_{\mu\nu}\), the commutator fixes the
action-normalized scalar equation

\[
 {3\kappa_1X_c\over N_0a_0(t)^2}\Box_4W=0.
\]

The full radial momentum density is

\[
 {\cal M}_\mu
 =-{3\kappa_1X_c\over N_0a_0(t)^2}D_\mu W.
\]

Consequently

\[
 -D^\mu{\cal M}_\mu
 ={3\kappa_1X_c\over N_0a_0(t)^2}\Box_4W,
\]

so the action equation has exactly the normalization of the divergence of
the momentum constraint.

For static spatial harmonics, the same commutator reduces to

\[
 \widehat K_\Sigma={2\over a_S^2}\Delta_{S^3},
\qquad
 K_\ell=-{2\ell(\ell+2)\over a_S^4},
\]

recovering v6.18 and its particular coefficient.

The action and momentum equations do not have identical kernels in the
homogeneous Lorentzian scalar-potential representation.  The action permits
\(\dot W=C_1/a_4^3\); the momentum equation requires \(\dot W=0\).
Equating the kernels requires an additional scalar-shift domain or state
condition.  None is stored.

## Endpoint trace

The gauge-invariant endpoint combination is

\[
 {\cal S}_\Sigma
 =B+N_0^2\zeta-a_0^2\partial_\rho E.
\]

In the normalized fixed-\(t\) chart this is the corresponding
\(\partial_tE\) form with the radial conversion included in the potential
normalization.

In fixed-endpoint gauge,

\[
 {\cal S}_\Sigma
 =-cq(u)+W_h(u).
\]

A moving-coordinate representative transforms

\[
 B\mapsto B-N_0^2\xi^\rho-a_0^2\partial_\rho L,\quad
 \zeta\mapsto\zeta+\xi^t,\quad
 E\mapsto E-L,
\]

and gives the same value.  Fixed and moving descriptions therefore agree.
The unresolved \(W_h\) is gauge invariant; it is a threading state mode, not
a physical embedding mode.

## B1 and normal-support stop

The direct particular threading pieces enter the four scalar junction
projections as follows:

- temporal: \(-3(\tau\chi_1/4)H_4\dot q\);
- scalar momentum: zero for \(q=q(u)\);
- spatial trace:
  \((\tau\chi_1/4)(\ddot q+2H_4\dot q)\);
- scalar traceless-longitudinal: zero for \(q=q(u)\).

The four projections still have two Ward dependencies and two expected
independent combinations.  But

\[
 \delta Q_{\mu\nu}[W_h]
 ={1\over N_0}
 \left[-D_\mu D_\nu W_h+h_{\mu\nu}\Box_4W_h\right]
 =-{1\over N_0}D_\mu D_\nu W_h
\]

is nonzero for the \(C_1\) mode.  Therefore the complete two equations,
their rank, and their compatibility cannot be assigned without choosing the
missing domain/state datum.  Matcher elimination remains algebraic.

The diagnostic residual remains

\[
 R_\perp
 ={1\over\sqrt{|h|}}
 \delta_\zeta^{\rm diag}S_{\rm total}\big|_{\zeta=0}.
\]

Its stored algebraic coefficient is \(c_0=0\).  The coefficient of
\(D_0D_0q\), and the equivalent \(\Box_4q\) and \(H_4\dot q\) coefficients,
cannot be made unique because \(D_0D_0W_h\neq0\) while
\(\Box_4W_h=0\).  The two-equation B1 and Noether dependency ranks must
therefore remain unevaluated.

## Hindsight ledger

Validated:

- the closed-dS4 Hessian and \(\Box_4\) identities;
- the local particular threading coefficient;
- exact action/divergence-of-momentum normalization;
- fixed/moving endpoint invariance;
- the direct \(\delta K\) and \(\delta Q\) threading pieces.

Invalidated:

- treating spatial homogeneity as four-dimensional constancy;
- silently extending \(C_\Sigma=0\) to the \(C_1\) Lorentzian mode;
- treating the local particular solution as the unique action response.

Still active:

- derive an action-selected Lorentzian scalar-shift domain that eliminates
  or retains the \(C_1/a_4^3\) mode, then complete the two B1 equations and
  \(R_\perp\).

## Verdicts

```text
BHSM_HOMOGENEOUS_THREADING_RESPONSE_BLOCKED_BY_UNSTORED_LORENTZIAN_STATE
BHSM_ENDPOINT_TRACE_RESPONSE_BLOCKED_BY_UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE
BHSM_SCALAR_B1_TWO_EQUATION_CLOSURE_BLOCKED_BY_UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE
BHSM_NORMAL_SUPPORT_RESIDUAL_D2Q_BLOCKED_BY_UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE
BHSM_SUPPORT_DOMAIN_DECISION_BLOCKED_BY_UNFIXED_SOURCE_FREE_HOMOGENEOUS_LORENTZIAN_THREADING_MODE
BHSM_DYNAMICAL_EMBEDDING_DOMAIN_NOT_REACHED_BECAUSE_NECESSITY_NOT_PROVEN
BHSM_FOLD_LOCAL_SCALAR_OPERATOR_REOPENING_BLOCKED_BY_UNDECIDED_SUPPORT_DOMAIN
BHSM_FOLD_SCHUR_REDUCTION_BLOCKED_BY_UNDECIDED_SUPPORT_DOMAIN
BHSM_FOLD_KINETIC_SIGN_REMAINS_UNRESOLVED_BY_UNDECIDED_SUPPORT_DOMAIN
```

No measured input, fitted coefficient, new primitive, action, scale, corner
term, arbitrary boundary condition, arbitrary Lorentzian state, local
\(X_{\rm FRW}(x)\) field, scalar-curvature inverse, chat-only candidate,
kinetic number, physical mass, or stability claim is introduced.
