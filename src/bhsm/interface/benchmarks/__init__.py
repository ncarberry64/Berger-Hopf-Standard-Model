"""Reproducible, claim-bounded BHSM performance microbenchmarks."""

from .coordinate_methods import (
    KERNELS,
    benchmark_kernel,
    bhsm_boundary_vectorized,
    branchy_cylindrical_scalar,
    cylindrical_vectorized_control,
    generate_kinematic_dataset,
    validate_kernel_equivalence,
)

__all__ = [
    "KERNELS",
    "benchmark_kernel",
    "bhsm_boundary_vectorized",
    "branchy_cylindrical_scalar",
    "cylindrical_vectorized_control",
    "generate_kinematic_dataset",
    "validate_kernel_equivalence",
]
