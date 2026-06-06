"""Symbolic Standard Model Lagrangian builders for the BHSM model.

These helpers return manuscript-readable strings only. They do not implement
full quantum-field-theory algebra.
"""

from __future__ import annotations


def gauge_kinetic_terms() -> str:
    """Return symbolic gauge kinetic terms."""

    return (
        r"-\frac14 G_{\mu\nu}^a G^{a\mu\nu} "
        r"-\frac14 W_{\mu\nu}^i W^{i\mu\nu} "
        r"-\frac14 B_{\mu\nu} B^{\mu\nu}"
    )


def fermion_kinetic_terms(fields: tuple[str, ...] = ("Q_L", "u_R", "d_R", "L_L", "e_R")) -> str:
    """Return symbolic fermion kinetic terms for the supplied fields."""

    return " + ".join(rf"\bar{{{field}}} i\gamma^\mu D_\mu {field}" for field in fields)


def higgs_kinetic_and_potential() -> str:
    """Return symbolic Higgs kinetic and potential terms."""

    return (
        r"(D_\mu H)^\dagger(D^\mu H) "
        r"-[-\mu^2 H^\dagger H + \lambda(H^\dagger H)^2]"
    )


def yukawa_terms() -> str:
    """Return symbolic charged-sector Yukawa terms."""

    return (
        r"-\bar Q_L Y_d H d_R "
        r"-\bar Q_L Y_u \tilde H u_R "
        r"-\bar L_L Y_e H e_R + h.c."
    )


def effective_neutrino_extension() -> str:
    """Return symbolic Weinberg-operator effective neutrino extension."""

    return r"\frac{c_{ij}}{\Lambda}(L_i H)(L_j H)"


def topographic_internal_correction() -> str:
    """Return symbolic topographic/internal correction placeholder."""

    return r"\mathcal L_{\rm topo/int}"


def full_symbolic_lagrangian(include_neutrino_extension: bool = True) -> dict[str, str]:
    """Return the symbolic low-energy Lagrangian blocks."""

    blocks = {
        "gauge_kinetic": gauge_kinetic_terms(),
        "fermion_kinetic": fermion_kinetic_terms(),
        "higgs": higgs_kinetic_and_potential(),
        "yukawa": yukawa_terms(),
        "topographic_internal": topographic_internal_correction(),
    }
    if include_neutrino_extension:
        blocks["effective_neutrino"] = effective_neutrino_extension()
    return blocks
