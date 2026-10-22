# Action-native R1 matter/radiation derivation checkpoint

Status: candidate action and numerical implementation saved; NOT a certified closure.
The held-out GP local-constraint comparison currently fails. No manuscript or
observational claim is changed. The original owner is unchanged.

## Conventions and owner

Units H0=Mpl=1; cosmic-time dot; N=ln(a) only for integration.
One real harmonic is normalized by integral sqrt(gamma) Q^2=1 on closed S3.
D^2 Q=-8K Q, (D^2+3K)Q=-5K Q. Set kappa=K/a^2,
b=8 kappa, s=5 kappa. ADM: lapse 1+alpha, covariant shift N_i=D_i chi,
h_ij=a^2 exp(2 zeta) gamma_ij; scalar-field unitary gauge.
Theta and Sigma are imported from code/closed_horndeski_n2.py without edits.
The fixed background uses the V0 already in preregistration/prediction_manifest.json;
the new module does NOT call shoot_v0().

The gravity/scalar owner Lagrangian per a^3 per harmonic is

    L_g = -3 zdot^2 + s z^2 + Sigma alpha^2
          +2 b Theta alpha chi -2 b zdot chi +6 Theta alpha zdot
          +2 s alpha z -b kappa chi^2.

Its two variations recover the supplied vacuum constraints. This is the
existing Akama--Kobayashi quadratic kernel, not a replacement or GP repair.
Primary reference: https://arxiv.org/abs/1810.01863, Eqs.35,44--48.

## Fluid convention and background-tadpole bookkeeping

Each isentropic irrotational scalar perfect fluid has Schutz--Sorkin action

    S_I = - integral d4x [ sqrt(-g) rho_I(n_I) + J_I^mu partial_mu ell_I ],
    n = sqrt(-g_mu_nu J^mu J^nu)/sqrt(-g),
    partial_mu ell = mu u_mu, mu = d rho/dn,
    rho(n) proportional to n^(1+w), c_s^2=w,
    ell_background_dot=-mu, delta ell=mu v.

Dust w=0 exactly; radiation w=1/3. No small positive dust sound speed is used.
rho_m=3 Omega_m0 a^-3, rho_r=3 Omega_r0 a^-4, h_I=rho_I+p_I.
D_I=delta J_I^0/Jbar_I^0=delta rho_I/h_I+3 zeta.
The spatial currents are eliminated algebraically. After integrating the
delta J^0 delta ell_dot term by parts, the canonical term is a^3 h v Ddot.
The background chemical-potential derivative is included by that integration
by parts; a^3 h has logarithmic time derivative -3w H.

Before combining gravity and fluid background equations, the fluid quadratic
terms contain +9p zeta^2/2+3p alpha zeta-h alpha D. The gravity sector expanded
on the TOTAL background differs from its vacuum-equation-simplified expression
by -9p_total zeta^2/2+3rho_total alpha zeta. These terms combine into
-h alpha(D-3zeta); no matter background term is simply discarded.

An explicit check of that bookkeeping starts from the unitary cubic-KGB ADM
action density

    N sqrt(h) [ (R3+Kij Kij-Kextr^2)/2
                + v_background^2/(2N^2)-V
                + 2 v_background^3 Kextr/(3 Lambda^3 N^3) ].

Its homogeneous part divided by a^3 is
-3H^2/N+v_background^2/(2N)-NV+2H v_background^3/(Lambda^3 N^3)+3kappa N.
The lapse derivative uses the total Friedmann equation; the zeta^2 term uses
the total pressure equation. This expansion is derived analytically here;
an independent symbolic expansion from the untruncated ADM action is still
a useful outstanding check, especially given the GP mismatch.

The combined candidate fluid contribution per a^3 is

    L_I = h_I [ v_I Ddot_I - b v_I^2/2 + b chi v_I
                - w_I (D_I-3zeta)^2/2 - alpha(D_I-3zeta) ].

Reference for the density-variable dust-regular action convention:
https://arxiv.org/abs/1609.03599, Sec.III. Curved harmonic specialization,
background bookkeeping and the following finite matrices are the current
derivation, not a claim that the reference certifies this implementation.

## Complete finite Hessian

Ordering: x=(zeta,D_m,D_r), u=(alpha,chi,v_m,v_r), h=h_m+h_r.

    L2/a^3 = 1/2 u^T A u + u^T(B xdot+D x)
             +1/2 xdot^T K0 xdot +1/2 x^T E x.

    A = [[2Sigma, 2bTheta, 0, 0],
         [2bTheta, -2b kappa, b h_m, b h_r],
         [0, b h_m, -b h_m, 0],
         [0, b h_r, 0, -b h_r]]

    B = [[6Theta,0,0],[-2b,0,0],[0,h_m,0],[0,0,h_r]]
    D = [[2s+3h,-h_m,-h_r],[0,0,0],[0,0,0],[0,0,0]]
    K0 = diag(-6,0,0)
    E = diag(2s,0,0) - sum_I h_I w_I d_I d_I^T,
    d_m=(-3,1,0), d_r=(-3,0,1).

The complete Hessian, ordering (u,xdot,x), is

    [[A,B,D],[B^T,K0,0],[D^T,0,E]].

Mixed lapse-density entries -h_I, lapse-zeta 3h_I, shift-velocity b h_I and
velocity-density-rate h_I all come from the same action above. There is no
separate q2 J_m/r coupling. The transpose blocks exhibit reciprocity in this
declared integration-by-parts convention. Perturbations vanish at temporal
variation endpoints; S3 has no spatial boundary.

Eliminating v_I first gives v_I=chi+Ddot_I/b and the metric block

    A_metric = [[2Sigma,2bTheta],[2bTheta,b(h-2kappa)]].

This is an alternative sequential Schur calculation to verify against the
implemented simultaneous four-auxiliary elimination, not a new equation.

## Exact reduction and evolution

    J=B xdot+D x;  u_*=-A^-1 J.
    Lred/a^3=1/2 [xdot^T K0 xdot+x^T E x-J^T A^-1 J]
             =1/2 xdot^T M xdot+xdot^T L x+1/2 x^T V x,
    M=K0-B^T A^-1 B, L=-B^T A^-1 D, V=E-D^T A^-1 D.

Canonical p=a^3(M xdot+L x), with exact equations

    xdot=M^-1(p/a^3-L x),
    pdot=a^3(L^T xdot+V x).

The implementation integrates this six-dimensional Hamiltonian system and
its full 6x6 fundamental matrix. It never evolves alpha/chi as independent
coordinates, and never projects an evolved solution onto constraints.
Reconstruction is algebraic evaluation of already-eliminated variables.

## Recovery identities and initial conditions

When the fluid sectors are REMOVED, retain x=zeta and u=(alpha,chi), so no
zero-density auxiliary with a zero Hessian row is retained. The expected
identities are M=2G_S,2, L=2s A_AK/Theta,
V=2s(1-A_AK kappa/Theta^2), A_AK=5/(8+Sigma/Theta^2).
They imply (Ldot+3HL-V)/M=s F_S,2/G_S,2 and the existing vacuum equation.
These identities still need an automated check. Instantaneous zero density
and momentum SOURCES recover the original constraints. Keeping nonzero
background fluids while forcing all their responses to remain zero is not
an invariant solution subspace, and must not be mislabeled a vacuum gate.

Fluid Euler-Lagrange equations are

    Ddot_I=b(v_I-chi),
    vdot_I=3w_I H v_I-alpha-w_I(D_I-3zeta).

Candidate dictionary: Phi=alpha+chidot, Psi=-zeta-Hchi, pi=-chi,
v_Newtonian=v_ADM-chi,
delta_Newtonian=(1+w)(D-3zeta-3Hchi)=(1+w)(D+3Psi).
It gives the required continuity/Euler conventions algebraically (Phi_dot
replaces Psi_dot only when the separately checked no-slip identity holds).
The velocity, density and pi conventions remain priority suspects for the
FAILED numerical comparison to existing GP local equations; do not assume
that a small no-slip residual establishes full compatibility.

Two seed columns use q2=zeta_anchor and Pi2=2 a_anchor^3 G_S,2 zdot_anchor,
with zero ADM fluid density and velocity at z=2.1. Thus D_I=3zeta and
Ddot_I=-b chi initially; constraints determine alpha and chi, and the
canonical momenta are computed from the reduced action. This is an explicit
unfitted initial-condition prescription, NOT a derivation that primordial
fluid modes are absent or that an observational normalization is unique.
The former (zeta,zeta_N) coordinates convert by
diag(1,2 a_anchor^3 G_S,2 H_anchor). No Pantheon state has been propagated.

## Evidence and limitations at stop

See artifacts/R1_ACTION_NATIVE_MATTER_BACKREACTION_V1.json for all 401 scan
points, auxiliary determinant/condition numbers, kinetic eigenvalues,
seven full propagator snapshots and two seed columns. No new test file or
test suite has yet been run. Positive sampled eigenvalues are candidate
evidence, not an interval proof or a gradient-stability theorem.

The GP prior provided by the user (2.16e-9 differentiated-constraint closure,
trace discrepancy -6kappa(pidot+Hpi), independent scalar Noether defect)
is accepted as prior evidence, not rederived here. The current checkout
does not contain the detailed later localization artifacts. Do not patch
the GP scalar, force a match or update manuscript claims.
