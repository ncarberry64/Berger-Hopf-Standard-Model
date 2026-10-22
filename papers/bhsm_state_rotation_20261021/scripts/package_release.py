"""Package both papers with SHA256 manifests; exclude transient build files."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
arg=argparse.ArgumentParser()
arg.add_argument('--output',type=Path,required=True)
args=arg.parse_args()
out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
old=ROOT.parent/'bhsm_angular_lensing_20261021'

def include(p,base):
    relative=p.relative_to(base)
    if any(x in ['__pycache__','.pytest_cache','matplotlib_cache'] for x in relative.parts):
        return False
    if base==old:
        return True  # preserve all 71 original file members, including bbl/logs
    if p.name=='RELEASE_MANIFEST.json':
        return False
    if 'pdf_render' in relative.parts and p.suffix=='.png':
        return False
    return p.suffix not in ['.aux','.blg','.fdb_latexmk','.fls','.log','.out'] and p.name!='build-console.txt'

files=[(ROOT.parent/'.gitattributes','papers/.gitattributes')]
for base in [old,ROOT]:
    for p in sorted(base.rglob('*')):
        if p.is_file() and include(p,base):
            arc='papers/'+str(p.relative_to(ROOT.parent)).replace('\\','/')
            files.append((p,arc))
manifest={'schema':'BHSM_HOPF_NODAL_RELEASE_V1','files':[{
    'path':arc,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    for p,arc in files]}
mp=ROOT/'provenance/RELEASE_MANIFEST.json'
mp.write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf8')
files.append((mp,'papers/'+ROOT.name+'/provenance/RELEASE_MANIFEST.json'))
archive=out/'BHSM_Hopf_Nodal_Lensing_Source.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for p,arc in files:
        info=zipfile.ZipInfo(arc,date_time=(2026,10,21,0,0,0))
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for f in manifest['files']:
        assert hashlib.sha256(z.read(f['path'])).hexdigest()==f['sha256']
shutil.copy2(ROOT/'manuscript/main.pdf',out/'BHSM_Hopf_Nodal_Lensing_Manuscript.pdf')
shutil.copy2(ROOT/'LAY_REPORT.md',out/'LAY_REPORT.md')
shutil.copy2(ROOT/'provenance/RECOVERY_MAP.md',out/'RECOVERY_MAP.md')
shutil.copy2(ROOT/'review/final_skeptical_review.md',out/'SKEPTICAL_REVIEW.md')
print(json.dumps({'archive':str(archive),'members':len(files),'sha256':hashlib.sha256(archive.read_bytes()).hexdigest()}))
