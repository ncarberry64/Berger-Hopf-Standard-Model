# BHSM common-domain eta/SU(3) reduction proof

## Result

The common-domain campaign reaches **Outcome C**:

```text
BHSM_COMMON_DOMAIN_ETA_TO_PHYSICAL_SU3_GAUGING_REMAINS_BLOCKED_OR_NONUNIQUE
```

The physical color associated bundle and its pulled-back connection are
globally well-defined for arbitrary retained second-Chern sector. What fails is
the action-owned map from the original eight-dimensional eta field to that
bundle, followed by a measure-preserving variational reduction. The v14.29
minimally gauged density remains a mathematically valid local candidate, not a
term derived from the retained stratified action.

The next campaign object from this intermediate audit is:

```text
FULL_HOPF_PREIMAGE_ETA_FIBER_MODE_REDUCTION_WITH_GAUGE_COVARIANT_DIRICHLET_TO_NEUMANN_EFFECTIVE_ACTION_AND_LOW_ENERGY_MATCHING_TO_THE_V14_29_LOCAL_ETA_SU3_ACTION
```

FR/Dirac matching, the non-Abelian singlet BVP, confinement, scale, masses, and
flavor remain ineligible downstream gates.

## Assumptions and field ontology

The retained geometry is

\[
M_8=I_t\times S^7,
\qquad
M_5=I_t\times S^4,
\qquad
M_4=I_t\times S^3,
\]

with

\[
\pi_{85}=\operatorname{id}_{I_t}\times p_H:M_8\to M_5,
\qquad
\iota_{54}:M_4\hookrightarrow M_5.
\]

Here \(p_H:S^7\to S^4\) is the quaternionic Hopf principal
\(\operatorname{Sp}(1)\) bundle with \(c_2=+1\). The original constrained
bosonic triality-spinor field \(\eta_8\) and its \(p=2+p=8\) action live on
\(M_8\). The physical color bundle \(P_{\rm color}\to M_4\), its connection
\(A_{\rm physical}\), and the Yang--Mills term are independent intrinsic
\(M_4\) data.

The candidate collar associated bundle is

\[
\Sigma_{\eta,C}
=\pi_C^*P_{\rm color}\times_{SU(3)}G_2/SU(3).
\]

Its independent variables would be \(A_{\rm physical}\) and a section
\(\eta_C\). The composite object
\(\theta=\Theta_{\eta_C}(D^{\pi^*A}\eta_C)\) is not independently varied.
The Berry/projector connection remains distinct from the physical connection.

## Audit of retained action structures

| Candidate | Acts on eta | Acts on physical SU(3) | Common domain and variation | Verdict |
| --- | --- | --- | --- | --- |
| \(R_{85}=(\pi_!,P_{\rm ret},Q_H)\) | only an undeclared Spin/Sp(1) retained-mode possibility | no | \(M_8\to M_5\), on invariant/equivariant retained modes | no \(\mathcal R_\eta\) |
| \(R_{54}\) trace/critical value | no eta trace declared | physical \(A\) is intrinsic, not traced | \(M_5\to M_4\), after a stationary branch and domain choice | no eta/color map |
| \(\Lambda_{85}\) | no | no | metric incidence on \(M_5\) | cannot be repurposed |
| \(\lambda_\sigma\) | no | no | scalar basic-mode matcher | cannot be repurposed |
| \(\Lambda_{54}\) | no | no | metric seam trace and reaction | no color matcher |
| v14.29 gauged eta density | yes | yes | declared candidate collar only | allowed local candidate, absent from retained action |

The reciprocal v11.3 attachment changes the support character of metric
incidence. It does not change the tensor type of these multipliers and does not
create an eta/color connection constraint.

## Theorem 1 — v7.1 does not select the requested collar lift

Let \(C_5\subset M_5\) be the v7.1 equatorial collar. Its restriction has no
four-dimensional characteristic-class obstruction and can be trivialized. A
chosen trivialization therefore gives an inclusion
\(\iota:C_5\hookrightarrow M_8\) satisfying
\(\pi_{85}\circ\iota=\operatorname{id}_{C_5}\). Different choices are related
by an arbitrary collar \(\operatorname{Sp}(1)\) gauge map. V7.1 does not select
one, does not couple one to physical color, and does not include its variation.

Moreover, such a section cannot extend across the retained full cap/base
geometry. A principal bundle with a global section is trivial, but the retained
Hopf bundle over the full \(S^4\) base has

\[
c_2(S^7\to S^4)=+1.
\]

Therefore topology does not forbid a collar lift, but it prevents promotion of
that choice to a full-base section and confirms that no canonical lift is
hidden in the Hopf fibration. The required action-owned, gauge-covariant collar
lift is not supplied by the v7.1 geometry.

A genuine geometric alternative exists:

\[
C_8=\pi_{85}^{-1}(C_5)\subset M_8,
\qquad
\pi_C=r_{54}\circ\pi_{85}:C_8\to M_4,
\]

where \(r_{54}\) is collar retraction. This is an eight-dimensional full Hopf
preimage, not the five-dimensional collar used in the v14.29 candidate. The
retained action does not select it as an eta/color common domain or prescribe
which of its normal and fiber modes are eliminated.

## Bundle theorem and its precise limit

Choose local sections of \(P_{\rm color}\) with transition functions
\(g_{ij}:U_i\cap U_j\to SU(3)\). Then

\[
\eta_j=g_{ij}^{-1}\eta_i,
\quad
A_j=g_{ij}^{-1}A_i g_{ij}+g_{ij}^{-1}dg_{ij},
\quad
D_{A_j}\eta_j=g_{ij}^{-1}D_{A_i}\eta_i.
\]

Thus \(\Sigma_{\eta,C}\) and \(D^{\pi^*A}\) are global for every allowed
\(P_{\rm color}\), including nonzero \(c_2\). This construction does not use
the trivial universal-projector pullback and does not force \(c_2=0\).

An action-owned reduction would additionally require local maps \(r_i\) obeying

\[
r_j(h^{\eta}_{ij}v)=g_{ij}^{-1}r_i(v),
\]

where \(h^{\eta}_{ij}\) are transitions of the original triality-spinor
bundle. No retained homomorphism, principal-bundle morphism, or multiplier
relates \(h^{\eta}_{ij}\) to the independently chosen \(g_{ij}\).

There is a local naturality no-go. If an uncolored input is mapped to the
complex tangent \(\mathbf3\) without a cocycle relation, gauge naturality
requires its output to be fixed by all of \(SU(3)\). The common fixed subspace
of the fundamental \(\mathbf3\) is zero. The only gauge-natural coset outputs
without bridge data are stabilizer-fixed poles; their tangent current is zero.
They cannot reproduce the nontrivial v14.29 tangent source.

The reductive representation remains valid:

\[
\mathfrak g_2=\mathfrak{su}(3)\oplus\mathfrak m,
\qquad
\mathfrak m_{\mathbb C}\simeq\mathbf3\oplus\bar{\mathbf3}.
\]

Orientation reversal conjugates the two complex branches. The retained action
does not select one as the physical color representation; this remains a
conditional topological branch, not a sign convention promoted to dynamics.

## Theorem 2 — the v7.1 measure identity does not close the eta action

On one v7.1 equatorial cap, with
\(0\leq\rho<\epsilon_\chi<\pi/2\) and
\(ds=a(t)d\rho\),

\[
d\mu_5=\cos^3\rho\,ds\,d\mu_4,
\qquad
d\mu_8=d\mu_F\,\cos^3\rho\,ds\,d\mu_4,
\]

and on the invariant round Hopf fiber

\[
V_F=\int_Fd\mu_F=16\pi^2a_F^3.
\]

The exact one-cap normal factor is

\[
\int_0^{\epsilon_\chi}a\cos^3\rho\,d\rho
=a\left(\sin\epsilon_\chi-rac{\sin^3\epsilon_\chi}{3}\right).
\]

This is a coarea/Fubini identity for densities on the full preimage. It is not
an action reduction for a general eta field.

First, a fiber-basic map \(\eta:S^7\to S^7\) factors through \(S^4\). Since
\(\pi_4(S^7)=0\), such a map has degree zero. The retained degree-one eta-knot
sector is therefore non-basic and necessarily contains vertical dependence.

Second, normalized fiber averaging does not preserve the nonlinear density.
Writing \(X=|D\eta|^2\), closure would require

\[
\int_F X^4d\nu_F
=\left(\int_FX\,d\nu_F\right)^4.
\]

For the exact two-value witness \(X=(1,3)\), the two sides are \(41\) and
\(16\). The defect \(25\) is strict Jensen inequality. Vertical kinetic energy
and higher retained-mode overlap tensors also survive. Consequently the
coefficient-free v14.29 \(p=2+p=8\) collar form is not the pushforward of the
degree-one \(M_8\) eta action.

## Theorem 3 — naive reduction does not commute with variation

The failure already occurs in the scalar normal model

\[
S[\phi]=\frac12\int_{-L}^{L}
\left[(\phi')^2+m^2\phi^2\right]ds,
\qquad \phi(0)=q.
\]

Eliminate the two bulk halves by their Euler equations. With natural Neumann
conditions at \(\pm L\),

\[
S_{\rm crit}(q)=\frac12q\,[2m\tanh(mL)]\,q.
\]

With Dirichlet outer endpoints, the Hessian is instead

\[
2m\coth(mL).
\]

On either critical bulk field the interior Euler operator is zero, but

\[
\frac{dS_{\rm crit}}{dq}=2m\tanh(mL)q
\]

is generally nonzero. It is the sum of conormal fluxes. It is not the trace or
ordinary pushforward of the zero interior Euler operator. In functional terms,
the adjoint of trace is distributional, and the correct reduced operator is a
boundary-condition-dependent Dirichlet-to-Neumann map.

Therefore the requested formula

\[
\frac{\delta S_{\eta,C}}{\delta\eta_C}
=\mathcal R_{\eta,*}\frac{\delta S_{\eta,8}}{\delta\eta_8}
\]

does not follow from the stored trace diagram. A valid theorem must add an
action-owned critical-value problem, self-adjoint normal domain, zero-mode
treatment, conormal boundary form, metric/measure variation, and the adjoint of
the actual nonlinear reduction. None is present for eta and physical color.

The local v14.29 connection variation remains correct *conditional on the
candidate collar action*:

\[
\delta_A S_{\eta A}^{\rm cand}
=-\int_{C_\eta}J_a^\mu\,\delta A_\mu^a,
\qquad
J_a^\mu=w(\kappa_1+X_\eta^3)K_{aI}D^\mu\eta^I.
\]

This identity does not prove that \(S_{\eta A}^{\rm cand}\) is the reduced
parent action.

## Action equivalence and double-action ledger

| Entry | Current owner | Status |
| --- | --- | --- |
| parent eta term | \(S_8\) on \(M_8\) | retained |
| gauged collar eta term | candidate \(C_\eta\) | absent from retained action |
| \(\mathcal R_\eta\) | none | missing |
| replacement/critical value | none | not derived |
| independent variables | \(\eta_8\) and intrinsic \(A_{\rm physical}\) on separate strata | known |
| eliminated variables | none declared | missing |
| residual boundary term | eta conormal flux | unresolved |
| double counting | no licensed replacement relation | unresolved; do not add both |

At \(A=0\), the v14.29 density reproduces the same *local formula* after a
collar field and measure are declared. It does not reproduce the retained
\(M_8\) critical value because the bridge, non-basic mode elimination, and
normal endpoint problem are absent.

## Uniqueness and coefficient audit

Once all of the following are fixed—\(\Sigma_{\eta,C}\), \(\pi^*A\), the
isotropy representation, the original function
\(F(X)=\kappa_1X/2+X^4/8\), locality, first derivatives, and exclusion of new
operators—the replacement \(\partial\eta\to D^A\eta\) is the usual minimal
covariantization and introduces no continuous coefficient.

That conditional fact is not a uniqueness theorem for the common-domain
completion. Inequivalent choices survive:

1. local five-dimensional lift versus the global eight-dimensional Hopf
   preimage;
2. \(\mathbf3\) versus \(\bar{\mathbf3}\) oriented branch;
3. spectral projection versus constrained critical-value reduction;
4. different self-adjoint normal endpoint domains;
5. local trace action versus the nonlocal Dirichlet-to-Neumann action.

Therefore Outcome B is not available. No new continuous coefficient was found
in the local minimal substitution, but the action and domain themselves are not
selected uniquely.

## Hessian and boundary conditions

No new physical Hessian is promoted. The conditional v14.29 candidate retains
the ordinary gauge-fixed Yang--Mills block, the eta tangent scalar block, and no
independent \(\theta\) block. The actual reduced eta Hessian would contain the
Dirichlet-to-Neumann operator and non-basic Hopf-mode Schur complement. Its
domain depends on outer collar conditions, the unit-norm multiplier, gauge
quotient, metric response, and zero-mode projection. Those objects are absent,
so a spectrum would describe an arbitrarily completed model rather than the
retained BHSM action.

## Validated, invalidated, reclassified, open

Validated:

- the arbitrary-\(c_2\) associated coset bundle and pulled-back physical
  connection;
- the \(\mathbf3\oplus\bar{\mathbf3}\) tangent representation;
- the v7.1 collar Jacobian and full-preimage measure identity;
- the topological non-basic obstruction;
- the nonlinear fiber-moment obstruction;
- the exact Dirichlet-to-Neumann variational counterexample.

Invalidated:

- an action-owned/canonical collar lift, or a full-base section of the retained
  \(c_2=+1\) Hopf bundle;
- reduction of the degree-one eta knot as a fiber-basic mode;
- preservation of the \(p=8\) density by normalized averaging;
- a naive trace/pushforward variational intertwiner;
- Outcome A and Outcome B from the retained data.

Reclassified:

- the full Hopf preimage is a valid candidate common domain but is not
  action-selected;
- the v14.29 current is an exact source of the conditional local action, not an
  action-owned source of the retained master action.

Open:

```text
FULL_HOPF_PREIMAGE_ETA_FIBER_MODE_REDUCTION_WITH_GAUGE_COVARIANT_DIRICHLET_TO_NEUMANN_EFFECTIVE_ACTION_AND_LOW_ENERGY_MATCHING_TO_THE_V14_29_LOCAL_ETA_SU3_ACTION
```

No new postulate is adopted. Frozen predictions remain unchanged, and no
physical mass, CKM, PMNS, neutrino splitting, string tension, or gauge coupling
is emitted.
