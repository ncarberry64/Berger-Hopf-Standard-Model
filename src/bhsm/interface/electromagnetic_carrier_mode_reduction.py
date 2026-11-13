"""Round-S3 Maxwell seed and nonlinear pullback controls, not a muon solve.

The four ambient forms are expressed below in the owned RIGHT Maurer frame.
Its orientation reverses the supplied Hopf-chart curl signs. Unit control
normalization must not replace the actual action's kinetic pairing.
"""
from __future__ import annotations

import numpy as np
import sympy as sp

SOURCE_SHA256 = "f76c648ffc716deb88146c59af4892adafd4bddd9dfb99a63e18cecebecffcbd"


def s3_mode_generators():
    """Ambient skew generators, in supplied order (two right, two left)."""
    return np.array([
        [[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]],
        [[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]],
        [[0,-1,0,0],[1,0,0,0],[0,0,0,1],[0,0,-1,0]],
        [[0,0,-1,0],[0,0,0,-1],[1,0,0,0],[0,1,0,0]],
    ], dtype=float)


def right_frame_s3_modes(quaternions):
    """Values, E_j values, E_k E_j values of four forms in right frame.

    E_i(q)=L_i q, [E_i,E_j]=-2 epsilon_ijk E_k. The owned SU(2)
    axes are (-generic3,-generic2,-generic1). Values are
    (point,mode,component); derivatives insert (j) or (k,j) after point.
    Inputs are actual unit quaternions; this function does not renormalize them.
    """
    raw=np.asarray(quaternions)
    if np.iscomplexobj(raw) and np.any(raw.imag):
        raise ValueError('real unit quaternions required')
    q=np.asarray(raw.real,dtype=float)
    if q.ndim!=2 or q.shape[1]!=4 or not np.all(np.isfinite(q)):
        raise ValueError('finite (point,4) unit quaternions required')
    if not np.allclose(np.sum(q*q,axis=1),1,rtol=0,atol=2e-13):
        raise ValueError('points must be on the unit sphere')
    m=s3_mode_generators()
    generic=np.concatenate((m[:2],np.array([[[0,0,0,-1],[0,0,-1,0],[0,1,0,0],[1,0,0,0]]])),axis=0)
    l=-generic[[2,1,0]]
    c=np.einsum('aij,kil->akjl',m,l)
    dc=np.stack([np.einsum('ij,akjl->akil',lj.T,c)+np.einsum('akij,jl->akil',c,lj) for lj in l])
    ddc=np.stack([np.einsum('ij,dakjl->dakil',lk.T,dc)+np.einsum('dakij,jl->dakil',dc,lk) for lk in l])
    return (np.einsum('pi,akij,pj->pak',q,c,q),
            np.einsum('pi,dakij,pj->pdak',q,dc,q),
            np.einsum('pi,edakij,pj->pedak',q,ddc,q))


def carrier_map_jet(sigma,theta,*,b,r):
    """Complete two-jet and Euclidean split of the restricted CONTROL map."""
    if not np.all(np.isfinite([sigma,theta,b,r])) or b<=0 or r<=0:
        raise ValueError('finite coordinates and positive b,r required')
    c,s=np.cos(theta),np.sin(theta)
    q=np.sqrt(b)*np.array([sigma*c,sigma*s,r*c,r*s])
    j=np.sqrt(b)*np.array([[c,-sigma*s],[s,sigma*c],[0,-r*s],[0,r*c]])
    d2=np.zeros((4,2,2))
    d2[:,0,1]=d2[:,1,0]=np.sqrt(b)*np.array([-s,c,0,0])
    d2[:,1,1]=-q
    den=sigma*sigma+r*r
    n=np.column_stack(([0,0,c,s],np.array([-r*s,r*c,sigma*s,-sigma*c])/np.sqrt(den)))
    gram=np.diag([b,b*den])
    pt=j@np.linalg.solve(gram,j.T)
    return {'Q':q,'DR':j,'D2R':d2,'gram':gram,'normal_basis':n,
            'tangent_projector':pt,'normal_projector':n@n.T,
            'gaussian_curvature':-r*r/(b*den*den)}


def nonlinear_action_pullback(gradient,hessian,dr,d2r):
    """Analytic dual (transpose), including the off-shell second-map term.

    Complex left leaves are not Hermitian adjoints. All moving field contacts
    must already be present in DR/D2R and the original action derivatives.
    """
    g,h,j,d2=map(np.asarray,(gradient,hessian,dr,d2r))
    if g.ndim!=1 or h.ndim!=2 or j.ndim!=2 or d2.ndim!=3 or not all(np.all(np.isfinite(a)) for a in (g,h,j,d2)):
        raise ValueError('finite gradient vector, Hessian, DR and D2R required')
    if h.shape!=(g.size,g.size) or j.shape[0]!=g.size or d2.shape!=(g.size,j.shape[1],j.shape[1]):
        raise ValueError('incompatible complete map jets')
    naive=j.T@h@j
    contact=np.einsum('a,aij->ij',g,d2)
    return {'gradient':j.T@g,'hessian':naive+contact,'naive':naive,'second_map_contact':contact}


def round_mode_residual(sigma,theta,sigma_dot,theta_dot,sigma_ddot,theta_ddot,*,b,r,omega):
    """Original four Maxwell rows, not merely projected scalar equations."""
    jet=carrier_map_jet(sigma,theta,b=b,r=r)
    v=np.array([sigma_dot,theta_dot])
    residual=jet['DR']@np.array([sigma_ddot,theta_ddot])+np.einsum('aij,i,j->a',jet['D2R'],v,v)+omega**2*jet['Q']
    return {'original':residual,'tangent_covector':jet['DR'].T@residual,
            'normal':jet['normal_basis'].T@residual}


def released_amplitude_phase_map(sigma,theta,amplitude,relative_phase,*,b):
    """Four original amplitudes; Cartesian fields remain valid at polar zeros."""
    if not np.all(np.isfinite([sigma,theta,amplitude,relative_phase,b])) or b<=0:
        raise ValueError('finite coordinates and positive b required')
    return np.sqrt(b)*np.array([sigma*np.cos(theta),sigma*np.sin(theta),
        amplitude*np.cos(theta+relative_phase),amplitude*np.sin(theta+relative_phase)])


def simp(x):
    return sp.simplify(sp.trigsimp(x))

def assert_zero(x, name: str) -> None:
    entries = list(x) if isinstance(x, sp.MatrixBase) else [x]
    for e in entries:
        if simp(e) != 0:
            raise AssertionError(f"{name}: nonzero expression {simp(e)}")

def exact_checks() -> dict:
    groups: dict[str, object] = {}
    eta, al, be = sp.symbols("eta alpha beta", real=True)
    se, ce = sp.sin(eta), sp.cos(eta)
    # Global forms alpha=(M x).dx restricted to the unit sphere.
    matrices = [
        sp.Matrix([[0,-1,0,0],[1,0,0,0],[0,0,0,-1],[0,0,1,0]]),
        sp.Matrix([[0,0,-1,0],[0,0,0,1],[1,0,0,0],[0,-1,0,0]]),
        sp.Matrix([[0,-1,0,0],[1,0,0,0],[0,0,0,1],[0,0,-1,0]]),
        sp.Matrix([[0,0,-1,0],[0,0,0,-1],[1,0,0,0],[0,1,0,0]]),
    ]
    xx = sp.Matrix([ce*sp.cos(al), ce*sp.sin(al), se*sp.cos(be), se*sp.sin(be)])
    forms = [
        sp.Matrix([0,ce**2,se**2]),
        sp.Matrix([sp.cos(al+be),se*ce*sp.sin(al+be),-se*ce*sp.sin(al+be)]),
        sp.Matrix([0,ce**2,-se**2]),
        sp.Matrix([sp.cos(al-be),se*ce*sp.sin(al-be),se*ce*sp.sin(al-be)]),
    ]
    ys=[eta,al,be]
    embedding_jac=xx.jacobian(ys)
    metric=sp.diag(1,ce**2,se**2)
    invmetric=sp.diag(1,ce**-2,se**-2)
    vol=se*ce
    for m,a in zip(matrices,forms):
        assert_zero(m+m.T,"ambient skew generator")
        assert_zero(m.T*m-sp.eye(4),"pointwise unit form generator")
        assert_zero(embedding_jac.T*m*xx-a,"global-to-chart form")
        assert_zero((a.T*invmetric*a)[0]-1,"pointwise norm")
    groups["global_smooth_s3_forms"]={"passed":True,"number_of_forms":4}
    gram=sp.Matrix(4,4,lambda i,j:sp.trace(matrices[i].T*matrices[j])/4)
    assert_zero(gram-sp.eye(4),"Haar Gram")
    groups["exact_volume_gram"]={"passed":True,"unit_sphere_unnormalized_gram":"2*pi^2 I4",
        "radius_R_normalization":"alpha/sqrt(2*pi^2*R), for unit Maxwell kinetic coefficient"}
    curls=[]
    for i,a in enumerate(forms):
        raw=sp.Matrix([sp.diff(a[2],al)-sp.diff(a[1],be),
                       sp.diff(a[0],be)-sp.diff(a[2],eta),
                       sp.diff(a[1],eta)-sp.diff(a[0],al)])
        cc=metric*raw/vol
        eig=-2 if i<2 else 2
        assert_zero(cc-eig*a,"curl eigensection")
        div=sum(sp.diff(vol*(invmetric*a)[j],ys[j]) for j in range(3))/vol
        assert_zero(div,"co-closed form")
        curls.append(eig)
    groups["transversality_and_curl"]={"passed":True,"unit_radius_curl_eigenvalues":curls,
        "positive_square_eigenvalue":"4/R^2","mode_has_nonzero_field_strength":True}

    sig,th=sp.symbols("sigma theta",real=True)
    b,r,kappa,zc,gg,Om=sp.symbols("b r kappa Zchi g Omega",positive=True)
    sigd,thd,sigdd,thdd=sp.symbols("sigma_dot theta_dot sigma_ddot theta_ddot",real=True)
    ct,st=sp.cos(th),sp.sin(th)
    d=sig**2+r**2
    q=sp.sqrt(b)*sp.Matrix([sig*ct,sig*st,r*ct,r*st])
    Jac=q.jacobian([sig,th])
    G=sp.diag(b,b*d)
    assert_zero(Jac.T*Jac-G,"collective-coordinate Gram")
    assert_zero((b*d*kappa**2).subs({r:1/sp.sqrt(gg),kappa:sp.sqrt(zc*gg/b)})-zc*(1+gg*sig**2),"BHSM kinetic target")
    groups["retained_scalar_kinetic_match"]={"passed":True,"coordinates":["sigma","theta"],
        "theta":"sqrt(Zchi*g/b)*chi","r":"1/sqrt(g)","pullback_metric":"diag(b, Zchi*(1+g*sigma^2)) in (sigma,chi)",
        "scope":"homogeneous kinetic matrix; full local spacetime action reduction not established"}
    assert_zero(q[2]**2+q[3]**2-b*r**2,"fixed reference radius")
    assert_zero(q[0]*q[3]-q[1]*q[2],"phase locking")
    groups["nonlinear_constraints_identified"]={"passed":True,
        "constraints":["q3^2+q4^2=b*r^2","q1*q4-q2*q3=0"],"imposed_by_source_free_Maxwell":False}
    n1=sp.Matrix([0,0,ct,st])
    n2=sp.Matrix([-r*st,r*ct,sig*st,-sig*ct])/sp.sqrt(d)
    N=sp.Matrix.hstack(n1,n2)
    assert_zero(N.T*N-sp.eye(2),"normal Gram")
    assert_zero(N.T*Jac,"normal/tangent separation")
    PT=Jac*G.inv()*Jac.T
    assert_zero(PT+N*N.T-sp.eye(4),"complete tangent/normal split")
    qss=q.diff(sig,2); qst=q.diff(sig).diff(th); qtt=q.diff(th,2)
    gauss=sum((ni.dot(qss)*ni.dot(qtt)-ni.dot(qst)**2) for ni in [n1,n2])/G.det()
    assert_zero(gauss+r**2/(b*d**2),"Gauss curvature")
    assert_zero(gauss.subs(r,1/sp.sqrt(gg))+gg/(b*(1+gg*sig**2)**2),"retained field curvature")
    groups["tangent_normal_projectors_and_curvature"]={"passed":True,"gaussian_curvature":"-g/(b*(1+g*sigma^2)^2)"}

    U=simp(Om**2*q.dot(q)/2)
    assert_zero(U-b*Om**2*(sig**2+r**2)/2,"quadratic Maxwell potential")
    a0,g0=sp.symbols("A0 G0",real=True)
    needed=(a0-b*Om**2)*sig**2/2+g0*sig**4/4
    assert_zero((U+needed-b*Om**2*r**2/2)-(a0*sig**2/2+g0*sig**4/4),"potential difference")
    groups["potential_comparison"]={"passed":True,"Maxwell_potential":"b*Omega^2*(sigma^2+r^2)/2",
        "missing_field_dependent_potential":"(A0-b*Omega^2)*sigma^2/2+G0*sigma^4/4",
        "G0_generated_by_fixed_round_linear_Maxwell":False}

    qacc=Jac*sp.Matrix([sigdd,thdd])+qss*sigd**2+2*qst*sigd*thd+qtt*thd**2
    R=qacc+Om**2*q
    Ered=sp.Matrix([b*(sigdd+sig*(Om**2-thd**2)), b*(d*thdd+2*sig*sigd*thd)])
    assert_zero(Jac.T*R-Ered,"original-to-reduced equations")
    normal=sp.Matrix([sp.sqrt(b)*r*(Om**2-thd**2),2*sp.sqrt(b)*r*sigd*thd/sp.sqrt(d)])
    assert_zero(N.T*R-normal,"normal reaction")
    on=R.subs({sigdd:-sig*(Om**2-thd**2),thdd:-2*sig*sigd*thd/d})
    assert_zero(on-N*normal,"full residual after tangent solution")
    qvel=Jac*sp.Matrix([sigd,thd])
    assert_zero(qvel.dot(on),"conserved energy despite unsolved normal rows")
    assert_zero(R.subs({sigd:0,sigdd:0,thd:Om,thdd:0}),"exact positive rotation")
    assert_zero(R.subs({sigd:0,sigdd:0,thd:-Om,thdd:0}),"exact negative rotation")
    sample={b:1,r:1,Om:1,sig:1,th:0,sigd:sp.Rational(1,3),thd:sp.Rational(1,2)}
    normal_sq=simp(normal.dot(normal))
    sample_sq=simp(normal_sq.subs(sample))
    assert_zero(sample_sq-sp.Rational(89,144),"counterexample residual squared")
    assert_zero((Jac.T*on).subs(sample),"counterexample reduced rows")
    groups["full_equation_admission_not_just_reduced_rows"]={"passed":True,
        "normal_loads":["sqrt(b)*r*(Omega^2-theta_dot^2)","2*sqrt(b)*r*sigma_dot*theta_dot/sqrt(sigma^2+r^2)"],
        "exact_source_free_locked_orbits":"sigma_dot=0, theta_dot=+/-Omega",
        "diagnostic_reduced_rows":"zero exactly","diagnostic_energy_derivative":"zero exactly",
        "diagnostic_full_norm_squared":"89/144",
        "diagnostic_full_norm":float(sp.sqrt(sample_sq)),"BHSM_physical_residual":None}

    # A second-map term cancels fictitious phase stiffness at an off-shell static state.
    HU=sp.hessian(U,[sig,th])
    naive=Jac.T*(Om**2*sp.eye(4))*Jac
    eq=Om**2*q
    contact=sp.Matrix(2,2,lambda i,j:eq.dot(q.diff([sig,th][i]).diff([sig,th][j])))
    assert_zero(HU-naive-contact,"nonlinear field-map Hessian")
    assert_zero(HU[1,1],"true phase stiffness")
    assert_zero(naive[1,1]-b*Om**2*d,"spurious stiffness")
    assert_zero(contact[1,1]+b*Om**2*d,"second-map cancellation")
    groups["offshell_second_map_contact"]={"passed":True,"naive_theta_theta":"b*Omega^2*(sigma^2+r^2)",
        "second_map_theta_theta":"-b*Omega^2*(sigma^2+r^2)","original_theta_theta":0,
        "explains_saved_muon_discrepancy":False}

    # Homogeneous 4D FLRW Maxwell supplies a scale-invariance diagnostic, not a chosen geometry.
    aa=sp.symbols("scale_factor",positive=True)
    # sqrt(-g)~a^d; each of two inverse metrics contributes a^-2.
    assert_zero(aa**4*aa**-4-1,"4D conformal cancellation")
    assert_zero(aa**8*aa**-4-aa**4,"8D conformal weight")
    groups["dimension_specific_conformal_weight"]={"passed":True,"4D_Maxwell_weight":"a^0","8D_Maxwell_weight":"a^4",
        "scale_selected":False}
    return {"groups":groups,"group_count":len(groups),"all_passed":True}

def numerical_checks() -> dict:
    out: dict[str,object]={}
    # Independent central differences for the two normal loads, in dimensionless CONTROL units.
    x=np.array([0.8,0.3,0.6]) # sigma, sigma_dot, theta_dot
    b=1.4; r=0.9; om=1.3
    def f(v):
        s,sv,w=v
        return np.array([np.sqrt(b)*r*(om*om-w*w),2*np.sqrt(b)*r*sv*w/np.sqrt(s*s+r*r)])
    s,sv,w=x; den=s*s+r*r
    analytic=np.array([[0,0,-2*np.sqrt(b)*r*w],
        [-2*np.sqrt(b)*r*sv*w*s/den**1.5,2*np.sqrt(b)*r*w/np.sqrt(den),2*np.sqrt(b)*r*sv/np.sqrt(den)]])
    table=[]
    for h in [0.02,0.01,0.005,0.0025]:
        fd=np.column_stack([(f(x+h*np.eye(3)[j])-f(x-h*np.eye(3)[j]))/(2*h) for j in range(3)])
        table.append({"h":h,"max_absolute_error":float(np.max(np.abs(fd-analytic)))})
    ratios=[table[i]["max_absolute_error"]/table[i+1]["max_absolute_error"] for i in range(3)]
    assert all(3.8<rr<4.2 for rr in ratios)
    out["normal_source_derivative"]={"passed":True,"table":table,"error_ratios":ratios,
        "scope":"independent finite-difference control, not the physical outgoing derivative"}

    modes=4; om=2.0; t=0.37
    I=np.eye(modes); Z=np.zeros((modes,modes))
    J=np.block([[Z,I],[-I,Z]])
    S=np.block([[np.cos(om*t)*I,np.sin(om*t)*I/om],[-om*np.sin(om*t)*I,np.cos(om*t)*I]])
    H=np.diag(np.r_[np.full(modes,om**2),np.ones(modes)])
    V0=np.diag(np.r_[np.full(modes,1/(2*om)),np.full(modes,om/2)])
    V3=7*V0
    symerr=float(np.linalg.norm(S@J@S.T-J,ord=2))
    assert symerr<1e-13
    states=[]
    for n,V in [(0,V0),(3,V3)]:
        mineig=float(np.min(np.linalg.eigvalsh(V+0.5j*J)))
        assert mineig>-1e-12
        energy=float(np.trace(H@V)/2)
        stationarity=float(np.linalg.norm(S@V@S.T-V,ord=2))
        assert stationarity<1e-12
        states.append({"occupation_control_n":n,"minimum_uncertainty_eigenvalue":mineig,
                       "energy_control_units":energy,"stationarity_residual":stationarity})
    out["bosonic_reference_controls"]={"passed":True,"hbar":1,"symplectic_residual":symerr,
        "states":states,"same_retarded_evolution":True,"covariances_equal":False,
        "primordial_reference_selected":False}

    # Energy domination works for all states with the finite moments, not just Gaussian states.
    K=np.diag(np.array([1,-0.5,0.2,1.4,-0.3,0.7,0.1,-0.8]))
    K[0,5]=K[5,0]=0.25; K[2,7]=K[7,2]=-0.15
    Hinvsqrt=np.diag(1/np.sqrt(np.diag(H)))
    kk=float(np.max(np.abs(np.linalg.eigvalsh(Hinvsqrt@K@Hinvsqrt))))
    psd_min=min(float(np.min(np.linalg.eigvalsh(kk*H-K))),float(np.min(np.linalg.eigvalsh(kk*H+K))))
    assert psd_min>-1e-12
    rows=[]
    for V in [V0,V3]:
        energy=float(np.trace(H@V)/2)
        obs=float(np.trace(K@V)/2)
        assert abs(obs)<=kk*energy+1e-12
        rows.append({"quadratic_observable":obs,"energy":energy,"dominating_bound":kk*energy})
    out["quadratic_bosonic_energy_bound"]={"passed":True,"kappa":kk,"minimum_matrix_order_eigenvalue":psd_min,
        "checks":rows,"physical_energy_budget":None,"muon_error_bound":None}
    return {"groups":out,"group_count":len(out),"all_passed":True}
