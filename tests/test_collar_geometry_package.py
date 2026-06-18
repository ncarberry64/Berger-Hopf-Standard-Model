import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP_PATH = ROOT / "data" / "bhsm_numerical_input_closure_map.json"
THEORY_PATH = ROOT / "theory" / "theorem_discharge_collar_geometry_package.md"
NORMAL_THEORY = ROOT / "theory" / "theorem_discharge_normal_coupling_collar_convention.md"
VARIATION_THEORY = ROOT / "theory" / "theorem_discharge_scalar_topographic_boundary_variation.md"
DOC_PATH = ROOT / "docs" / "bhsm_numerical_input_closure_map.md"
STATUS_PATH = ROOT / "docs" / "current_bhsm_status.md"
CLAIM_TABLE = ROOT / "docs" / "claim_status_table.md"
BACKLOG = ROOT / "docs" / "open_blockers_backlog.md"


def load_map():
    return json.loads(MAP_PATH.read_text(encoding="utf-8"))


def entry_by_id(data, entry_id):
    for entry in data["entries"]:
        if entry["id"] == entry_id:
            return entry
    raise AssertionError(f"missing closure-map entry: {entry_id}")


def test_collar_geometry_objects_exist_in_closure_map():
    data = load_map()
    assert "collar_geometry_package" in data
    package = data["collar_geometry_package"]
    assert package["id"] == "PO-BH-55"
    assert package["status"] == "OPEN_LOCALIZABLE"

    expected = {
        "collar_coordinate_rho": "DERIVED_CONDITIONAL",
        "collar_measure": "OPEN_LOCALIZABLE",
        "normal_orientation": "OPEN_LOCALIZABLE",
        "inner_collar_edge_condition": "OPEN_LOCALIZABLE",
        "admissible_collar_variation_data": "OPEN_LOCALIZABLE",
        "robin_coefficients_A_B": "OPEN_LOCALIZABLE",
    }
    for entry_id, status in expected.items():
        assert entry_by_id(data, entry_id)["status"] == status
        assert any(dep["id"] == entry_id for dep in package["depends_on"])


def test_rnu_and_collar_convention_depend_on_explicit_collar_objects():
    data = load_map()
    rnu_deps = {dep["id"] for dep in data["R_nu_normal_coupling"]["depends_on"]}
    collar_deps = {dep["id"] for dep in data["normal_collar_convention"]["depends_on"]}
    expected_open = {
        "collar_measure",
        "normal_orientation",
        "inner_collar_edge_condition",
        "admissible_collar_variation_data",
    }
    assert expected_open <= rnu_deps
    assert "robin_coefficients_A_B" in rnu_deps
    assert "collar_coordinate_rho" in collar_deps
    assert expected_open <= collar_deps


def test_theorem_defines_thin_collar_coordinate():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "C_epsilon(partialB) = partialB x [0,epsilon]" in text
    assert "(Y^A, rho)" in text
    assert "n.grad Phi = partial_rho Phi" in text
    assert "DERIVED_CONDITIONAL" in text


def test_theorem_includes_measure_candidate_and_jacobian_status():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "dV_collar = J(Y,rho) dA d rho" in text
    assert "J(Y,0)=1" in text
    assert "`collar_measure`" in text
    assert "The measure form is localized, but `J` is not derived" in text


def test_theorem_tracks_orientation_sign_effect():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "n = s_n partial_rho" in text
    assert "s_n in {+1,-1}" in text
    assert "s_n lambda_nu Phi partial_rho Phi" in text
    assert "`normal_orientation`" in text


def test_theorem_lists_inner_edge_options():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "rho=epsilon" in text
    assert "Dirichlet" in text
    assert "Neumann" in text
    assert "subsurface matching" in text
    assert "decay/localization" in text


def test_theorem_lists_admissible_variation_data():
    text = THEORY_PATH.read_text(encoding="utf-8")
    assert "delta Phi at rho=0" in text
    assert "delta partial_rho Phi at rho=0" in text
    assert "delta Phi at rho=epsilon" in text
    assert "delta partial_rho Phi at rho=epsilon" in text
    assert "the BHSM-admissible choice is not yet derived" in text


def test_theorem_localizes_robin_coefficients_without_values():
    data = load_map()
    text = THEORY_PATH.read_text(encoding="utf-8")
    robin = entry_by_id(data, "robin_coefficients_A_B")
    assert "R_nu -> A_nu Phi + B_nu n.grad Phi" in text
    assert "A_nu,B_nu = F(lambda_nu, epsilon, J, s_n, edge data)" in text
    assert "No numerical values are derived" in text
    assert robin["status"] == "OPEN_LOCALIZABLE"
    assert "post-comparison Robin coefficient fit" in robin["forbidden_inputs"]


def test_forbidden_inputs_cover_neutrino_pmns_anomaly_and_collar_fits():
    data = load_map()
    package_forbidden = set(data["collar_geometry_package"]["forbidden_inputs"])
    for forbidden in (
        "observed neutrino masses",
        "observed neutrino mass splittings",
        "PMNS angles",
        "PMNS CP phase",
        "fitted FTL/anomaly data",
        "post-comparison collar width fit",
        "post-comparison orientation fit",
        "post-comparison edge-condition fit",
        "post-comparison Robin coefficient fit",
    ):
        assert forbidden in package_forbidden
    assert any("collar coordinate, measure, orientation" in route for route in data["forbidden_fit_routes"])


def test_docs_preserve_public_status_and_collar_package_language():
    combined = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (
            THEORY_PATH,
            NORMAL_THEORY,
            VARIATION_THEORY,
            DOC_PATH,
            STATUS_PATH,
            CLAIM_TABLE,
            BACKLOG,
        )
    )
    assert "structural architecture integrated conditional; numerical closure open" in combined
    assert "The collar geometry package has been localized as the missing convention set" in combined
    assert "Robin coefficients remain open unless a full collar convention is derived" in combined
    forbidden = [
        "neutrino masses are predicted",
        "neutrino mass prediction is achieved",
        "PMNS numerical prediction is achieved",
        "experimental FTL is claimed",
        "local causality violation is claimed",
        "Robin coefficients are fitted",
        "lambda_nu is derived from observed neutrino masses",
    ]
    for phrase in forbidden:
        assert phrase not in combined


def test_public_status_flags_and_po_bh_55_labels_remain_guarded():
    data = load_map()
    assert data["status"] == "STRUCTURAL_ARCHITECTURE_INTEGRATED_CONDITIONAL_NUMERICAL_CLOSURE_OPEN"
    assert data["full_numerical_sm_prediction_derived"] is False
    assert data["replacement_readiness_achieved"] is False
    assert data["frozen_predictions_changed"] is False
    assert data["official_predictions_changed"] is False
    assert "PO_BH_55_COLLAR_GEOMETRY_PACKAGE_LOCALIZED" in data["verdict_labels"]
    assert "COLLAR_GEOMETRY_PACKAGE_OPEN" in data["verdict_labels"]
    assert "ROBIN_COEFFICIENTS_A_B_OPEN" in data["verdict_labels"]
