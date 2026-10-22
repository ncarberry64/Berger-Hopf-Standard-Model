"""Install a tracker wheel outside the repository and verify a real fit/replay."""
from pathlib import Path
import argparse
import os
import subprocess
import tempfile
import venv


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wheel", required=True, type=Path)
    args = parser.parse_args()
    wheel = args.wheel.resolve(strict=True)
    with tempfile.TemporaryDirectory(prefix="bhsm-formal-wheel-") as name:
        outside = Path(name)
        environment = outside / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        subprocess.run([str(python), "-m", "pip", "install", str(wheel)],
                       cwd=outside, env=env, check=True)
        code = r'''
from pathlib import Path
import sys
import numpy as np
import bhtracker
from bhtracker import fit,predict
from bhtracker.examples import make_example
from bhtracker.report import export_analysis_bundle,replay_analysis
assert Path(bhtracker.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
raw,truth=make_example('nearby_motion',noise=False)
result=fit(raw,starts=1,nuisance='shear')
assert result['status']=='TRACKED'
assert abs(result['estimates']['mass_msun']/truth['mass_msun']-1)<1e-5
np.testing.assert_allclose(predict(raw,result['_internal']['parameters']),result['predictions'],rtol=2e-11,atol=1e-12)
assert result['bhsm_interpretation']['interpretation_schema_version']==2
root=Path(bhtracker.__file__).parent
for relative in ['web/app.js','theory/BHSM_CORE_SURFACE_CONTRACT.json','theory/BHSM_INTERPRETATION_MANIFEST.json','theory/provider/code/action_native_matter_n2.py']:
    assert (root/relative).is_file(),relative
bundle=Path('analysis.zip');bundle.write_bytes(export_analysis_bundle(result))
replay=replay_analysis(bundle,Path('replay'))
assert replay['passed'] and replay['same_status'] and replay['same_interpretation']
print('FORMAL_INSTALLED_WHEEL_FIT_REPLAY_PASS')
from bhtracker.observations import parse_ogle_photometry
from bhtracker.photometry import fit_photometry
t=np.linspace(1000,1900,180)
u2=.28**2+((t-1375)/72)**2
A=(u2+2)/np.sqrt(u2*(u2+4))
mag=18-2.5*np.log10(1+.65*(A-1))
native=parse_ogle_photometry('\n'.join(f'{x:.9f} {y:.12f} .008' for x,y in zip(t,mag)).encode('ascii'),source_name='SYNTHETIC.dat',metadata={'synthetic':True})
phot=fit_photometry(native,starts=4)
assert phot['mass_status']=='MASS_UNRESOLVED'
assert abs(phot['parameters']['tE_days']/72-1)<1e-5
assert all(value is None for value in phot['unresolved_quantities'].values())
assert phot['bhsm_interpretation']['framework']=='BHSM'
for relative in ['web/photometry.html','web/photometry.js','observations.py','photometry.py']:
    assert (root/relative).is_file(),relative
native_bundle=Path('native.zip');native_bundle.write_bytes(export_analysis_bundle(phot))
native_check=replay_analysis(native_bundle,Path('native_replay'))
assert native_check['passed'] and native_check['same_native_row_identities_and_order']
print('FORMAL_INSTALLED_NATIVE_PHOTOMETRY_REPLAY_PASS_SYNTHETIC_ONLY')
'''
        subprocess.run([str(python), "-c", code], cwd=outside, env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
