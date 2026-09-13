"""Resume the unchanged curvature campaign with bounded read-check retries."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]


def main():
    import run_n12_gate7_curvature_with_status_retry as original
    import run_n12_gate7_full_direct_curvature_campaign as campaign
    from bhsm.interface import artifact_read_retry as retry
    h=campaign.h;old_init=campaign.Runner.__init__
    names=('hessian_status','local_status','full_composition_status','verify_full_df','verify_seed')
    checks={name:getattr(campaign,name) for name in names}
    def event(path,attempt,error):
        if attempt==1:print(json.dumps(dict(artifact_read_retry=str(path),errno=error.errno)),flush=True)
    def initialize(runner,sources,min_free_gib):
        sources=dict(sources)
        h.merge(sources,{h.df.file_key(p):h.df.values.sha(p) for p in (Path(__file__),Path(retry.__file__))})
        old_init(runner,sources,min_free_gib)
    campaign.Runner.__init__=initialize
    for name,check in checks.items():
        setattr(campaign,name,retry.retry_read_check(check,[ROOT/'artifacts'],on_retry=event))
    try:original.main()
    finally:
        campaign.Runner.__init__=old_init
        for name,check in checks.items():setattr(campaign,name,check)


if __name__=='__main__':main()
