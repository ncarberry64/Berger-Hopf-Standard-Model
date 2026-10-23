from pathlib import Path
import argparse
import hashlib
import json
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description='Execute saved notebooks, optionally with an installed wheel interpreter outside the checkout')
parser.add_argument('--kernel-python',type=Path)
parser.add_argument('--work-directory',type=Path,default=ROOT)
args=parser.parse_args()
args.work_directory.mkdir(parents=True,exist_ok=True)
receipts=[]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    print('Executing '+path.name,flush=True)
    book=nbformat.read(path,as_version=4)
    manager=KernelManager(kernel_name='python3')
    if args.kernel_python:
        manager.kernel_spec.argv=[str(args.kernel_python.resolve()),'-m','ipykernel_launcher','-f','{connection_file}']
    try:
        NotebookClient(book,timeout=180,km=manager,resources={'metadata':{'path':str(args.work_directory.resolve())}}).execute()
    finally:
        if manager.has_kernel:manager.shutdown_kernel(now=True)
    nbformat.write(book,path)
    receipts.append({'notebook':path.name,'status':'EXECUTED_NO_ERRORS','code_cells':sum(c.cell_type=='code' for c in book.cells),
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'kernel_python':str(args.kernel_python.resolve()) if args.kernel_python else 'python3 default kernel',
                     'working_directory':str(args.work_directory.resolve())})
out=ROOT/'validation';out.mkdir(exist_ok=True)
(out/'notebook_receipt.json').write_text(json.dumps(receipts,indent=2)+'\n')
print(json.dumps(receipts,indent=2))
