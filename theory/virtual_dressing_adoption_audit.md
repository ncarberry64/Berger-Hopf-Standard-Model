# BHSM Virtual-Dressed Adoption Criteria Audit

This audit evaluates whether the virtual dressing rule qualifies as an adoption candidate. It does not mark the rule as canonically adopted.

Rule status after audit: `ADOPTION_CANDIDATE`
Adopted canonical dressed: `False`

## Adoption Criteria

| ID | Statement | Passes | Evidence | Limitations |
| --- | --- | --- | --- | --- |
| `C1` | Rule is derived from model-internal representation data. | `True` | sector=up_quarks<br>mode=(6,0)<br>Hopf charge q=6<br>base index j=0<br>boundary equation Omega_u=6<br>weak-doublet projection source rule | Full action variation of the projection is still open. |
| `C2` | Rule is independent of empirical residual minimization. | `True` | Factor fixed by weak-doublet probability projection candidate, not by c/t residual. | The numerical improvement is reported only after the rule is defined. |
| `C3` | Rule is local in scope and does not alter unrelated modes. | `True` | changed_outputs=('up_quarks.middle',) | Only the current mode-specific rule passes; broader scopes remain diagnostics. |
| `C4` | Rule improves or preserves already-successful canonical outputs. | `True` | u/t unchanged<br>CKM sin(theta_13) unchanged<br>down-sector ratios unchanged<br>lepton ratios unchanged<br>gauge/electroweak outputs depend on unchanged model constants | This is an output-preservation check, not a proof of the dressing loop. |
| `C5` | Rule has a field-theory interpretation as virtual-environment / weak-doublet probability projection. | `True` | source=WEAK_DOUBLE_PROJECTION<br>factor=1/2 as probability-level projection from two weak components | Interpretation remains virtual-environment-linked, not full loop derivation. |
| `C6` | Rule is applied before residual comparison in the dressed model variant. | `True` | Dressed ratios are computed before threshold-reference comparison rows. | Residual comparison remains diagnostic and scheme-dependent. |

## Bare vs Dressed Candidate

| Variant | c/t | u/t | s/b | d/b | sin(theta_13) |
| --- | --- | --- | --- | --- | --- |
| `BHSM_BARE_CANONICAL` | `0.008310500554068288` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` |
| `BHSM_DRESSED_CANDIDATE` | `0.004155250277034144` | `1.2690463017606151e-05` | `0.021933971495439474` | `0.0011165200546001757` | `0.0035623676140463315` |

Changed outputs: `('up_quarks.middle',)`
Unrelated sectors changed: `()`

## Limitations

- ADOPTION_CANDIDATE is not final canonical adoption.
- No empirical residual is used to set the factor.
- Full virtual loop/threshold derivation remains open.
