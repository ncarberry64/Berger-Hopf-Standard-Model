"""Evaluate an unapplied finite root-defect diagnostic and preserve its scope."""
from pathlib import Path
from hashlib import sha256
import argparse
import json
import sys
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parent))
from muon_complex_pole_slope import pole_slope_invariants


def encode(x):
    if isinstance(x,dict):return {k:encode(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [encode(v)for v in x]
    if isinstance(x,np.ndarray):return encode(x.tolist())
    if isinstance(x,(complex,np.complexfloating)):return [float(x.real),float(x.imag)]
    if isinstance(x,np.generic):return x.item()
    return x


def run(repository,output):
    r,out=Path(repository).resolve(),Path(output).resolve()
    pins={};records=[]
    for p in [Path(__file__).resolve(),Path(__file__).with_name('muon_complex_pole_slope.py'),
              r/'src/bhsm/interface/muon_unsquared_physical_boundary_pole.py',
              r/'src/bhsm/interface/universal_precision_form_factor.py']:
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
    for stage in range(2):
        p=r/f'artifacts/muon_d5_finite_trace_pole_match_20261012/trial_0000_stage_pair_run_3/stage_{stage:04d}_finite_trace_pole_and_clock_rows.npz'
        pins[str(p)]=sha256(p.read_bytes()).hexdigest()
        with np.load(p,allow_pickle=False)as z:
            S=z['charged_two_spin_equation'].copy()
            Z=z['candidate_rank2_kinetic'].copy()
        # Diagnostic of the linearized reduced equation S+Z*dE. It is NOT
        # applied as an update, or interpreted as a magnetic insertion.
        H=-np.linalg.solve(Z,S)
        values=pole_slope_invariants(H)
        records.append(dict(stage=stage,diagnostic=values,
            matrix_equation_residual=float(np.max(abs(Z@H+S))),
            candidate_admitted=False,energy_update_applied=False,
            magnetic_probe_parameter_supplied=False))
    result=dict(
        classification='UNAPPLIED_FINITE_ROOT_DEFECT_AND_COMPLEX_POLE_OBSERVABLE_CONVENTION_CHECK',
        records=records,
        interpretation='Nonzero complex traceless root defects survive scalar trace centering. These linearized defect eigenvalues are neither validated pole updates nor magnetic moments.',
        retained_pole_convention='E=M-i*Gamma/2. For a physically admitted parameter response, Re(dE) and -2Im(dE) are energy and width slopes. Basis changes preserve the two unordered complex eigenvalues.',
        existing_readouts='The unsquared boundary API retains complex magnetic response matrices; the universal real on-shell F2 promotion path requires a real F2. A physical correspondence between these conventions is required, not a silent removal of absorptive response.',
        literature_scope='Unstable-particle electromagnetic moments can have absorptive contributions associated with field-dependent lifetime changes. This established possibility supplies no BHSM coefficient, state or correction.',
        primary_reference='https://arxiv.org/abs/0704.0377',
        physical_magnetic_moment=None,physical_complex_Pauli_coefficient=None,
        coupled_matching_corrections_applied=0,
        old_source_D5_profile_canonical_or_pairing_campaign_restarted=False,
        exact_scope='Binary64 small-matrix diagnostic on retained finite candidates; no physical domain, pole, external state, EM normalization or perturbation analyticity is inferred.',
        input_sha256=pins)
    for p,h in pins.items():
        if sha256(Path(p).read_bytes()).hexdigest()!=h:raise RuntimeError('input changed')
    out.mkdir(parents=True,exist_ok=False)
    data=json.dumps(encode(result),sort_keys=True,indent=2,allow_nan=False)+'\n'
    (out/'result.json').write_text(data,encoding='utf8',newline='\n')
    print(json.dumps(dict(path=str(out/'result.json'),sha256=sha256(data.encode()).hexdigest(),
        maximum_linear_equation_residual=max(v['matrix_equation_residual']for v in records),
        physical_magnetic_moment=None)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--repository',required=True);p.add_argument('--output',required=True)
    a=p.parse_args();run(a.repository,a.output)
