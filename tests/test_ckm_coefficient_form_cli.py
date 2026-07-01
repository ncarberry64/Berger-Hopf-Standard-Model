import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
COMMANDS=("ckm-coefficient-form-source-search","weak-charged-current-coefficient-form","g2-bh-source","alpha2-bh-source","weak-coupling-convention","ckm-coefficient-form","ckm-coefficient-value-source","ckm-measure-coefficient-attachment-v2-9","ckm-coefficient-form-report")
def test_cli():
 env=os.environ.copy(); env["PYTHONPATH"]=str(ROOT/"src")
 for c in COMMANDS:
  r=subprocess.run([sys.executable,"-m","bhsm.interface",c,"--format","json"],cwd=ROOT,env=env,capture_output=True,text=True,check=True); assert json.loads(r.stdout)
