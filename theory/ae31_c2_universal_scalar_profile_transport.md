# AE3.1 current-C2 universal scalar-profile transport

BHSM already contains the conditional universal internal profile

```text
Phi(y)=Phi0 exp[-sigma d_I(y,y0)^2]
```

and the canonical profile-normalization statement

```text
integral_B |Phi|^2 dmu_Berger=1.
```

This unit transports those existing objects; it does not invent a new scalar
profile or rebuild the particle spectrum.

For finite `Phi0` and `sigma>=0`, multiplication by `Phi` is bounded on the
internal Hilbert space:

```text
||M_Phi||_op=||Phi||_infinity<=|Phi0|.
```

On the current-C2 tensor product it acts as `I_C2 tensor M_Phi`, so

```text
[D_C2 tensor I, I tensor M_Phi]=0.
```

It therefore preserves the reset-generated radial operator, its domain and
endpoint condition, and the retained birth trace. This is a domain theorem,
not a claim that the current AE3.1 action has already selected this profile.

For finite-rank retained harmonic projectors, the response from the previous
bridge is automatically finite:

```text
R_f=||P_A,f M_Phi P_S,f||_HS^2
   <=min(rank(P_A,f),rank(P_S,f)) ||M_Phi||_op^2.
```

No trace-class assumption on the uncompressed infinite-dimensional operator
is needed. The parent action must still decide whether its internal trace is
exactly this complete retained-subspace trace.

If canonical normalization is action-owned, its amplitude is not an
independent coefficient:

```text
Phi0=[integral_B exp(-2 sigma d_I(y,y0)^2) dmu_Berger]^-1/2.
```

The existing `Z_H=1` statement has the repository status
`DERIVED_CONDITIONAL_FROM_AUTHOR_PROFILE_NORMALIZATION_AXIOM`; this unit does
not upgrade it to an action derivation. Likewise, the numerical no-fit package
values for `sigma` and `Phi0` are not imported as quark Yukawa inputs.

The same profile serves the two conjugate scalar channels:
`H_tilde=epsilon conjugate(H)`. Conjugation preserves the multiplier norm but
does not force equal up/down responses, because the active/singlet projectors
in the two sectors are different compressions.

The next action calculation is now exact: vary the intrinsic AE3.1 Higgs
coordinate on the fixed current-C2 domain and derive whether

```text
H(x) -> H(x) Phi(y)
```

and the complete retained internal trace actually follow from the same parent
action. If they do, evaluate `sigma,Phi0,R_up,R_down` with the same Berger
measure and common field normalization. If they do not, record the missing or
mismatched term; do not import the historical boundary targets as residues.

Promoted conditionally:

- boundedness of the recovered universal profile multiplier;
- preservation of the current-C2 radial domain and birth trace;
- finiteness and an exact upper bound for every retained projector response;
- the canonical amplitude formula under unit profile normalization.

Not promoted:

- current-AE3.1 action ownership of the internal profile attachment or trace;
- action-derived numerical `sigma,Phi0,c_u,c_d`;
- quark poles, masses, or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
