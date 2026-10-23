"""Direct analytic geometry/source first of the original unsquared D5."""
import numpy as np


def d5_coefficient_source(c,*,gamma,generators,eta,eta_first,energy,sheet_orientation,source_slot=0):
    """Apply source coefficient firsts before any mode or trace projection.

    These are full Spin4/SM16 coefficient matrices on n0. The caller must
    separately supply its trial/state/domain firsts; they are not inferred
    zero by this direct coefficient derivative.
    """
    G,T=np.asarray(gamma,complex),np.asarray(generators,complex);E=complex(energy);eps=int(sheet_orientation);k=int(source_slot)
    if G.shape!=(5,4,4)or T.shape!=(4,16,16)or eps not in(-1,1):raise ValueError('original full five Clifford and carrier representation required')
    q=len(c['lapse']);g=np.array([np.kron(a,np.eye(16))for a in G]);t=np.array([np.kron(np.eye(4),a)for a in T])
    Eta,dEta=np.asarray(eta,complex),np.asarray(eta_first,complex)
    if Eta.shape!=(q,64,64)or dEta.shape!=Eta.shape:raise ValueError('actual independently differentiated normal eta contacts required')
    spin=np.kron(-1.5j*G[1]@G[2]@G[3],np.eye(16));value=[];first=[];time=[];time_first=[];radial=[];radial_first=[]
    for i in range(q):
        N,C,R,z,h0,h4,clock=(c[n][i]for n in('lapse','radial_coframe','radius','coordinate_shift','geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate'))
        dN,dC,dR,dz,dh0,dh4,dclock=(c[n+'_first'][k,i]for n in('lapse','radial_coframe','radius','coordinate_shift','geometric_time_contact','geometric_radial_contact','surface_proper_clock_rate'))
        A=np.einsum('fc,cij->fij',c['gauge_connection_material'][i],t);dA=np.einsum('fc,cij->fij',c['gauge_connection_material_first'][k,i],t)
        temporal=A[0]-z*A[1];dtemporal=dA[0]-dz*A[1]-z*dA[1]
        D=1j*g[0]*h0+1j*eps*g[4]*h4+Eta[i]+spin/R+g[0]*E*clock/N
        dD=1j*g[0]*dh0+1j*eps*g[4]*dh4+dEta[i]-spin*dR/R**2+g[0]*E*(dclock/N-clock*dN/N**2)
        D+=1j*g[0]@temporal/N+1j*eps*g[4]@A[1]/C+sum(1j*g[a+1]@A[a+2]/R for a in range(3))
        dD+=1j*g[0]@(dtemporal/N-temporal*dN/N**2)+1j*eps*g[4]@(dA[1]/C-A[1]*dC/C**2)
        dD+=sum(1j*g[a+1]@(dA[a+2]/R-A[a+2]*dR/R**2)for a in range(3))
        value.append(D);first.append(dD);time.append(1j*g[0]/N);time_first.append(-1j*g[0]*dN/N**2)
        radial.append(-1j*g[0]*z/N+1j*eps*g[4]/C)
        radial_first.append(-1j*g[0]*(dz/N-z*dN/N**2)-1j*eps*g[4]*dC/C**2)
    return dict(original_D5_zero_order=np.array(value),direct_source_D5_zero_order=np.array(first),
        original_D5_time_principal=np.array(time),direct_source_D5_time_principal=np.array(time_first),
        original_D5_radial_principal=np.array(radial),direct_source_D5_radial_principal=np.array(radial_first),
        intrinsic_Higgs_mass_only_at_seam=True,trial_state_domain_and_normal_inclusion_firsts_not_inferred_zero=True)
