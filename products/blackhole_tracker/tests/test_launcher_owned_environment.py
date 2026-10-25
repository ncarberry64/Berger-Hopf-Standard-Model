"""Mocked path/setup/dependency contracts; never create venvs or install packages."""
from contextlib import redirect_stdout,redirect_stderr
import importlib.util,json,os,tempfile,types,unittest
from io import StringIO
from pathlib import Path
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/'scripts/launch_local.py'
spec=importlib.util.spec_from_file_location('bhsm_launcher_control',SOURCE)
launcher=importlib.util.module_from_spec(spec);spec.loader.exec_module(launcher)

class OwnedLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary=tempfile.TemporaryDirectory(prefix='bhsm launcher mock ');self.addCleanup(self.temporary.cleanup)
        self.root=Path(self.temporary.name);self.product=self.root/'source with spaces';self.product.mkdir()
        self.patch=patch.object(launcher,'ROOT',self.product);self.patch.start();self.addCleanup(self.patch.stop)
        self.env=self.root/'owned environment'
    def owned_python(self):
        marker,owner=launcher.owned_environment(self.env)
        python=self.env/'Scripts/python.exe';python.parent.mkdir();python.write_bytes(b'NOT_EXECUTABLE_LITERAL')
        owner['installed_source_sha256']='f'*64;marker.write_text(json.dumps(owner),encoding='utf-8')
        return python
    def invoke(self,args,*,checks=(0,0),create_error=False):
        calls=[];checks=iter(checks)
        def created(path,**kwargs):
            calls.append(('create',Path(path),kwargs))
            if create_error:raise OSError('INVENTED_VENV_FAILURE')
            python=Path(path)/'Scripts/python.exe';python.parent.mkdir();python.write_bytes(b'NOT_EXECUTABLE_LITERAL')
        def run(command,**kwargs):
            calls.append(('run',command,kwargs))
            if '-c' in command:return types.SimpleNamespace(returncode=next(checks),stderr='INVENTED_CHECK_FAILURE')
            return types.SimpleNamespace(returncode=0)
        output=StringIO();error=StringIO()
        with patch.object(launcher.venv,'create',side_effect=created),patch.object(launcher.subprocess,'run',side_effect=run),patch.object(launcher,'source_signature',return_value='f'*64),redirect_stdout(output),redirect_stderr(error):
            code=launcher.main(args)
        return code,calls,output.getvalue(),error.getvalue()
    def test01_default_short_versioned_owned_path_is_source_specific(self):
        with patch.dict(os.environ,{'LOCALAPPDATA':str(self.root/'local')}):
            one=launcher.environment_path();self.assertEqual(one,launcher.environment_path())
            self.assertIn(launcher.VERSION,one.name);self.assertIn('BHSM',one.parts);self.assertNotIn('.venv',one.parts)
            with patch.object(launcher,'ROOT',self.root/'other source'):self.assertNotEqual(one,launcher.environment_path())
    def test02_explicit_path_does_not_require_localappdata(self):
        with patch.dict(os.environ,{},clear=True):
            self.assertEqual(launcher.environment_path(self.env),self.env.resolve())
            with self.assertRaisesRegex(ValueError,'--environment'):launcher.environment_path()
    def test03_foreign_directory_is_refused_without_setup_or_mutation(self):
        self.env.mkdir();sentinel=self.env/'PRESERVE';sentinel.write_bytes(b'UNRELATED')
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--check-install'])
        self.assertEqual(code,2);self.assertEqual(calls,[]);self.assertEqual(sentinel.read_bytes(),b'UNRELATED');self.assertIn('unowned',error)
    def test04_old_project_venv_is_preserved_when_new_default_is_used(self):
        legacy=self.product/'.venv';legacy.mkdir();(legacy/'PRESERVE').write_bytes(b'OLD')
        with patch.dict(os.environ,{'LOCALAPPDATA':str(self.root/'local')}):
            code,calls,out,error=self.invoke(['--check-install'])
        self.assertEqual(code,0);self.assertEqual((legacy/'PRESERVE').read_bytes(),b'OLD')
        self.assertNotEqual(calls[0][1],legacy);self.assertIn('Python environment:',out)
    def test05_mismatched_owner_is_not_repaired_or_adopted(self):
        self.owned_python();marker=self.env/launcher.OWNER_FILE;old=json.loads(marker.read_bytes());old['source_root']='FOREIGN';marker.write_text(json.dumps(old),encoding='utf-8');before=marker.read_bytes()
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--check-install'])
        self.assertEqual(code,2);self.assertEqual(calls,[]);self.assertEqual(marker.read_bytes(),before)
    def test06_joint_probe_checks_fits_dll_and_exact_celerite_without_fallback(self):
        base=launcher.dependency_probe();astrometry=launcher.dependency_probe(astrometry=True);joint=launcher.dependency_probe(joint_research=True)
        self.assertNotIn('astropy',base);self.assertNotIn('celerite2',base);self.assertIn('_compression',astrometry)
        self.assertNotIn('celerite2',astrometry);self.assertIn('_compression',joint);self.assertIn('"0.3.3"',joint)
    def test07_explicit_joint_extra_is_installed_then_rechecked(self):
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--joint-research','--check-install'],checks=(1,0))
        self.assertEqual(code,0);commands=[x[1] for x in calls if x[0]=='run']
        self.assertEqual(sum('-c' in x for x in commands),2);self.assertEqual(commands[1][-1],str(self.product)+'[joint-research]')
        self.assertIn('with optional joint-research support',out);self.assertEqual(json.loads((self.env/launcher.OWNER_FILE).read_bytes())['installed_source_sha256'],'f'*64)
    def test08_postinstall_dependency_failure_never_reports_ready_or_serves(self):
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--joint-research'],checks=(1,1))
        self.assertEqual(code,2);self.assertNotIn('installation is ready',out);self.assertIn('dependency check failed',error)
        self.assertFalse(any('serve' in x[1] for x in calls if x[0]=='run'))
    def test09_current_owned_environment_check_never_installs_optional_extra(self):
        self.owned_python();code,calls,out,error=self.invoke(['--environment',str(self.env),'--check-install'],checks=(0,))
        self.assertEqual(code,0);self.assertEqual(len(calls),1);self.assertNotIn('pip',calls[0][1]);self.assertNotIn('astropy',calls[0][1][-1])
    def test10_environment_symlink_target_is_refused(self):
        with patch.object(Path,'is_symlink',return_value=True),self.assertRaisesRegex(ValueError,'symlinks'):launcher.owned_environment(self.env)
    def test11_source_signature_tracks_sources_but_ignores_bytecode(self):
        (self.product/'pyproject.toml').write_bytes(b'project');package=self.product/'bhtracker';package.mkdir();source=package/'sample.py';source.write_bytes(b'one')
        first=launcher.source_signature();self.assertEqual(first,launcher.source_signature());cache=package/'__pycache__';cache.mkdir();(cache/'sample.pyc').write_bytes(b'ignored')
        self.assertEqual(first,launcher.source_signature());source.write_bytes(b'two');self.assertNotEqual(first,launcher.source_signature())
    def test12_failed_environment_creation_is_retained_with_owner_marker(self):
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--check-install'],create_error=True)
        self.assertEqual(code,2);self.assertTrue((self.env/launcher.OWNER_FILE).is_file());self.assertEqual(len(calls),1)
    def test13_existing_routes_spaces_no_open_and_clean_environment_are_preserved(self):
        self.owned_python()
        with patch.dict(os.environ,{'PYTHONPATH':'UNWANTED','PYTHONHOME':'UNWANTED'}):
            code,calls,out,error=self.invoke(['--environment',str(self.env),'--no-open','--port','8766','--page','spectrum'],checks=(0,))
        self.assertEqual(code,0);command=calls[-1][1];self.assertIn(str(self.env.resolve()/'Scripts/python.exe'),command)
        self.assertEqual(command[-4:],['--port','8766','--page','spectrum']);self.assertNotIn('--open',command)
        self.assertNotIn('PYTHONPATH',calls[-1][2]['env']);self.assertNotIn('PYTHONHOME',calls[-1][2]['env'])
    def test14_nonobject_owner_json_is_actionable_and_preserved(self):
        self.env.mkdir();marker=self.env/launcher.OWNER_FILE;marker.write_bytes(b'[]\n')
        code,calls,out,error=self.invoke(['--environment',str(self.env),'--check-install'])
        self.assertEqual(code,2);self.assertEqual(calls,[]);self.assertEqual(marker.read_bytes(),b'[]\n')
        self.assertIn('must be a JSON object',error);self.assertNotIn('Traceback',error)
    def test15_optional_probe_refuses_old_astropy_with_wholly_fake_imports(self):
        def execute(version):
            modules={name:types.SimpleNamespace() for name in ('numpy','scipy','matplotlib','celerite2')}
            modules['bhtracker']=types.SimpleNamespace(__version__=launcher.VERSION)
            modules['astropy']=types.SimpleNamespace()
            metadata=types.SimpleNamespace(version=lambda name:version if name=='astropy' else '0.3.3')
            modules['importlib.metadata']=types.SimpleNamespace(metadata=metadata)
            modules['astropy.io']=types.SimpleNamespace(fits=object())
            modules['astropy.io.fits.hdu.compressed']=types.SimpleNamespace(_compression=object())
            def fake_import(name,globals=None,locals=None,fromlist=(),level=0):return modules[name]
            exec(launcher.dependency_probe(joint_research=True),{'__builtins__':{'__import__':fake_import,'int':int}})
        with self.assertRaises(AssertionError):execute('5.3.4')
        execute('6.0.1');execute('7.2.0')
    def test16_existing_mc_page_is_forwarded_without_starting_work(self):
        self.owned_python();code,calls,out,error=self.invoke(['--environment',str(self.env),'--no-open','--page','photometry-mc'],checks=(0,))
        self.assertEqual(code,0);self.assertEqual(calls[-1][1][-2:],['--page','photometry-mc'])
        self.assertNotIn('--open',calls[-1][1]);self.assertFalse(any('pip' in x[1] for x in calls if x[0]=='run'))
