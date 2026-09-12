"""Keep the original numerical campaign and journal status-only I/O wrappers."""
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]


def main():
    import run_n12_gate7_full_direct_curvature_campaign as campaign
    from bhsm.interface import status_file_retry as retry
    h=campaign.h
    wrapper=ROOT/'scripts/run_n12_gate7_hessian_with_status_retry.py'
    original_popen=subprocess.Popen
    original_init=campaign.Runner.__init__

    class StatusRetryPopen(original_popen):
        def __init__(self,args,*rest,**kwargs):
            if isinstance(args,(list,tuple)) and len(args)>=2 and Path(args[1]).resolve()==Path(h.__file__).resolve():
                args=[args[0],str(wrapper),*args[2:]]
            super().__init__(args,*rest,**kwargs)

    def initialize(runner,sources,min_free_gib):
        sources=dict(sources)
        h.merge(sources,{h.df.file_key(path):h.df.values.sha(path) for path in (Path(__file__),wrapper,Path(retry.__file__))})
        original_init(runner,sources,min_free_gib)

    def event(path,attempt,error):
        if attempt==1:print(json.dumps(dict(status_write_retry=str(path),winerror=error.winerror)),flush=True)

    subprocess.Popen=StatusRetryPopen
    campaign.Runner.__init__=initialize
    try:
        with retry.retry_status_writes(h,[campaign.STATE,h.WORK/'active_state.json'],on_retry=event):
            campaign.main()
    finally:
        subprocess.Popen=original_popen;campaign.Runner.__init__=original_init


if __name__=='__main__':main()
