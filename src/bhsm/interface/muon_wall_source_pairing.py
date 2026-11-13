"""Actual source-reached geometric pairing, before an unevaluated wall overlap.

The material join density is not substituted for the normalized Dirac wall
mode. The result supplies the known factor in T=<W e,p>_5, not W or B54.
"""
from fractions import Fraction
from math import comb
import numpy as np

from bhsm.interface.muon_parent_source_contact import exact_affine_integral,scalar_enclosure


def radial_slice_causal_certificate(geometry,cells):
    """Bernstein enclosure on the exact binary64 affine nodal model.

    h_tau_tau=nu^2-(C*zeta)^2 is quartic on each rho cell. Bounds cover
    the whole selected cells, not merely the saved Gauss samples. They do
    not bound the supplied continuum/history reconstruction error.
    """
    records=[]
    for c in sorted(set(map(int,cells))):
        polys=[]
        for k in ('proper_lapse','C_rho','proper_shift_rho'):
            l,r=map(lambda z:Fraction(float(z)),geometry[k][0,c:c+2])
            polys.append([l,r-l])
        nu,C,z=polys
        def mul(a,b):
            p=[Fraction(0)]*(len(a)+len(b)-1)
            for i,x in enumerate(a):
                for j,y in enumerate(b):p[i+j]+=x*y
            return p
        plus=mul(nu,nu);cz=mul(C,z);minus=mul(cz,cz)
        power=[(plus[i] if i<len(plus) else Fraction(0))-minus[i] for i in range(5)]
        bern=[sum((power[i]*Fraction(comb(k,i),comb(4,i)) for i in range(k+1)),Fraction(0)) for k in range(5)]
        records.append(dict(cell=c,power=[str(a) for a in power],bernstein=[str(a) for a in bern],
            lower_exact=str(min(bern)),upper_exact=str(max(bern)),strictly_negative=max(bern)<0))
    low=min(Fraction(r['lower_exact']) for r in records)
    high=max(Fraction(r['upper_exact']) for r in records)
    return dict(records=records,all_source_support_cells_strictly_negative=all(r['strictly_negative'] for r in records),
        global_lower_outward=float(np.nextafter(float(low),-np.inf)),
        global_upper_outward=float(np.nextafter(float(high),np.inf)),
        scope='exact binary64 affine nodal model on source support cells; continuum/history uncertainty excluded')


def source_reached_pairing(contact,geometry,corrected,cut_rate):
    """Evaluate p_Ak and its geometric Gram without selecting a wall mode.

    p_Ak=(T_b chi_hat/r) Xi_A e_k, with all n1/n3 angular coefficients,
    every 64-component output and the four retained input spin coordinates.
    No inverse of the possibly redundant source Gram is taken.
    """
    rho=geometry['rho'];cells=corrected['gauss_cells'];points=corrected['gauss_rho']
    x=(points-rho[cells])/np.diff(rho)[cells]
    def val(k):return geometry[k][0,cells]*(1-x)+geometry[k][0,cells+1]*x
    nu,C,r,zeta=(val(k) for k in ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    Tb=float(contact['T_b'])
    if cut_rate['cut_id']!='C2_step1222' or Tb!=cut_rate['T_b']:raise ValueError('same cut/source required')
    chi=np.interp(points,contact['rho'],contact['spinor_probe_hat_nodes'])
    factor=Tb*chi/r
    mu5=2*np.pi**2*nu*C*r**3
    columns=corrected['source_image_probe_columns']
    unit_gram=np.zeros((32,32),complex);arrays={}
    for n in (1,3):
        xi=contact[f'Xi_A_unit_n{n}'][:,:,columns]
        # i=(photon source A,input spin coordinate k); no angular compression.
        f=xi.transpose(1,3,4,0,2).reshape(-1,32)
        unit_gram+=f.conj().T@f
        p=factor[:,None,None,None,None,None]*xi[None]
        arrays[f'actual_source_trial_n{n}']=p
        arrays[f'known_T_integrand_factor_mu5_p_n{n}']=mu5[:,None,None,None,None,None]*p
    rat=exact_affine_integral(rho,[geometry['proper_lapse'][0],geometry['C_rho'][0],
        geometry['base_radius'][0],contact['spinor_probe_hat_nodes'],contact['spinor_probe_hat_nodes']])
    scalar=scalar_enclosure(rat,Fraction(Tb)**2)
    gram=scalar['midpoint']*unit_gram
    # Wall M4 geometric volume density, per retained proper boundary time
    # and normalized S3 Haar. This is not a CAR slice measure or a pole residue.
    nb,cb,rb,zb=(float(geometry[k][0,-1]) for k in
                ('proper_lapse','C_rho','base_radius','proper_shift_rho'))
    hb=nb*nb-(cb*zb)**2
    if hb<=0:raise ValueError('material wall must be timelike for this retained trace realization')
    wall_mu=2*np.pi**2*np.sqrt(hb)*rb**3
    m4=wall_mu*np.eye(64)
    # R4' = H_f R4 in boundary proper time. nu_boundary=1 by definition;
    # its cache roundoff does not define an additional lapse history.
    m4_tau=3*float(cut_rate['value'])*m4
    dt=float(geometry['proper_times'][1]-geometry['proper_times'][0])
    Cr=(geometry['C_rho'][0,-1]-geometry['C_rho'][0,-2])/(rho[-1]-rho[-2])
    zr=(geometry['proper_shift_rho'][0,-1]-geometry['proper_shift_rho'][0,-2])/(rho[-1]-rho[-2])
    Ct=(geometry['C_rho'][1,-1]-geometry['C_rho'][0,-1])/dt
    # Limiting seam zeta=0, nu=1; exact endpoint shift is zero from sin(pi).
    # These are initial Gaussian normal jets, not a solved collar chart.
    tau_ss=-(Ct-cb*zr)/(cb*nb*nb)
    rho_ss=-Cr/cb**3
    gamma5=corrected['gamma5']
    arrays.update(gauss_rho=points,gauss_cells=cells,source_input_columns=columns,
        mu5_volume_density_per_tau_normalized_Haar=mu5,
        constant_rho_induced_h_tau_tau=nu*nu-(C*zeta)**2,
        source_unit_Haar_Gram=unit_gram,source_geometric_Gram=gram,
        M4_wall_geometric_density=m4,M4_wall_geometric_density_tau=m4_tau,
        wall_chiral_left=(np.eye(4)-gamma5)/2,wall_chiral_right=(np.eye(4)+gamma5)/2)
    source_frame=[dict(column=4*A+k,source_A=A,input_spin=k,input_carrier_column=int(columns[k]))
                  for A in range(8) for k in range(4)]
    checks=dict(source_Gram_Hermitian_residual=float(np.linalg.norm(gram-gram.conj().T)),
        source_Gram_min_eigenvalue_float=float(np.linalg.eigvalsh(gram)[0]),
        source_Gram_rank_tolerance_1e_minus10=int(np.linalg.matrix_rank(gram,tol=1e-10)),
        source_Gram_rank_is_only_diagnostic=True,
        connected_n1_source_norm=float(np.linalg.norm(arrays['actual_source_trial_n1'])),
        connected_n3_source_norm=float(np.linalg.norm(arrays['actual_source_trial_n3'])),
        boundary_radius_match_residual=abs(rb-float(geometry['boundary_radius'][0])),
        endpoint_shift_cache_roundoff=zb,
        wall_geometric_density=wall_mu,
        wall_geometric_density_tau=3*float(cut_rate['value'])*wall_mu)
    return arrays,dict(radial_source_Gram_scalar=scalar,radial_source_Gram_rational=str(rat),
        source_frame=source_frame,checks=checks,
        radial_slice_certificate=radial_slice_causal_certificate(geometry,cells),
        wall_chart_initial_jet=dict(coordinate='proper spacelike Gaussian normal through true material wall',
            inherited_boundary_rho=float(rho[-1]),
            outgoing=dict(tau_s=0.0,rho_s=1/cb,tau_ss_right_time_model=float(tau_ss),rho_ss=float(rho_ss)),
            incoming=dict(tau_s=0.0,rho_s=-1/cb,tau_ss_right_time_model=float(tau_ss),rho_ss=float(rho_ss)),
            scope='initial seam jet only; right first-cell time reconstruction separate from inherited H. No finite collar extension evaluated.'),
        oriented_sectors='opposite normal orientations with both saved LR projectors; one common Spin4 x SM16 carrier, family I3 retained symbolically without multiplying density',
        not_evaluated=['current wall inclusion W_eta','T=<W e,p>_5','B_required=M4^-1 T','source and pairing derivatives of W/B','same-owner exterior shifted solve','stationary conormal N_out','native heat contact','physical a_mu/g_mu'])
