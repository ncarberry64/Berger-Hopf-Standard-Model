"""Apply M8/Hopf scalar coefficients to two frozen complex geometry germs.

Read-only frozen inputs; outputs remain under the supplied repository.
No stage, history, radial integral, D5 field action or profile is recomputed.
"""
from __future__ import annotations

import argparse
from collections.abc import Mapping
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REPO_DEFAULT=ROOT
sys.path.insert(0,str(ROOT/"src"))
OLD_REL=Path("artifacts/muon_trial_d5_trace_action_20261012/trial_0000_corrected_sigma_energy_0_run_2")
REPORT_SHA="3647c939e8ee150d79483f1e32066e08cee261cac82ef0ef29eecf009a5f75f2"

from bhsm.interface.muon_m8_m5_geometric_coefficients import (
    FIELD_NAMES,KEYS,m8_m5_geometric_coefficient_jets,
)


def encode(a):
    z=np.asarray(a,complex)
    return dict(real=z.real.tolist(),imag=z.imag.tolist())


def scalar_jet(a,time):
    return dict(value=a.value,x=a.gradient@time,y=a.gradient[25],
                xy=time@a.hessian[:,25])


def jet_comparison(a,b):
    return {key:dict(absolute=float(np.max(abs(a[key]-b[key]))),
        scaled=float(np.max(abs(a[key]-b[key]))/max(1.,float(np.max(abs(a[key]))),float(np.max(abs(b[key]))))))
        for key in KEYS}


def evaluate(repository,output):
    repo=Path(repository).resolve()
    out=Path(output)
    if not out.is_absolute():out=repo/out
    out=out.resolve()
    if not out.is_relative_to(repo):raise ValueError("application outputs must remain in the repository")
    if out.exists():raise FileExistsError("preserve each independently executed application")
    sys.path.insert(0,str(repo/"src"))
    from bhsm.interface.muon_holomorphic_normal_geometry import _geometry_variables,_fields,_sqrt
    from bhsm.interface.muon_parent_retarded_hypercharge import WALL
    pins={}
    def pin(path,expected=None):
        path=Path(path);digest=sha256(path.read_bytes()).hexdigest()
        if expected is not None and digest!=expected:raise ValueError("frozen input changed: "+str(path))
        label=path.relative_to(repo).as_posix()
        pins[label]=digest
    old=repo/OLD_REL
    report_path=old/"result.json";pin(report_path,REPORT_SHA)
    report=json.loads(report_path.read_bytes())
    records=[]
    for stage in range(2):
        geometry_path=old/f"stage_{stage:04d}_current_geometry_normal_and_material_trace.npz"
        pin(geometry_path,report["archives"][geometry_path.name]["sha256"])
        with np.load(geometry_path,allow_pickle=False) as saved:
            time=saved["canonical_raw_coordinate_time_direction"][:100].copy()
            original_rho=saved["radial_points"].copy()
        stage_path=repo/report["trial"]/f"stage_{stage:04d}.npz"
        pin(stage_path,report["input_hashes"][stage_path.relative_to(repo).as_posix()])
        with np.load(stage_path,allow_pickle=False) as saved:
            raw=saved["stage_raw"].copy()
            coordinate_time=saved["coordinate_time"].item()
        if raw.shape!=(268,) or time.shape!=(100,) or not np.isfinite(raw).all() or not np.isfinite(time).all():
            raise ValueError("same complete frozen raw268 and canonical geometry100 time germ required")
        if np.any(abs(original_rho.imag)>1e-15) or np.any(original_rho.real<=0) or np.any(original_rho.real>=WALL):
            raise ValueError("saved original radial nodes must be genuinely interior")
        node_indices=tuple(dict.fromkeys((0,len(original_rho)//2,len(original_rho)-1)))
        q,v,m,delta,wall_rate,wall,Cstar=_geometry_variables(raw[:100])
        if abs(wall.gradient[25])>1e-14 or abs(Cstar.gradient[25])>1e-14:
            raise ValueError("declared qb0/raw25 partial unexpectedly moves wall/Cstar")
        samples=[("original_interior_node",i,float(original_rho[i].real)) for i in node_indices]
        samples.append(("actual_material_wall",None,float(WALL)))
        for kind,index,rho in samples:
            chi=(rho/WALL)*wall
            original=_fields(12,q,v,m,chi)
            f={name:scalar_jet(original[name],time) for name in FIELD_NAMES}
            N,C,A,B,beta=(original[name] for name in ("N","C","A","B","beta"))
            L=_sqrt(A*A+B*B)
            # These are inherited local analytic values, not absolute-value
            # replacements. The source _sqrt supplies the frozen LF branch.
            logL=np.log(L.value)
            coeff=m8_m5_geometric_coefficient_jets(f,
                fiber_radius_value=L.value,fiber_log_value=logL)
            r=A*B/L
            Lt=(A*A*original["la"]+B*B*original["lb"])/(A*A+B*B)
            Lc=(A*A*original["ap"]+B*B*original["bp"])/(A*A+B*B)
            rt=original["la"]+original["lb"]-Lt
            rc=original["ap"]+original["bp"]-Lc
            # Independent original Jet100 divergence products, differentiated
            # before contraction with the two frozen source directions.
            S8=C*A**3*B**3
            dtS8=S8*(original["lc"]+3*original["la"]+3*original["lb"])
            dcBetaS8=original["betap"]*S8+beta*S8*(original["cp"]+3*original["ap"]+3*original["bp"])
            S5=C*r**3
            dtS5=S5*(original["lc"]+3*rt)
            dcBetaS5=original["betap"]*S5+beta*S5*(original["cp"]+3*rc)
            h08=(dtS8-dcBetaS8)/(2*N*S8)
            hc8=(N*A**3*B**3)*(original["np"]+3*original["ap"]+3*original["bp"])/(2*N*C*A**3*B**3)
            h05=(dtS5-dcBetaS5)/(2*N*S5)
            hc5=(N*r**3)*(original["np"]+3*rc)/(2*N*C*r**3)
            direct=dict(LF=L,r=r,**{"lambda":A*A/(A*A+B*B)},
                h0_M8=h08,hchi_M8=hc8,h0_M5=h05,hchi_M5=hc5,
                mu8=N*C*A**3*B**3,mu5=N*C*r**3,
                fiber_norm_Lm32=1/(_sqrt(L)**3),
                original_time_principal_coefficient=1/N,
                original_chi_Gamma0_principal_coefficient=-beta/N,
                vertical_DF_coefficient=1/L)
            comparisons={name:jet_comparison(coeff[name],scalar_jet(a,time)) for name,a in direct.items()}
            direct_mean0=h08-h05-1.5*(Lt-beta*Lc)/N
            direct_meanc=hc8-hc5-1.5*Lc/C
            direct_coarea=N*C*A**3*B**3-N*C*r**3*L**3
            direct_identity_rows={name:{key:float(abs(value)) for key,value in scalar_jet(a,time).items()}
                for name,a in (('mean_cancellation_0',direct_mean0),('mean_cancellation_chi',direct_meanc),('coarea',direct_coarea))}
            identity_rows={name:{key:float(np.max(abs(coeff[name][key]))) for key in KEYS}
                for name in ('coarea_density_rows','analytic_fiber_normalization_rows',
                             'mean_contact_cancellation_0','mean_contact_cancellation_chi')}
            values={name:{key:encode(value[key]) for key in KEYS}
                    for name,value in coeff.items() if isinstance(value,Mapping) and set(value)==set(KEYS)}
            records.append(dict(stage=stage,coordinate_time=encode(coordinate_time),
                sample_kind=kind,original_radial_node_index=index,original_material_rho=rho,
                original_material_wall_rho=float(WALL),actual_moving_chi=encode(chi.value),
                interior_last_node_used_as_wall=False,
                coframe_scope="original chi coframe; evaluation point pulled back by chi=(rho/WALL)*wall",
                original_field_source_jets={name:{key:encode(value[key]) for key in KEYS} for name,value in f.items()},
                coefficient_jets=values,direct_original_Jet100_comparisons=comparisons,
                direct_original_Jet100_identity_rows=direct_identity_rows,helper_identity_rows=identity_rows,
                nonzero_component_norms={name:{key:float(np.linalg.norm(np.atleast_1d(coeff[name][key]))) for key in KEYS}
                    for name in ('KK_full_ordered','F_full','vertical_DF_coefficient',
                                 'original_time_principal_coefficient','original_chi_Gamma0_principal_coefficient',
                                 'original_seven_spatial_coframe_inverse_scales')},
                explicit_LF_sqrt_anchor=encode(L.value),explicit_log_LF_anchor=encode(logL)))
    component_paths=(Path(__file__).resolve(),repo/'src/bhsm/interface/muon_m8_m5_geometric_coefficients.py',repo/'tests/test_muon_m8_m5_geometric_coefficients.py')
    for path in component_paths:pin(path)
    # Bind every actually imported local BHSM source, without rerunning any
    # of their producer entrypoints. This catches transitive source changes.
    for name,module in sorted(sys.modules.items()):
        path=getattr(module,'__file__',None)
        if name.startswith('bhsm.') and path and Path(path).is_relative_to(repo):pin(Path(path))
    payload=dict(classification="M8_M5_GEOMETRIC_COEFFICIENTS_ON_FROZEN_COMPLEX_AFFINE_GERMS",
        records=records,input_and_source_sha256=dict(sorted(pins.items())),
        x_axis="frozen saved canonical raw100 coordinate-time tangent",
        y_axis="declared partial qb0/raw25 anisotropy coordinate; fixed raw time tangent",
        mixed_axis="rawtime^T Hessian e25 on raw=raw0+x rawtime+y e25; no rawxy contact imposed",
        partial_source_is_energy_or_measuring_B=False,physical_background_claimed=False,
        original_six_angular_and_one_normal_principals_retained=True,
        original_time_and_shift_principals_retained=True,vertical_DF_coefficient_set_zero=False,
        Clifford_native_SM_or_statistics_carrier_selected=False,
        full_M8_M5_native_or_retarded_operator_realized=False,
        physical_radial_or_angular_convergence_claimed=False,
        new_history_stage_profile_D5_or_radial_integrations=0,
        full_physical_derivative_at_2e_minus10_passed=False,coupled_corrections=0,
        normalized_physical_spins=None,physical_muon_magnetic_moment=None)
    sys.path.insert(0,str(repo/"tests"))
    from test_muon_m8_m5_geometric_coefficients import run_independent_controls
    controls=run_independent_controls()
    controls['scope']='separate off-shell integrable MP64 geometry controls; not saved-field physical checks'
    controls['source_sha256']={path.relative_to(repo).as_posix():pins[path.relative_to(repo).as_posix()] for path in component_paths}
    out.mkdir(parents=True)
    result=out/'result.json';controlpath=out/'controls.json'
    result.write_text(json.dumps(payload,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    controlpath.write_text(json.dumps(controls,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    summary=dict(result_sha256=sha256(result.read_bytes()).hexdigest(),controls_sha256=sha256(controlpath.read_bytes()).hexdigest(),
        samples=len(records),max_direct_scaled=max(v['scaled'] for r in records for c in r['direct_original_Jet100_comparisons'].values() for v in c.values()),
        max_helper_identity=max(v for r in records for c in r['helper_identity_rows'].values() for v in c.values()),
        physical_derivative_pass=False,coupled_corrections=0)
    print(json.dumps(summary,sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',default=str(REPO_DEFAULT));p.add_argument('--output',required=True)
    args=p.parse_args();evaluate(args.repository,args.output)
