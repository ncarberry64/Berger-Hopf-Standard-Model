from __future__ import annotations

from bhsm.interface.neutrino_scale import (
    build_neutral_scale_candidates,
    search_neutral_scale_sources,
)


def test_local_candidate_search_is_offline_and_fail_closed() -> None:
    candidates = {row.candidate_key: row for row in build_neutral_scale_candidates()}
    assert candidates["tau"].status == "DIMENSIONLESS_ARTIFACT"
    assert candidates["sigma"].status == "DIMENSIONLESS_ARTIFACT"
    assert candidates["tau"].can_map_to_eV is False
    assert candidates["sigma"].can_map_to_eV is False
    assert candidates["w_mass_calibration"].status == "EMPIRICAL_FORBIDDEN"
    assert candidates["electron_neutrino_upper_limit"].status == "EMPIRICAL_FORBIDDEN"
    assert not any(row.status == "DIMENSIONFUL_ARTIFACT" for row in candidates.values())


def test_source_inventory_records_machine_readable_provenance() -> None:
    sources = search_neutral_scale_sources()
    assert any(row.source_key == "neutral_kernel" and row.discovered for row in sources)
    assert any(row.source_category == "EMPIRICAL_FORBIDDEN" for row in sources)

