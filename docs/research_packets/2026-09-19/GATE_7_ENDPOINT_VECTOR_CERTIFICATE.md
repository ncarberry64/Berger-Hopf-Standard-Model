# Complete endpoint vector and shared local transport

Gate 7 remains OPEN. The previous interval-13, right-column-14 obstruction
is removed: all 74 output coordinates of that complete local column obey

    ||Q D_R,14(theta)||_2 <= 0.589573466401 < 1,
    1-||Q D_R,14(theta)||_2 >= 0.410426533599.

The decimal upper/lower bounds round outward from exact rational endpoints.
This is one complete local column on the original retained domain, not an
operator-norm or full-history contraction theorem.

## Endpoint vector

The endpoint scalar `row_73[(2h/3)QP] DF(Z_R)e` has the independently repeated
anchor-deviation bound `0.006560135436`, including its nonlinear remainder.
The same exact descriptor-elimination identity used at the midpoint reconstructs
all 99 endpoint rate coordinates as shared Taylor models. All 74 projected
endpoint rows then have the Euclidean anchor-deviation bound

    ||(2h/3) Q P [DF(Z_R)e-DF(Z_R,0)e]||_2 <= 0.021620265469.

No coordinate is discarded. The endpoint model has 75 original parameters
and 248 implicit corrections. The mean-value correction tightening uses
the original verified point solves and same-family derivative solves; it
does not shrink the physical domain or reduce the scalar nonlinear remainder.

## Exact transport and parameter identity

Let `A=DF(Z_R)e`, `M=DF(Z_M)` and retain the original fixed `w0`. The exact
repository-native Hermite--Simpson chain is

    Q D = Q[u14-Pe+(h/6)PA]
          +(2h/3)QP DF(Z_M)w0
          +(2h/3)QP M(e/2-hA/8-w0).

The 249 midpoint parameters retain, in order, the two longitudinal intervals,
left and right 74-dimensional balls, and the 99-dimensional endpoint-field
remainder box. Endpoint 14's longitudinal parameter is midpoint parameter 1;
its transverse parameters map to midpoint parameters 76 through 149 (zero
based). The saved direction maps and source fingerprints are checked before
identifying these symbols. The midpoint and endpoint correction coordinates
are then appended separately, producing 745 shared coordinates in total.
Every actual endpoint/midpoint pair is covered by this same outer domain.

The complete endpoint Taylor rate is substituted into the chain before any
support bounds. In particular, form `e/2-hA/8-w0` before multiplying by M.
This preserves its small center shift. The full previously certified 99-by-99
midpoint derivative enclosure supplies M; it is never replaced by its point
value. Its coefficient dependence is conservatively relaxed, explicitly
recorded in the artifact. This relaxation is strong enough: the complete
result still has the strict margin above. No physical input dependence is
discarded to force acceptance.

For each output row, the certificate retains the center, common linear
coefficients, complete nonlinear remainder, total support, direct endpoint
contribution and transport-correction contribution. The support is taken only
after combining every term. The largest transported component is row 73,
with support about 0.517327; it includes about 0.174509 from the direction
correction. Neither term is omitted.

## Evidence and independent reproduction

The record is
`artifacts/gate7/GATE7_ENDPOINT_VECTOR_CERTIFICATE_v1/record.json`, SHA256
`52E607EA476427901BA839FB77DD10B65FA39142BE3ECF08930CF38C893C3251`.
The full coefficient archive alongside it is `models.json.gz`, SHA256
`FDD60ACE9A639A09B1655A23DEF4DC0733BB811A20A3F63E7E5776AA80A94F36`.
Both independently reproduced byte-for-byte. The endpoint adjoint, scalar
arithmetic and recovered scalar coefficients also reproduced; the receipt
distinguishes arithmetic repetition from checkpoint recovery.

```powershell
C:/Python314/python.exe scripts/evaluate_n12_gate7_full_output_adjoint.py --evidence-root ../BHSM-ae32-crossing-correction --family endpoint --out tmp/endpoint_reproduction/adjoint.json
C:/Python314/python.exe scripts/certify_n12_gate7_shared_scalar_output.py --evidence-root ../BHSM-ae32-crossing-correction --family endpoint --adjoint tmp/endpoint_reproduction/adjoint.json --out tmp/endpoint_reproduction/scalar.json
C:/Python314/python.exe scripts/export_n12_gate7_scalar_taylor.py --evidence-root ../BHSM-ae32-crossing-correction --adjoint tmp/endpoint_reproduction/adjoint.json --certificate tmp/endpoint_reproduction/scalar.json --checkpoints tmp/endpoint_reproduction/scalar.terms --out tmp/endpoint_reproduction/coefficients.json
C:/Python314/python.exe scripts/certify_n12_gate7_endpoint_vector_transport.py --evidence-root ../BHSM-ae32-crossing-correction --scalar tmp/endpoint_reproduction/scalar.json --coefficients tmp/endpoint_reproduction/coefficients.json --midpoint-vector artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v2.json --out tmp/endpoint_reproduction/vector
C:/Python314/python.exe scripts/verify_n12_gate7_vector_certificates.py --midpoint artifacts/gate7/GATE7_PROJECTED_VECTOR_CERTIFICATE_v2.json --endpoint tmp/endpoint_reproduction/vector/record.json --out tmp/endpoint_reproduction/support-check.json
```

Use entirely fresh output/checkpoint directories for the second arithmetic
run. The support verifier independently replays all 222 projected row
supports from the stored exact coefficients, checks the original parameter
embedding and all 99 raw endpoint coordinates, then recomputes the norms
and strict local margin. This coefficient replay does not replace the
independent physical arithmetic pair.

## Remaining mathematical boundary

The former independent-Hessian coefficient relaxation admitted gain at least
48.720352347851 for this column. That remains a valid statement about that
looser model; it is superseded as an obstacle for the actual column by the
new rigorous upper bound below one.

The new result concerns input column 14 of interval 13. A full operator bound
requires all input directions simultaneously; bounds on individual columns
alone also need a justified operator-norm combination. The other intervals,
required frame/quotient derivatives, same-map physical Y/Z1/Z2 majorants,
joint operator/force/KKT conditions and continuum obligations remain governed
by the canonical Gate-7 specification. This certificate promotes none of them.
