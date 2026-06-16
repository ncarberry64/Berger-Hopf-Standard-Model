# Derived Yukawa Mode-Distance Scaffold

Diagnostic distances:

```text
D_f(i,j)=|q_i-q_j|+|j_i-j_j|
D2_f(i,j)=(q_i-q_j)^2+(j_i-j_j)^2
```

These are diagnostic distances, not numerical Yukawa values.

## L1 Distance Matrices

### cyclic_upper

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 6 | 9 |
| 2 | 6 | 0 | 3 |
| 3 | 9 | 3 | 0 |

### cyclic_lower

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 3 | 6 |
| 2 | 3 | 0 | 5 |
| 3 | 6 | 5 | 0 |

### reference_charged

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 3 | 6 |
| 2 | 3 | 0 | 3 |
| 3 | 6 | 3 | 0 |

### reference_neutral

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 3 | 2 |
| 2 | 3 | 0 | 3 |
| 3 | 2 | 3 | 0 |


## Squared Distance Matrices

### cyclic_upper

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 36 | 65 |
| 2 | 36 | 0 | 5 |
| 3 | 65 | 5 | 0 |

### cyclic_lower

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 9 | 20 |
| 2 | 9 | 0 | 17 |
| 3 | 20 | 17 | 0 |

### reference_charged

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 5 | 18 |
| 2 | 5 | 0 | 5 |
| 3 | 18 | 5 | 0 |

### reference_neutral

| row/col | 1 | 2 | 3 |
| --- | --- | --- | --- |
| 1 | 0 | 9 | 2 |
| 2 | 9 | 0 | 5 |
| 3 | 2 | 5 | 0 |


Status: `YUKAWA_MODE_DISTANCE_SCAFFOLD_DERIVED_CONDITIONAL`.
