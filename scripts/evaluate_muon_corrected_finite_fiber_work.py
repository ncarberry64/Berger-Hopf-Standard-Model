"""Consume the admitted stored Jacobi images in the COMPLETE finite work.

This keeps the finite-natural terminal control separate from a physical
retarded exterior. Both endpoint cotangents and all67 tests remain.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
from flint import acb,acb_mat,ctx
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz


def run(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve all finite work applications')
    out.mkdir(parents=True);pins={}
    def read(folder,name):
        p=ROOT/folder/name;b=p.read_bytes();pins[p.relative_to(ROOT).as_posix()]=sha256(b).hexdigest()
        if p.suffix=='.json':return json.loads(b)
        with np.load(p,allow_pickle=False)as a:return{k:a[k].copy()for k in a.files}
    bf=Path('artifacts/muon_fixed_parent_finite_shooting_20261012/run_1/trial_0000')
    tf=Path('artifacts/muon_stored_fiber_canonical_tangent_20261012/run_1')
    old=read(bf,'action_and_shooting_rows.npz');base=read(bf,'candidate.npz')
    first=read(tf,'initial_literal_Ward_fiber.npz');last=read(tf,'final_full67_canonical_transfer_image.npz')
    receipt=read(tf,'result.json');oldreceipt=read(bf,'result.json')
    def matrix(a):
        a=np.asarray(a,complex)
        return acb_mat([[acb(float(z.real),float(z.imag))for z in row]for row in a])
    def convert(a):
        h=np.empty((a.nrows(),a.ncols()),complex);lo=h.copy();upper=np.empty_like(h.real)
        for i in range(a.nrows()):
            for j in range(a.ncols()):
                z=a[i,j];h[i,j]=complex(float(z.real.mid()),float(z.imag.mid()))
                d=z-acb(h[i,j].real,h[i,j].imag);lo[i,j]=complex(float(d.real.mid()),float(d.imag.mid()))
                upper[i,j]=float(abs(d-acb(lo[i,j].real,lo[i,j].imag)).upper())
        return h,lo,upper
    with ctx.workprec(192):
        XB=matrix(first['canonical_direction_high'][:106])+matrix(first['canonical_direction_low'][:106])
        XT=matrix(last['canonical_high'][:106])+matrix(last['canonical_low'][:106])
        terminal=matrix(old['terminal_Pi'][None]) * XT
        initial=matrix(base['own_child_Pi'][None]) * XB
        work=terminal-initial
        interval=complex(old['recorded_coordinate_interval'].item())
        if interval==0:raise ValueError('actual nonzero chronological interval required')
        scaled=work/acb(interval.real,interval.imag)
        h,l,b=convert(work);sh,sl,sb=convert(scaled)
        th,tl,tb=convert(terminal);ih,il,ib=convert(initial)
        oldwork=matrix(old['full_action_work'][None]);dh,dl,db=convert(work-oldwork)
    path=out/'complete_finite_action_work.npz';_compressed_npz(path,dict(
        full_action_work_high=h,full_action_work_low=l,full_action_work_rounding_radius_upper=b,
        clock_scaled_full_action_work_high=sh,clock_scaled_full_action_work_low=sl,
        clock_scaled_full_action_work_rounding_radius_upper=sb,
        terminal_only_high=th,terminal_only_low=tl,initial_cotangent_high=ih,initial_cotangent_low=il,
        corrected_minus_binary_work_high=dh,corrected_minus_binary_work_low=dl,
        original_binary_full_action_work=old['full_action_work'],
        actual_interval=old['recorded_coordinate_interval'],full_terminal106=old['full_terminal_graph_residual']))
    result=dict(classification='EVALUATED_ADMITTED_STORED_JACOBI_IMAGES_CONSUMED_IN_COMPLETE_FINITE_ACTION_WORK',
        input_hashes=pins,archives={path.name:dict(bytes=path.stat().st_size,sha256=sha256(path.read_bytes()).hexdigest())},
        original_base_birth226_max=oldreceipt['all_original226_max'],
        complete_work_max=float(np.max(abs(h+l))),clock_scaled_complete_work_max=float(np.max(abs(sh+sl))),
        complete_work_norm=float(np.linalg.norm(h+l)),
        corrected_minus_binary_complete_work_max=float(np.max(abs(dh+dl))),
        corrected_minus_binary_complete_work_norm=float(np.linalg.norm(dh+dl)),
        stored_work_arithmetic_radius_upper=float(np.max(b)),
        stored_scaled_work_arithmetic_radius_upper=float(np.max(sb)),
        full_terminal106_norm=float(np.linalg.norm(old['full_terminal_graph_residual'])),
        stored_source_tangent_358_upper=max(r['original358_upper']for r in receipt['history']),
        finite_terminal_Y0_control=True,complete_initial_face_work_retained=True,
        physical_retarded_formation_cutoff_or_Pauli_admitted=False,
        scope='Exact supplied binary endpoint cotangents and H/h source-solve images, with high+low storage. This rules out the admitted stored tangent arithmetic as the cause of the large finite-action mismatch; it is not action coefficient, temporal/domain, physical normal-mode or observable error control.')
    p=out/'result.json';p.write_text(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(stage='corrected_complete_finite_work',**{k:v for k,v in result.items()if k not in ('input_hashes','archives')})),flush=True)
    print('result_sha256',sha256(p.read_bytes()).hexdigest(),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
