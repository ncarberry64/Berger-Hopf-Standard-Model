"""Focused current source pairings and collar-coordinate checks, not B54."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import numpy as np


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,x):p.write_bytes((json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n').encode())


def run(root,output):
    if output.exists():raise FileExistsError('fresh output directory required')
    sys.path.insert(0,str(root/'src'))
    from bhsm.interface.muon_wall_source_pairing import source_reached_pairing
    base=root/'artifacts/muon_parent_source_rate_20261003'
    contact=root/'artifacts/muon_parent_source_contact_20261003/replay_reference/parent_source_contact.npz'
    geometry=root/'artifacts/muon_parent_geometry_20261001/replay_reference/local_parent_velocity_density.npz'
    corrected=base/'replay_reference/parent_source_rate_corrected.npz'
    rate_path=base/'replay_reference/cut_rate_record.json'
    rate=json.loads(rate_path.read_text())
    with np.load(contact) as c,np.load(geometry) as g,np.load(corrected) as p:
        arrays,result=source_reached_pairing(c,g,p,rate)
    output.mkdir(parents=True)
    np.savez_compressed(output/'source_reached_pairings.npz',**arrays)
    save(output/'radial_slice_causal_certificate.json',result.pop('radial_slice_certificate'))
    save(output/'result.json',dict(classification='evaluated source-reached geometric pairing and initial wall normal jet; current wall overlap not evaluated',
        start_HEAD='e983e4cfd98de81679d74106d181325e7b618935',
        code_base_HEAD=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        equations=dict(source_trial='p_Ak=(T_b chi_hat/r) Xi_A e_k with full n1/n3',
            T='T_ij=integral mu5 (W_eta e_i)^dagger p_j',B='M4 B_required=T',
            M4='2*pi^2 sqrt(nu_wall^2-C_wall^2 zeta_wall^2) r_wall^3 I64 per tau and normalized Haar',
            source_Gram='2*pi^2 T_b^2 integral nu C r chi_hat^2 d_rho * Gram_Haar(Xi_A e_k)'),
        result=result,
        profile_reconciliation=dict(retained_profile_exists=True,
            retained_static='v13.1 p2+p8 degree-one F(r), imported by v15.26; no static solve rerun',
            current_join='f=chi and material overlap sin^2 f cos^2 f; v15.32 explicitly rejects transplant of the S6 radial trace',
            required_probability_identity='J_current abs(u0_current)^2 ds = N^2 sin^2 f_eta,current ds; not identified by the inspected equations with d sigma_join',
            first_profile_coefficient='m_eta,current=-partial_s log sin f_eta,current on source-reached collar support',
            missing_attachment='the current-background pullback of the adopted eta wall profile/probability into the same collar/radial/Spin carrier realization; not a new freely fitted profile'),
        error_scope='binary64 source/Gram/volume data; radial scalar and causal polynomial certificate only for exact binary64 affine nodal model. Actual collar/profile/transport matching and continuum/history errors unevaluated.',
        interface_application=dict(M4_density_evaluated=True,actual_overlap_T=None,B_required=None,
            K_interface=None,M_interface_off_diagonal=None,stationary_exterior_response=None),
        execution=dict(old_H_repair_replayed=False,old_body_contact_or_trial_conormal_replayed=False,
            static_eta_profile_resolved_again=False,wall_overlap_evaluations=0,exterior_shifted_solves=0,
            native_heat_evaluations=0,physical_transfer_directions=0),physical_a_mu=None,physical_g_mu=None))
    inputs=[contact,geometry,corrected,rate_path,root/'src/bhsm/interface/muon_wall_source_pairing.py',
        root/'src/bhsm/interface/muon_parent_source_contact.py',Path(__file__)]
    save(output/'input_hashes.json',[dict(path=str(p),sha256=sha(p)) for p in inputs])
    save(output/'receipt.json',dict(files=[dict(path=p.name,sha256=sha(p)) for p in sorted(output.iterdir())]))
    print(json.dumps(dict(output=str(output),checks=result['checks'],wall_chart_initial_jet=result['wall_chart_initial_jet'],wall_overlap_evaluations=0)))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--repository',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();run(a.repository.resolve(),a.output.resolve())
