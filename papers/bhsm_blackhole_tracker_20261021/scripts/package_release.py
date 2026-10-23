"""Build a complete portable source release without caches or TeX scratch."""
from pathlib import Path
import hashlib
import json
import shutil
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
PAPERS=ROOT.parent
REPO=PAPERS.parent
OUTPUT=Path(sys.argv[1]).resolve()
OUTPUT.mkdir(parents=True,exist_ok=True)
product=REPO/'products/blackhole_tracker'
if not product.is_dir():
    product=REPO/'product'
directories=[PAPERS/'bhsm_angular_lensing_20261021',PAPERS/'bhsm_state_rotation_20261021',ROOT,product]
missing=[str(directory) for directory in directories if not directory.is_dir()]
if missing:
    raise SystemExit('Required release directories missing: '+', '.join(missing))
excluded={'.aux','.log','.out','.fls','.fdb_latexmk','.synctex.gz','.blg','.pyc'}
files=[]
for name in ['LICENSE.md','ACADEMIC_USE.md']:
    license_file=REPO/name
    if license_file.is_file():
        files.append(license_file)
for directory in directories:
    for path in sorted(directory.rglob('*')):
        if not path.is_file() or any(part in path.parts for part in ['__pycache__','.pytest_cache','.venv','build','dist','user_runs','.ipynb_checkpoints']):continue
        if any(part.endswith('.egg-info') for part in path.parts):continue
        if path.suffix in excluded or path.name.endswith('.synctex.gz'):continue
        if path==ROOT/'provenance/RELEASE_MANIFEST.json':continue
        files.append(path)
for name in ['verify_blackhole_tracker_snapshot.py','smoke_blackhole_tracker_wheel.py','verify_blackhole_tracker_release.py']:
    tool=REPO/'tools'/name
    if tool.is_file():
        files.append(tool)
manifest={'scope':'runnable product and three paper directories; tracker central, earlier research preserved',
          'formal_reviewer_repository':'https://github.com/ncarberry64/Berger-Hopf-Standard-Model',
          'product_path':product.relative_to(REPO).as_posix(),
          'manifest_excludes_its_own_hash':True,
          'files':[{'path':p.relative_to(REPO).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                    'bytes':p.stat().st_size} for p in files]}
mf=ROOT/'provenance/RELEASE_MANIFEST.json'
mf.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
files.append(mf)
zip_path=OUTPUT/'BHSM_Blackhole_Tracker_Source.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for path in files:
        info=zipfile.ZipInfo(path.relative_to(REPO).as_posix(),date_time=(1980,1,1,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        info.external_attr=0o100644 << 16
        z.writestr(info,path.read_bytes(),compresslevel=9)
shutil.copy2(ROOT/'manuscript/main.pdf',OUTPUT/'BHSM_Blackhole_Tracker_Manuscript.pdf')
for name in ['LAY_REPORT.md','RESULT_STATEMENT.md','VALIDATION.md','CHAIN_AND_FREEDOMS.md','GIT_HANDOFF.md']:
    shutil.copy2(ROOT/name,OUTPUT/name)
shutil.copy2(ROOT/'provenance/RECOVERY_MAP.md',OUTPUT/'RECOVERY_MAP.md')
print(json.dumps({'source_archive':str(zip_path),'members':len(files),
                 'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest()},indent=2))
