# AE3.2 current-C2 first-order Einstein--Cartan LR action

## Action decision

The coefficient-free first-order Einstein--Dirac completion already derived
in v15.75--v15.76 is formulated as the candidate
`BHSM-AE-3.2.0-CANDIDATE` and tested on current C2. This would be a change of
representative, not a second Einstein term:

```text
S_AE3.2 = FirstOrderLift_spin_connection[S_AE3.1],
S_AE3.2_reduced = S_AE3.1 + Gamma_EC.
```

Thus the Levi-Civita spin connection is replaced by the independent
first-order variable

```text
omega = omega_LeviCivita + C,
```

where the contorsion `C` is algebraic. The reset-generated current-C2
background, the AE2 spin x gauge reset domain, the intrinsic M4 Higgs term,
and the attached family/mode fibers are retained. No continuous coefficient
or elementary field is added. On the current symmetric zero-fermion
background `J_S=0`, so `Gamma_EC=0` and the background geometry's first
variation is unchanged.

## Exact Schur complement

The contorsion block is

```text
S_C = 1/2 <C,K_G5 Lambda(sigma) M_Clifford C> + <C,J_S>,
J_S^ABC = 1/4 bar(Psi) Gamma^[A Gamma^B Gamma^C] Psi.
```

Eliminating `C` gives

```text
Gamma_EC = -1/2 <J_S,(K_G5 Lambda M_Clifford)^(-1) J_S>.
```

The v15.76 Clifford and four-dimensional Fierz calculation fixes the scalar
LR coefficient without a new parameter:

```text
c_EC = 3/4,
G_EC(sigma) = (3/4)/(K_G5 [1-4 sigma^2]).
```

For every regular current-C2 interior point `|sigma|<1/2`, this kernel is
positive, finite, and even under the reciprocal reflection. It diverges at
the localization-support endpoints. A global weighted zero-mode
integrability theorem is not asserted here.
## Endpoint domain no-go

The retained round join and degree-one zero mode give, on the enclosed half,

```text
f=chi,
J=sin(2chi)^3,
u0=N J^(-1/2) sin(chi),
0<chi<=pi/4.
```

The mode is ordinary `L2(J dchi)` because its norm shape is

```text
integral_0^(pi/4) sin(chi)^2 dchi = pi/8-1/4 > 0.
```

At the collapse endpoint,

```text
sigma+1/2 = (16/(3pi)) chi^3 + O(chi^5),
Lambda = (64/(3pi)) chi^3 + O(chi^5),
J = 8 chi^3 + O(chi^5).
```

Therefore its EC quartic shape density is

```text
sin(chi)^4/(J Lambda)
  = (3pi/512) chi^(-2) + O(1),
```

and the cutoff form diverges as `(3pi/512)/epsilon` before the finite `N^4`
normalization factor. The retained zero mode is not in the reduced EC form
domain, and minimizing over contorsion is not bounded below on this source.

No counterterm, boundary condition, or mode deletion is inserted to hide the
failure. The global AE3.2 action promotion is withdrawn. What survives is the
exact local interior LR kernel and the endpoint obstruction.

## Channel attachment

The scalar Fierz product attaches to all retained LR channels:

```text
(bar Q_L u_R)(bar u_R Q_L),
(bar Q_L d_R)(bar d_R Q_L),
(bar L_L e_R)(bar e_R L_L),
(bar L_L nu_R)(bar nu_R L_L).
```

The last row remains an effective neutrino extension. On three families the
historical pairing multiplicities are `9,9,3,3`, totaling 24. The current
kernel acts as `I3` on family and therefore does not by itself generate a
family hierarchy or CKM mixing.

## What the HS transform does and does not establish

The attractive LR kernel has the exact algebraic Hubbard--Stratonovich
representation

```text
exp[+G_EC O_f^dagger O_f]
  proportional to
integral D H_f exp[-(H_f^dagger G_EC^(-1) H_f
                     - H_f O_f^dagger - H_f^dagger O_f)].
```

This produces a positive auxiliary quadratic block and a unit unnormalized
LR/HS vertex. It does not produce a derivative kinetic term for `H_f`.
Consequently it does not yet define a canonical Yukawa residue, a propagating
composite Higgs, or the physical direction/mixing between these auxiliaries
and the existing intrinsic M4 Higgs.

This distinction also resolves the historical charged-boundary coefficients.
The old `beta_f,kappa_f` values are conditional entries of tridiagonal family
bridge candidates. They act inside the frozen three-slot family module. The
Einstein--Cartan kernel instead multiplies the gauge-singlet LR channel and is
family-central. They are different functional variations and the historical
values cannot be relabelled as `c_u,c_d` or canonical quark Yukawas.

## Result and next operator

Derived:

- the formulated first-order Einstein--Cartan action candidate;
- the exact coefficient `c_EC=3/4`;
- a positive local current-C2 algebraic LR kernel;
- its four-channel, 24-pair attachment;
- the exact auxiliary-field block.
- the exact retained-zero-mode endpoint divergence.

Not derived:

- a propagating current-C2 HS kinetic two-point function;
- a physical Higgs/composite direction or mixing map;
- absolute up/down Yukawa operators or quark masses;
- a family-noncentral quark response or physical CKM matrix;
- global endpoint integrability of the LR kernel.

The next object is an action-derived current-C2 endpoint domain or counterterm
that makes the contorsion Schur form finite without removing the retained zero
mode or fitting a coefficient. No historical bridge coefficient or fitted
quark scale may substitute for it.
