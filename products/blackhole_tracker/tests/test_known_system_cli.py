"""Lazy namespace/packaging engineering only; no scientific engine calls."""
from contextlib import redirect_stdout,redirect_stderr
from io import StringIO
from pathlib import Path
import sys,tomllib,types,unittest
from unittest.mock import patch
from bhtracker.cli import main

class KnownSystemCLIAddendumTests(unittest.TestCase):
    def test01_exact_lazy_remainder_and_return_code(self):
        calls=[];fake=types.ModuleType('bhtracker.known_system_v3');fake.main=lambda argv:(calls.append(argv) or 17)
        before=set(sys.modules)
        with patch.dict(sys.modules,{'bhtracker.known_system_v3':fake}):result=main(['known-system','replay','path with spaces.zip','--mode','numerical'])
        self.assertEqual(result,17);self.assertEqual(calls,[['replay','path with spaces.zip','--mode','numerical']])
        self.assertEqual([name for name in set(sys.modules)-before if name.startswith('bhtracker._joint_v3')],[])
    def test02_default_sysargv_and_help_are_delegated(self):
        calls=[];fake=types.ModuleType('bhtracker.known_system_v3');fake.main=lambda argv:calls.append(argv)
        with patch.dict(sys.modules,{'bhtracker.known_system_v3':fake}),patch.object(sys,'argv',['blackhole-tracker','known-system','--help']):main()
        self.assertEqual(calls,[['--help']])
    def test03_actionable_error_without_legacy_fallback(self):
        fake=types.ModuleType('bhtracker.known_system_v3')
        def refuse(argv):raise ValueError('INVENTED_SOURCE_BINDING_REFUSAL')
        fake.main=refuse;message=StringIO()
        with patch.dict(sys.modules,{'bhtracker.known_system_v3':fake}),redirect_stderr(message),self.assertRaises(SystemExit) as failed:
            main(['known-system','evaluate','not-a-native-file'])
        self.assertEqual(failed.exception.code,2);self.assertIn('INVENTED_SOURCE_BINDING_REFUSAL',message.getvalue())
    def test04_global_help_retains_both_old_and_new_routes(self):
        stream=StringIO()
        with redirect_stdout(stream),self.assertRaises(SystemExit) as done:main(['--help'])
        self.assertEqual(done.exception.code,0)
        for name in ('known-system','mc-photometry','fit-photometry','joint','serve'):self.assertIn(name,stream.getvalue())
    def test05_packaging_extra_and_manifest_only_no_version_or_legal_change(self):
        path=Path(__file__).resolve().parents[1]/'pyproject.toml';value=tomllib.loads(path.read_text(encoding='utf-8'))
        self.assertEqual(value['project']['optional-dependencies']['joint-research'],['astropy>=6','celerite2==0.3.3'])
        self.assertEqual(value['tool']['setuptools']['package-data']['bhtracker._joint_v3'],['SOURCE_MANIFEST_v1.json'])
        self.assertEqual(value['project']['license'],'LicenseRef-AllRightsReserved')
        self.assertEqual(value['project']['urls']['Repository'],'https://github.com/ncarberry64/Berger-Hopf-Standard-Model')
