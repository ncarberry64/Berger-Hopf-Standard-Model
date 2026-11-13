"""Source-complete finite D5 field Poisson and moving-frame contacts.

The supplied coordinate traces and their independent literal left maps are
computational field tests. They neither select the normal mode nor replace
the action's retarded exterior trace/domain and its first variations.
"""
import numpy as np
from .muon_d5_fixed_radial_poisson import fixed_radial_field_poisson


def response_raw_slots(data, sector):
    """Unit shape and common-gamma coefficient keep distinct incidence.

    The area response archive retains b as a comparison test; its actual
    area channel has no second direct normal shape. Total coefficients
    have already been assembled upstream before any field projection.
    """
    if sector not in ('base','area'): raise ValueError('explicit base/area source incidence required')
    labels=[f'{name}_{half}' for name in ('direct','induced','total') for half in ('high','low')]
    arrays=[np.asarray(data[f'{name}_raw_{half}'],complex) for name in ('direct','induced','total') for half in ('high','low')]
    if any(a.ndim!=2 or a.shape!=(268,1) or not np.isfinite(a).all() for a in arrays):
        raise ValueError('all actual full raw268 high/low source constituents required')
    if sector=='area': arrays[:2]=[np.zeros_like(a) for a in arrays[:2]]
    return np.column_stack([a[:,0] for a in arrays]),labels


def fixed_field_source_and_frame(K, KE, source, source_energy, left, right,
                                left_first, right_first, green, green_first):
    """Consume coefficient sources before raw-wall/Spin projection.

    K already contains the fixed Dirac-bar Gamma0. Consequently its
    moving left coefficient map is Gamma0 S^-1 Gamma0, supplied by the
    caller, rather than appending a second Dirac-bar factor.
    """
    K, KE, S, SE, A, R, dA, dR, G, dG = map(
        lambda a: np.asarray(a, complex),
        (K, KE, source, source_energy, left, right, left_first, right_first,
         green, green_first))
    n = len(A); k = len(S)
    if (A.shape != (n, n) or R.shape != A.shape or G.shape != A.shape
            or dA.shape != (k, n, n) or dR.shape != dA.shape or dG.shape != dA.shape):
        raise ValueError('same complete raw wall/frame and every independent source jet required')
    p = fixed_radial_field_poisson(K, KE, S, SE, wall_dimension=n)
    C, CE = (p[q] for q in ('finite_raw_field_boundary_equation',
                             'finite_raw_field_boundary_equation_energy'))
    Cs, CEs = (p[q] for q in ('source_field_boundary_contact',
                               'complete_source_energy_return'))
    # Source-complete field images are separately retained for downstream
    # trace/domain contacts, even though their stationary terms cancel in
    # the boundary contraction L K P.
    ni = len(K)-n; Ai = K[:ni,:ni]
    P, L, PE, LE = (p[q] for q in ('original_raw_field_Poisson',
        'original_literal_left_field_Poisson','original_raw_field_Poisson_energy',
        'original_literal_left_field_Poisson_energy'))
    PS = np.array([np.r_[np.linalg.solve(Ai,-s[:ni]@P),np.zeros((n,n))] for s in S])
    LS = np.array([np.c_[np.linalg.solve(Ai.T,(-L@s[:,:ni]).T).T,np.zeros((n,n))] for s in S])
    PSE = np.array([np.r_[np.linalg.solve(Ai,-(se[:ni]@P+s[:ni]@PE+KE[:ni]@ps)),
        np.zeros((n,n))] for s,se,ps in zip(S,SE,PS)])
    LSE = np.array([np.c_[np.linalg.solve(Ai.T,(-(LE@s[:,:ni]+L@se[:,:ni]+ls@KE[:,:ni])).T).T,
        np.zeros((n,n))] for s,se,ls in zip(S,SE,LS)])
    right_rows=np.array([s@P+K@ps-np.r_[np.zeros((ni,n)),cs] for s,ps,cs in zip(S,PS,Cs)])
    left_rows=np.array([ls@K+L@s-np.c_[np.zeros((n,ni)),cs] for s,ls,cs in zip(S,LS,Cs)])
    right_E_rows=np.array([se@P+s@PE+KE@ps+K@pse-np.r_[np.zeros((ni,n)),ces]
        for s,se,ps,pse,ces in zip(S,SE,PS,PSE,CEs)])
    left_E_rows=np.array([lse@K+ls@KE+LE@s+L@se-np.c_[np.zeros((n,ni)),ces]
        for s,se,ls,lse,ces in zip(S,SE,LS,LSE,CEs)])
    def contacts(value, first):
        l = np.array([a @ value @ R for a in dA])
        c = np.array([A @ a @ R for a in first])
        r = np.array([A @ value @ a for a in dR])
        return l, c, r
    ls, cs, rs = contacts(C, Cs)
    le, ce, re = contacts(CE, CEs)
    lg, cg, rg = contacts(G, dG)
    return dict(p,
        original_raw_field_Poisson_source=PS,original_literal_left_field_Poisson_source=LS,
        original_raw_field_Poisson_source_energy=PSE,original_literal_left_field_Poisson_source_energy=LSE,
        original_right_source_field_rows=right_rows,original_left_source_field_rows=left_rows,
        original_right_source_energy_field_rows=right_E_rows,original_left_source_energy_field_rows=left_E_rows,
        adapted_finite_field_boundary_equation=A @ C @ R,
        adapted_finite_field_boundary_equation_energy=A @ CE @ R,
        adapted_source_left_frame=ls, adapted_source_field=cs,
        adapted_source_right_frame=rs, adapted_complete_source=ls + cs + rs,
        adapted_source_energy_left_frame=le, adapted_source_energy_field=ce,
        adapted_source_energy_right_frame=re,
        adapted_complete_source_energy=le + ce + re,
        adapted_material_wall_Green_return=A @ G @ R,
        adapted_Green_source_left_frame=lg, adapted_Green_source_field=cg,
        adapted_Green_source_right_frame=rg,
        adapted_complete_Green_source=lg + cg + rg,
        material_wall_return_sign='outward source return, not a retarded exterior selector',
        physical_normal_scalar_trace_and_domain_firsts_not_selected=True,
        fixed_raw_wall_value_map_E_first_zero_by_basis_definition=True,
        physical_boundary_energy_contacts_not_inferred_zero=True)
