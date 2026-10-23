"""Evaluate the unregulated full-time Green on the same complete field sources."""
from pathlib import Path
from hashlib import sha256
import argparse,json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
from bhsm.interface.muon_dirichlet_source_green_collocation import dirichlet_source_current_collocation
from bhsm.interface.muon_source_directed_temporal_green import invariant_source_blocks,_source_point
from bhsm.interface.muon_profile_preserving_phase_sample import load_profile_preserving_phase
from bhsm.interface.muon_parent_maxwell_full_q_application import retained_full_q_angular_space
from bhsm.interface.muon_native_dirac_hamiltonian import lepton_current_hilbert_representation
from evaluate_muon_reached_trace_action import deterministic_archive


def materialize(output):
    out=ROOT/output
    if out.exists():raise FileExistsError('preserve earlier direct Green applications')
    folder=ROOT/'artifacts/muon_changing_coupled_open_current_20261011/run_1'
    original=(folder/'result.json').read_bytes();receipt=json.loads(original)
    if receipt['classification']!='EVALUATED_CHANGING_COUPLED_FIELD_FERMION_OPEN_EXCHANGE':
        raise ValueError('same changing field/current reference required')
    enriched=ROOT/'artifacts/muon_source_directed_temporal_green_20261011/run_1/result.json'
    raw_enriched=enriched.read_bytes();enriched_receipt=json.loads(raw_enriched)
    refs=dict(receipt['input_hashes']);refs[(folder/'result.json').relative_to(ROOT).as_posix()]=sha256(original).hexdigest()
    refs[enriched.relative_to(ROOT).as_posix()]=sha256(raw_enriched).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise ValueError('consumed owner changed')
    angular=retained_full_q_angular_space(ROOT);blocks=invariant_source_blocks(angular)
    alpha=lepton_current_hilbert_representation()['alpha'];arrays={};rows=[]
    for side in ('incoming','outgoing'):
        phase=load_profile_preserving_phase('artifacts/muon_finite_normal_phase_20261011/incoming_run_1'if side=='incoming'
            else'artifacts/muon_inherited_finite_normal_phase_20261011/run_1')
        refs.update(phase['input_hashes']);L=abs(phase['receipt']['span']);modes=[];data={}
        for name in ('result','field_modes_0','field_modes_1'):
            p=folder/(side+'_'+name+'.npz');b=p.read_bytes();h=sha256(b).hexdigest()
            if h!=receipt['array_archives'][p.name]['sha256']:raise ValueError('field Green array changed')
            refs[p.relative_to(ROOT).as_posix()]=h
            with np.load(p,allow_pickle=False)as z:
                if name=='result':data={k:z[k].copy()for k in z.files}
                else:modes.append(z['field_Gram_orthonormal_eigenvectors'].copy())
        lb=data['field_generalized_eigenvalues'];UB=np.concatenate(modes,axis=1)
        if min(lb)<=0 or UB.shape!=(1200,1200):raise ValueError('complete same positive field inverse required')
        # One complete field inverse is absorbed once across its two vertices.
        UBsqrt=UB/np.sqrt(lb)[None,:]
        extnorm=next(r['external_tent_Gram']for r in enriched_receipt['records']if r['side']==side)
        points={};scale=np.sqrt(extnorm)
        # Shared exact Gauss collocation point grid; all evaluated source points retained in the receipt.
        grid={0.}
        for count in (8,10):
            zz,_=np.polynomial.legendre.leggauss(count)
            grid.update(float(L*(half+(x+1)/2)/2)for half in (0,1)for x in zz)
        grid=np.array(sorted(grid))
        for k,u in enumerate(grid):
            a=_source_point(phase,u,L,angular,blocks)
            a['field_sqrt_right']=(a['right_fields'].reshape(480,1200)@UBsqrt).reshape(24,20,1200)
            del a['right_fields'],a['left_fields'];points[k]=a
        outputs={};block_records=[]
        for steps in (8,10):
            total=np.zeros((18,18),complex);maxres=0.;maxcond=0.
            for family,fi in enumerate(blocks['family_indices']):
                for ab in blocks['angular_blocks']:
                    hi=ab['harmonic_indices'];d=6*len(hi);cached={}
                    def evaluate(u):
                        k=int(np.argmin(abs(grid-u)))
                        if abs(grid[k]-u)>1e-12*L:raise ValueError('direct source grid escaped retained point applications')
                        if k not in cached:
                            a=points[k];E=blocks['complex_derivatives'][:,hi][:,:,hi]
                            B=np.kron(a['W'][np.ix_(fi,fi)]+a['Omega'][np.ix_(fi,fi)],np.eye(len(hi)))-1j*sum(
                                np.kron(v[np.ix_(fi,fi)],e)for v,e in zip(alpha,E))/a['R']
                            V=a['vertices'][:,fi][:,:,fi];fields=a['field_sqrt_right'][:,hi]
                            sr=np.einsum('chf,cij->hfij',fields,V)
                            sl=np.einsum('chf,cij->hfij',fields.conj(),V)
                            cached[k]=dict(N=a['N'],B=B,S=sr.transpose(2,0,3,1).reshape(d,6,1200)*a['b']/scale,
                                L=sl.transpose(2,3,0,1).reshape(6,d,1200)*a['b']/scale)
                        return cached[k]
                    r=dirichlet_source_current_collocation(evaluate,length=L,stages=steps)
                    total[np.ix_(fi,fi)]+=r['signed_source_current'];maxres=max(maxres,r['endpoint_relative_residual']);maxcond=max(maxcond,r['fundamental_source_condition'])
                    block_records.append(dict(Gauss_stages=steps,family=family,level=ab['level'],spectator=ab['spectator'],
                        dimension=d,current_norm=float(np.linalg.norm(r['signed_source_current'])),
                        endpoint_relative_residual=r['endpoint_relative_residual'],stage_relative_residual=r['stage_relative_residual'],
                        fundamental_source_condition=r['fundamental_source_condition']))
                    print(json.dumps(dict(side=side,**block_records[-1]),sort_keys=True),flush=True)
            arrays[side+'_unregulated_full_time_current_'+str(steps)]=total;outputs[steps]=total
        arrays[side+'_coefficient_time']=grid+( -L if side=='incoming'else 0.)
        arrays[side+'_N_R_samples']=np.array([[a['N'],a['R']]for a in points.values()])
        rows.append(dict(side=side,length=L,external_tent_Gram=extnorm,Gauss_stages=[8,10],
            unregulated_full_time_current_norm=float(np.linalg.norm(outputs[10])),
            refinement_difference_norm=float(np.linalg.norm(outputs[10]-outputs[8])),
            relative_refinement_difference=float(np.linalg.norm(outputs[10]-outputs[8])/np.linalg.norm(outputs[10])),
            Hermitian_defect=float(np.linalg.norm(outputs[10]-outputs[10].conj().T)),block_records=block_records))
        print(json.dumps(dict(stage='complete_direct_dirichlet_current',**{k:v for k,v in rows[-1].items()if k!='block_records'}),sort_keys=True),flush=True)
        del points,modes,data,UB,UBsqrt
    for p in ('src/bhsm/interface/muon_dirichlet_source_green_collocation.py','tests/test_muon_dirichlet_source_green_collocation.py',
        'src/bhsm/interface/muon_source_directed_temporal_green.py',Path(__file__).relative_to(ROOT).as_posix()):
        refs[p]=sha256((ROOT/p).read_bytes()).hexdigest()
    if any(sha256((ROOT/p).read_bytes()).hexdigest()!=h for p,h in refs.items()):raise RuntimeError('consumed source/action changed')
    out.mkdir(parents=True);deterministic_archive(out/'application.npz',arrays)
    result=dict(classification='EVALUATED_GAUSS_COLLOCATED_FULL_TIME_UNREGULATED_SOURCE_GREEN',input_hashes=refs,records=rows,
        archive=dict(path='application.npz',bytes=(out/'application.npz').stat().st_size,sha256=sha256((out/'application.npz').read_bytes()).hexdigest()),
        source_domain='same changing full1200 field Green, all18 fibers and odd20 harmonics, exact family/Wigner spectators',
        temporal_domain='continuous Dirichlet full-time source Green on same analytic coefficient cell, split at source tent midpoint',
        field_Green_normalization='same physical action Gram and one UB lambda^-1 UB^T inverse; two lambda^-1/2 placements once',
        quantum_scope='formal unregulated reference Gaussian -1 open-current benchmark, not the finite-common-cutoff heat or Lorentz/native self-energy',
        numerical_finite_time_trial_projection_removed=True,full_native_temporal_loop_completed=False,
        physical_a_mu=None,physical_g_mu=None,
        error_scope='Gauss8/10 split-interval collocation convergence and Dirichlet face residuals are evaluated diagnostics; no outward integration, field inverse/eigenproduction, native completion or observable uncertainty enclosure')
    (out/'result.json').write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(classification=result['classification'],archive=result['archive']),sort_keys=True))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();materialize(a.output)
