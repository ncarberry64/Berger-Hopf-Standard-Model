# BHSM v1.3E Hilbert-Space Domain Scaffold

Status: `DOMAIN_SCAFFOLD`
Theorem complete: `False`

## Basis

- Basis label: `e_{k,j,q,chi,sector}`
- k range: k in nonnegative integers
- j range: 0 <= j <= floor(k/2)
- Hopf charge: `q = k - 2j`
- Chiralities: `(-1, 1)`
- Sectors: `('lepton', 'up', 'down')`

## Protected Zero Modes

| k | j | q | chi | sector |
| --- | --- | --- | --- | --- |
| `0` | `0` | `0` | `-1` | `lepton` |
| `0` | `0` | `0` | `-1` | `up` |
| `0` | `0` | `0` | `-1` | `down` |

## Operator Domains

| Name | Expression | Status | Domain | Limitations |
| --- | --- | --- | --- | --- |
| `diagonal_berger_dirac_kinetic` | `D0^2` | `DOMAIN_SCAFFOLD` | psi with sum lambda_{k,j}^2 |psi_{k,j,chi,sector}|^2 finite | Self-adjointness is stated as a domain assumption, not proven here. |
| `sector_coupling` | `K_sector` | `RELATIVE_BOUND_SCAFFOLD` | relative-bound domain inherited from D0^2 on the common core | Uniform relative boundedness is an assumption to be proven beyond finite scans. |
| `protected_zero_mode_subspace` | `P0 H` | `KERNEL_SCAFFOLD` | span of the three protected zero-mode labels | The full kernel computation remains open. |
| `orthogonal_complement` | `H_perp = (P0 H)^perp` | `COMPLEMENT_SCAFFOLD` | closed complement of the protected zero-mode span | The infinite-dimensional projector compatibility is not proven here. |

## Limitations

- The full twisted Dirac Hilbert space has not been derived from the complete internal action.
- The protected zero-mode labels are formal scaffold labels, not a completed kernel proof.

## v1.3G Zero-Mode/Complement Update

v1.3G adds a dedicated zero-mode/index and complement-projector scaffold.
The formal target remains:

```text
H = ker(D_twist) direct_sum H_perp
dim ker(D_twist) = 3
```

The finite Level 2 projector identities pass, and the finite sector-coupling
block vanishes on the protected coordinate block. The mirror-mode exclusion
and full topological index calculation remain open; theorem_complete remains
`False`.
