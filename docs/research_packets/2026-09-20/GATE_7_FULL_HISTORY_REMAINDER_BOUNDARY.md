# Full-history Gate-7 remainder boundary

Verdict: **OPEN — SPECIFIC REMAINING OBSTRUCTION**.

Interval 13 is a closed, frozen lemma. Its local gain 0.7222150952138733
and margin 0.2777849047861267 are accepted without replay in this work.
No frozen physical parameter, radius, norm, or prediction was changed.

## Mathematical extension actually computed

The 70 independently reproduced signed physical quadratic source sets for
intervals 0 through 69 were reused. Their longitudinal (LL) and mixed (LT)
families were composed through all 370 frozen causal history maps. A shared
input-node diagonal injected in two neighboring intervals was added with
its signs before taking its norm. Independent input-node amplitudes remain
independent. No action derivative was reevaluated.

The resulting outward coefficients, with outputs ordered longitudinal and
transverse, are:

| Selected source family | Longitudinal output | Transverse output |
| --- | ---: | ---: |
| LL, source intervals 0–69 | 4.593400426361419 | 1.7444657117170934 |
| LT, source intervals 0–69 | 14650.38436050771 | 6007.721386423591 |

The mixed convention is `2 M r_L r_T`. These are additive components of
the full-history quadratic map, not complete physical neighborhood bounds.
Source intervals 70–369 are not assigned zero coefficients.

## Three inequalities and their unresolved terms

Use the unchanged radii

`r_L = 9.160189721418071e-7`, `r_T = 1.9369612593815614e-9`.

The retained complete point-data lemmas give

```
Y = [6.152420034927598e-7, 3.415489649323201e-10]
Z0 = [[0.00025093473163449975, 0.41592204108935404],
      [0.00013933283207465512, 0.16248123881002047]]
```

These lemmas cover the selected branch and fixed frames. They do not identify
the final physical quotient or enclose a nonlinear neighborhood.

Let `Q` denote the selected LL/LT homogeneous quadratic operator. Define the
remainder of the full frozen Newton map after its constant, center-linear,
and `Q` terms. Let `R_L,R_T` bound its values on the original domain, and let
`E_L,E_T` bound its derivative rows in the original radius norm. No bound on
these four quantities is inserted by assumption.

The known value contribution is `Y_i + sum_j Z0_ij r_j + Q_i(r)`.
The known derivative row is
`(sum_j Z0_ij r_j + 2 Q_i(r))/r_i`.
The factor two follows by differentiating the retained bilinear quadratic
terms, with their input correlations unchanged.

Conservatively rounded conditional expressions are:

| Required full-history inequality | LHS upper expression, conditional on remainder bounds | Required threshold | Certified full margin | Certification |
| --- | --- | --- | --- | --- |
| Longitudinal self-map | `6.16333331784572e-7 + R_L` | `< 9.160189721418071e-7` | Unavailable | FAIL: missing bound |
| Transverse self-map | `8.06683031712031e-10 + R_T` | `< 1.9369612593815614e-9` | Unavailable | FAIL: missing bound |
| Contraction | `max(0.001252343852095472 + E_L, 0.2518980431964024 + E_T)` | `< 1` | Unavailable | FAIL: missing bound |

Here FAIL refers to certification. **No physical violation has been proved.**
The mathematical status of all three full inequalities is UNDECIDED.
In particular, the positive allowances below are not rigorous full margins.

Sufficient remaining allowances, rounded downward, are:

```
R_L < 2.99685640357235e-7
R_T < 1.13027822766953e-9
E_L < 0.998747656147904
E_T < 0.748101956803597
```

The exact rational allowances and binary64 outward brackets are produced by
`scripts/derive_n12_gate7_remaining_history_budget.py`. Its algebra uses exact
rationals for every input binary64 value and never optimizes the radii.

## Exact remaining dependency

The value and derivative remainders still require the TT family, the missing
LL/LT source intervals 70–369, and the uniform nonlinear neighborhood
remainder. Point Hessians alone cannot enclose variation away from their
centers. The separately retained uniform local operators cover intervals
13–18, but their old coordinate enclosures do not retain the dependencies
needed for a useful global bound. The new structured certificate covers
interval 13 and is not replaced by those older enclosures.

A targeted read of interval 14's older enclosure identifies the largest
entry radius in both DL and DR at output coordinate 73, input coordinate 14
(zero-based). The DR radius is about 1.47216067e9; its old projected
transverse weighted row estimate is 2.2045424820742657e11. This is an
enclosure-width diagnostic, not the physical operator's measured norm or a
lower bound on that norm.

The dependency to refine is

```
interval 14 endpoint 15 derivative
    -> actual HS midpoint derivative and endpoint incidence
    -> R_frozen^-1 T Dr1 E1
    -> DR = I - R_frozen^-1 T Dr1 E1
    -> output coordinate 73, input coordinate 14
```

The refinement must form the shared implicit-solve residual and its output
projection before relaxing dependencies. The existing seven-solve family
machinery provides the method; its interval-13 saved model cannot silently
be reused as an interval-14 neighborhood certificate. The next interval also
needs its own common-parameter model and rigorous remainder on its original
domain. No local interval-13 validation or general verification campaign is
required by this obstruction.

## Reproduction and scope

The LL/LT producers write separate first and repeat outputs under
`tmp/gate7_vector_20260919/history_{LL,LT}_70_{first,repeat}.json`.
The budget producer refuses to consume them unless each pair is byte-identical.
Its output retains source hashes and explicitly null full-LHS bounds and
margins. The interval-14 diagnostic also has distinct first/repeat outputs.
Six focused tests cover the new budget algebra, exact outward brackets, and
its refusal to promote missing remainders to successful certification.

Both source-family compositions, the interval-14 width diagnostic, and the
exact budget now reproduce byte-for-byte in separate processes. The receipt
is `tmp/gate7_vector_20260919/history_composition_reproduction.json`.
The budget digest is
`B1F7EAB0D09C1B45D559BEAF4A0EF04848A8CE12091F94318BE275B014CADE7B`.

No Gate-7 closure certificate or BHSM completion certificate is emitted.
The remaining physical operator/domain obligations are not declared complete.
