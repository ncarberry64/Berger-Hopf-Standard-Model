"""Scientific regression and correction tests for the portable reproduction."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "audits" / "bhsm_coupled_event_20261113.py"
spec = importlib.util.spec_from_file_location("coupled_event", SCRIPT)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class CoupledEventReproduction(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = audit.load_inputs()
        cls.result = audit.evaluate(cls.data)

    def test_reviewed_rows_and_positive_energies(self):
        result = self.result
        self.assertEqual(result["status"], "PASS_RETAINED_PARTIAL_ROWS")
        self.assertLess(result["max_abs_residual"], 2e-9)
        for key in ("electric_energy", "magnetic_energy", "total_energy"):
            self.assertGreater(result[key], 0)
            self.assertAlmostEqual(result[key], self.data["independent_reference"][key], delta=2e-9)

    def test_omitting_normal_momentum_contact_gives_false_failure(self):
        result = self.result
        self.assertGreater(abs(result["partial_material_Lx"]), 40)
        self.assertLess(abs(result["full_normal_Euler"]), 2e-9)
        self.assertLess(abs(result["normal_contact_error"]), 2e-7)
        self.assertAlmostEqual(result["direct_dt_LU"], result["partial_material_Lx"], delta=2e-7)

    def test_amplitude_change_breaks_retained_constraint_closure(self):
        data = copy.deepcopy(self.data)
        data["active_carriers"][0]["amplitude"] *= 1.01
        result = audit.evaluate(data)
        self.assertEqual(result["status"], "RETAINED_ROWS_NOT_CLOSED")
        self.assertGreater(result["max_abs_residual"], 1e-3)

    def test_discarding_magnetic_fields_breaks_normal_balance(self):
        data = copy.deepcopy(self.data)
        for row in data["active_carriers"]:
            if row["kind"] == "M":
                row["amplitude"] = 0
        result = audit.evaluate(data)
        self.assertEqual(result["status"], "RETAINED_ROWS_NOT_CLOSED")
        self.assertGreater(abs(result["full_normal_Euler"]), 1)

    def test_radius_force_remains_open_despite_thirteen_row_closure(self):
        result = self.result
        self.assertAlmostEqual(result["radius_7T_minus_5V_minus_xF"],
                               self.data["independent_reference"]["radius_force"], delta=2e-8)
        self.assertGreater(result["radius_7T_minus_5V_minus_xF"], 40)
        self.assertFalse(result["scope"]["full_metric_solution"])
        self.assertFalse(result["scope"]["physical_mass_gap"])

    def test_cli_is_byte_deterministic_and_optional_output_matches(self):
        first = subprocess.check_output([sys.executable, str(SCRIPT)])
        second = subprocess.check_output([sys.executable, str(SCRIPT)])
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "PASS_RETAINED_PARTIAL_ROWS")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/"result.json"
            subprocess.run([sys.executable, str(SCRIPT), "--output", str(target)], check=True)
            # stdout may use the operating system's newline translation.
            self.assertEqual(target.read_text(encoding="utf-8"), first.decode().replace("\r\n", "\n"))

    def test_inputs_have_source_relative_provenance_and_reject_overlap(self):
        raw = json.dumps(self.data)
        self.assertNotIn("C:\\", raw)
        self.assertNotIn("Users", raw)
        self.assertTrue(all(not Path(path).is_absolute() for path in self.data["provenance"]))
        data = copy.deepcopy(self.data)
        data["active_carriers"][1]["center"] = data["active_carriers"][0]["center"]
        with self.assertRaises(ValueError):
            audit.evaluate(data)


if __name__ == "__main__":
    unittest.main()
