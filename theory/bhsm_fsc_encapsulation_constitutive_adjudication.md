# BHSM FSC encapsulation constitutive adjudication

## Verdict

The owner clarification establishes `alpha_FSC` as one symbolic, positive,
dimensionless BHSM reference unit.  It does not establish a universal literal
force strength or select the value of that object at an unspecified scale and
scheme.  Factoring a nonzero constant from the maximal interface class,

```text
S_enc = alpha_FSC S_hat_enc,
```

is always possible, but it is only a change of normalization: the map
`W_s -> W_s/alpha_FSC` is bijective.  It does not select `W_s`, a carrier,
an attachment, a boundary relation, an FSC power, or the relative coefficient
of any allowed invariant.  The primary result is therefore

```text
FSC-P1 / GEFF5 / SCALE4 / FSC-IF5 / EM-FSC3 / GEO-FSC3 / GEO-FSC4
LOOP3 / RSP5 / N12 rank added 0 / residual 67 (66 after time quotient)
```

## Lineage and authority

The observed low-energy electromagnetic number in `src/constants.py` is the
empirical reference `alpha_EM(0)^(-1)=137.035999084`.  It is not a BHSM action
coefficient.  The present owner statement `alpha_FSC approximately 1/137` is
recorded as `FSC-P1`: a typed structural rule making the symbolic coupling a
common constitutive yardstick.  It does not convert the empirical decimal into
an exact primitive.

The historical fine-structure manuscript instead proposed
`Xi_geom=1/(12*pi^2)`, whose inverse is `118.435...`.  That arithmetic is an
`FSC-P2` geometric candidate, not `1/137`.  Its theory core says
`1/e^2=Xi/g^2`, while its operational path uses `e^2=g^2 Xi`; its running
coefficient was then calibrated to the observed low-energy inverse coupling.
Those physical-identification paths are `SUPERSEDED` for upstream use.

The exact factor `1/(6*pi^2)=1/[3 Vol(S^3)]` is `FSC-P3` as a Weyl/volume
identity only.  The registered `alpha_i=w_i/(6*pi^2)`, `w=(1,2,7)`, remains an
`FSC-P2` matching screen.  The Casimir-shell interpretation of `(1,2,7)` is
also an `FSC-P2` spectral candidate.  The later v14.20 theorem shows that the
rank-`dim(g)-1` projectors are not Ad-invariant and that `6*pi^2` is an
unnormalized measure/trace factor rather than a common coupling.  It therefore
supersedes the physical coupling interpretation, not the underlying volume
identity.

The v14.19 trace result `K1:K2:K3=10/3:2:2`, conditionally implying the
squared-coupling ratio `3/5:1:1`, is `FSC-P3` in its declared chiral-seam trace
domain.  It is a relative relation, not an absolute physical coupling theorem.
The `13*pi^2` electroweak inverse-alpha expression remains an `FSC-P2` matching
screen and is distinct from low-energy `137.035999084`.

The one-loop Standard Model RG formula in `src/rg_matching.py` is an `FSC-P2`
comparison scaffold with empirical boundary data.  Two-loop and threshold
matching are explicitly open.  The v14.79 `Q_b=alpha_FS Qhat_b` and
`H_lift=alpha_FS Omega_b G_b` rules are `FSC-P1` architecture with canonical
action attachment still open.

## Primitive convention

The primitive object is `alpha_FSC`, not `e`, `g`, `1/(6*pi^2)`,
`1/(12*pi^2)`, or `1/(13*pi^2)`.  No exact numeric value, reference scale,
renormalization scheme, or physical U(1) projection is currently selected.
In a canonically normalized electromagnetic channel only, the conventional
identity

```text
alpha = e^2/(4*pi),
e = sqrt(4*pi*alpha),
-Tr(F^2)/(4 e^2) = -Tr(F^2)/(16*pi*alpha)
```

is valid.  It proves that a universal linear `alpha` prefactor cannot be
inferred from the word “coupling”: the kinetic coefficient carries
`alpha^(-1)`, a canonical vertex carries `alpha^(1/2)`, and squared or loop
responses can carry `alpha`.

## Channel weights

For an electromagnetic/U(1)-like reference, `W_EM=1` is `W1`: conditional on
selecting the surviving physical U(1) projection and its canonical
normalization.  It is a reference convention, not a theorem selecting an
interface operator.

For weak and strong channels the v14.19 trace convention conditionally gives
`W_weak=W_strong=5/3` relative to its U(1) coefficient, hence `W1` in that
declared domain.  The historical alternatives `2` and `7` are `W3`; v14.20
prevents promoting them to universal action weights.  Neither path supplies a
selected physical P-A* coefficient or overwrites Standard Model running.

Scalar/topographic, geometric/gravitational, and pregeometric/emergent
channels are each `W4`.  The repository contains structures in those sectors,
but no theorem maps them to an FSC-weighted encapsulation coefficient.

## Effective map and scale

The most specific no-fit form currently permitted is

```text
alpha_eff^(r)(mu,Xi)
  = alpha_FSC^(p_r) W_r
    R_r(mu/mu_ref,I_event,I_environment,I_scale;discrete_data).
```

Neither `p_r`, all physical `W_r`, the event-scale map, nor `R_r` is selected.
`R_r` may remain scalar-, matrix-, or operator-valued depending on the
interface representation and multiplicity.  This is `GEFF5`, not a finite
ambiguity.  The special form `alpha_FSC W_r` is an allowed ansatz only after a
linear power and normalized operator have been independently derived.

For P-A*, the scale classification is `SCALE4`: there is no valid interface
running authority.  The repository's Standard Model one-loop routine is a
conditional `SCALE2`-shaped comparison scaffold, but it neither derives the
event scale `mu_s` nor attaches the FSC boundary value to the new interface.

## Interface densities and perturbation theory

None of the ten live/nonredundant families in the certified ORD1 ledger gains
an action-derived FSC power, channel weight, or response coefficient.  The
existing GHY/Hayward completion is redundant as new P-A* strength; the new
second-jet family is excluded from the minimal class; a topological level must
be fixed by topology rather than FSC.

There is no common nonnegative-integer FSC perturbation series.  Canonical
normalization exposes `alpha^(-1)`, `alpha^(1/2)`, `alpha`, and higher response
orders in different objects.  The relevant coupling's smallness at the event
scale is not proved, and no convergence or asymptotic theorem covers the
geometric/pregeometric regimes.  Consequently there is no selected first
nonzero order.

## Electromagnetic, geometric, and energy/spacetime tests

The electromagnetic result is `EM-FSC3`: a conditional reference-channel
normalization is available, but several inequivalent covariant operator laws
remain.  The exact strength at the interface scale and the tensor/operator
shape are not fixed.

The geometric result is `GEO-FSC3`: FSC can be a bookkeeping yardstick but is
not the physical gravitational or envelopment coupling.  The pregeometric
result is `GEO-FSC4`: there is no legitimate current map carrying an
electromagnetic-style coupling through `C_A -> G_A`, and no ordinary embedded
carrier is asserted inside `C_A`.

The candidate `chi_enc=alpha_eff^(r) rho_E/ST` is not derived.  A dimensionless
coupling cannot supply the missing common charge, reference, carrier measure,
or covariant energy/spacetime contraction, so FSC does not define or
dimensionless-normalize `rho_E/ST`.

## Closure, variation, and firewalls

The constitutive result remains `FSC-IF5`.  No `S_enc`, carrier,
`F_B`, `L_s`, or numerical `Delta_enc` is selected.  The prior formal identity

```text
Delta_enc = Pi_c + C(F_B)^* Pi_e
          = -[E_qc(S_enc) + C(F_B)^* E_qe(S_enc)]
```

continues to hold for a selected member, but it is not an explicit
constitutive equation.  It adds no N12 rank.  The residual remains `67`, or
`66` after the time quotient.  Because `FSC-IF5` persists, the dependency cycle
is not rerun: `LOOP3` and `RSP5` are unchanged.

All frozen gauge, family/mode, mass, CKM, neutrino, collider, and claim-boundary
records remain unchanged.  No measured value was fitted, no interface
coefficient or function was chosen, and no Gate-7, new-particle, neutrino, or
full-completion claim is made.

The exact next object is

```text
ACTION_OWNED_FSC_TO_INTERFACE_CONSTITUTIVE_MAP_FIXING_THE_REFERENCE_SCALE_AND_NORMALIZATION_CONVENTION_CHANNEL_EXPONENTS_AND_WEIGHTS_AND_THE_INVARIANT_OPERATOR_COEFFICIENTS_WITHOUT_FIT
```

There is no owner question: `FSC-IF5` is a theorem deficit rather than a small
finite ambiguity.
