# Physical current connection review and implementation handoff

Prepared 2026-10-18 by the read-only scientific review subagent. No repository
source, Git state, scientific array, or original package was changed by this
review. This document is outside the live repository. The parent agent is the
sole implementation writer.

## Concrete new application that is justified

The latest fixed-geometry field-to-spin package already evaluates the actual
Hamiltonian insertions V_c(t), c=0..165, and their interaction-picture integrals
J_c. It can now be used to evaluate an additional **finite lepton matter-current
weak covector and its retarded susceptibility**, keeping its initial one-body
occupation/reference operator unselected. This is a genuine action-current
application. It is not a physical collider source, a full reference construction,
or a physical field solution.

Use the same two arms separately and the same canonical initial30 space, with
all84 reached modes as intermediate states. Do not add the direct magnetic
insertion again: it already occurs in c=160..165. The first32 coordinates are
scalar canonical initial variations; the last134 are wall/magnetic variations.
The 574 classical input coordinates are (Maxwell408,Higgs32,wall134).

For E: C^30 -> C^84 the saved initial isometry, define

    V_c^I(t) = U(t)^dagger V_c(t) U(t),
    J_c(t)   = integral_lo^t V_c^I(s) ds,
    L_c      = -E^dagger J_c(tf) E.

The saved J_gauge+J_Higgs already supplies all columns needed for L_c; use the
initial30 rows of its 84x30 map. The L_c are finite Hermitian **operators dual to
the response coordinates**, not spin readouts. For an explicitly supplied finite
one-body occupation matrix N on that initial space,

    ell_c[N] = Tr(N L_c) = -Tr(N E^dagger J_c E).

N is not automatically a trace-one one-particle density. The absolute continuum
occupation/reference cannot be replaced by this finite matrix. An admitted
relative excitation Delta N can be used for a relative source. No N=0 or N=I/2
is selected as physical data. The exact prepared electron/positron pair lives in
the full18 representation with its physical U/V sections; the retained middle6
sector is not that prepared state.

## Original canonical normalization, with no guessed cap factor

The strongest live normalization owner is
`src/bhsm/interface/muon_charged_current_fermi_reduction.py`,
`transported_fermi_template`, lines 19-27 and 45-49. Exact owner statements:

    chi_hat=R4^(3/2)psi/V, angular carrier=1/sqrt(V), V=2pi^2.
    Raw intrinsic S4 is divided by V^2 in the common cap action.
    This is the declared unit canonical-fermion action convention.

The independently used
`muon_static_coupled_charged_current.static_coupled_charged_current` states that
the physical constant angular function is 1/sqrt(V), its current integral is
V*(1/sqrt(V))^2=1, and no additional cap factor is inserted in that normalized
fermion current.

For general normalized Haar harmonics phi, let Phi=phi/sqrt(V). Then
integral_dOmega Phi^dagger Phi=I. Write chi_hat=Phi a. Substitution into
S_l,common=S_l,raw/V^2 gives

    psi = sqrt(V) R4^(-3/2) phi a,
    S_l,common = integral dt a^dagger(i partial_t-h_t)a.

The standalone normalized-Haar operator matrices are exactly the matrices in
this coefficient a chart. Thus no V, V^2, Maxwell-to-cap conversion, electric
charge, or family multiplicity is appended to -J_c. This derivation distinguishes
the raw intrinsic field psi from its normalized canonical coefficient a; merely
equating two fields named chi in different reports would be unsafe.

The existing classical response uses S_hat=T S_common, tau=(t-tlo)/T and
T=1e-5 in action coordinate-time units. Its matching matter covectors are

    L_hat_c = T L_c.

J_c already contains dt=T d tau. The Athat_t=T A_t coordinate conversion 1/T is
already included in `OpenFieldPath.coefficients`; it must not be inserted again.
The extra T above is solely the common action rescaling needed to join the
classical W_classical maps. The physical time unit and common GeV calibration
remain unestablished by this calculation.

## Endpoint bookkeeping: do not differentiate an on-shell zero into no current

Use the symmetrized unit canonical action

    S_l = integral dt [i/2(a^dagger adot-adot^dagger a)-a^dagger h_t a].

Its explicit field variation, at held field sections, is -integral a^dagger
delta h_t a. Its temporal conormal is

    theta_l(delta a)=i/2(a^dagger delta a-delta a^dagger a).

For fixed initial coefficient a0 and delta U(tf)=-i U(tf) J_c,

    theta_l,final(delta_c a)=a0^dagger J_c a0,
    theta_l,initial=0,
    explicit bulk field variation=-a0^dagger J_c a0.

Their sum vanishes along the same exact propagated solution. This is the correct
on-shell first-variation/Green identity, NOT a vanishing Maxwell/Higgs matter
source. The bulk field equation differentiates the action with respect to its
bosonic field while holding the fermion section independent. The separate
fermion endpoint equation uses its temporal conormal. Store L_hat=-T J and
Q_hat,final=+T J separately; do not add and erase the field source, and do not
mislabel the endpoint phase as a second independent current. Moving initial
sections/density require both initial and final temporal terms.

The original direct intrinsic matter action has no gauge-rate vertex. That fact
does not set the classical wall momentum, radial flux, native rate terms, or
quantum Cauchy endpoint conormal to zero.

## Retarded susceptibility, without selecting a density

Choose one actual existing source direction d, for example a unit c=160 magnetic
profile. In the declared affine linearized-field family h_epsilon=h0+epsilon V_d,
the insertion V_c is explicitly held fixed, so V_cd=0 in THIS family only.

    R_cd = D_d L_c
         = -E^dagger integral dt i[J_d(t),V_c^I(t)] E.

This retarded current susceptibility is a generally nonsymmetric causal response,
not the Hessian of a scalar functional with both temporal endpoints fixed. Use
all84 intermediate modes before projecting the result to initial30. Projecting
each insertion prematurely to30 can delete the n2 return channels. For two n1
insertions between initial n<=1 states the reached intermediate n<=2 space is
sufficient; finite epsilon higher-order evolution still has its stated cutoff.

In a genuinely nonlinear physical source chart the formula additionally has

    -E^dagger integral dt U^dagger V_cd U E,

plus moving E, pairing, source limits, geometry, domain, and state terms. The
neutral Higgs-axis source has its already established field-dependent contact;
an affine c=160 control does not supply that full physical derivative. For moving
occupation, D ell_c = Tr(N R_cd)+Tr((D_d N) L_c). None of the missing terms is set
to zero in the physical equation.

Independent verification should integrate U_epsilon from the original h0+epsilon
V_d field path and quadrature-evaluate

    L_c(epsilon)=-E^dagger integral U_epsilon^dagger V_c U_epsilon E dt.

Compare matrix derivatives (not a chosen state's scalar expectation) at three
shrinking central-difference steps. Include raw absolute/relative differences,
quadrature-order comparison, U unitarity, Hermiticity and endpoint/bulk Green
balance. A stronger independent point-Hamiltonian insertion is available via
`independently_projected_insertion`; at least selected current contractions can
check the normalization/sign against it. This finite affine-source test must
not be called the complete physical outgoing derivative admission.

## Consumption in the 574-coordinate open equation

**Causal scalar-feedback correction to this paragraph:** the bare -J_total is
the current pulled back on the saved forward test responses. It is not by itself
the complete reduced causal wall force after eliminating scalar feedback. The
actual current-driven scalar return and its symplectic endpoint correction are
derived and implemented in the following section. In particular, merely setting
W_classical eta+Tr(N L_hat_wall)=0 would still omit that causal endpoint correction
and every other uncompleted sector.

Define P eta=eta[408:] for eta in R^574. The finite matter covector operators on
that chart are

    L574 = P^T L_hat166,
    R574,d = P^T (T R166,d).

The 408 leading zeros are the established fixed-geometry zero-wall-trace
intrinsic vertex statement only. They do not delete Maxwell initial-data effects
through physical feedback. On the 134 wall-test rows use the last134 entries:

    R_wall = W_classical eta
             + Tr(N L_hat_wall)
             + true interface/geometry/exterior/native/reference/preparation terms.

This equation now consumes an actual quantum matter-current summand. It is not
closed by setting the remaining terms or N to zero. For a source perturbation,
the operator R_hat_wall,d supplies its declared finite affine causal derivative.
The scalar-initial32 covectors and the quantum Cauchy endpoint covectors must be
retained with their actual matching rows rather than silently discarded.

## New causal current-to-Higgs-to-wall application

Draft implementation files were saved outside the repository at
`handoff/review/causal_matter_wall.py` and
`handoff/review/run_causal_matter_wall.py`. The application has NOT been run; the
two files have only been syntax-parsed without importing their modules. The
parent must first publish Phase A, then review/copy/run the new application.

At each of the original four nodes, form the actual Higgs current operator on
initial30, with all84 intermediate components retained:

    j_H,a(tau)=-T^2 N_lapse sum_r J_H[r,a]
                     E^dagger U^dagger V_scalar,r U E.

Here H_original=J_H h_conditioned. These are the **dual** J_H^T contacts, not an
assumed unit scalar normalization. This action has no H-rate vertex. The direct
gauge source uses -T^2 E^dagger U^dagger(partial_g h_t)UE and its actual G wall
profiles; its At 1/T is included once.

For the current-forced scalar correction z_l=(h_l,p_l), solve only

    z_l'=F z_l+(0,j_H),  delta z_l(0)=0.

The held-initial correction is a response derivative at fixed existing scalar
initial state. It is not a choice of physical zero scalar initial data. Reuse
the saved F_j and factor the128-by128 four-stage matrix with900 operator-entry
right sides. No classical coefficient, gauge response, or old scalar response
column is regenerated. The draft also independently assembles/solves the original
192-dimensional DAE in (h16,v16,p16) per node, enforcing

    h_i=sum_j a_ij v_j,
    p_i=M_i v_i+B_i^T h_i,
    p_i=sum_j a_ij(B_j v_j+K_j h_j+j_H,j).

At zero gauge correction the original scalar action supplies

    ell_g=K_gh h_l+B_gh h_l',
    p_g=B_hg^T h_l+M_gh h_l',
    W_return=sum_i b_i(G_i^T ell_g,i+G_i'^T p_g,i).

All actual saved blocks are consumed even if some vanish structurally. The
separate temporal gauge endpoint [G^T p_g] is retained. The additional causal
wall load is W_direct+W_return, a134x30x30 operator-valued covector. Its scalar
initial32 companions are separate pullbacks; they are not 32 extra wall tests.

For saved classical test response (h_c,p_c), discrete action reciprocity gives

    W_return,c = sum_i b_i h_c,i^T j_H,i
                   +[h_l^T p_c-h_c^T p_l]_lo^hi.

Thus the causal load equals the pulled current PLUS the displayed scalar
symplectic endpoint. Omitting that endpoint is an explicit negative control.
It is generally nonzero: no future endpoint equation was imposed. The stage4
identity must use the SAME Gauss nodes and weights on both sides; saved spin J
used12-node integration. The draft records4-vs12 and12-vs16 discrepancies and
compares the saved12-node J without silently replacing its time rule.

Source/current operators remain Hermitian; no density is contracted. If later
an admitted occupation/reference is supplied, its finite contraction gives the
additional forcing and causal wall load. This does not assert that linear
addition at the old base solves the nonlinear self-consistent mean equation.
Source-dependent lepton response, state and domain jets still belong to the
complete derivative. The separately described Kubo derivative supplies another
finite coefficient and must not replace those total derivatives.

The draft reports absolute maximum-entry and Frobenius norms in the declared
conditioned/time-scaled finite coordinates, original scalar H and momentum
restorations, all new canonical/DAE residuals, endpoint identity/omission controls,
Hermiticity, propagator reuse/unitarity and selected independent point-Hamiltonian
current contractions. These are scoped numerical checks. They are not the
original physical all226/source-domain norms or the physical2e-10 admission.

## Cauchy/reference terms and exact unresolved correspondences

At fixed homogeneous geometry the normalized harmonic chart has G=I and E fixed;
that is the declared partial calculation. For a moving Cauchy Gram G>0, use
S=G^(1/2), with S D S+(D S)S=D G. The transformed generator is
h_hat=S h S^(-1)+i (partial_t S) S^(-1), with every derivative and independently
continued left leaf on analytic source charts. Freezing normalized packet
coefficients while G changes is not a physical normalization derivative.

The live covariance convention is C_plus=<a a^dagger>, N=I-C_plus, recorded in
`theory/muon_birth_covariance_sensitivity_20261008.md`. Thus relative current
differences obey Delta ell=-Tr(Delta N J)=+Tr(Delta C_plus J). Do not confuse C_plus
with an occupied density or add an arbitrary Nambu factor. Absolute native
currents additionally require the real microscopic/domain/subtraction owner.

It is not established that a reference selection is required for the final
physical birth observable. The correct state-independence decision needs the
complete oriented same-domain kernel

    K_complete=K_event+U_geo^dagger K_child,oriented U_geo
                 +K_return/source/constraint/domain.

Only its admissible CAR-odd charge/family projection decides whether reference
moments survive. `muon_birth_covariance_sensitivity.py` owns that exact quotient.
The new finite fixed-geometry L/R is one real summand, not K_complete; neither its
nonzero norm nor noncentrality proves physical reference dependence. Conversely,
retarded U alone cannot select a reference covariance: homogeneous changes C+X
leave G_R=-i theta U U^dagger unchanged.

The exact missing physical correspondences remain: actual action-normalized
collider electron/positron sections from the fixed adopted preparation; their
common constrained fields/unit/positive-frequency construction; collision
incidence to the two histories; the interaction-dependent two-collar graph and
its jets; exterior/native/normal-geometry completions and surviving reference
moments. None is an additional beam-control request. Do not glue the two arms
with an identity map. Do not infer physical impossibility from this scoped
unperformed correspondence.

## Reusable files and owner functions

Package root:
`C:/Users/carbe/Downloads/BHSM_CODEX_RESTART_20261018/extracted/BHSM_field_to_spin_response_20261018`.

- `replay_A/{side}_spin_response.npz`: J_gauge,J_Higgs,initial_isometry,final_unperturbed.
- `replay_A/{side}_joint_open_response.npz`: actual classical weak maps.
- `field_spin_connection.OpenFieldPath`: unchanged saved scalar response reconstruction;
  `coefficients`, `insertion`, `original_fields`: actual field-to-Hamiltonian inputs.
- `field_spin_connection.field_vertices`: exact 80 angular/fiber matrices.
- `dependencies/finite_time_response.evolve`: same h0 evolution; no field solve.
- `field_spin_connection.independently_projected_insertion`: independent local
  Hamiltonian/Haar projection for selected contractions.

Live original action owners in
`C:/Users/carbe/Downloads/BHSM_muon_parent_maxwell_worktree_20261001`:

- `src/bhsm/interface/muon_charged_current_fermi_reduction.py`:
  `transported_fermi_template` (canonical/common normalization).
- `src/bhsm/interface/muon_static_coupled_charged_current.py`:
  `static_coupled_charged_current` (physical angular normalization/no extra cap).
- `src/bhsm/interface/muon_native_dirac_hamiltonian.py`:
  `canonical_lepton_hamiltonian_maps` (actual field representation/generator).
- `audits/bhsm_collider_incoming_field_current.py`:
  `construct_action_packet_sections`, `validate_action_packet_Cauchy_Gram`,
  `apply_incoming_packet_current`, `original_material_Gauss_source` (real physical
  packet/current consumers, no chosen packet supplied by those functions).
- `src/bhsm/interface/muon_two_collar_weak_domain.py`:
  `two_collar_weak_domain_jets` (interaction-dependent graph, original duals).
- `src/bhsm/interface/muon_baton_zoo_original_validation.py`:
  `independent_original_maxwell_weak` (original action and canonical momenta),
  `compare_original_equation_direction` (five-part full physical derivative gate).

## Scope that must remain explicit

This new application is per the saved provisional histories, original finite
harmonic space, fixed geometry and declared affine field path. Density is an
operand, not zero. No Maxwell/Higgs coefficient or response solve needs rerunning.
Previous stricter Maxwell gauge-reconstruction failures, membrane finite-step
nonpass, inherited calibration and unenclosed continuum/time errors persist.
No physical 2e-10 admission, coupled correction, fresh physical Maxwell/all226
after-state, physical pole, a_mu, g_mu or total uncertainty follows.

NEXT_OPERAND: evaluate this actual finite current/susceptibility summand and its
separate endpoint conormals in the common 574-coordinate response, then derive
and consume the missing same-domain physical collision/interface/normal/native
and complete-reference terms. Do not solve W_classical eta=0 as closure.
