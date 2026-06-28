"""Exact rational audit of the artifact-backed neutral kernel."""

from __future__ import annotations

from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

from ..neutrino_propagation.neutral_kernel import load_neutral_kernel
from ..neutrino_scale.common import repository_path
from .common import NeutralKernelExactAudit, NeutralQuadraticForm, guard_fields


def _fraction(value: float) -> Fraction:
    return Fraction(str(value)).limit_denominator(1_000_000)


def _fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def _exact_matrix(numeric: tuple[tuple[float, ...], ...]) -> tuple[tuple[Fraction, ...], ...]:
    return tuple(tuple(_fraction(value) for value in row) for row in numeric)


def _det3(matrix: tuple[tuple[Fraction, ...], ...]) -> Fraction:
    a, b, c = matrix[0]
    d, e, f = matrix[1]
    g, h, i = matrix[2]
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def _characteristic_coefficients(
    matrix: tuple[tuple[Fraction, ...], ...],
) -> tuple[Fraction, Fraction, Fraction, Fraction]:
    trace = sum(matrix[i][i] for i in range(3))
    trace_square = sum(matrix[i][j] * matrix[j][i] for i in range(3) for j in range(3))
    second = (trace * trace - trace_square) / 2
    return Fraction(1), -trace, second, -_det3(matrix)


def _polynomial_text(coefficients: tuple[Fraction, ...]) -> str:
    labels = ("lambda^3", "lambda^2", "lambda", "1")
    terms: list[str] = []
    for coefficient, label in zip(coefficients, labels):
        if coefficient == 0:
            continue
        magnitude = abs(coefficient)
        factor = "" if magnitude == 1 and label != "1" else _fraction_text(magnitude)
        body = factor if label == "1" else (f"{factor}*{label}" if factor else label)
        if not terms:
            terms.append(f"-{body}" if coefficient < 0 else body)
        else:
            terms.append(f" {'-' if coefficient < 0 else '+'} {body}")
    return "".join(terms)


def _quadratic_form_text(matrix: tuple[tuple[Fraction, ...], ...]) -> str:
    terms: list[str] = []
    for i in range(3):
        if matrix[i][i]:
            terms.append(f"{_fraction_text(matrix[i][i])}*x{i + 1}^2")
        for j in range(i + 1, 3):
            coefficient = 2 * matrix[i][j]
            if coefficient:
                terms.append(f"{_fraction_text(coefficient)}*x{i + 1}*x{j + 1}")
    return " + ".join(terms)


def _base_payload(audit: NeutralKernelExactAudit) -> dict[str, Any]:
    payload = audit.to_dict()
    payload.pop("candidate_key")
    payload.pop("status")
    payload.pop("claim_boundary")
    payload.pop("remaining_missing_object")
    payload.pop("source_artifact")
    return payload


def audit_neutral_kernel_exact(
    repository: str | Path | None = None,
) -> NeutralKernelExactAudit:
    root = repository_path(repository)
    kernel = load_neutral_kernel(root)
    numeric = tuple(tuple(float(value) for value in row) for row in kernel.matrix)
    exact = _exact_matrix(numeric)
    coefficients = _characteristic_coefficients(exact)
    polynomial = _polynomial_text(coefficients)
    array = np.asarray(numeric, dtype=float)
    eigenvalues, eigenvectors = np.linalg.eigh(array)
    raw_values = tuple(float(value) for value in eigenvalues)
    raw_psd = min(raw_values) >= -1.0e-12
    negative_direction = None if raw_psd else tuple(float(value) for value in eigenvectors[:, 0])
    exact_roots = tuple(f"RootOf({polynomial}, {index})" for index in range(3))
    exact_text = tuple(tuple(_fraction_text(value) for value in row) for row in exact)
    return NeutralKernelExactAudit(
        candidate_key="neutral_kernel_exact_audit",
        status="RAW_KERNEL_POSITIVE_SEMIDEFINITE" if raw_psd else "RAW_KERNEL_NOT_POSITIVE_SEMIDEFINITE",
        kernel_matrix_exact=exact_text,
        kernel_matrix_numeric=numeric,
        characteristic_polynomial=polynomial,
        raw_eigenvalues_exact=exact_roots,
        raw_eigenvalues_numeric=raw_values,
        raw_psd=raw_psd,
        negative_eigendirection=negative_direction,
        admissible_domain_defined=False,
        admissible_domain_constraints=(),
        projection_matrix=None,
        projected_kernel=None,
        projected_eigenvalues=(),
        projected_psd=None,
        quadratic_form=_quadratic_form_text(exact),
        minimum_on_admissible_domain=None,
        counterexample={
            "domain": "raw_full_vector_space",
            "vector": negative_direction,
            "quadratic_value": raw_values[0],
        } if negative_direction is not None else None,
        thresholding_used=False,
        positivity_proven_without_thresholding=False,
        counterexample_found=negative_direction is not None,
        claim_boundary="The exact raw audit is a full-vector-space result. It does not decide positivity on a separately justified response cone.",
        remaining_missing_object="explicit admissible neutral domain",
        source_artifact=kernel.source_artifact,
        **guard_fields(),
    )


def build_neutral_quadratic_form(
    repository: str | Path | None = None,
) -> NeutralQuadraticForm:
    audit = audit_neutral_kernel_exact(repository)
    return NeutralQuadraticForm(
        candidate_key="neutral_quadratic_form",
        status=audit.status,
        claim_boundary="The rational quadratic form is exact for the artifact-backed kernel; its sign depends on the stated domain.",
        remaining_missing_object="admissible-domain sign analysis",
        termwise_nonnegative_on_domain=False,
        **_base_payload(audit),
    )


__all__ = ["audit_neutral_kernel_exact", "build_neutral_quadratic_form", "_base_payload"]
