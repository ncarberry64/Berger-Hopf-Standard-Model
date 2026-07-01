.PHONY: bhsm-hep-preflight bhsm-download-assets bhsm-map-wolfram bhsm-map-feynrules bhsm-map-madgraph bhsm-live-validation bhsm-ufo-export bhsm-madgraph-smoke bhsm-hep-report reviewer-smoke reviewer-full reviewer-cern-open-data reviewer-invariants reviewer-claims-audit reviewer-engine-report reviewer-physics-status

bhsm-hep-preflight:
	python scripts/setup/check_bhsm_hep_environment.py

bhsm-download-assets:
	python scripts/setup/download_allowed_assets.py

bhsm-map-wolfram:
	python scripts/setup/map_wolfram_runtime.py

bhsm-map-feynrules:
	python scripts/setup/install_or_map_feynrules.py

bhsm-map-madgraph:
	python scripts/setup/install_or_map_madgraph.py

bhsm-live-validation:
	python tools/run_phase_three_n_execution_gate_v1_6.py

bhsm-ufo-export:
	python scripts/feynrules/run_ufo_export_if_validated.py

bhsm-madgraph-smoke:
	python scripts/madgraph/run_minimal_ufo_smoke_if_available.py

bhsm-hep-report:
	python tools/export_institutional_hep_handoff_manifest_v1_7.py

reviewer-smoke:
	python -m pytest -q tests/test_engine_invariant_preservation.py tests/test_engine_physics_status_separation.py

reviewer-full:
	python -m pytest -q

reviewer-cern-open-data:
	python -m bhsm.interface.benchmarks.cern_open_data_benchmark --download --summary

reviewer-invariants:
	python -m bhsm.interface engine-invariants --format json

reviewer-claims-audit:
	python tools/audit_forbidden_claims.py

reviewer-engine-report:
	python -m bhsm.interface engine-status --format markdown

reviewer-physics-status:
	python -m bhsm.interface physics-status --format markdown

