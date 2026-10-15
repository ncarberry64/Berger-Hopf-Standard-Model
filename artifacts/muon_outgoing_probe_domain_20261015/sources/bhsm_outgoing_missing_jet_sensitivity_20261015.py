"""Read-only sensitivity of retained finite poles to unassigned boundary jets.

These are algebraic perturbations of missing matrix entries, not proposed
physical exteriors. No magnetic insertion, spin assignment or moment is made.
"""
from argparse import ArgumentParser
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import zipfile
import numpy as np


def missing_jet_direction(gamma_energy, right, literal_left):
    """Return D=(Gamma_E r)(l Gamma_E)/(l Gamma_E r), without conjugation.

    l D r/z=1, so an unassigned additive magnetic jet tD changes a
    hypothetical same-pole energy slope by -t. An additive energy jet tD
    changes its kinetic residue from z to (1+t)z. Neither t nor D is an
    action-produced physical exterior completion.
    """
    ge, r, l = (np.asarray(a, complex) for a in (gamma_energy, right, literal_left))
    n = len(ge)
    if (ge.shape != (n,n) or r.shape != (n,1) or l.shape != (1,n)
            or any(not np.isfinite(a).all() for a in (ge,r,l))):
        raise ValueError('Full square energy jet and independent analytic left/right required')
    z = (l @ ge @ r).item()
    if z == 0:
        raise ValueError('Nonzero simple-pole kinetic pairing required')
    d = (ge @ r) @ (l @ ge) / z
    return dict(direction=d,kinetic_pairing=z,
                projected_direction=(l @ d @ r).item(),
                energy_slope_sensitivity=-(l @ d @ r).item()/z,
                direction_is_not_a_physical_outgoing_jet=True)


def encoded(value):
    if isinstance(value,dict):return {k:encoded(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [encoded(v) for v in value]
    if isinstance(value,np.ndarray):return encoded(value.tolist())
    if isinstance(value,(complex,np.complexfloating)):return [float(value.real),float(value.imag)]
    if isinstance(value,np.generic):return value.item()
    return value


def save(path, arrays):
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,value in sorted(arrays.items()):
            stream=BytesIO();np.lib.format.write_array(stream,np.asarray(value),allow_pickle=False)
            info=zipfile.ZipInfo(name+'.npy',date_time=(1980,1,1,0,0,0))
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,stream.getvalue())


def run(repository, output):
    repo,output=Path(repository).resolve(),Path(output).resolve()
    output.mkdir(parents=True,exist_ok=False)
    pins={};records=[];archives={}
    polebase=repo/'artifacts/muon_physical_outgoing_energy_20261015/split_poles/run_1'
    for stage in range(2):
        for branch in range(2):
            source=polebase/f'stage_{stage:04d}_branch_{branch}_actual_finite_simple_pole.npz'
            pins[str(source)]=sha256(source.read_bytes()).hexdigest()
            with np.load(source,allow_pickle=False) as a:
                g,ge,r,l=(a[k].copy() for k in ('gamma6','gamma_energy6','normalized_right6','normalized_literal_left6'))
                energy=a['energy'].item()
            app=missing_jet_direction(ge,r,l);d=app['direction'];z=app['kinetic_pairing']
            # An invertible analytic change of equation rows, not a tail.
            s=np.eye(6,dtype=complex)+.03*np.triu(np.ones((6,6)),1)+.01j*np.diag(np.arange(1,7))
            newleft=np.linalg.solve(s.T,l.T).T
            changed=missing_jet_direction(s@ge,r,newleft)
            t=.25-.125j
            kinetic_changed=(l@(ge+t*d)@r).item()
            row_sensitivity=(l@d@r).item()/z
            checks=dict(unit_missing_B_slope=abs(app['energy_slope_sensitivity']+1),
                energy_pairing_affine_identity=abs(kinetic_changed-(1+t)*z),
                analytic_row_covariance=np.linalg.norm(changed['direction']-s@d)/np.linalg.norm(s@d),
                projected_row_covariance=abs(changed['energy_slope_sensitivity']-app['energy_slope_sensitivity']))
            if max(checks.values())>2e-10:raise ArithmeticError('Algebraic sensitivity identity failed')
            filename=f'stage_{stage:04d}_branch_{branch}_missing_jet_direction.npz'
            save(output/filename,dict(gamma6=g,gamma_energy6=ge,right6=r,literal_left6=l,
                algebraic_missing_jet_direction=d,finite_kinetic_pairing=z,
                projected_missing_jet_direction=app['projected_direction'],energy=energy))
            archives[filename]=sha256((output/filename).read_bytes()).hexdigest()
            records.append(dict(stage=stage,branch=branch,energy=energy,
                branch_is_not_a_physical_spin_assignment=True,
                finite_kinetic_pairing=z,finite_original_right_rows=float(np.max(abs(g@r))),
                finite_original_literal_left_rows=float(np.max(abs(l@g))),
                direction_frobenius_norm=float(np.linalg.norm(d)),
                missing_B_jet_slope_sensitivity=-row_sensitivity,
                missing_E_jet_kinetic_sensitivity=app['projected_direction'],checks=checks))
    final=repo/'artifacts/muon_angular_retarded_polynomial_20261015/polynomial_lepton/run_3/result.json'
    pins[str(final)]=sha256(final.read_bytes()).hexdigest();finite=json.loads(final.read_text())
    result=dict(classification='EVALUATED_BOUNDARY_JET_IDENTIFIABILITY_ON_FOUR_RETAINED_FINITE_POLES',
        records=records,archives=archives,input_sha256=pins,
        identity='D=(Gamma_E r)(l Gamma_E)/(l Gamma_E r); l D r/z=1.',
        implication='The finite pole value/left/right/residue do not determine an omitted outgoing B jet or E jet. The displayed difference-only direction is nonzero on every retained finite pole.',
        limitation='Algebraic unassigned-matrix sensitivity only. No claim that the directions arise from an admissible physical exterior; no zero baseline magnetic jet is supplied.',
        finite_angular_derivative_discrepancy=max(x['relative_B_difference'] for x in finite['finite_B_difference_checks']),
        finite_derivative_scope_cannot_bound_unassigned_exterior_jets=True,
        full_physical_derivative_admitted=False,physical_outgoing_Gamma_E=None,physical_outgoing_Gamma_B=None,
        normalized_physical_two_spin_state=None,physical_magnetic_moment=None,physical_g_mu=None,physical_a_mu=None,
        coupled_matching_corrections_applied=0,completed_source_D5_profile_history_canonical_pairing_campaigns_restarted=False,
        original_finite_poles_resolved_again=False,coefficients_or_frozen_predictions_changed=False,
        measured_mass_or_anomaly_consumed=False,producer_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
    for path,value in pins.items():assert sha256(Path(path).read_bytes()).hexdigest()==value
    payload=(json.dumps(encoded(result),sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    (output/'result.json').write_bytes(payload)
    print(json.dumps(dict(output=str(output),result_sha256=sha256(payload).hexdigest(),
        maximum_algebra_identity_error=max(max(r['checks'].values()) for r in records))))


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('--repository',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();run(args.repository,args.output)
