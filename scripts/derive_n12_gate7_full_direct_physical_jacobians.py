"""Isolate the full DF campaign while reusing the unchanged point producer."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import derive_n12_gate7_direct_physical_jacobians as producer

ROOT=producer.ROOT
WORK=ROOT/'artifacts/flagship_integration/.full_direct_physical_jacobian_work'
ALGORITHM='ISOLATED_DIRECT_PHYSICAL_HS_POINT_AMBIENT_DF_ARB256_NORMALIZED_INDEX24_V1'
INSTALLED=False


def install_backend():
    global INSTALLED
    if INSTALLED:
        if producer.WORK!=WORK or producer.ALGORITHM!=ALGORITHM:
            raise RuntimeError('full derivative backend changed within this process')
        return producer
    if producer.WORK!=ROOT/'artifacts/flagship_integration/.direct_physical_jacobian_work':
        raise RuntimeError('one direct derivative backend per process required')
    original_binding=producer.binding
    def binding():
        result=original_binding()
        result['files'][Path(__file__).relative_to(ROOT).as_posix()]=producer.values.sha(Path(__file__))
        result['campaign_workspace']=WORK.relative_to(ROOT).as_posix()
        return result
    producer.WORK=WORK
    producer.ALGORITHM=ALGORITHM
    producer.binding=binding
    INSTALLED=True
    return producer


# Windows spawn re-executes this entry point as __mp_main__. Install before
# unpickling the original producer.worker, whose module owns the globals.
if __name__ in ('__main__','__mp_main__'):
    install_backend()
if __name__=='__main__':
    producer.main()
