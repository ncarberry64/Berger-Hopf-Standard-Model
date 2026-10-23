"""Shared-profile and restricted one-plane consistency calculations.

The redshift contrast concerns a specified decomposition into a fixed local
potential and one physical quadratic term at the main lens.  It is not a
generic observable, an exclusion of line-of-sight structure, or an MST cure.
"""
from pathlib import Path
import json
import numpy as np
from angular_optical_response import AngularOpticalProvider, angular_hessian_tf, stf4_basis

ROOT=Path(__file__).resolve().parents[1]


def run():
    data=json.loads((ROOT/'artifacts/temporal/angular_response.json').read_text())
    q=np.array([0.,0.,.001,0.,0.,0.])
    c=np.array([[.5,.23,-.11],[.23,-.1,.08],[-.11,.08,-.4]])
    c/=np.sqrt(np.trace(c@c))
    a=np.zeros((4,4));a[1:,1:]=c
    n=np.array([1.,2.,3.]);n/=np.linalg.norm(n)
    H=angular_hessian_tf(a,n)
    shears=[]
    for item in data['configurations']:
        for key in ['ol','os','ls']:
            g=np.array(item['segments'][key]['g_per_physical_anchor'])
            shear=(g@q)*H
            shears.append([shear[0,0],shear[0,1]])
    shears=np.array(shears)
    determinants=np.outer(shears[:,0],shears[:,1])-np.outer(shears[:,1],shears[:,0])
    # Fixed z_l=.3, source redshift 1.0 minus .6, with fixed physical local body.
    first,second=data['configurations'][0],data['configurations'][1]
    def reduced_quadratic(item):
        s=item['segments']
        p=s['ls']['background_distance_c_over_H0']/s['os']['background_distance_c_over_H0']
        return p,np.array(item['fermat_shear_kernel_g_ol_minus_g_ls_plus_g_os'])/p
    p1,b1=reduced_quadratic(first);p2,b2=reduced_quadratic(second)
    contrast=b1-b2
    provider=AngularOpticalProvider()
    scan=[]
    for zs in np.linspace(.4,2.,33):
        r=provider.three_segments(.3,float(zs))
        p=r['ls'].distance/r['os'].distance
        B=(r['ol'].g-r['ls'].g+r['os'].g)/p
        scan.append({'z_l':.3,'z_s':float(zs),'p':float(p),
                     'quadratic_coefficient_over_p_per_anchor':B.tolist(),
                     'density_seed_B11_over_p':float(np.sqrt(2)*(B@q)),
                     'fractional_delay_kernel':(np.sqrt(2)*(r['os'].g-r['ol'].g)).tolist()})
    result={'schema':'BHSM-SHARED-STATE-RELATIONS-V1',
            'common_profile':{'C':c.tolist(),'sightline':n.tolist(),'anchor':q.tolist(),
                              'shear_components':shears.tolist(),
                              'max_pairwise_determinant_absolute':float(np.max(abs(determinants))),
                              'singular_values':np.linalg.svd(shears,compute_uv=False).tolist(),
                              'assumption':'all six temporal components share the same fixed spatial C'},
            'restricted_single_plane_contrast':{
                 'z_l':.3,'source_redshifts_order':[1.,.6],
                 'p_values':[p1,p2],
                 'coefficient_rows_over_p':[b1.tolist(),b2.tolist()],
                 'difference_per_anchor':contrast.tolist(),
                 'illustrative_nodal_density_seed_R11':float(np.sqrt(2)*(contrast@q)),
                 'definition':'R_st=B_s/p_s-B_t/p_t; B_s=(g_ol-g_ls+g_os) dot q H_C',
                 'null_scope':'one fixed physical quadratic potential at the main lens with common D_ol and fixed other local potential',
                 'not_claimed':'directly measured contrast, generic multi-source identification, or breaking generalized mass-sheet/LOS freedom'},
            'redshift_scan':scan,
            'observational_data_used':False}
    assert result['common_profile']['max_pairwise_determinant_absolute'] < 1.e-25
    out=ROOT/'artifacts/lensing/shared_state_relations.json'
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'common_profile_determinant':result['common_profile']['max_pairwise_determinant_absolute'],
                      'two_source_contrast_R11':result['restricted_single_plane_contrast']['illustrative_nodal_density_seed_R11'],
                      'scan_points':len(scan)},indent=2))


if __name__=='__main__':
    run()
