# Virtual Mixing Dressing Candidate

Status: `CANDIDATE_NOT_OFFICIAL`

BHSM has an already-released mass dressing for the middle-up mode:

```text
Z_virt^{u,2} = 1/2
```

In the official `BHSM_DRESSED_V1_CANDIDATE` branch, this dressing applies only
to the middle-up mass ratio `c/t`. The CKM frozen values remain unchanged in
that released branch.

The CKM 2-3 mixing channel is high in the same middle-up/heavy-family region.
The clean candidate hypothesis is that mass eigenvalue dressing and
mixing-amplitude dressing are different projections of the same virtual mode:

- mass receives the full factor `Z_mass = Z_virt^{u,2} = 1/2`;
- CKM 2-3 mixing receives a weaker overlap-level factor
  `Z_mix = (Z_virt^{u,2})^(1/16)`.

The exploratory audit found `Z^(1/16)` to be the best predeclared candidate
among no correction, `Z^(1/4)`, `Z^(1/8)`, and `Z^(1/16)`. The exponent `1/16`
is not yet derived and remains a derivation target.

The candidate rule is:

```text
s23_candidate = s23_frozen * (Z_virt^{u,2})^(1/16)
```

Only CKM 2-3 mixing changes. The official frozen branches, the released
`c/t` dressed value, `u/t`, `d/b`, `s/b`, charged-lepton ratios, gauge
couplings, `s12`, `s13`, and `delta_cp` remain unchanged.

This candidate is not part of the official frozen release. It is a clean repair
candidate for the CKM 2-3 pressure point and requires derivation of the 1/16
exponent before promotion.

## Promotion Criteria

The candidate can only be promoted if:

1. the `1/16` exponent is derived or independently motivated from BHSM
   structure;
2. the candidate improves `Vcb` and `Vts`;
3. the candidate does not damage `Vus`, `Vub`, `J_CKM`, or non-2-3 entries;
4. frozen release outputs remain protected;
5. the result is documented as a new frozen candidate branch, not silently
   merged into old predictions.

## Rejection Criteria

Reject the candidate if:

1. `1/16` remains purely fitted;
2. it damages non-2-3 CKM entries;
3. it damages `J_CKM` beyond tolerance;
4. future PDG-style CKM inputs move away from the candidate;
5. the rule must be modified separately for `Vcb` and `Vts`.

## Derivation Targets

Promotion requires deriving the `1/16` exponent from BHSM geometry, boundary
operators, mode overlap order, or the internal action. Until that derivation is
available, this remains a candidate repair branch only.
