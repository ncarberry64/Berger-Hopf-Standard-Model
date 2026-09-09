"""Explicitly fingerprinted factored-integrand backend for bounded row campaigns."""
from pathlib import Path
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import derive_n12_gate7_physical_midpoint_hessian_errors as campaign
from bhsm.interface import factored_arb_integrand as factored

ALGORITHM='PHYSICAL_MIDPOINT_HESSIAN_ERROR_ARB256_FACTORED_INTEGRAND_V2'
_original_load=campaign.load_inputs
_original_worker=campaign.worker
_installed=False


def load_inputs(interval):
    values,binding,_=_original_load(interval)
    binding['algorithm']=ALGORITHM
    for path in (Path(__file__),Path(factored.__file__)):
        binding['sources'][path.relative_to(ROOT).as_posix()]=campaign.sha(path)
    binding['parent_integrand_SHA256']=factored.PARENT_INTEGRAND_SHA256
    fingerprint=hashlib.sha256(json.dumps(binding,sort_keys=True).encode()).hexdigest().upper()
    return values,binding,fingerprint


def worker(interval,row,expected):
    install_backend()
    # Build and cache the parent's base action jets/eigenline before changing
    # contraction algebra; their original computation remains untouched.
    values,_,_=campaign.prepare_worker(interval,expected)
    if (campaign.point_directory(interval)/f'row_{row:03d}.npz').exists():
        return _original_worker(interval,row,expected)
    with factored.use_factored_integrand(campaign.graph.cert,values['state']):
        return _original_worker(interval,row,expected)


def install_backend():
    global _installed
    if _installed:return
    campaign.WORK=ROOT/'artifacts/flagship_integration/.factored_physical_midpoint_hessian_error_work'
    campaign.load_inputs=load_inputs
    campaign.worker=worker
    _installed=True


def main():
    if '--adopt-first-midpoint' in sys.argv:
        raise ValueError('legacy evidence stays in its original fingerprinted cache')
    install_backend()
    if '--aggregate' in sys.argv:
        sys.argv.remove('--aggregate')
        import certify_n12_gate7_selected_physical_hessian_pullbacks as aggregate
        aggregate.RESULT=ROOT/'artifacts/flagship_integration/.factored_physical_midpoint_hessian_pullback_work'
        aggregate.main()
    else:
        campaign.main()


if __name__=='__main__':main()
