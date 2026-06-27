"""Physical conversions and source-traced BHSM interface defaults."""

from __future__ import annotations

from math import pi

from constants import ALPHA_INV_LOW_ENERGY, S_OVERLAP

# The electron-volt/joule relation and c are exact SI definitions.
GEV_PER_EV = 1.0e-9
EV_PER_GEV = 1.0e9
JOULE_PER_GEV = 1.602176634e-10
C_LIGHT = 299_792_458.0

# Derived from E = m c^2 and the exact joule/eV and c definitions.
KG_PER_GEV_C2 = JOULE_PER_GEV / C_LIGHT**2


def default_bhsm_constants() -> dict[str, float]:
    """Return existing BHSM constants without introducing new model inputs."""

    return {
        "S": S_OVERLAP,
        "tau": 1.0 / (4.0 * pi ** 1.5),
        "sigma": 4.0 * pi ** 2.5,
        "kappa_H": 64.0 * pi**5,
        "anisotropy_alpha_anchored": ALPHA_INV_LOW_ENERGY / (12.0 * pi**2),
    }
