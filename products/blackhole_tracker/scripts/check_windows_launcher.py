"""Execute the documented CMD launcher in a source copy with spaces in its path."""
import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import socket
import subprocess
import tempfile
import threading
import urllib.request
import venv

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if os.name!='nt':parser.error('This is an actual Windows CMD check; run on Windows')
    product=Path(__file__).resolve().parents[1]
    root=Path(tempfile.mkdtemp(prefix='BHSM launcher spaces '))
    source=root/'product with spaces'
    shutil.copytree(product,source,ignore=shutil.ignore_patterns('.venv','build','dist','*.egg-info','__pycache__','.pytest_cache','user_runs'))
    command=[os.path.join(os.environ['SystemRoot'],'System32','cmd.exe'),'/d','/c','Start_Blackhole_Tracker.cmd']
    env=os.environ.copy();env['BHSM_TRACKER_NONINTERACTIVE']='1'
    for key in ('PYTHONPATH','PYTHONHOME'):env.pop(key,None)
    receipt={'status':'failed','source_copy':str(source),'checks':{}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    try:
        missing=env.copy();missing['PATH']=os.path.join(os.environ['SystemRoot'],'System32')
        p=subprocess.run([*command,'--check-install'],cwd=source,env=missing,text=True,capture_output=True,timeout=30)
        assert p.returncode==2 and 'Python 3.11 or newer was not found' in p.stdout,p.stdout+p.stderr
        receipt['checks']['missing_python']={'exit':p.returncode,'message':p.stdout}
        # Deliberately create an existing venv without the package/dependencies.
        venv.create(source/'.venv',with_pip=True)
        p=subprocess.run([*command,'--check-install'],cwd=source,env=env,text=True,capture_output=True,timeout=600)
        assert p.returncode==0 and 'installation is ready' in p.stdout,p.stdout+p.stderr
        receipt['checks']['existing_venv_missing_dependencies_repaired']={'exit':p.returncode,'log':p.stdout+p.stderr}
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1',0));occupied.listen(1);port=occupied.getsockname()[1]
            p=subprocess.run([*command,'--no-open','--port',str(port)],cwd=source,env=env,text=True,capture_output=True,timeout=30)
            assert p.returncode!=0 and 'choose another port' in p.stderr,p.stdout+p.stderr
            receipt['checks']['occupied_port']={'exit':p.returncode,'message':p.stdout+p.stderr}
        # Use the launcher itself; capture the actual ephemeral port from stdout.
        p=subprocess.Popen([*command,'--no-open','--port','0'],cwd=source,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        lines=queue.Queue()
        def reader():
            for line in p.stdout:lines.put(line)
        threading.Thread(target=reader,daemon=True).start()
        try:
            line=lines.get(timeout=30)
            assert 'ready at http://127.0.0.1:' in line,line
            url=line.split('ready at ',1)[1].strip()
            with urllib.request.urlopen(url+'api/health') as response:health=json.load(response)
            assert health['version']=='0.2.0rc2'
            receipt['checks']['actual_launcher_server']={'url':url,'health':health}
        finally:
            # Terminate only the process tree created by this test.
            subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
            p.wait(timeout=15)
        receipt['status']='passed'
    finally:
        args.output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf8')
        print(str(args.output.resolve()))
    # Preserve the source/venv copy for inspection rather than recursively deleting it.

if __name__=='__main__':main()
