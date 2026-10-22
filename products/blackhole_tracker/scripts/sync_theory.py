"""Developer source sync; installed distributions carry these pinned inputs."""
from pathlib import Path
import hashlib
import json
import shutil
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent.parent if ROOT.parent.name=='products' else ROOT.parent
PAPERS=REPO/'papers'
if not PAPERS.is_dir():
    raise SystemExit('Source sync requires the complete repository or source archive, including its papers directory.')
target=ROOT/'bhtracker/theory';target.mkdir(parents=True,exist_ok=True)
(target/'__init__.py').write_text('')
original=PAPERS/'bhsm_blackhole_tracker_20261021/code/radial_response.py'
source=original.read_text()
old="VENDOR = ROOT.parent/'bhsm_angular_lensing_20261021'/'code'/'vendor_original'"
assert source.count(old)==1
source=source.replace(old,"VENDOR = Path(__file__).resolve().parent/'provider'")
source=source.replace('G_PC_KMS2_MSUN = 4.300917270036279e-3',
    'G_PC_KMS2_MSUN = 1.3271244e20 / (3.085677581491367e16 * 1e6)  # IAU nominal GM_sun')
(target/'radial_response.py').write_text(source,encoding='utf8',newline='\r\n')
vendor=PAPERS/'bhsm_angular_lensing_20261021/code/vendor_original'
manifest=json.loads((vendor/'SOURCE_MANIFEST.json').read_text())
for record in manifest['files']:
    path=record['path'];file=vendor/path
    assert hashlib.sha256(file.read_bytes()).hexdigest()==record['sha256']
    dest=target/'provider'/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
shutil.copy2(vendor/'SOURCE_MANIFEST.json',target/'provider/SOURCE_MANIFEST.json')
(target/'ADAPTATION.json').write_text(json.dumps({'radial_source_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),
    'change':'provider path adapted; physical solar mass uses IAU nominal GM_sun consistently with product forward model; field equations unchanged',
    'provider_commit':manifest['source_commit'],'pinned_files':len(manifest['files'])},indent=2)+'\n',encoding='utf8',newline='\r\n')
print('Self-contained theory provider: six pinned inputs verified and copied.')
