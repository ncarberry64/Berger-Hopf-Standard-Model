.PHONY: bhsm-hep-preflight bhsm-download-assets bhsm-map-wolfram bhsm-map-feynrules bhsm-map-madgraph bhsm-live-validation bhsm-ufo-export bhsm-madgraph-smoke bhsm-hep-report

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

