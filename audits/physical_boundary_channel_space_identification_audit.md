# BHSM Physical Boundary Channel-Space Identification

This sprint tests whether cyclic orbit states are physical stochastic boundary channels rather than formal bookkeeping.
The result is partial: the orbit-residue, group-algebra, and density/covariance models are coherent and tied to the boundary scaffold, while primitive closure and full stochastic dynamics remain open.

## Summary

Physical channel-space status: `PHYSICAL_CHANNEL_SPACE_PARTIAL`
Orbit residue channel status: `ORBIT_RESIDUE_CHANNELS_PARTIAL`
Attractor Hessian channel status: `ATTRACTOR_HESSIAN_CHANNEL_SPACE_STRUCTURAL_CANDIDATE`
Density/covariance channel status: `DENSITY_COVARIANCE_CHANNEL_SPACE_PARTIAL`
Group algebra physical channel status: `GROUP_ALGEBRA_PHYSICAL_CHANNEL_PARTIAL`
Cyclic random-walk channel status: `CYCLIC_RANDOM_WALK_CHANNEL_STRUCTURAL_CANDIDATE`
End(H) stochastic algebra status: `END_H_STOCHASTIC_ALGEBRA_PARTIAL`
Lepton 8/9 consequence: `LEPTON_8_9_CHANNEL_RULE_PARTIAL_DERIVATION`
Quark consequence: `QUARK_CHANNEL_SPACE_CONSEQUENCE_CANDIDATE_ONLY`
Neutrino consequence: `NEUTRINO_CHANNEL_SPACE_CONSEQUENCE_CANDIDATE_ONLY`

## Physical Channel Model

```text
|r>_f = U_f^r |0>_f,  r=0,...,|Omega_f|-1
H_f^chan = span{|r>_f}
H_f^chan ~= C[Z_|Omega_f|]
rho_f, covariance_f in End(H_f^chan)
End(H_f) = C I_f + su(d_f)
```

Orbit basis defines physical channels: `True`
Stochastic dressing samples orbit states: `True`
Density/covariance lives on H_f: `True`
End(H) is physical stochastic algebra: `True`

## Sector Counts

| Sector | Omega | dim(H) | dim End(H) | Identity | Traceless | Active fraction | Simplex zero-sum dim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `charged_lepton` | `3` | `3` | `9` | `1` | `8` | `8/9` | `2` |
| `up` | `6` | `6` | `36` | `1` | `35` | `35/36` | `5` |
| `down` | `12` | `12` | `144` | `1` | `143` | `143/144` | `11` |

## Dimension Warning

probability simplex zero-sum dimension is d-1; lepton 8/9 uses traceless End(H) dimension d^2-1 over d^2

## Consequences

Lepton eta from physical channel: `0.002064728414019306`
Promotes lepton 8/9 to partial: `True`
Promotes full lepton 8/9: `False`

## Blockers Closed

- physical_interpretation_of_orbit_residue_basis_as_boundary_channels
- density_covariance_model_on_H_f
- End_H_operator_algebra_distinguished_from_probability_simplex
- partial_lepton_8_9_channel_space_identification

## Blockers Remaining

- derive primitive finite cyclic quotient from the completed boundary action
- derive stochastic residue sampling from the full topographic/BHSM dynamics
- derive the Brownian generator on su(d_f)
- fix A_j normalization and global bundle coupling without convention dependence

## Claim Safety

- No official frozen outputs are changed.
- No retuning is performed.
- No frozen lepton or quark dressing rule is changed.
- No neutrino speed anomaly claim is made.
- No lab-scale environmental mass-drift claim is made.
- No Standard Model replacement claim is made.
