# Common-Scale Quark RG Closure Audit

## Why Mixed-Scale Quark Comparisons Are Not Precision Tests

Quark masses are scheme- and scale-dependent. Mixed PDG-style inputs combine light-quark, charm, bottom, and top references at different scales, so they are useful screens but not precision verdicts.

## What Common-Scale Comparison Means

This audit compares BHSM frozen quark ratios with a single M_Z MSbar running-mass reference table.

## What Source Was Used

Scale: `M_Z = 91.1876 GeV`
Scheme: `MSbar running quark masses at M_Z in SM convention`
Source: A. Abdalgabar, A. S. Cornell, A. Deandrea, and A. Tarhini, Eur. Phys. J. C 74, 2893 (2014), Sec. 2.1, quoting Z.-z. Xing, H. Zhang, and S. Zhou, Phys. Rev. D 77, 113016 (2008), arXiv:0712.1419.

## What BHSM Predicts

| Branch | Ratio | BHSM | M_Z Reference | Relative Error | Passes 25% Band | Classification |
| --- | --- | --- | --- | --- | --- | --- |
| `BHSM_BARE_V1` | `c/t` | `0.008310500554068288` | `0.0035718407386035773` | `1.3266716413893933` | `False` | `COMMON_SCALE_RG_VALIDATED_WARNING` |
| `BHSM_BARE_V1` | `u/t` | `1.2690463017606151e-05` | `7.328332371609925e-06` | `0.7316986149221621` | `False` | `COMMON_SCALE_RG_VALIDATED_WARNING` |
| `BHSM_BARE_V1` | `s/b` | `0.021933971495439474` | `0.01903114186851211` | `0.15253050221491055` | `True` | `COMMON_SCALE_RG_VALIDATED_SURVIVAL` |
| `BHSM_BARE_V1` | `d/b` | `0.0011165200546001757` | `0.0010034602076124566` | `0.11266998544638215` | `True` | `COMMON_SCALE_RG_VALIDATED_SURVIVAL` |
| `BHSM_DRESSED_V1_CANDIDATE` | `c/t` | `0.004155250277034144` | `0.0035718407386035773` | `0.16333582069469663` | `True` | `COMMON_SCALE_RG_VALIDATED_SURVIVAL` |
| `BHSM_DRESSED_V1_CANDIDATE` | `u/t` | `1.2690463017606151e-05` | `7.328332371609925e-06` | `0.7316986149221621` | `False` | `COMMON_SCALE_RG_VALIDATED_WARNING` |
| `BHSM_DRESSED_V1_CANDIDATE` | `s/b` | `0.021933971495439474` | `0.01903114186851211` | `0.15253050221491055` | `True` | `COMMON_SCALE_RG_VALIDATED_SURVIVAL` |
| `BHSM_DRESSED_V1_CANDIDATE` | `d/b` | `0.0011165200546001757` | `0.0010034602076124566` | `0.11266998544638215` | `True` | `COMMON_SCALE_RG_VALIDATED_SURVIVAL` |

## What Survives

- Dressed `c/t` improves versus bare: `True`
- Dressed `s/b` survives: `True`
- Dressed `d/b` survives: `True`

## What Remains Warning-Level

- Dressed `u/t` survives: `False`
- Real warning-level tensions: `('u/t',)`

## Whether Quark Precision Is Now Claimable

Classification: `COMMON_SCALE_RG_VALIDATED_WARNING`
Common-scale input blocker closed: `True`
Precision quark matching claimable: `False`

The missing-input blocker is closed by the common-scale table, but full precision quark matching is not claimed because `u/t` remains outside tolerance and uncertainties are not propagated.

## Limitations

- The M_Z table supplies common-scale reference ratios but no uncertainty propagation.
- The dressed c/t branch is compared as frozen; it is not retuned.
- u/t remains outside the scheme-aware tolerance and is reported as a real warning-level tension.
- This audit closes the missing-input blocker only; full precision quark matching remains open.
