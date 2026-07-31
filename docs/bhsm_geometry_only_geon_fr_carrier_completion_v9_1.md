# BHSM geometry-only geon/FR carrier completion v9.1

## Result

The existing eight-dimensional metric-plus-real-scalar action does not
generate the requested geometry-only Finkelstein--Rubinstein (FR), chiral,
and flavor carrier. This is an exact configuration-space and field-bundle
obstruction, not a failure to find a numerical solution.

Primary verdict:

`BHSM_GEOMETRY_ONLY_PARENT_ACTION_CANNOT_GENERATE_THE_REQUIRED_FR_CHIRAL_FLAVOR_CARRIER`

No fundamental spinor, new continuous coefficient, fitted flavor datum,
historical proxy matrix, or modified frozen prediction is introduced.

## 1. Exact field and manifold doctrine

The active parent fields remain

\[
\Phi=(G_{AB},\chi,\sigma)
\]

on

\[
M_8=I_t\times S^7.
\]

The canonical spatial slice is the standard smooth, oriented \(S^7\). It
has no spatial boundary and has a unique spin structure because
\(H^1(S^7;\mathbb Z_2)=0\). Histories use fixed endpoint traces, with
compactly supported interior variations. For Sobolev order \(s>9/2\), set

\[
\mathcal C_{\rm geom}^s=
\operatorname{Met}_+^s(S^7)
\times H^s(S^7,\mathbb R)_\chi
\times H^s(S^7,\mathbb R)_\sigma.
\]

Choose an observer point and an oriented tangent frame. The small gauge
group is the identity component

\[
\mathcal D_{0,\mathrm{fr}}^{s+1}
=\operatorname{Diff}_{0,\mathrm{fr}}^{s+1}(S^7),
\]

which fixes that observer data. The action-owned physical canonical
configuration space is

\[
\mathcal Q_{\rm geom}^0=
\mathcal C_{\rm geom}^s/
\mathcal D_{0,\mathrm{fr}}^{s+1}.
\]

This is distinct from an ansatz space, a stationary moduli space, a
collective-coordinate space, and a quotient by the full large-diffeomorphism
group. Topology change and connected-sum sectors are not part of the current
action domain.

The slice/observer construction follows the standard geometry of the space of
metrics; see Ebin, [*The manifold of Riemannian
metrics*](https://doi.org/10.1090/pspum/015/0267604).

## 2. Small-diffeomorphism fundamental-group theorem

The positive metric cone is convex, and the two scalar spaces are real
topological vector spaces. Therefore \(\mathcal C_{\rm geom}^s\) is
contractible. Observer framing makes the diffeomorphism action free: a
Riemannian isometry fixing a point and its entire tangent frame is the
identity.

The principal fibration

\[
\mathcal D_{0,\mathrm{fr}}^{s+1}
\longrightarrow
\mathcal C_{\rm geom}^s
\longrightarrow
\mathcal Q_{\rm geom}^0
\]

and its long exact homotopy sequence give

\[
\pi_1(\mathcal Q_{\rm geom}^0)
\cong
\pi_0(\mathcal D_{0,\mathrm{fr}}^{s+1})
=0,
\]

because the gauge group is its identity component. Consequently the
declared geometry-only quotient has no nontrivial order-two character and no
nontrivial FR line:

\[
L_{\rm FR}^{\rm geom}=\mathrm{undefined}.
\]

This proves

`BHSM_SMALL_DIFF_GEOMETRY_CONFIGURATION_SPACE_HAS_NO_FR_Z2`.

## 3. Large diffeomorphisms are a different question

For the standard high-dimensional sphere, the orientation-preserving mapping
class group is related to homotopy spheres:

\[
\pi_0\operatorname{Diff}^+(S^7)
\cong\Theta_8\cong\mathbb Z_2.
\]

The generator is the exotic-eight-sphere gluing class obtained by gluing two
eight-disks along an \(S^7\) diffeomorphism. See Kervaire and Milnor,
[*Groups of Homotopy Spheres:
I*](https://people.math.rochester.edu/faculty/doug/otherpapers/kervaire-milnor.pdf).

That \(\mathbb Z_2\) does not belong to the quotient by
\(\operatorname{Diff}_0\). Gauging the full observer group would define a
different theory space. Even there:

- the class is an exotic-sphere mapping class, not a proved \(2\pi\)
  spatial-rotation or identical-geon-exchange loop;
- the trivial and sign characters are both available;
- the current action does not select between them;
- a sign line over configuration space is not a local spinor bundle.

Thus the large-diffeomorphism \(\mathbb Z_2\) cannot be silently promoted to
the required BHSM carrier.

## 4. Reconciliation with the v6.6 FR theorem

BHSM v6.6 correctly established

\[
\pi_1\operatorname{Map}_*^N(S^3,S^3)
=\pi_4(S^3)=\mathbb Z_2
\]

and the nontrivial character \((-1)^N\). Its report also classified
\(\operatorname{Map}_*^N(S^3,S^3)\) as an adopted BHSM identification, not a
parent-action theorem. The v9.1 calculation preserves that result and
closes the integration ambiguity:

\[
\operatorname{Map}_*^N(S^3,S^3)
\ne
\mathcal Q_{\rm geom}^0.
\]

The current \(S_8\) bundle contains no \(S^3\)-valued degree field and no
action-derived map from the metric/scalar quotient to the v6.6 mapping
space. The v6.6 line therefore remains conditional and unpromoted. The
general FR sign-line mechanism is the one introduced by Finkelstein and
Rubinstein, [*Connection between spin, statistics, and
kinks*](https://doi.org/10.1063/1.1664510).

## 5. Requested loop classification

| Candidate | Result in the declared quotient |
|---|---|
| Large \(S^7\) diffeomorphism | Belongs to a different full-diffeomorphism quotient |
| \(2\pi\) spatial rotation | Lies in the small gauge orbit and projects to the constant loop |
| Two-geon exchange | No two-geon stationary sector or exchange space is derived |
| Quaternionic Hopf cycle | Fixed bundle geometry, not an active coordinate |
| Compatible \(G_2\) path | \(G_2\) structure is not an active field |
| Metric-plus-frame rotation | Observer frame is gauge fixing, not a rotor |
| Two-cap reflection | Independently owned \(S_{5|4}\) data, not \(S_8\) topology |
| Triality permutation | Order-three representation automorphism, not a metric loop |
| Connected sum/handle | Changes the fixed-manifold action domain |

No requested rotation or exchange loop defines a nontrivial order-two class
in \(\mathcal Q_{\rm geom}^0\).

## 6. Metric-only \(G_2\) selection no-go

For a fixed oriented seven-dimensional metric, compatible \(G_2\) structures
form the fiber

\[
SO(7)/G_2\cong\mathbb{RP}^7.
\]

This is also described as the projectivized unit-spinor fiber; see Crowley
and Nordström, [*New invariants of
\(G_2\)-structures*](https://msp.org/gt/2015/19-5/gt-v19-n5-p12-p.pdf).
An \(SO(7)\)-natural metric-only selection would be a fixed point of the
transitive \(SO(7)\) action on this homogeneous space. No such point exists.

Holonomy cannot repair this on \(S^7\). A torsion-free \(G_2\) form is a
nonzero harmonic three-form, but

\[
H^3(S^7)=0.
\]

Nearly parallel \(G_2\) structures exist on round and squashed seven-spheres,
but the metric alone does not select one, and the current action contains no
\(G_2\)-energy or polarization constraint. Consequently

\[
\eta_\varphi,\ J_u,\ \Pi_{10},\
P_{\chi_0},P_{\chi_1},P_{\chi_2}
\]

remain undefined as action-selected objects.

## 7. Closed-FLRW reduction

For

\[
ds_8^2=-N(t)^2dt^2+a(t)^2g_{S^7},
\]

the lapse-retaining reduced action, after the endpoint term, is

\[
\begin{aligned}
S={\rm Vol}(S^7)\int dt\bigg[&
-\frac{21\kappa_1a^5\dot a^2}{N}
+21\kappa_1Na^5-Na^7U_{\rm eff}(\sigma)\\
&+\frac{a^7}{2N}\left(
Z_\chi(1+g\sigma^2)\dot\chi^2
+Z_\sigma\dot\sigma^2\right)\bigg],
\end{aligned}
\]

where

\[
U_{\rm eff}=\frac{\kappa_0}{2}
+\frac{A_0}{2}\sigma^2+\frac{G_0}{4}\sigma^4.
\]

The lapse equation is

\[
21\kappa_1\left[
\left(\frac{\dot a}{Na}\right)^2+\frac1{a^2}
\right]
=U_{\rm eff}
+\frac{Z_\chi(1+g\sigma^2)\dot\chi^2+Z_\sigma\dot\sigma^2}{2N^2}.
\]

For constant scalars and
\(H^2=U_{\rm eff}/(21\kappa_1)>0\), the exact solution is

\[
a(t)=H^{-1}\cosh(H(t-t_0)).
\]

It satisfies both the constraint and evolution equation exactly. It is not
stationary: at its turning point, \(\ddot a=H\ne0\). Nor is it periodic,
because \(\ddot a=H^2a>0\) for \(a>0\). Its scale depends on independent
action inputs, the scalar root, the time origin, and the unfixed constant
\(\chi\) modulus.

For the representative dimensionless normalization \(H=\kappa_1=1\),
\(U_{\rm eff}=21\), two independent solvers give:

| Check | Residual |
|---|---:|
| DOP853 versus exact solution | \(2.19\times10^{-12}\) |
| Collocation versus exact solution | \(8.22\times10^{-15}\) |
| Cross-method solution difference | \(2.20\times10^{-12}\) |
| DOP853 Hamiltonian constraint | \(3.88\times10^{-12}\) |
| Collocation Hamiltonian constraint | \(1.67\times10^{-14}\) |
| Boundary residual | \(0\) |
| Action cross-method difference | \(1.80\times10^{-14}\) |

The representative action per unit \(S^7\) volume on \(t\in[-1,1]\) is
\(-157.9148638911968\). This is an ansatz validation, not a physical vacuum
action or parameter choice.

## 8. Quaternionic Berger/Hopf reduction

For

\[
ds_8^2=-N^2dt^2
+a_H^2g_{S^4}
+a_F^2\langle\omega,\omega\rangle,
\]

the canonical connection curvature gives

\[
R_7=\frac{48}{a_H^2}
+\frac6{a_F^2}
-\frac{12a_F^2}{a_H^4},
\qquad
\sqrt h\propto a_H^4a_F^3.
\]

The gravitational kinetic form is

\[
\frac{\kappa_1a_H^4a_F^3}{2N}
\left[-12H_H^2-6H_F^2-24H_HH_F\right].
\]

The volume-normalized Einstein-shape equation, with
\(x=(a_F/a_H)^2\), is

\[
5x^2-6x+1=0,
\]

giving the round \(x=1\) and Jensen-squashed \(x=1/5\) shapes. Neither is a
static eight-dimensional product vacuum. The static lapse constraint sets
\(\kappa_1R_7/2=U_{\rm eff}\); the two scale equations then require both
derivatives of \(R_7\) to vanish, while

\[
\frac{\partial R_7}{\partial a_F}
=-\frac{12}{a_F^3}-\frac{24a_F}{a_H^4}<0
\]

for positive scales. Hence no positive-scale static solution exists in the
complete homogeneous two-scale sector.

## 9. Nonhomogeneous and localized ladder

The cohomogeneity-one class does not define a unique reduced problem until
the orbit type, singular-orbit regularity, retained metric modes, lapse/shift
gauge, scalar coefficient signs, and global domain are specified. On compact
\(S^7\), maps into the contractible scalar target carry no wall charge; a
single topologically protected scalar wall is unavailable.

A smooth localized metric/scalar PDE solution is not ruled out in every
coefficient domain. What is ruled out is its promotion to the requested
carrier: the fixed manifold contains no connected-sum geon sector, no
two-geon exchange space is derived, and the exact FR/local-chirality
obstructions remain even if a non-topological lump were found.

## 10. Composite, Hessian, current, and flavor gates

Because no \(\Phi_*\), \(L_{\rm FR}\), selected \(G_2\) structure, or local
spinor transgression exists, the nonlinear states and immersions fail closed:

\[
\Phi_{f,i}=\mathfrak C_f=A_f=\mathrm{undefined}.
\]

Therefore

\[
\mathbb K_8=\mathbb H_8=
G_u=Q_u=G_d=Q_d=K_{ud}=V_{\rm BHSM}
=\mathrm{undefined}.
\]

Gram positivity, simple spectrum, current rank, polar decomposition,
unitarity, basis covariance, mixing angles, and the Jarlskog identities are
not evaluable. The conditional v8.9 theorem remains valid but receives no
physical inputs from v9.1.

No charged mass, neutrino spectrum, PMNS matrix, scale, \(1/(4\pi)\) origin,
or action location for \(Z_{\rm virt}^{u,2}=1/2\) is derived.

## 11. Minimal-extension comparison

The extension comparison was performed only after the original-action no-go.
Seven classes were audited: global topology sectors, an \(S^7\)-valued
topological sigma field, a unit spinor, a stable \(G_2\) three-form, an
octonion section, a constrained frame/triality field, and a higher-form gauge
field.

No candidate closes all missing arrows. The global topology option adds the
least local data but lacks local chirality and current ownership. A unit
spinor or \(G_2\) form supplies polarization but not FR topology or the parent
current. A topological sigma field can supply a mapping-space \(\mathbb Z_2\)
but not the Clifford/current chain. The remaining candidates add still more
independent structure.

There is consequently no uniquely minimal extension under the declared
criteria. No BHSM v2 action is adopted or proposed by this campaign.

## 12. Exact obstruction

The failure chain is

\[
\boxed{
\pi_1(\mathcal Q_{\rm geom}^0)=0,
\quad
L_{\rm FR}=\varnothing,
\quad
\eta_\varphi=\varnothing,
\quad
\mathfrak C_f=\varnothing,
\quad
K_{ud}=\varnothing.
}
\]

The next exact object, if the theory is deliberately extended, is:

`ACTION_LEVEL_GLOBAL_TOPOLOGICAL_SECTOR_WITH_LOCAL_CHIRAL_TRANSGRESSION_AND_COMMON_PARENT_CURRENT_OWNERSHIP`
