"""Sparse high/low gauge and extra point tables from literal radial laws.

No state, coefficients, momentum or source is assigned. Consumers must
bind these tables to their actual original/extra coordinate incidences.
"""
from pathlib import Path
import argparse
import json


def run(repository,profiles,output):
    from bhsm_baton_zoo_radial_convergence import environment
    root,out,read,save,finish=environment(repository,output)
    import numpy as np
    from evaluate_muon_continued_current_factor import retained_input
    from flint import ctx,acb_mat
    from bhsm.interface.muon_stored_admission_correction import _matrix,_upper
    from bhsm.interface.muon_stored_fiber_canonical_tangent import _split
    phase,_=retained_input('outgoing',{});rep=phase['representation'];records=[];ctx.prec=192
    for degree in(2,4,6,8):
        p=read(Path(profiles)/f'degree_{degree:02d}_literal_MP_radial_profiles_and_derivative_complex.npz')
        nr=len(p['rho']);N=36*(degree+1);tables={}
        for half in('high','low'):
            values=p['values_'+half];derivatives=p['first_'+half]
            gb=np.zeros((nr,80,1,5,4),complex);gr=gb.copy();wall=np.zeros((5,4,80),complex);wallr=wall.copy()
            for j,label in enumerate(rep['gauge_labels']):
                f=next(i for i,name in enumerate(('A_tau','A_rho','A_1','A_2','A_3'))if name==label['field'])if label['field'] in('A_tau','A_rho','A_1','A_2','A_3')else None
                if f is None:
                    from bhsm.interface.muon_parent_maxwell_full_weak import FIELD_ORDER
                    f=FIELD_ORDER.index(label['field'])
                r,c=label['radial'],label['internal'];gb[:,j,0,f,c]=values[:,r];gr[:,j,0,f,c]=derivatives[:,r]
                wall[f,c,j]=p['wall_values_'+half][0,r];wallr[f,c,j]=p['wall_first_'+half][0,r]
            T=np.zeros((nr,60,N+8),complex);Tw=np.zeros((5,4,N+8),complex);Twr=Tw.copy()
            for l in range(degree+1):
                v,vr=values[:,4+l],derivatives[:,4+l]
                for f in range(1,5):
                    for c in range(4):
                        pos=36*l+4*(f-1)+c;rate=pos+16;T[:,4*f+c,pos]=v;T[:,40+4*f+c,pos]=vr;T[:,20+4*f+c,rate]=v
                        Tw[f,c,pos]=p['wall_values_'+half][0,4+l];Twr[f,c,pos]=p['wall_first_'+half][0,4+l]
                for c in range(4):
                    at=36*l+32+c;T[:,c,at]=v;T[:,40+c,at]=vr
                    Tw[0,c,at]=p['wall_values_'+half][0,4+l];Twr[0,c,at]=p['wall_first_'+half][0,4+l]
            T[:,7,N:N+4]=p['psi_'+half];T[:,47,N:N+4]=p['psi_first_'+half];T[:,27,N+4:]=p['psi_'+half]
            Tw[1,3,N:N+4]=p['wall_psi_'+half][0];Twr[1,3,N:N+4]=p['wall_psi_first_'+half][0]
            tables.update({f'original_gauge_basis_{half}':gb,f'original_gauge_radial_basis_{half}':gr,
                f'original_wall_trace_map_{half}':wall,f'original_wall_radial_derivative_map_{half}':wallr,
                f'compatible_extra_point_lift_{half}':T,f'compatible_extra_wall_lift_{half}':Tw,
                f'compatible_extra_wall_radial_lift_{half}':Twr,
                f'phi_extra_point_lift_{half}':T[:,:,:N],f'phi_extra_wall_lift_{half}':Tw[:,:,:N]})
        # Exact pointwise check of every central derivative, independently
        # of a future action/Cauchy-domain solve.
        max_identity=0.
        for r in range(nr):
            v=_matrix(p['values_high'][r:r+1])+_matrix(p['values_low'][r:r+1])
            psi=_matrix(p['psi_high'][r:r+1])+_matrix(p['psi_low'][r:r+1])
            vals=acb_mat([[v[0,j]for j in range(v.ncols())]+[psi[0,j]for j in range(4)]])
            coeff=_matrix(p['derivative_coefficients_high'])+_matrix(p['derivative_coefficients_low'])
            first=_matrix(p['first_high'][r:r+1])+_matrix(p['first_low'][r:r+1])
            max_identity=max(max_identity,_upper(vals*coeff-first))
        tables.update(rho=p['rho'],profile_degrees=np.arange(degree+1),
            compatible_extra_profile_block_order=np.asarray([36]*(degree+1)+[8]),
            original_gauge_labels_radial=np.asarray([x['radial']for x in rep['gauge_labels']]),
            original_gauge_labels_internal=np.asarray([x['internal']for x in rep['gauge_labels']]))
        save(f'degree_{degree:02d}_literal_MP_original_and_extra_point_wall_tables.npz',tables)
        records.append(dict(degree=degree,phi_extra_count=N,compatible_extra_count=N+8,central_derivative_identity_upper=max_identity,
            new_wall_Ar_values_max=float(np.max(abs(tables['compatible_extra_wall_lift_high']+tables['compatible_extra_wall_lift_low'])))))
    finish(dict(classification='LITERAL_HIGH_LOW_ORIGINAL_AND_EXTRA_GAUGE_POINT_TABLES_EXPORTED',records=records,
        original_profile_constants_and_independent_Cauchy_momenta_preserved=True,
        Cauchy_or_source_or_exterior_identification_performed=False),producer_paths=(Path(__file__),))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in('repository','profiles','output'):p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();run(a.repository,a.profiles,a.output)
