"""Focused classification, identity and provenance tests; no model imports."""
import copy
import importlib.util
import json
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location("inventory_reviewed",HERE/"build_inventory_v3.py")
M=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)

class InventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.freeze=json.loads((HERE/"INPUT_FREEZE_v3.json").read_bytes())
        cls.raw=M.load_frozen(cls.freeze)
        cls.doc=M.build(cls.freeze)
        cls.events={e["event_id"]:e for e in cls.doc["events"]}
    def test_01_exact_union_and_four_primary_identity_pairs(self):
        self.assertEqual(len(self.events),155)
        self.assertEqual({(p["pilot_event_id"],p["parallax_event_id"]) for p in self.doc["identity_crossmatch"]["pairs"]},
            {("OGLE3-ULENS-0264","OGLE3-ULENS-PAR-07"),("OGLE3-ULENS-0568","OGLE3-ULENS-PAR-21"),("OGLE3-ULENS-2122","OGLE3-ULENS-PAR-37"),("OGLE3-ULENS-3404","OGLE3-ULENS-PAR-17")})
        self.assertTrue(all(p["separation_arcsec"]<1e-8 for p in self.doc["identity_crossmatch"]["pairs"]))
    def test_02_native_pilot_outcomes_are_unchanged(self):
        original=json.loads(self.raw["pilot_results"])
        self.assertEqual(len(original),100)
        for p in original:
            self.assertEqual(self.events[p["event_id"]]["source_records"]["pilot_result"],p)
        c=self.doc["metadata"]["counts"]
        self.assertEqual((c["pilot_inadequate_simple_model"],c["pilot_scalar_nonrejected"],c["pilot_frozen_followup_targets"]),(89,11,2))
    def test_03_scalar_nonrejection_does_not_promote_nine_flagged_events(self):
        original=json.loads(self.raw["pilot_results"])
        for p in original:
            if p["status"]!="PHOTOMETRIC_MODEL_INADEQUATE" and not p["followup_eligible"]:
                self.assertEqual(self.events[p["event_id"]]["tier"],"REVIEW_REQUIRED")
    def test_04_only_three_explicit_search_targets_and_no_candidate_claim(self):
        self.assertEqual({e["event_id"] for e in self.events.values() if e["tier"]=="BLACK_HOLE_SEARCH_TARGET"},
            {"OGLE3-ULENS-0585","OGLE3-ULENS-3092","OGLE3-ULENS-PAR-13"})
        self.assertFalse(any(e["tier"] in {"BLACK_HOLE_CANDIDATE","STRONGLY_SUPPORTED_BLACK_HOLE_IDENTIFICATION"} for e in self.events.values()))
    def test_05_later_literature_conflict_is_not_erased(self):
        p=self.events["OGLE3-ULENS-PAR-02"]
        self.assertEqual(p["tier"],"SUPPORTED_LENSING_EVENT")
        self.assertTrue(any("0.9" in x.get("caution","") for x in p["literature_assessment"]["interpretations"]))
        q=self.events["OGLE3-ULENS-PAR-13"]
        self.assertIn("GAIA_SOURCE_ASTROMETRIC_SOLUTION_UNRELIABLE",q["quality_flags"])
        self.assertTrue(any("alternative OGLE" in x.get("caution","") for x in q["literature_assessment"]["interpretations"]))
    def test_06_all_modes_and_native_table_versions_retained(self):
        par=[e for e in self.events.values() if "WYRZYKOWSKI_2016_PARALLAX_59" in e["cohorts"]]
        self.assertEqual(len(par),59)
        self.assertEqual(sum(len(e["source_records"]["parallax2016_all_degenerate_fit_modes"]) for e in par),142)
        c=self.doc["metadata"]["counts"]
        self.assertEqual((c["historical_dark_remnant_consistent"],c["older_classA"],c["older_classB"],c["older_native_unavailable"]),(13,23,3,33))
        self.assertTrue(all(e["native_data_availability"]["raw_clock_scale"] is None for e in par))
        self.assertTrue(all(not e["native_data_availability"]["extra_error_rescaling_applied"] for e in par))
    def test_07_unknown_quantities_and_epoch_stay_null(self):
        for e in self.doc["events"]+self.doc["benchmarks"]:
            self.assertTrue(all(v is None for v in e["lens"].values()))
            self.assertIsNone(e["source_direction"]["epoch"])
            self.assertFalse(e["map_eligibility"]["three_dimensional"])
            self.assertFalse(e["map_eligibility"]["propagate_position"])
    def test_08_coordinates_sign_units_and_poles(self):
        self.assertEqual(M.angle("00:00:00","-00:30:00"),(0.,-0.5))
        self.assertEqual(M.angle("12:00:00","+90:00:00"),(180.,90.))
        self.assertAlmostEqual(M.separation((359.999,0),(0.001,0)),7.2,places=8)
        for ra,de in [("24:00:00","0:0:0"),("1:60:0","0:0:0"),("1:0:0","90:0:1")]:
            with self.assertRaises(ValueError): M.angle(ra,de)
    def test_09_source_tamper_fails_before_build(self):
        f=copy.deepcopy(self.freeze); f["sources"]["pilot_results"]["snapshot_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"Source integrity mismatch"): M.build(f)
    def test_10_identity_conflict_fails_closed(self):
        raws=copy.copy(self.raw); x=json.loads(raws["cohort59"])
        x["events"][6]["aliases"].append("OGLE-2007-BLG-057")
        raws["cohort59"]=M.json_bytes(x)
        with patch.object(M,"load_frozen",return_value=raws):
            with self.assertRaisesRegex(ValueError,"Identity/direction contradiction"): M.build(self.freeze)
    def test_11_replay_is_deterministic_and_inputs_still_match(self):
        self.assertEqual(M.json_bytes(self.doc),M.json_bytes(M.build(self.freeze)))
        self.assertEqual(M.load_frozen(self.freeze),self.raw)
    def test_12_benchmark_is_separate_literature_label_not_engine_acceptance(self):
        self.assertEqual(len(self.doc["benchmarks"]),1)
        b=self.doc["benchmarks"][0]
        self.assertEqual(b["classification_source"],"LITERATURE")
        self.assertFalse(b["accepted_engine_black_hole"])
        self.assertEqual(b["tracker_recovery_status"],"NOT_ESTABLISHED_NUMERICAL_STAGE_UNRESOLVED")
        self.assertNotIn(b["event_id"],self.events)
    def test_13_benchmark_changed_status_requires_review(self):
        raws=copy.copy(self.raw); x=json.loads(raws["benchmark_recovery_outcome"])
        x["accepted_black_hole_interpretation"]=True; raws["benchmark_recovery_outcome"]=M.json_bytes(x)
        with patch.object(M,"load_frozen",return_value=raws):
            with self.assertRaisesRegex(ValueError,"Re-review benchmark"): M.build(self.freeze)
    def test_14_no_promotion_of_search_bounds_or_motion(self):
        changed=copy.deepcopy(self.doc); changed["events"][0]["lens"]["mass_msun"]=3.0
        with self.assertRaisesRegex(ValueError,"Unidentified lens quantity"): M.validate_inventory(changed)
        changed=copy.deepcopy(self.doc); changed["events"][0]["map_eligibility"]["propagate_position"]=True
        with self.assertRaisesRegex(ValueError,"localization promotion"): M.validate_inventory(changed)
    def test_15_metadata_rebuild_relocated_with_original_source_access_forbidden(self):
        with tempfile.TemporaryDirectory(prefix="atlas_metadata_relocation_",dir=HERE) as folder:
            destination=Path(folder)
            shutil.copytree(HERE/"metadata_sources_v3",destination/"metadata_sources_v3")
            original_reader=Path.read_bytes
            def confined_reader(path):
                if not path.resolve().is_relative_to(destination.resolve()):
                    raise AssertionError("Offline rebuild attempted to read original source: "+str(path))
                return original_reader(path)
            with patch.object(Path,"read_bytes",confined_reader):
                replay=M.build(self.freeze,destination)
            self.assertEqual(M.json_bytes(replay),M.json_bytes(self.doc))
    def test_16_snapshot_contains_no_native_observations_or_article_html(self):
        benchmark=json.loads(self.raw["benchmark_input"])
        self.assertEqual(set(benchmark),{"schema","data_version","target","sky_position_icrs_deg"})
        self.assertNotIn(b"<html",self.raw["reanalysis2021"].lower())
        self.assertEqual(len(self.raw["catalog2015"].decode().splitlines()),100)
        self.assertTrue(all(r["snapshot_path"] is None for k,r in self.freeze["sources"].items() if k.startswith("older_native:")))
    def test_17_availability_audit_mismatch_cannot_be_silently_accepted(self):
        raws=copy.copy(self.raw); a=json.loads(raws["native_availability_audit"])
        a["records"]["OGLE3-ULENS-PAR-07"]["numeric_rows"]+=1
        raws["native_availability_audit"]=M.json_bytes(a)
        with patch.object(M,"load_frozen",return_value=raws):
            with self.assertRaisesRegex(ValueError,"availability metadata contradiction"): M.build(self.freeze)
    def test_18_optional_original_reacquisition_hash_guard(self):
        source=self.freeze["sources"]["catalog2016"]
        M.load_frozen(self.freeze,original_source_map={"catalog2016":HERE/source["snapshot_path"]})
        with self.assertRaisesRegex(ValueError,"Original source integrity mismatch"):
            M.load_frozen(self.freeze,original_source_map={"catalog2016":HERE/self.freeze["sources"]["pilot_results"]["snapshot_path"]})

if __name__=="__main__": unittest.main(verbosity=2)
