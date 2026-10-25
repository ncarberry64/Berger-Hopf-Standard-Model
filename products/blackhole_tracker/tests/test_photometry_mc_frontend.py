"""Portable frontend engineering controls; no backend/model/native calls."""
from html.parser import HTMLParser
from copy import deepcopy
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = []; self.labels = []; self.scripts = []; self.inline_scripts = 0; self.text = []
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if tag == 'label' and 'for' in a: self.labels.append(a['for'])
        if tag == 'script':
            if 'src' in a: self.scripts.append(a['src'])
            else: self.inline_scripts += 1
    def handle_data(self, data): self.text.append(data)


class PhotometryMCFrontendTests(unittest.TestCase):
    def test_mocked_dom_workflow_preserves_bytes_unknowns_and_replay_scope(self):
        node = shutil.which('node')
        if node is None: self.skipTest('Node is required for portable mocked frontend checks')
        command = [node, str(ROOT / 'tests/frontend/test_photometry_mc_dom.js')]
        result = subprocess.run(command, text=True, capture_output=True, timeout=60)
        if os.environ.get('BHSM_MC_PRESENTATION_ARTIFACTS'):
            artifact=Path(os.environ['BHSM_MC_PRESENTATION_ARTIFACTS'])
            with (artifact/'DOM_stdout.json').open('x',encoding='utf-8') as stream:stream.write(result.stdout)
            with (artifact/'DOM_stderr.log').open('x',encoding='utf-8') as stream:stream.write(result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        receipt = json.loads(result.stdout)
        self.assertTrue(receipt['passed']); self.assertEqual(receipt['tests'], 32)
        self.assertEqual(receipt['backend_calls'], 0); self.assertEqual(receipt['native_model_calls'], 0)
        self.assertFalse(receipt['scientific_validation'])

    def test_static_page_has_accessible_inputs_and_explicit_scientific_limits(self):
        page = Page(); page.feed((ROOT / 'bhtracker/web/photometry-mc.html').read_text(encoding='utf-8'))
        self.assertEqual(len(page.ids), len(set(page.ids)))
        for control in ('mc-input-file', 'mc-te-grid', 'mc-u0-grid', 'mc-entropy', 'mc-wall', 'mc-replay-file', 'mc-job-history'):
            self.assertIn(control, page.labels)
        self.assertEqual(page.scripts, ['/photometry-mc.js']); self.assertEqual(page.inline_scripts, 0)
        words = ' '.join(page.text)
        for statement in ('VALIDATION PENDING', 'continuous confidence interval', 'Mass: unavailable',
                          'Lens distance: unavailable', 'θE: unavailable', 'πE: unavailable',
                          'Absolute angular motion: unavailable', 'no optimization', '32 MB (32,000,000 bytes)', '128 MiB', '512 MiB'):
            self.assertIn(statement, words)
        self.assertIn('https://github.com/ncarberry64/Berger-Hopf-Standard-Model', (ROOT / 'bhtracker/web/photometry-mc.html').read_text(encoding='utf-8'))
        for statement in ('two fixed cadence/error/truth designs', '4,096 datasets', '8,192 pointwise tests',
                          'Seven unavailable tests counted as misses', 'supports those designs only',
                          'general user-input calibration remains pending', 'historical three local/reference calibration failures remain preserved'):
            self.assertIn(statement, words)

    def test_native_presentation_preserves_values_and_distinguishes_uncertainty_routes(self):
        from bhtracker.unresolved_report import report_html
        # Literal display fixture only: no provider, generation, likelihood or fit.
        result={'status':'PHOTOMETRIC_FIT','point_count':3,'excluded_point_count':0,
          'parameters':{'t0':1000.,'tE_days':25.,'u0':.3,'time_numeric_origin_jd':2450000.},
          'uncertainty':{'standard_errors':{'t0':3.,'tE_days':2.5,'u0':None},'qualification':'CONTROL_ONLY_LOCAL_QUALIFICATION'},
          'bhsm_interpretation':{'one_potential_rule':'CONTROL_ONLY_ONE_POTENTIAL'},'diagnostics':{},
          'dataset_input':{'instruments':{}},'timescale_uncertainty':{'sigma_days':2.5,'coverage_claim':False},
          'analysis_configuration':{},'product_version':'CONTROL_ONLY','protocol_sha256':'0'*64,'input_sha256':'1'*64}
        original=deepcopy(result);rendered=report_html(result)
        self.assertEqual(result,original);self.assertIn('<td>25</td><td>2.5</td>',rendered)
        self.assertIn('unavailable / unresolved',rendered)
        for text in ('Local curvature σ · uncalibrated','not calibrated confidence intervals','510/512','461/512','504/512',
                     '/photometry-mc','two fixed cadence/error/truth designs only','general user-input calibration remains pending','MASS_UNRESOLVED'):
            self.assertIn(text,rendered)
        native=(ROOT/'bhtracker/web/photometry.html').read_text(encoding='utf-8')
        script=(ROOT/'bhtracker/web/photometry.js').read_text(encoding='utf-8')
        self.assertIn('Point estimates and local curvature',native);self.assertIn('For requested tE/u0 pointwise uncertainty decisions',native)
        self.assertEqual(script.count('(local curvature σ)'),3)
        for page in ('photometry.html','index.html'):
            self.assertIn('href="/photometry-mc"',(ROOT/'bhtracker/web'/page).read_text(encoding='utf-8'))
        guide=(ROOT/'docs/PHOTOMETRY_POINTWISE_EVIDENCE_20261025_V1.md').read_text(encoding='utf-8')
        for count in ('1,947 / 2,048','1,948 / 2,048','1,939 / 2,048','seven unavailable tests remained misses',
                      'b037d6bc4e9b44381a6bed79d79b283e0078d524cc91269790f4aabdb9895af9'):
            self.assertIn(count,guide)
        self.assertNotIn('C:/',guide);self.assertNotIn('C:\\',guide)


if __name__ == '__main__':
    unittest.main()
