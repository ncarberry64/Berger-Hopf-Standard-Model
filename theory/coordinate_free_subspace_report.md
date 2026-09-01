# BHSM v1.3O Coordinate-Free Formal-Kernel Subspace

Theorem complete: `False`
Subspace status: `COORDINATE_FREE_SCAFFOLD`
Basis realization status: `BASIS_REALIZED`

## Coordinate-Free Kernel

`K_formal = span{|ell,0,0,q=0,chi=-1>, |u,0,0,q=0,chi=-1>, |d,0,0,q=0,chi=-1>}`

`H_perp = K_formal^perp`

| sector | state |
| --- | --- |
| `lepton` | `|ell,0,0,q=0,chi=-1>` |
| `up` | `|u,0,0,q=0,chi=-1>` |
| `down` | `|d,0,0,q=0,chi=-1>` |

## Basis Realization

Formula: `M(k_max)=sum_{k=0}^{k_max}(floor(k/2)+1); ell=0, u=2M, d=4M`

| k_max | M(k_max) | lepton | up | down | operator coordinates | matches |
| --- | --- | --- | --- | --- | --- | --- |
| `4` | `9` | `0` | `18` | `36` | `(0, 18, 36)` | `True` |

## Realization Scan

| k_max | M(k_max) | realized coordinates | matches current basis |
| --- | --- | --- | --- |
| `4` | `9` | `(0, 18, 36)` | `True` |
| `6` | `16` | `(0, 32, 64)` | `True` |
| `8` | `25` | `(0, 50, 100)` | `True` |
| `10` | `36` | `(0, 72, 144)` | `True` |
| `12` | `49` | `(0, 98, 196)` | `True` |

## Limitations

- This does not prove the full index theorem or complete H_T spectrum.
- Finite coordinate checks remain scaffold evidence.
