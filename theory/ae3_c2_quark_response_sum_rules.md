# Current-C2 quark response sum rules

## Reused internal operator

The frozen BHSM up/down family modes and projectors are already attached over
the current `C2` carrier.  For a mode `(k,j)`, define

```text
K = k(k+2),
q^2 = (k-2j)^2,
T_f(a) = exp[-(K_f+(a^2-1)q_f^2)/(4 pi)].
```

Within a sector, use the ratios `r_f=T_f/T_heavy`.  Any common sector
prefactor cancels.  The calculation below eliminates the remaining Berger
squashing from the already-defined response weights.  It does not rebuild the
mode ledger or turn the weights into quark masses.

## Up-sector identity

The frozen up slots are

```text
heavy:  (k,j)=(0,0),  (K,q^2)=(0,0),
middle: (k,j)=(6,0),  (K,q^2)=(48,36),
light:  (k,j)=(10,1), (K,q^2)=(120,64).
```

The primitive integer combination that removes `a^2-1` is

```text
16 log(r_middle) - 9 log(r_light) = 78/pi,
```

equivalently

```text
9 log(r_light) - 16 log(r_middle) = -78/pi,
r_light^9 = exp(-78/pi) r_middle^16.
```

The constant follows from `16*48-9*120=-312`; no measured up-type quark mass
enters.

## Down-sector identity

The frozen down slots are

```text
heavy:  (k,j)=(0,0), (K,q^2)=(0,0),
middle: (k,j)=(6,3), (K,q^2)=(48,0),
light:  (k,j)=(8,2), (K,q^2)=(80,16).
```

The middle mode has the same zero Berger charge as the heavy mode.  Its ratio
is therefore already independent of squashing:

```text
log(r_middle) = -12/pi,
r_middle = exp(-12/pi) = 0.02193397149543947...
```

The light ratio retains squashing dependence; no second independent down
ratio can remove it because the heavy and middle slots both have `q^2=0`.

## Claim boundary

Both identities hold for every positive internal Berger squashing and are
verified on the previously attached frozen operator.  They are exact
parameter-eliminated constraints on the current-C2 Hopf response shape.

They are not yet quark mass relations.  The current action does not contain
action-owned intrinsic-M4 up/down LR--Higgs operators or their absolute
Yukawa prefactors, and the present charged-current family kernel gives only
the canonical response-basis identity, not the physical CKM matrix.  Those
operators must be derived before the response identities can be tested on
tree or dressed quark poles.

Promoted:

- `CURRENT_C2_UP_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED = TRUE`;
- `CURRENT_C2_DOWN_QUARK_SCALE_FREE_RESPONSE_SUM_RULE_DERIVED = TRUE`.

Open:

- intrinsic-M4 up/down LR--Higgs action ownership;
- absolute up/down Yukawa prefactors;
- physical quark mass ratios and poles;
- nontrivial CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
