"""Constants, assumptions, empirical references, and supplied ledgers."""

from __future__ import annotations

from fractions import Fraction
from math import pi

S_OVERLAP = 1.0 / (4.0 * pi)
BERGER_A_DEFAULT = 1.0

HIGGS_HYPERCHARGE = Fraction(1, 2)

PLANCK_ENERGY_GEV = 1.220890e19
ALPHA_INV_LOW_ENERGY = 137.035999084
V_HIGGS_EMPIRICAL_GEV = 246.21965

ALPHA_EM_INV_EW_EMPIRICAL = 127.95
SIN2_THETA_W_EMPIRICAL = 0.23122
ALPHA3_MZ_EMPIRICAL = 0.1179

EMPIRICAL_MASS_RATIOS = {
    "charged_leptons": {
        "middle": 105.6583755 / 1776.86,
        "light": 0.510998950 / 1776.86,
    },
    "up_quarks": {
        "middle": 1.27 / 172.69,
        "light": 0.00216 / 172.69,
    },
    "down_quarks": {
        "middle": 0.0934 / 4.18,
        "light": 0.00467 / 4.18,
    },
}

MODE_LEDGER = {
    "charged_leptons": {
        "heavy": (0, 0),
        "middle": (5, 2),
        "light": (9, 3),
    },
    "up_quarks": {
        "heavy": (0, 0),
        "middle": (6, 0),
        "light": (10, 1),
    },
    "down_quarks": {
        "heavy": (0, 0),
        "middle": (6, 3),
        "light": (8, 2),
    },
}

