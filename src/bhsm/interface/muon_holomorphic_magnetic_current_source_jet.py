"""Independent reference for the mixed magnetic current verification.

The supplied normal/area field jets, geometry and current jets are applied
before contraction. Time steps and the declared source pulse stay fixed.
Production uses muon_holomorphic_n1_magnetic_action; this independent
assembly is CONTROL_ONLY. No exterior pole, LSZ factor or moving physical
stop is selected here.
"""
from __future__ import annotations
import numpy as np
from scipy.linalg import expm, expm_frechet
from .muon_holomorphic_em_current import holomorphic_unit_em_moments
from .muon_holomorphic_n1_magnetic_action import magnetic_angular_trace
from .muon_native_dirac_hamiltonian import lepton_current_hilbert_representation


def mixed_higgs_current(h, dh, hb, dhb, lapse, lapse_first):
    """Differentiate the explicit B current, including the charge Hessian.

    h and hb are independent realified complex action coordinates. There
    is no conjugation of either source, and the last six charge fibers
    have an exact constant charge, hence zero Higgs derivative.
    """
    h, dh, hb, dhb = [np.asarray(a, complex) for a in (h, dh, hb, dhb)]
    N, dN = complex(lapse), np.asarray(lapse_first, complex)
    if (h.shape != (4,) or dh.ndim != 2 or dh.shape[0] != 4
            or hb.ndim != 2 or hb.shape[0] != 4
            or dhb.shape != (dh.shape[1], 4, hb.shape[1])
            or dN.shape != (dh.shape[1],) or N == 0):
        raise ValueError('same full Higgs and all background/B mixed directions required')
    k, ns = dh.shape[1], hb.shape[1]
    hp, hm = h[:2]+1j*h[2:], h[:2]-1j*h[2:]
    dp, dm = dh[:2]+1j*dh[2:], dh[:2]-1j*dh[2:]
    bp, bm = hb[:2]+1j*hb[2:], hb[:2]-1j*hb[2:]
    dbp, dbm = dhb[:, :2]+1j*dhb[:, 2:], dhb[:, :2]-1j*dhb[:, 2:]
    q, dq, qb = h@h, 2*h@dh, 2*h@hb
    if q == 0:
        raise ValueError('nonzero actual Higgs charge norm required')
    U = np.outer(hp, hm)
    Un = np.array([np.outer(a, hm)+np.outer(hp, b) for a,b in zip(dp.T,dm.T)])
    Ub = np.array([np.outer(a, hm)+np.outer(hp, b) for a,b in zip(bp.T,bm.T)])
    PB = Ub/q-U[None]*qb[:,None,None]/q**2
    PBn = np.empty((k,ns,2,2),complex)
    for a in range(k):
        qbn = 2*(dh[:,a]@hb+h@dhb[a])
        Ubn = np.array([np.outer(dbp[a,:,b],hm)+np.outer(bp[:,b],dm[:,a])
            +np.outer(dp[:,a],bm[:,b])+np.outer(hp,dbm[a,:,b]) for b in range(ns)])
        PBn[a] = (Ubn/q-Ub*dq[a]/q**2-Un[a][None]*qb[:,None,None]/q**2
            -U[None]*qbn[:,None,None]/q**2+2*U[None]*qb[:,None,None]*dq[a]/q**3)
    QB = np.zeros((ns,18,18),complex)
    dQB = np.zeros((k,ns,18,18),complex)
    QB[:,:12,:12] = -np.array([np.kron(p,np.eye(6)) for p in PB])
    for a in range(k):
        dQB[a,:,:12,:12] = -np.array([np.kron(p,np.eye(6)) for p in PBn[a]])
    J = -QB/N
    dJ = -dQB/N+QB[None]*dN[:,None,None,None]/N**2
    return dict(right=J,right_first=dJ,left=J.swapaxes(-1,-2),
        left_first=dJ.swapaxes(-1,-2),charge_B=QB,charge_B_first=dQB)


def mixed_magnetic_unsquared_current(bindings, coordinate_steps, response):
    """Apply all three B placements and their supplied background derivatives.

    This is the same n0+n1/full18 coordinate-current consumer as the value
    application. Both current legs, both Green responses, dN/dR, the
    canonical wall-vertex derivative, induced Higgs and its mixed charge
    contact are retained. Original84 wall/H maps are fixed representation
    maps. Physical domain/time/pulse variations are not assigned zero.
    """
    h = np.asarray(coordinate_steps,complex)
    if len(bindings) != 2 or h.shape != (2,):
        raise ValueError('same two actual stage bindings and oriented steps required')
    E = magnetic_angular_trace()['derivative_matrices']
    alpha = lepton_current_hilbert_representation()['alpha']
    angular = -1j*sum(np.kron(a,e) for a,e in zip(alpha,E))
    k = len(bindings[0]['stage']['Hcan_first'])
    d, ns = 90, 3
    stages = []
    for b in bindings:
        s = b['stage']; R, N = s['R4'].item(), s['induced_lapse'].item()
        dR, dN = s['R4_first'], s['induced_lapse_first']
        em = holomorphic_unit_em_moments(b['row']['H'],b['row_first']['H'].T,N,dN)
        body = np.zeros((d,d),complex); J = body.copy(); T = body.copy()
        db = np.zeros((k,d,d),complex); dJ=db.copy(); dT=db.copy()
        body[:18,:18] = s['Hcan']
        body[18:,18:] = np.kron(s['Hcan'],np.eye(4))+angular/R
        db[:,:18,:18] = s['Hcan_first']
        for a in range(k):
            db[a,18:,18:] = np.kron(s['Hcan_first'][a],np.eye(4))-angular*dR[a]/R**2
        for value, first, name in ((J,dJ,'literal_right'),(T,dT,'literal_left')):
            value[:18,:18]=em[name]; value[18:,18:]=np.kron(em[name],np.eye(4))
            first[:,:18,:18]=em[name+'_first']
            for a in range(k):first[a,18:,18:]=np.kron(em[name+'_first'][a],np.eye(4))
        stages.append(dict(B=-1j*N*body,dB=-1j*(dN[:,None,None]*body+N*db),
            F=1j*N*J,dF=1j*(dN[:,None,None]*J+N*dJ),
            T=1j*N*T,dT=1j*(dN[:,None,None]*T+N*dT),N=N,dN=dN,
            H=b['row']['H'],dH=b['row_first']['H'].T,
            vertices=s['canonical_wall_current_vertices'],
            vertices_first=s['canonical_wall_current_vertices_first']))

    def segment(j, dt):
        s=stages[j]; A=np.zeros((2*d,2*d),complex)
        A[:d,:d]=s['B'];A[:d,d:]=np.eye(d)
        Z=expm(dt*A);U,M=Z[:d,:d],Z[:d,d:]
        dZ=[]
        for a in range(k):
            dA=np.zeros_like(A);dA[:d,:d]=s['dB'][a]
            dZ.append(expm_frechet(dt*A,dt*dA,compute_expm=False))
        dZ=np.array(dZ);dU,dM=dZ[:,:d,:d],dZ[:,:d,d:]
        return dict(U=U,r=M@s['F'],l=s['T']@M,dU=dU,
            dr=dM@s['F']+M@s['dF'],dl=s['dT']@M+s['T']@dM)

    full=[segment(j,dt) for j,dt in enumerate(h)]
    names=('operator_insertion','right_current_motion','literal_left_motion')
    values={n:np.zeros((ns,d,d),complex) for n in names}
    first={n:np.zeros((k,ns,d,d),complex) for n in names}
    for point in response['point_sources']:
        j=point['cell'];local=2*point['sigma']-j;s=stages[j]
        if np.asarray(point['total_field_first']).shape != (k,336,ns):
            raise ValueError('actual same-domain mixed field source must be supplied')
        a=segment(j,local*h[j]);u,du=a['r'],a['dr']
        if j:
            du=du+a['dU']@full[0]['r']+a['U']@full[0]['dr']
            u=u+a['U']@full[0]['r']
        a=segment(j,(1-local)*h[j]);p,dp=a['l'],a['dl']
        if j==0:
            dp=dp+full[1]['dl']@a['U']+full[1]['l']@a['dU']
            p=p+full[1]['l']@a['U']
        W=np.r_[bindings[j]['lifts']['W'],bindings[j]['lifts']['hv']]
        wall=np.einsum('ca,ahb->chb',W,point['total_field'].reshape(84,4,ns))
        dwall=np.einsum('ca,kahb->kchb',W,point['total_field_first'].reshape(k,84,4,ns))
        Xi=np.einsum('chb,cij->bhij',wall,s['vertices'])
        dXi=np.einsum('kchb,cij->kbhij',dwall,s['vertices'])
        dXi+=np.einsum('chb,kcij->kbhij',wall,s['vertices_first'])
        emB=mixed_higgs_current(s['H'],s['dH'],wall[20:].reshape(4,12),
            dwall[:,20:].reshape(k,4,12),s['N'],s['dN'])
        Jb=emB['right'].reshape(4,ns,18,18).transpose(1,0,2,3)
        Tb=emB['left'].reshape(4,ns,18,18).transpose(1,0,2,3)
        dJb=emB['right_first'].reshape(k,4,ns,18,18).transpose(0,2,1,3,4)
        dTb=emB['left_first'].reshape(k,4,ns,18,18).transpose(0,2,1,3,4)
        def assemble(a,da):
            out=np.zeros((ns,d,d),complex);dout=np.zeros((k,ns,d,d),complex)
            for axis in range(ns):
                out[axis,18:,:18]=a[axis].transpose(1,0,2).reshape(72,18)
                out[axis,:18,18:]=a[axis].transpose(1,2,0).reshape(18,72)
                for c in range(k):
                    dout[c,axis,18:,:18]=da[c,axis].transpose(1,0,2).reshape(72,18)
                    dout[c,axis,:18,18:]=da[c,axis].transpose(1,2,0).reshape(18,72)
            return out,dout
        X,dX=assemble(Xi,dXi);JB,dJB=assemble(Jb,dJb);TB,dTB=assemble(Tb,dTb)
        G=-1j*s['N']*X;dG=-1j*(s['dN'][:,None,None,None]*X+s['N']*dX)
        F=1j*s['N']*JB;dF=1j*(s['dN'][:,None,None,None]*JB+s['N']*dJB)
        T=1j*s['N']*TB;dT=1j*(s['dN'][:,None,None,None]*TB+s['N']*dTB)
        weight=1j*point['scale']
        values['operator_insertion']+=weight*(p@G@u)
        values['right_current_motion']+=weight*(p@F)
        values['literal_left_motion']+=weight*(T@u)
        for c in range(k):
            first['operator_insertion'][c]+=weight*(dp[c]@G@u+p@dG[c]@u+p@G@du[c])
            first['right_current_motion'][c]+=weight*(dp[c]@F+p@dF[c])
            first['literal_left_motion'][c]+=weight*(dT[c]@u+T@du[c])
    return dict(**values,**{n+'_first':v for n,v in first.items()},
        total=sum(values.values()),total_first=sum(first.values()),
        all_operator_and_both_current_and_Green_source_contacts=True,
        actual_mixed_Higgs_charge_contact=True,analytic_dual_conjugated=False,
        fixed_computational_steps_and_pulse=True,
        physical_stop_domain_pole_or_Pauli_selected=False)
