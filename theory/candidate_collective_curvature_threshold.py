from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Iterable, Sequence


BRANCH = "bhsm-collective-curvature-threshold-layer"
STATUS = "candidate_only"

PREVIOUS_BEST_BRANCH_THRESHOLD_LAW = "D_log_threshold_plus_type"
PREVIOUS_RMS_TO_EXISTING_BARE = 0.510697459271581
PREVIOUS_MAX_ABS_LOG_ERROR = 1.0380747597108453

ALLOWED_VERDICT_LABELS = {
    "COLLECTIVE_CURVATURE_THRESHOLD_LAYER_DOCUMENTED",
    "MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE",
    "LOG_THRESHOLD_BRIDGE_DOCUMENTED",
    "COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE",
    "NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL",
    "EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL",
    "NO_NUMERICAL_CLOSURE",
}

CLAIM_LABELS = [
    "COLLECTIVE_CURVATURE_THRESHOLD_LAYER_CANDIDATE",
    "MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE",
    "LOG_THRESHOLD_SCALE_COMPRESSED_RESPONSE_CANDIDATE",
    "BRANCH_TYPE_CURVATURE_SPECIALNESS_CANDIDATE",
    "COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE",
    "EFFECTIVE_DARK_MATTER_AS_CURVATURE_RESIDUE_CANDIDATE",
    "NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL",
    "EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL",
]

FUTURE_GRAVITY_TESTS = [
    "galaxy rotation curves",
    "baryonic Tully-Fisher relation",
    "weak/strong lensing",
    "cluster lensing",
    "colliding clusters",
    "large-scale structure",
    "CMB consistency",
    "Solar System constraints",
]


def positive_part(x: float) -> float:
    """Return [x]_+ = max(x, 0)."""
    return max(float(x), 0.0)


def log_threshold(N: float) -> float:
    """Scale-compressed threshold coordinate log(1 + N)."""
    if N < 0:
        raise ValueError("N must be nonnegative for log-threshold diagnostics.")
    return math.log1p(float(N))


def branch_type_multiplier(
    pure_fiber: bool,
    pure_base: bool,
    b_fiber: float,
    b_base: float,
    *,
    mixed_factor: float = 1.0,
) -> float:
    """Candidate multiplicative branch-specialness factor.

    Mixed modes get no pure-branch factor unless a caller explicitly supplies a
    diagnostic-only mixed_factor.
    """
    factor = 1.0
    if pure_fiber:
        factor *= math.exp(float(b_fiber))
    if pure_base:
        factor *= math.exp(float(b_base))
    if not pure_fiber and not pure_base:
        factor *= float(mixed_factor)
    return factor


def _dot_rows(matrix: Sequence[Sequence[float]], vector: Sequence[float]) -> list[float]:
    if not matrix:
        return []
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("coupling matrix rows must match mass-vector length.")
    return [sum(float(g) * float(m) for g, m in zip(row, vector)) for row in matrix]


def _as_vector(value: float | Sequence[float], length: int) -> list[float]:
    if isinstance(value, (int, float)):
        return [float(value)] * length
    if len(value) != length:
        raise ValueError("vector-valued offsets must match mass-vector length.")
    return [float(x) for x in value]


def collective_curvature_effective(
    K_self: float | Sequence[float],
    coupling_matrix: Sequence[Sequence[float]],
    masses: Sequence[float],
    K_boundary: float | Sequence[float] = 0.0,
    K_envelope: float | Sequence[float] = 0.0,
) -> float | list[float]:
    """Compute K_eff = K_self + G*m + K_boundary + K_envelope.

    Scalar inputs return a scalar when the coupling matrix has one row; otherwise
    a vector is returned. This is a diagnostic candidate utility, not an official
    mass engine.
    """
    coupled = _dot_rows(coupling_matrix, masses)
    n = len(coupled)
    if n == 0:
        raise ValueError("coupling matrix must contain at least one row.")
    self_vec = _as_vector(K_self, n)
    boundary_vec = _as_vector(K_boundary, n)
    envelope_vec = _as_vector(K_envelope, n)
    result = [
        self_vec[i] + coupled[i] + boundary_vec[i] + envelope_vec[i]
        for i in range(n)
    ]
    return result[0] if n == 1 else result


def threshold_mass(
    K_eff: float,
    K_crit: float,
    scale: float = 1.0,
    power: float = 1.0,
    response: float = 1.0,
) -> float:
    """Candidate threshold-opening mass M [K_eff - K_crit]_+^p Z."""
    if scale < 0:
        raise ValueError("scale must be nonnegative.")
    if response < 0:
        raise ValueError("response must be nonnegative for this diagnostic.")
    return float(scale) * positive_part(float(K_eff) - float(K_crit)) ** float(power) * float(response)


def effective_dark_curvature(K_obs: float, K_visible: float) -> float:
    """Diagnostic residual K_DM_eff = K_obs - K_visible."""
    return float(K_obs) - float(K_visible)


def build_results_payload() -> dict:
    verdict_labels = [
        "COLLECTIVE_CURVATURE_THRESHOLD_LAYER_DOCUMENTED",
        "MASS_AS_COLLECTIVE_THRESHOLD_RESPONSE_CANDIDATE",
        "LOG_THRESHOLD_BRIDGE_DOCUMENTED",
        "COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE",
        "NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL",
        "EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL",
        "NO_NUMERICAL_CLOSURE",
    ]
    return {
        "status": STATUS,
        "branch": BRANCH,
        "official_predictions_changed": False,
        "frozen_predictions_changed": False,
        "inputs": {
            "previous_best_branch_threshold_law": PREVIOUS_BEST_BRANCH_THRESHOLD_LAW,
            "previous_rms_to_existing_bare": PREVIOUS_RMS_TO_EXISTING_BARE,
            "previous_max_abs_log_error": PREVIOUS_MAX_ABS_LOG_ERROR,
            "previous_limitations": [
                "hidden response remains",
                "overfit risk",
                "reference scheme limitation",
                "no numerical closure",
            ],
        },
        "candidate_layer": {
            "mass_interpretation": "collective_curvature_threshold",
            "dark_matter_interpretation": "effective_collective_curvature_residue",
            "official": False,
        },
        "candidate_equations": {
            "topographic_operator": "L_T T = S_total, L_T = nabla^2 - B*nabla^4",
            "effective_curvature": "K_i_eff = K_i_self + sum_j G_ij m_j + K_i_boundary + K_i_envelope",
            "threshold_mass": "m_i = M_f * [K_i_eff - K_i_crit]_+^p * Z_i",
            "scale_compressed_shape": "m_shape ~ (1+N)^(-a) * exp(b_fiber*I_fiber + b_base*I_base) * R_hidden",
            "effective_dark_curvature": "K_DM_eff = K_obs - K_visible",
        },
        "guardrails": {
            "does_not_claim_dark_matter_solved": True,
            "does_not_disprove_particle_dark_matter": True,
            "does_not_change_official_predictions": True,
            "requires_empirical_gravity_tests": True,
            "future_empirical_tests": FUTURE_GRAVITY_TESTS,
        },
        "claim_labels": CLAIM_LABELS,
        "verdict_labels": verdict_labels,
        "notes": [
            "candidate-only",
            "no frozen predictions changed",
            "no official predictions changed",
            "mass numerical closure not achieved",
            "empirical dark-matter tests required",
        ],
    }


def render_layer_markdown() -> str:
    return f"""# Collective Curvature Threshold Layer

Status: `candidate_only`

Claim labels:

{chr(10).join(f"- `{label}`" for label in CLAIM_LABELS[:4])}

## Motivation

The isolated heat-kernel spectral-action mass screen did not reproduce the
existing BHSM charged-fermion outputs as well as the frozen bare engine. The
minimal branch-threshold reconstruction found `{PREVIOUS_BEST_BRANCH_THRESHOLD_LAW}`
as the strongest diagnostic law, with RMS log error
`{PREVIOUS_RMS_TO_EXISTING_BARE}` and maximum absolute log error
`{PREVIOUS_MAX_ABS_LOG_ERROR}` against existing bare predictions. That result
kept explicit warnings: hidden response remains, overfit risk remains,
reference-scheme limitations remain, and numerical closure was not achieved.

## Candidate Interpretation

The candidate reading is that the mass engine behaves more like a collective
curvature threshold response than an isolated single-mode spectral decay. In
this view, local mass thresholds contribute to a shared topographic curvature
field, and a mode opens only after its effective curvature passes a threshold.

```text
L_T T = S_total
L_T = nabla^2 - B*nabla^4
S_total = S_visible + S_internal_modes + S_boundary + S_interaction
```

Each mode contributes to and samples an effective field:

```text
K_i_eff = K_i_self + sum_j G_ij m_j + K_i_boundary + K_i_envelope
```

The candidate threshold-opening rule is:

```text
m_i = M_f * [K_i_eff - K_i_crit]_+^p * Z_i
```

where `[x]_+ = max(x,0)`. This is not an official mass formula.

## Branch Identity

The previous branch-threshold audit found branch identity and branch type to be
diagnostically important. Pure-fiber and pure-base modes may sit on special
threshold channels, while mixed modes retain a hidden response term. This
supports the candidate label:

`BRANCH_TYPE_CURVATURE_SPECIALNESS_CANDIDATE`

## Scale Compression

The strongest diagnostic law used a log threshold:

```text
S_eff ~ a * log(1 + N) - b_fiber*I_fiber - b_base*I_base + hidden_response
```

so:

```text
m_shape ~ (1+N)^(-a) * exp(b_fiber*I_fiber + b_base*I_base) * R_hidden
```

This suggests scale-compressed collective response, not a completed derivation.

## Topographic Stability

The fourth-order topographic operator supplies a natural place for envelope and
stability behavior. In this candidate layer, the fourth-order term damps
runaway short-scale response while allowing collective curvature envelopes.

## Guardrails

- Candidate only.
- No frozen predictions are changed.
- No official predictions are changed.
- No new official mass formula is introduced.
- Numerical closure is not claimed.
"""


def render_bridge_markdown() -> str:
    return f"""# Collective Curvature Mass-Engine Bridge

Status: `candidate_only`

The diagnostic law `{PREVIOUS_BEST_BRANCH_THRESHOLD_LAW}` is not an official
formula. It approximates the existing bare engine better than the failed
isolated heat-kernel baseline, but overfit risk and hidden response remain.

## Bridge

The diagnostic form:

```text
log_pred = A0 - a*log(1+N) + b_fiber*I_fiber + b_base*I_base
```

is consistent with a scale-compressed threshold response:

```text
m_shape ~ (1+N)^(-a) * exp(b_fiber*I_fiber + b_base*I_base) * R_hidden
```

The missing `R_hidden` term is the reason this bridge remains candidate-only.

## Candidate Fixed Point

The next derivation target is a self-consistent curvature fixed point:

```text
m_i = M_f * [K_i^0 + sum_j G_ij m_j - K_i_crit]_+^p * Z_i
```

or in matrix form:

```text
m = M * [K0 + G m - Kcrit]_+^p * Z
```

This sprint does not solve or fit that system as an official model. It only
records the bridge suggested by the prior branch-threshold diagnostics.

## Limitations

- `D_log_threshold_plus_type` remains diagnostic.
- Hidden response remains.
- Overfit risk remains.
- Reference-scheme limitations remain.
- No numerical closure is claimed.
"""


def render_dark_matter_markdown() -> str:
    tests = "\n".join(f"- {item}" for item in FUTURE_GRAVITY_TESTS)
    return f"""# Collective Curvature Dark-Matter Interpretation

Status: `candidate_only`

Claim labels:

- `COLLECTIVE_CURVATURE_DARK_MATTER_INTERPRETATION_CANDIDATE`
- `EFFECTIVE_DARK_MATTER_AS_CURVATURE_RESIDUE_CANDIDATE`
- `NO_DARK_MATTER_SOLUTION_CLAIM_GUARDRAIL`
- `EMPIRICAL_GRAVITY_TESTS_REQUIRED_GUARDRAIL`

## Candidate Interpretation

In the collective-curvature interpretation, the gravitational field follows the
largest stable collective curvature envelope generated by local mass-threshold
curvatures across available scales. The apparent dark matter distribution is the
residual between that collective curvature envelope and the curvature expected
from visible matter alone.

```text
K_obs = K_visible + K_collective
K_DM_eff = K_collective
rho_DM_eff = (1/(4*pi*G)) * nabla^2 Phi_collective
```

Equivalently, in diagnostics:

```text
K_DM_eff = K_obs - K_visible
```

## Guardrails

- Candidate only.
- This does not reject particle dark matter.
- This does not assert that galaxy rotation curves, lensing, clusters, the
  Bullet Cluster, CMB anisotropies, or structure growth are explained.
- This does not change BHSM mass predictions or frozen release values.

## Required Future Empirical Tests

{tests}
"""


def export_outputs(root: str | Path = ".") -> dict:
    root = Path(root)
    theory = root / "theory"
    theory.mkdir(exist_ok=True)
    payload = build_results_payload()
    (theory / "collective_curvature_threshold_layer.md").write_text(
        render_layer_markdown(), encoding="utf-8"
    )
    (theory / "collective_curvature_mass_engine_bridge.md").write_text(
        render_bridge_markdown(), encoding="utf-8"
    )
    (theory / "collective_curvature_dark_matter_interpretation.md").write_text(
        render_dark_matter_markdown(), encoding="utf-8"
    )
    (theory / "collective_curvature_threshold_results.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return payload


if __name__ == "__main__":
    export_outputs(Path(__file__).resolve().parents[1])
