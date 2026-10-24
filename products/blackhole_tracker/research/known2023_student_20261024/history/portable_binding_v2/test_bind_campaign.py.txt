"""Portable binding only, with invented input and no provider imports or fitting."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import bind_campaign as binding

ROOT=Path(__file__).resolve().parent

class BindingControls(unittest.TestCase):
    def test_source_verification_no_scientific_import(self):
        with patch.object(binding,'actual_runtime',side_effect=AssertionError('No runtime/science work needed')):
            self.assertTrue(binding.verify_sources()['sources_verified'])

    def test_invented_prepare_in_spaced_fresh_path_and_verify(self):
        with tempfile.TemporaryDirectory()as tmp:
            output=Path(tmp)/'new portable output'
            record=binding.prepare(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json','WHOLLY_INVENTED',output,runtime=binding.RUNTIME)
            self.assertEqual(record['native_or_model_calls'],0)
            self.assertFalse(record['scientific_acceptance'])
            self.assertTrue(binding.verify_existing(output/'POINT_FREEZE.json')['all_bound_bytes_verified'])
            frozen=json.loads((output/'POINT_FREEZE.json').read_text())
            self.assertEqual(frozen['configuration'],binding.CONFIG)

    def test_existing_output_preserved(self):
        with tempfile.TemporaryDirectory()as tmp:
            output=Path(tmp)/'old';output.mkdir();(output/'prior').write_bytes(b'untouched')
            with self.assertRaises(FileExistsError):binding.prepare(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json','WHOLLY_INVENTED',output,runtime=binding.RUNTIME)
            self.assertEqual({p.name:p.read_bytes()for p in output.iterdir()},{'prior':b'untouched'})

    def test_runtime_refusal_before_output(self):
        with tempfile.TemporaryDirectory()as tmp:
            output=Path(tmp)/'never_created'
            with self.assertRaises(ValueError):binding.prepare(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json','WHOLLY_INVENTED',output,runtime=dict(binding.RUNTIME,python='3.14.3'))
            self.assertFalse(output.exists())

    def test_invalid_native_namespace_and_registry_rejected(self):
        raw=(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json').read_bytes()
        with self.assertRaises(ValueError):binding.verify_input(raw,'AUTHENTIC2023',{})
        with self.assertRaises(ValueError):binding.verify_input(raw,'WHOLLY_INVENTED',{'wholly_invented_sha256':[]})

    def test_existing_binding_changed_input_refused(self):
        with tempfile.TemporaryDirectory()as tmp:
            copied=Path(tmp)/'input';copied.write_bytes((ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json').read_bytes())
            output=Path(tmp)/'new'
            binding.prepare(copied,'WHOLLY_INVENTED',output,runtime=binding.RUNTIME)
            copied.write_bytes(copied.read_bytes()+b' ')
            with self.assertRaises(ValueError):binding.verify_existing(output/'POINT_FREEZE.json')

    def test_method_choice_is_explicit_and_original_still_available(self):
        with tempfile.TemporaryDirectory()as tmp:
            record=binding.prepare(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json','WHOLLY_INVENTED',Path(tmp)/'v2',runtime=binding.RUNTIME,method='original-v2')
            self.assertEqual(record['numerical_method'],'original-v2')
            self.assertIn('run_known2023_point_v2.py',record['commands_not_executed'][0][2])
            with self.assertRaises(ValueError):binding.prepare(ROOT/'invented_fixture_v1/INVENTED_DATASET_v1.json','WHOLLY_INVENTED',Path(tmp)/'invalid',runtime=binding.RUNTIME,method='unknown')

if __name__=='__main__':unittest.main()
