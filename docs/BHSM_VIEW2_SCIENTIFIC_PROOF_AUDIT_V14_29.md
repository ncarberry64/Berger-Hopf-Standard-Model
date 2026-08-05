# BHSM View 2 scientific proof audit v14.29

## Verdict

**Outcome B**:

`BHSM_VIEW2_MINIMALLY_GAUGED_ETA_ACTION_AND_COMPOSITE_THETA_CURRENT_ARE_CONSTRUCTED_CONDITIONALLY_BUT_FULL_MASTER_ACTION_OWNERSHIP_REMAINS_BLOCKED`

The local `G2/SU3` associated-bundle construction, the composite nature of `theta`, the variation of a minimally covariantized eta action, its gauge identity, the stabilizer zero-current result, and a finite-action off-shell tangent-current witness are mathematically consistent. They are not yet a theorem of the retained BHSM action. The prior action contains the eta field on `M8` with its induced Spin covariant derivative, while the independently varied physical SU(3) connection lives in the intrinsic `B1/M4` EFT. The common-domain bundle map, collar pushforward measure, and variational intertwiner are absent. In addition, no collective-quantization/matching theorem maps the bosonic eta current to a normalized FR/Dirac quark current without double counting.

## 1. Assumptions and retained conventions

The audit uses these repository facts.

1. The v10 structural-postulate eta sector is on `M8=I_t x S7`, with Lorentzian measure `dmu_8=sqrt(-G) d^8x`, a dimensionless bosonic unit triality-spinor `eta`, and an auxiliary multiplier `Lambda_eta`.
2. In the v10 notation `D_A eta`, the capital `A` is an eight-dimensional tensor index and `D` contains the induced Spin connection. It is not the independent physical color potential.
3. The physical connection is an anti-Hermitian SU(3) connection `A=A_mu^a t_a dx^mu` on `P_color->M4`, with `tr(t_a^dagger t_b)=delta_ab/2`. The v14.2 convention does not absorb `g3` into `A`; the coupling occurs in `S_YM`.
4. The exact v7 collar identity is `C=B1 x (-epsilon,epsilon)` with

   `dmu_C=J_C(rho,x) dmu_h(x) d rho`, `J_C=det(I+rho S)`.

   Its embedding, width, and pushforward normalization are explicitly open. It therefore defines a conditional geometric measure, not a completed cross-stratum action measure.
5. The inclusion `SU3 -> G2` and a retained `P_color` define `Q_G2=P_color x_SU3 G2` and `Sigma_eta=Q_G2/SU3=P_color x_SU3 S6`. This does not trivialize `P_color` or set `c2(P_color)=0`.

## 2. The actual retained action and the candidate completion

The relevant eta term actually retained before v14.29 is

```text
S_eta^(8)[G,sigma,eta,Lambda_eta]
 = integral_M8 d^8x sqrt(-G) {
     -(1+g sigma^2)[(kappa1/2) X_eta+(1/8) X_eta^4]
     +(Lambda_eta/2)(<eta,eta>-1)
   },

X_eta=<D_A^Spin eta,D^{A,Spin} eta>.
```

The surrounding retained `M8` action also contains `kappa1 R8/2-kappa0/2`, the `chi` and `sigma` kinetic terms, and `U(sigma)`. They are inherited and are not varied in this color-source audit. Variation of `Lambda_eta` gives `<eta,eta>=1`.

The independently owned intrinsic color term is

```text
S_YM[A]= - integral_M4 d^4x sqrt(-h)
             [1/(4 g3^2)] Tr(F_mu_nu F^mu_nu).
```

The retained Wilson-dressed meson and baryon expressions are gauge-invariant source/observable insertions. They are not terms integrated over as new dynamical fields. The conditional FR field is likewise not a proved ultraviolet-independent field.

There is no retained action of the requested joint form because `S_eta^(8)` and `S_YM^(4)` do not share a sourced bundle/measure reduction. The v14.29 candidate is

```text
S_etaA^cand[A,eta]
 = - integral_C dmu_C w(sigma)
       [(kappa1/2) X_eta+(1/8)X_eta^4]
   + integral_C dmu_C (Lambda_eta/2)(<eta,eta>-1),

w=1+g sigma^2,
X_eta=G_IJ(eta) D_M^A eta^I D^{M,A} eta^J,
D_mu^A eta^I=partial_mu eta^I+A_mu^a K_a^I(eta).
```

`S_etaA^cand` replaces the ungauged eta kinetic density; it must not be added beside a second copy. No new numerical coefficient is introduced. Nevertheless the replacement itself, the map from the original `M8` eta section to `Gamma(Sigma_eta|_C)`, and the collar-to-`M4` variational pushforward are new author-directed completion data. No uniqueness theorem selects them from the prior action.

At `A=0`, `D^A eta=partial eta` in the color directions and the candidate reduces algebraically to the corresponding ungauged collar eta density. This is an exact algebraic limit of the candidate; it does not prove equality to the original `M8` functional because the domains and measures remain unmatched.

Classification: the retained `M8` and intrinsic `M4` terms are `VALIDATED`; the joint covariantization is `VALIDATED_CONDITIONALLY`; its derivation from the parent action is `OPEN`.

## 3. Line-by-line connection variation

Let

```text
F(X)=(kappa1/2)X+(1/8)X^4.
```

Then

```text
F'(X)=kappa1/2+(4/8)X^3=(1/2)(kappa1+X^3).
```

At fixed `eta`, metric, and collar geometry,

```text
delta_A(D_mu eta^I)=K_a^I(eta) delta A_mu^a,

delta_A X
 = G_IJ[delta(D_mu eta^I)D^mu eta^J
        +D_mu eta^I delta(D^mu eta^J)]
 =2 K_aI(eta)D^mu eta^I delta A_mu^a.
```

Therefore

```text
delta_A S_etaA^cand
 =-integral_C dmu_C w F'(X) delta X
 =-integral_C dmu_C
    w(kappa1+X^3)K_aI(eta)D^mu eta^I delta A_mu^a.
```

With the explicit source convention

```text
delta_A S_etaA^cand=-integral_C dmu_C J_a^mu delta A_mu^a,
```

the source is

```text
J_a^mu=w(kappa1+X^3)K_aI(eta)D^mu eta^I.
```

There is no residual factor two: it cancels the `1/2` in `F'`. In a local complex tangent chart `m_C=3`, with metric `G(v,z)=2 Re(v^dagger z)`, this becomes

```text
J_a^mu=2w(kappa1+X^3) Re[(t_a xi)^dagger D^mu xi].
```

The functional derivative is `delta S/delta A=-J`; confusing it with `J` reverses the sign. The collar Jacobian belongs to `dmu_C`; the integrated four-dimensional candidate source is

```text
j_a^mu(x)=integral_{-epsilon}^{epsilon} d rho
           J_C(rho,x) J_a^mu(rho,x).
```

No `g3` appears inside `D` in the retained v14.2 convention, no trace occurs in the sigma-model kinetic term, and generator normalization is fixed by `tr(t_a^dagger t_b)=delta_ab/2`. A convention with `g3 A` inside `D` would multiply the source variation by `g3` and must simultaneously change the Yang-Mills convention; it is not used here.

## 4. Gauge invariance and Noether identity

For infinitesimal `epsilon=epsilon^a t_a`, use

```text
delta_epsilon A_mu=-D_mu epsilon,
delta_epsilon eta^I=epsilon^a K_a^I(eta).
```

Equivariance of the associated-bundle covariant derivative gives

```text
delta_epsilon(D_mu eta)^I
 =epsilon^a partial_J K_a^I(eta)D_mu eta^J.
```

The `G2/SU3` metric is SU(3)-invariant, so the Killing equation implies `delta X=0`. `sigma`, `G`, `h`, `J_C`, and `Lambda_eta` are color singlets; the unit constraint is invariant. Hence the bulk candidate density is invariant. Gauge invariance of the functional additionally requires gauge parameters/boundary data for which

```text
integral_{partial C} dSigma_mu J_a^mu epsilon^a=0,
```

for example compactly supported `epsilon`, fixed gauge transformations at the boundary, or covariant no-flux boundary conditions.

Write the eta Euler density as `E_I=delta S/delta eta^I` and retain the source convention `delta S/delta A_mu^a=-J_a^mu`. Gauge invariance gives

```text
0=integral_C dmu_C [E_I epsilon^a K_a^I+J_a^mu D_mu epsilon^a]
 =integral_C dmu_C epsilon^a[E_I K_a^I-(D_mu J^mu)_a]
  +boundary.
```

Thus the exact off-shell identity in this convention is

```text
(D_mu J^mu)_a-E_I K_a^I=0.
```

Equivalently, for the functional current `calJ=delta S/delta A=-J`,

```text
D_mu calJ_a^mu+E_I K_a^I=0.
```

The often-written plus-sign identity therefore refers to `calJ`, not to the source in `delta S=-int J delta A`. On the eta equation `E=0`, with the unit constraint included and the stated boundary condition, `D_mu J^mu=0`. If the collar is integrated out, the normal boundary flux must vanish or be retained as an interface source before the four-dimensional current is conserved.

## 5. Composite theta theorem

For the reductive homogeneous space

```text
g2=su3 direct_sum m,
Ad_SU3(m) subset m,
dim_R(m)=6,
m_C=3 direct_sum bar3,
```

the standard homogeneous-space identification is

```text
T(G2/SU3)=G2 x_SU3 m.
```

At a coset point `eta=[g]`, the map

```text
Theta_eta:T_eta(G2/SU3)->m_eta=[g,m]
```

is the canonical fiber isomorphism induced by the reductive decomposition. For a section of `Sigma_eta`, define

```text
theta_M:=Theta_eta(D_M^A eta).
```

Under `h in SU3`, `theta_M -> Ad_h theta_M`. This equality is canonical associated-bundle geometry followed by a definition. It is not an algebraic equation of motion and is not derived by varying the action. Its use with the physical `P_color` is conditional on the new common-domain associated-bundle construction; the map from the original `M8` eta field is not supplied by the retained action.

The allowed linearization is

```text
delta theta=DTheta[delta eta,D_A eta]
            +Theta(D_A delta eta+delta A.K(eta)).
```

There is no allowed variation with `delta eta=delta A=0` and `delta theta!=0`. Thus theta is composite once the conditional geometry is adopted.

## 6. Quadratic Hessian and degrees of freedom

Consider the candidate around `A=0`, the SU(3)-fixed coset base point `eta0`, and constant background fields. Write `eta=Exp_eta0(xi)`, `xi in m`. Since `K_a(eta0)=0`,

```text
D_mu eta=partial_mu xi+O(a xi,xi^2),
X=(partial xi)^2+O(fields^3).
```

The `X^4` term starts at eighth fluctuation order. On tangent fluctuations the constraint removes the radial eta component. The quadratic blocks are therefore

```text
H_AA=(1/g3^2) delta_ab[-h_mn partial^2
      +(1-1/alpha)partial_m partial_n]          (gauge fixed),

H_Aeta=0,

H_etaeta=w kappa1(-partial^2) G_mn              (tangent scalars),
```

up to curvature/lower-order background terms. The Faddeev-Popov operator is `M_FP=-partial^2 delta_ab` at this vacuum. Before gauge fixing, longitudinal Yang-Mills directions are gauge zero modes; after gauge fixing the ordinary eight adjoint vector symbols and ghosts remain. There is no `H_thetatheta` block because theta is not a configuration coordinate. The six eta tangent directions are scalar sigma-model/collective directions, not one-form gauge potentials. Hence the conditional candidate adds no six vector principal symbols or vector poles.

This proves a field-content statement for the candidate Hessian. It does not prove that every eta scalar is absent from the physical spectrum, nor does it repair the missing cross-stratum action ownership.

## 7. Stabilizer, pure wall, and legitimate tangent witness

At the coset base point, by definition of `G2/SU3`,

```text
K_a(eta0)=0, a=1,...,8.
```

Therefore `J[eta0]=0`. If `eta=eta(s)` has only normal dependence and the physical gauge field has tangential components, then `D_mu eta=0` and the tangential four-current vanishes. Likewise a one-form `theta=theta_s ds` satisfies `[theta wedge theta]=0`.

A legitimate nonzero test can be built without violating the unit constraint. Choose a smooth normalizable `u(s)` that vanishes at the collar ends, a compactly supported `chi(x)`, a tangent unit vector `e1 in m_C`, and

```text
xi(s,x)=a u(s) chi(x) exp(i k x^1)e1,
eta(s,x)=Exp_eta0[xi(s,x)].
```

The exponential-map field lies exactly on `S6`, returns to `eta0` at the collar boundary, and has finite candidate action. At leading order,

```text
J_3^1=2w k |a u chi|^2 Re[(-i t_3 e1)^dagger e1]+derivative-envelope terms,
```

which is nonzero on an interior region for the standard Cartan generator. This is a finite-action **off-shell test configuration** of the conditional candidate. It is not an eta/Yang-Mills solution, a normalized particle, or a proved collective eigenmode. The earlier constant fundamental-vector witness is invalid as a proof of the stabilizer claim and has been replaced.

The v14.21 result `u0 proportional to sin(f_eta)` proves one normalizable chiral wall mode in its declared normal measure, while the formal `csc(f_eta)` partner is nonnormalizable. It does not fix the physical collar Jacobian/width or provide a complete Dirac pair. Consequently a physical `Z_eta` for the four-dimensional source remains `OPEN`; positivity for any declared positive reference measure is only conditional.

## 8. Is this the physical quark color current?

The provenance chain is:

| Arrow | Classification | Result |
|---|---|---|
| eta tangent mode -> bosonic SU(3) Noether source | VALIDATED_CONDITIONALLY | Valid for `S_etaA^cand`. |
| degree-one eta knot -> FR-odd line/spin parity | VALIDATED_CONDITIONALLY | Topological FR sign and finite diagnostic inertia exist. |
| FR state -> normalized one-knot Hilbert bundle | OPEN | Moduli measure, zero-mode quotient, normalized states, and domain are missing. |
| polarization label -> physical `3/bar3` associated bundle | OPEN | Rank-three polarization and Berry bundle do not supply transition maps for the retained `P_color`. |
| one-knot bundle -> first-order Dirac action | OPEN | A conditional Weyl symbol exists; the action and self-adjoint domain are not derived. |
| bosonic current -> `bar(Psi) gamma T Psi` | OPEN | No collective quantization/current-matching theorem exists. |

Thus the candidate current is a local color Noether source of a bosonic sigma model. Calling it the physical quark current is `INVALIDATED` at present.

## 9. Double-counting audit

The safe alternatives are:

```text
Classical: S_YM+S_etaA^cand.

Quantized low energy: S_YM+S_Dirac^eff[Psi_eta,A],
after the eta collective mode has been integrated/quantized and matched.
```

A matched description would require a decomposition `eta=eta_collective(q)+eta_perp`, a gauge-fixed moduli measure and Jacobian, integration over `eta_perp`, derivation of the FR Hilbert bundle and first-order operator, and a matching/subtraction functional showing that the same zero mode is not retained in both sectors. None is present. The v14.29 ledger's instruction “never sum both” is a valid policy, not a matching theorem. A master action containing both complete eta and Dirac source terms is therefore not authorized.

This missing map alone prevents Outcome A under the required gate.

## 10. Local Gauss source versus confinement

| Layer | Classification |
|---|---|
| Local candidate bosonic Gauss source | VALIDATED_CONDITIONALLY |
| Exact normalized Wilson singlet identities | VALIDATED |
| Non-Abelian gauge-dressed saddle | OPEN |
| Stable finite-width flux tube | OPEN |
| Gauge/ghost/fermion relative determinant | OPEN |
| Wilson-loop area law/worldsheet limit | OPEN |
| Dynamical-quark string breaking | OPEN |
| Physical `c_sigma` | OPEN |

The singlet has zero total one-point color charge while the local operator may be nonzero and `sum_a <T_q^a T_qbar^a>=-4/3`. No contradiction occurs. The v14.28 Gaussian collar has zero asymptotic string tension and remains an `INVALIDATED` confinement route.

## 11. BHSM dependency impact

```text
retained P_color -------------------------- VALIDATED
        |
        +--> associated G2/SU3 geometry --- VALIDATED_CONDITIONALLY
                     |
M8 eta --missing reduction/measure map-----+--> candidate eta-SU3 action
                                                   |
                                                   +--> local bosonic source -- VALIDATED_CONDITIONALLY
                                                   |
FR/Hilbert/Dirac matching -- OPEN -----------------+--> physical quark source -- OPEN
                                                                 |
common c_YM -- OPEN ----------------------------------------------+--> coupled saddle -- OPEN
                                                                        |
scale/thresholds -- OPEN -----------------------------------------------+--> confinement/masses -- OPEN
family response action -- OPEN --> CKM/PMNS/neutrino Delta m2/absolute masses -- OPEN
```

| Major object | Classification after View 2 |
|---|---|
| Common physical SU(3) connection | VALIDATED as an independent `M4` field; its eta attachment is OPEN. |
| Eta-collar attachment | VALIDATED_CONDITIONALLY as geometry; action reduction is OPEN. |
| Action-owned physical Gauss source | OPEN; only the candidate bosonic source is derived. |
| Chiral pair completion | INVALIDATED for one wall; a second action-owned profile/operator is OPEN. |
| Common Yang-Mills normalization | OPEN; v14.20-v14.21 rule out `6pi2`, trace, and topology as absolute derivations. |
| Dimensional scale | OPEN. |
| Gauge-dressed meson/baryon solution | OPEN. |
| Confinement/worldsheet/string breaking | OPEN. |
| Family response operators | OPEN; `J_+^family=I3` remains. |
| CKM | OPEN; no hand-selected `K_ud`. |
| PMNS | OPEN. |
| Neutrino `Delta m^2` | OPEN. |
| Absolute masses | OPEN. |

## 12. Exact unresolved objects

The first ownership blocker is

`COMMON_DOMAIN_ETA_TO_PHYSICAL_SU3_ASSOCIATED_BUNDLE_REDUCTION_WITH_COLLAR_MEASURE_AND_VARIATIONAL_INTERTWINER`.

The independent no-double-counting blocker is

`COLLECTIVE_COORDINATE_PATH_INTEGRAL_MATCHING_OF_THE_ETA_ZERO_MODE_CURRENT_TO_A_NORMALIZED_FR_DIRAC_ACTION_WITH_SELF_ADJOINT_DOMAIN_AND_MODE_SUBTRACTION`.

Only after both close does the downstream numerical object become eligible:

`GAUGE_FIXED_COUPLED_ETA_SU3_COLLAR_WILSON_SINGLET_BOUNDARY_VALUE_PROBLEM_WITH_SELF_ADJOINT_DOMAIN_PARENT_RELATIVE_SUBTRACTION_AND_NONRADIAL_HESSIAN`.

Frozen predictions are unchanged. No physical coupling, CKM, PMNS, absolute mass, mass splitting, neutrino `Delta m^2`, or string tension is emitted.
