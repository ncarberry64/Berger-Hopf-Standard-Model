"""Preserve the actual full-cap sigma-normal rejection; no normal is replaced."""
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
import numpy as np
import bhsm_real_full_d5_open_form_20261016 as app
from bhsm.interface.muon_holomorphic_d5_trace_action import d5_sigma_foliation_eta
from bhsm.interface.muon_birth_phase_continuation import _compressed_npz

def execute(output):
    out=Path(output).resolve()
    if out.exists():raise FileExistsError("Preserve independent failure packets")
    source=Path(app.__file__);source_bytes=source.read_bytes()
    q,_=np.polynomial.legendre.leggauss(4);rho=np.r_[(q+1)*app.WALL/2,app.WALL]
    tx,_=np.polynomial.legendre.leggauss(2)
    arrays={};records=[];pins={}
    for side,path in app.PHASES.items():
        phase=app.load_profile_preserving_phase(path,repository=app.REPO);pins.update(phase["input_hashes"])
        rep=app.radial_representation(phase["representation"],rho);span=float(phase["receipt"]["span"])
        lo,hi=min(0.,span),max(0.,span)
        times=np.r_[lo+(tx+1)*(hi-lo)/2,(lo+hi)/2]
        for k,t in enumerate(times):
            c,s=app.sample_coefficients(phase,float(t),rep)
            N,C,z=(c[a]for a in("lapse","radial_coframe","coordinate_shift"))
            s0=(c["sigma_coordinate_time"]-z*c["sigma_radial"])/N;s4=c["sigma_radial"]/C
            f0=(c["eta_profile_coordinate_time"]-z*c["eta_profile_radial"])/N;f4=c["eta_profile_radial"]/C
            Qs,Qf=s4*s4-s0*s0,f4*f4-f0*f0
            failure=None
            try:
                d5_sigma_foliation_eta(c,gamma=app.full_d5_localized_lepton_trace()["gamma5D_particle"],
                    carrier_count=1,angular_count=1,sheet_orientation=1)
            except ValueError as error:failure=dict(type=type(error).__name__,message=str(error))
            prefix=f"{side}_sample{k}_"
            for key,value in c.items():
                if isinstance(value,np.ndarray):arrays[prefix+"c_"+key]=value
            arrays[prefix+"raw"]=s["raw_fields"];arrays[prefix+"raw_future_time"]=s["raw_coordinate_time_derivative"]
            for key,value in dict(rho=rho,s0=s0,s4=s4,Q_sigma=Qs,f0=f0,f4=f4,Q_f=Qf).items():arrays[prefix+key]=value
            brackets={}
            for name,value in(("sigma",Qs),("f",Qf)):
                brackets[name]=[[float(rho[j]),float(rho[j+1])]for j in range(len(rho)-1)if value[j].real*value[j+1].real<0]
            records.append(dict(side=side,coordinate_time=float(t),sample_kind="actualGauss2"if k<2 else"actualsavedcellmidpoint",
                sigma_normal_exception=failure,minimum_Q_sigma=float(np.min(Qs.real)),minimum_Q_f=float(np.min(Qf.real)),
                wall_Q_sigma=float(Qs[-1].real),wall_Q_f=float(Qf[-1].real),null_locus_brackets=brackets,
                f_coordinate_time_vs_actual_raw_time_jet_error=float(np.max(abs(c["eta_profile_coordinate_time"]-c["eta_profile_first"][0])))))
    for name,module in list(sys.modules.items()):
        p=getattr(module,"__file__",None)
        if name.startswith("bhsm.")and p and Path(p).is_relative_to(app.REPO):
            pins[Path(p).relative_to(app.REPO).as_posix()]=sha256(Path(p).read_bytes()).hexdigest()
    pins["WORK/"+source.name]=sha256(source_bytes).hexdigest()
    pins["WORK/"+Path(__file__).name]=sha256(Path(__file__).read_bytes()).hexdigest()
    out.mkdir(parents=True)
    (out/"failed_requested_full_cap_producer.py").write_bytes(source_bytes)
    _compressed_npz(out/"actual_real_coefficients_and_normal_squares.npz",arrays)
    result=dict(classification="PRESERVED_ACTUAL_REAL_FULL_CAP_SIGMA_NORMAL_REJECTION",
        attempted_producer=source.name,attempted_angular_level=1,attempted_time_order=2,attempted_radial_order=4,
        exception_source="muon_holomorphic_d5_trace_action.d5_sigma_foliation_eta, outward nonnull analytic normal guard",
        records=records,source_normal_scope="Foundation uses proper-wall normal; v15.26 grad(f_eta) is explicitly on regular wall collar. No global grad(sigma) or grad(f) adoption inferred.",
        no_abs_or_complex_projection_or_zero_eta=True,alternative_normal_or_collar_chosen=False,
        full_cap_form_assembled=False,full_D5_or_original_action_globally_undefined_inferred=False,
        physical_derivative_pass=False,coupled_corrections=0,new_history_or_source_campaigns=0,
        input_and_source_sha256=dict(sorted(pins.items())),
        numerical_sha256=sha256((out/"actual_real_coefficients_and_normal_squares.npz").read_bytes()).hexdigest())
    (out/"result.json").write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n",encoding="utf8",newline="\n")
    print(json.dumps(dict(samples=len(records),numerical_sha256=result["numerical_sha256"],
        all_source_sigma_guards_rejected=all(r["sigma_normal_exception"]is not None for r in records),
        physical_derivative_pass=False)))
    return result

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--output",required=True)
    execute(p.parse_args().output)
