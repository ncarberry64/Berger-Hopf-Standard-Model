# BHSM data in the existing Museum engines

The completion target is to supply real, validated BHSM outputs to the existing
exhibit engines. A separate progress chart does not fulfill that target.
`FULL_BHSM_COMPLETE = FALSE` remains the current scientific state.

## Installed calculation data

The existing no-fit provenance/residual monitor now consumes
`data/museum/bhsm_gate7_scalar_response.json`. Its 370 plotted values are
`local_projected_HS_second_residual_norm_upper` from the frozen central scalar
certificate, converted upward to binary64 for display by the verified exporter.
They are numerical residual bounds, not prediction-minus-measurement residuals.
The largest is `0.08778167488957692` at computational interval 8.

The engine verifies the immutable export SHA-256 before rendering. Missing or
changed input stops generation; it never falls back to synthetic values. The
existing PNG, SVG, GIF, card, and motion controls are reused. All intervals are
drawn; animation moves the cursor over saved entries. No smoothing, fitted
curve, added noise, or physical-unit assignment is applied. The raw JSON and
pinned scientific certificate are linked from the existing card. The standalone
scalar chart introduced in Museum version 6 is removed.

## Required inputs for the remaining engines

| Existing engine | Required BHSM input | Current disposition |
|---|---|---|
| CMS coordinate engine | Verified measured four-vectors and coordinate transformation | Existing real CMS input retained; software validation |
| Action expansion | Same-action S²/S³/S⁴ contractions at a stated background and quotient | Explanatory display until compatible action contractions are exported; scalar response norms cannot stand in for derivatives |
| Particle spectrum | Action-owned quadratic spectrum, residues, state identities, and scale with physical promotion gates | Temporary simulated dataset remains clearly labeled |
| Spectral forecast | Certified spectral enclosures/exclusions from the compatible operator and domain | Explanatory structural classes; no invented exclusion bands |
| Magnetic moment | Electromagnetic vertex and F₁/F₂ projection, with external states, Ward identity, enclosure, and renormalization | Numerical physical output gated |
| Collision readout | Same-action amplitudes, external states, flux, phase space, and scale | Numerical physical output gated |
| Decay/stability | Physical states, complete channel ledger, amplitudes, phase space, and scale | Numerical physical output gated |
| No-fit provenance/residual monitor | Verified numerical residual operands and immutable source identity | Actual frozen scalar certificate installed |
| Physical identification bridge | Action-domain carrier and persistence certificates | Existing historical AE2 audit retained; current AE3 extension stated separately |

Each new compatible result should enter its existing engine through a verified
export, with source revision, source hashes, units, background/domain identity,
validation status, and claim class. Passing a stored-matrix certificate is not
authority to promote a full physical Hessian or downstream observable. The
six-worker transverse recovery must finish and the documented physical gates
must close before those stronger outputs can be installed. Cosmology is separate
other work and is unaffected.

Regenerate only the installed monitor with:

```sh
python docs/assets/generate_bhsm_museum_engines.py --engine bhsm_no_fit_firewall
```
