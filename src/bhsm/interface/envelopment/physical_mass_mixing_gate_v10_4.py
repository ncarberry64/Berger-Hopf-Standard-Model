"""Physical mass, CKM, PMNS, and M4 readout gate for BHSM v10.4."""

from __future__ import annotations

from typing import Any


MASS_MIXING_VERDICT = "BHSM_PHYSICAL_MASS_AND_MIXING_READOUT_REMAINS_FAIL_CLOSED"


def mass_mixing_payload() -> dict[str, Any]:
    return {
        "artifact": "BHSM_generation_mass_mixing_gate_v10_4",
        "mass_functional": "m_fi=mu_global epsilon_f(q_f,theta_fi)",
        "mu_global": None,
        "cycle_energies": None,
        "phase_dependence": None,
        "mass_ratios": None,
        "frozen_screen_mass_ratios_changed": False,
        "historical_screen_values_retained": True,
        "physical_mass_values": None,
        "Theta_f_status": "frozen candidate cycle-transfer/residue operator; exact action origin open",
        "G_f": None,
        "Q_f": None,
        "K_ud": None,
        "Gram_positive": None,
        "full_rank_pullbacks": None,
        "CKM": None,
        "PMNS": None,
        "matrices_printed": False,
        "measured_particle_inputs_used": [],
        "M4_reduction": {
            "map": "R_M4:Phi_core/3m -> (g_mu_nu,A_mu,psi_f,H,J_mu)_effective",
            "field_dictionary_complete": False,
            "canonical_normalization_complete": False,
            "gauge_Lorentz_representations_complete": False,
            "interaction_vertices_complete": False,
            "current_ownership_complete": False,
            "collider_runtime": None,
            "effective_fields_retained": True,
            "fields": [
                {"field": "g_mu_nu", "parent_source": "M8/M5 metric pullback conditional", "Lorentz": "symmetric tensor", "gauge": "Diff(M4)", "normalization": "incomplete common reduction", "kinetic": "intrinsic M4 term retained", "vertex": None, "mass": "massless metric layer", "current_owner": "intrinsic M4"},
                {"field": "A_mu", "parent_source": "Hopf connections plus retained SM layer; full bridge open", "Lorentz": "vector", "gauge": "retained SM gauge representations", "normalization": "action attachment incomplete", "kinetic": "conditional", "vertex": None, "mass": None, "current_owner": "intrinsic M4/common parent incomplete"},
                {"field": "psi_f", "parent_source": None, "Lorentz": "chiral spinor ledger retained", "gauge": "frozen SM representation ledger", "normalization": None, "kinetic": "intrinsic M4 retained", "vertex": None, "mass": None, "current_owner": "intrinsic M4"},
                {"field": "H", "parent_source": "topographic/scalar identification conditional", "Lorentz": "scalar doublet convention retained", "gauge": "retained electroweak layer", "normalization": None, "kinetic": "intrinsic M4 retained", "vertex": None, "mass": None, "current_owner": "intrinsic M4"},
                {"field": "J_mu", "parent_source": "effective composite current", "Lorentz": "vector current", "gauge": "representation dependent", "normalization": None, "kinetic": "not independent", "vertex": None, "mass": None, "current_owner": "cross-stratum ownership incomplete"},
            ],
        },
        "reason": "no q_D, three-mode orbit, global unit, family tangent maps, or complete common currents",
        "verdict": MASS_MIXING_VERDICT,
        "validation_passed": True,
    }
