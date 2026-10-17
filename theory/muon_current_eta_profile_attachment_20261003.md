# Daughter eta field and its current collar restriction

Start `1eb713fa12e26858c78913951b600643027714d5`, PR #465,
`codex/muon-parent-maxwell-density-review`. Scientific reference remains
`524ed90689bd5923c249bba2e699abf627e703cd`.

**The eta field identity is resolved at the adopted effective-action scope.**
The normal eta field is the outgoing child's eta field restricted to a
compatible collar. The earlier checkpoint's claim that an additional scalar
identification was absent was too strong: v15.76/v15.82 explicitly apply the
adopted v14.45 mode to `cap_fields['f']`. Their spatial-slice measure does not
automatically supply the current collar measure, but this geometric limitation
does not create another physical scalar profile.

Following the user's daughter-enclosure interpretation, the static preon
texture is incoming provenance. It is neither copied nor deformed into the
muon's wall profile. No new decay/channel selection gate, profile, common-A
coupling, normalization, state or boundary law is introduced.

## Outgoing event-to-child rule

Historical v15.57 `full_reconstruction_operator` specifies
`R_s(I_star)=z_star`: a post-event v15.46 child followed by the v15.51
constraint projection. It reconstructs outgoing data instead of carrying an
incoming static metric/profile through the firewall. The outgoing cap has

\[
 \eta_{\rm out}=(\cos\chi\,u,\sin\chi\,v),\quad f_{\rm out}=\chi,
 \quad f(0)=0,\quad f(L)=\pi/4,\quad\sigma(L)=0.
\]

v15.51 enforces `q1=q2=q1_dot=q2_dot=0` in the eta-coordinate gauge.
Current v15.81 retains `f=chi`, including the shift term `f_normal=-beta/N`
in X_eta. A coordinate-fixed scalar does not have zero covariant derivatives.

For the **current** C2 arm, the retained producer is
`aether_full_reset_action_jacobian.full_reset_residual`: 57 rows contain
event/child constraints, the ordered-event equation, three configuration
traces plus an attachment match, and two canonical child-minus-event
momentum rows. The geometry state has 98 entries; the launch chart consumes
its outgoing fixed-descriptor field and does not choose a new reset member.
The historical constant reset is provenance, not a replacement for that
current relation or the saved history. None of these production solves is rerun.

AE2 separately fixes `Gamma0_child=U_R Gamma0_event` and
`Gamma1_child=-U_R Gamma1_event` on the squared domain, with no independent
spinor contact. These are spinor trace/flux maps, not an eta profile or a
zero exterior response. Historical `A_SM=H_SM=Psi=0` names classical matter
fluctuations; eta is nonzero, and the resolved common-A prescription remains.

The decay/collision module integrates **supplied** masses and amplitudes.
It does not generate daughter fields. Hence the actual event/current-child
rules above are used, rather than a phase-space readout or static texture.
The chosen canonical C2 history is not promoted to a solved physical muon state.

## Same-field action identity

v15.39 defines one physical eta scalar f. v15.76 `shell_geometry` takes
the cap's f and explicitly inserts it in the v14.45 zero mode; v15.82
`regular_einstein_cartan_kernel` repeats that identification. On a compatible
oriented collar X(s,y) the same field therefore obeys

\[
 f_{\eta,c}=f_{\rm child}\circ X=\rho(X)/2,\qquad
 \boxed{m_{\eta,c}=-\tfrac12\rho_s\cot(\rho/2)}.               \tag{1}
\]

This is an action-producer field identification followed by restriction,
not a coordinate change equating distinct scalar reductions. The normal
action and mode are

\[
 D_{\perp,\epsilon}=i\epsilon\Gamma_\perp
 [\partial_s+\tfrac12\partial_s\log J_c+m_{\eta,c}],\quad
 u_c=N_cJ_c^{-1/2}\sin(f_{\rm child}\circ X),\quad
 N_c^{-2}=\int\sin^2(f_{\rm child}\circ X)ds.                  \tag{2}
\]

Unit normalization and the normal zero-mode identity do not select f.
Here the outgoing action field does. No sech, static BVP, trigonometric
rescaling or equality of normalized material/fermion densities is used.
The complete normal integration domain in (2) still requires realization.

Differentiation stays in b: `delta_b Omega=T_b Y_A(-iQ)`, `beta=T_b b`,
`A_Q=sqrt(2)beta`. Differentiate the SAME outgoing field, X, J, transport and
normalization where their source dependence is owned. No action-index 2/3
vertex factor, independent source-state choices or zero assignments for
uncomputed induced derivatives are made.

## Actual finite collar/profile evaluation

The saved Lorentz metric is
`nu^2 d_tau^2-C^2(d_rho+zeta d_tau)^2-r^2 dOmega3^2`.
One inward spacelike normal geodesic is integrated from an interior wall
base time using `X_ss+Gamma[X_s,X_s]=0`, `rho=pi/2`, `tau_s=0`,
`rho_s=-1/C_wall`. A base-time sample is a coordinate point, not a new
physical state or endpoint condition. The full time/shift terms are retained.
No metric sign is flipped or outside-cache extrapolation permitted.

The metric is the saved 48-time by 65-radial bilinear nodal reconstruction.
The radial/time subsystem is closed at fixed angular coordinates. Its rho(s)
is used immediately in (1) to evaluate a nonzero finite m_eta(s). The saved
`daughter_collar_profile.npz` contains the curve, tangent, f, f_s, m and
`g(X_s,X_s)`; `result.json` records endpoints, covered metric cells and
unit-normal residual. This is beyond the initial jet, which is not rerun.

In the executed nodal curve, s runs from 0 to 0.001 at wall-base proper
time 0.00009585390525338264. The covered rho interval is
`[1.5697543648492294,1.5707963267948966]`; m_eta changes from
`0.5209738896552569` to `0.5215383505509632` in the inherited geometric
inverse-length convention. This coefficient is not the muon pole mass.
The maximum observed `abs(g(X_s,X_s)+1)` is `7.127631818093505e-14`.
The saved source support envelope is approximately `[0.58905,0.98175]`,
so it lies outside this local patch. There were 33 profile samples, one
curve integration and 689 RHS evaluations; no parameter sweep was run.

The short curve does **not** cover the saved compact source support. It is
also not yet a full-rank collar chart: transverse Jacobi/pairing data, full
normal integral, spin/carrier transport and domain coverage remain to be
evaluated. Compatible patches may be needed when a single Gaussian chart
loses rank. A unit-normal residual is not a chart-rank theorem.

The tail cache starts at the artificial step1222 cut. If continuation reaches
that edge it must use the inherited physical prefix, not extrapolate the tail
or impose a new boundary there. The old fixed-rho certificate rejects that
normal-foliation shortcut, not every proper collar. The first remaining
dependency is now geometric/transport implementation, not an unselected
physical eta field. The past-prefix and canonical-stop domain is preserved.

## Source-overlap cotangent

For the actual full collar define `I=integral sin^2 f ds`, `v=sin f/sqrt(I)`,
`u=J^-1/2 v`, `phi_ij=(U54 e_i)^dagger p_j(X)` and
`T_ij(y)=integral J u^* phi_ij ds`. The saved source trials are
`p_Ak=(T_b chi_hat/r)Xi_A e_k`, with all 64 outputs and connected n1/n3
retained. The consumer is `M4 B_required=T` in the owned pairing.

For an owned profile tangent h, at fixed X/J/U let `k=h cot f`. Exact
normalization differentiation gives

\[
 \delta u=u(k-\langle k\rangle_{|v|^2}),\quad\delta m=-\partial_s k,
 \quad\delta T_{ij}=\int[J u^*\phi_{ij}-|v|^2T_{ij}]k\,ds.      \tag{3}
\]

The explicit kernel against h is
`sqrt(J)cos(f)phi/sqrt(I)-sin(f)cos(f)T/I`. Smooth compact support and finite
positive norm justify differentiating this overlap; no regulator/heat/soft
limit interchange is asserted. The bound
`|delta T|<=||(I-|u><u|)phi||_J sqrt(Var_|v|^2(k))` is conditional and exact,
not a numerical anomaly uncertainty. Algebraic profile deformations do not
represent freely selectable physical daughter profiles or alternate saddles.

The earlier working draft explored underdetermination before the concrete
cap-mode producers were recovered. Its overlap derivative remains valid;
its missing-scalar claim is superseded. The explicitly labelled draft is
preserved in Downloads and is not the current checkpoint.

## Verification, errors and one next operand

Seven exact identities cover the normal action, profile/mode derivatives,
normalization term and conditional probability-pullback Jacobians. Three
targeted algebra tests pass. The first run had two passes and an equivalent
trigonometric expression not reduced to zero; a sine rewrite reduced it
exactly, and only that failed check was rerun. This did not change the equation.
The cached-curve test validates (1), unit-normal residual and cache containment
without repeating integration. The execution receipt reports actual outcomes.

Solver tolerances and norm residual are not rigorous absolute solution-error
bounds. Bilinear metric reconstruction and its interface derivatives, full
collar coverage, J/transport, source continuation, normalization and domain/
complement errors remain separate and unevaluated. H uncertainty is preserved;
H is not substituted for metric derivatives or the affine logR slope.

All older pairings, H-corrected arrays, contact/nodal certificates, trial
conormal, common-A actions, frames and frozen local contributions are preserved,
not replayed. T, B54, interface K/M, stationary exterior response, heat contact
and physical a_mu/g_mu remain null. Native physical transfer directions: zero.
No local contribution is refit or added twice.

Replay: `python scripts/replay_muon_eta_profile_attachment.py --output <fresh-directory>`.
The standalone Downloads copy accepts `--repository`. Producer functions are
AST-read, not executed. The packet records source/input hashes, branch/revision/
diff, curve data, equation checks, frozen uncertainty convention and native ledger.

**One next operand:** the same-domain collar pullback **on the saved source
support**, with its J and Spin x SM transport and inherited-prefix/patch
continuation. Its equations are normal geodesic/Jacobi evolution, the same-
connection parallel equation and the owned pairing pullback. Its consumer
is `T=<W_eta e_i,p_j>_5`, then `M4 B_required=T` and coupled exterior K/M.
The daughter eta field to use there is now fixed by (1); no profile choice
is pending.
