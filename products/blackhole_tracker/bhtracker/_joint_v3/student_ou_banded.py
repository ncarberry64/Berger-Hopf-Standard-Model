"""Synthetic numerical version of the unchanged Student innovation law.

Same normalized density and analytical adjoints as student_ou.py. Banded
compiled Cholesky/triangular solves replace Python scalar recurrences. No
authentic input, physical model, optimizer, adopted noise or acceptance API.
"""
from pathlib import Path
import hashlib,math
import numpy as np
from scipy.linalg import cholesky_banded,solve_banded
from scipy.special import betaln
from . import student_ou as student_provider
from .student_ou import _vector,_scalar,_student_terms

ROOT=Path(__file__).resolve().parent
PIN='1ad508ad93f6ea1aec706e25c0fcbcb9aabd32ada77bac732fd7843c2f917834'

def _pin():
    if (Path(student_provider.__file__).resolve()!=ROOT/'student_ou.py'
        or any(function is not getattr(student_provider,name) for name,function in (('_vector',_vector),('_scalar',_scalar),('_student_terms',_student_terms)))
        or hashlib.sha256((ROOT/'student_ou.py').read_bytes()).hexdigest()!=PIN):
        raise ValueError('Reviewed Student-law provider differs')

def student_ou_banded_deviance_score(times,residual,scale,fraction,tau_days,nu,*,row_ids=None):
    """Exact same chronological Student law/score, O(N) banded algorithms.

    Reverse Cholesky: with l diagonal, q subdiagonal, base adjoints
    h_l=2/l-g_w*z, h_q=-g_w[1:]*z[:-1], let a be adjoint of T's diagonal.
    Then a_i-(q_i/l_i)^2*a_(i+1)
      =(h_l_i-q_i*h_q_i/l_i)/(2*l_i).
    The last RHS is h_l_last/(2*l_last). A single upper-bidiagonal solve
    gives all a; the offdiagonal adjoint is (h_q-2*q*a[1:])/l[:-1].
    This is algebraic elimination of the original reverse scalar recurrence.
    """
    _pin()
    t,r,s=[_vector(value,name) for value,name in ((times,'times'),(residual,'residual'),(scale,'scale'))]
    f,tau,nu=[_scalar(value,name) for value,name in ((fraction,'fraction'),(tau_days,'tau_days'),(nu,'nu'))]
    n=len(t)
    if r.shape!=t.shape or s.shape!=t.shape or np.any(s<=0) or np.any(np.diff(t)<0):
        raise ValueError('Matched chronological vectors and positive scales required')
    if not 0<=f<1 or tau<=0 or nu<=2:raise ValueError('Require0<=f<1,tau>0,nu>2')
    if row_ids is not None:
        row_ids=list(row_ids)
        if len(row_ids)!=n or any(not isinstance(v,str) or not v for v in row_ids) or len(set(row_ids))!=n:
            raise ValueError('Matched unique stable row identities required')
    delta=np.diff(t)
    if not np.isfinite(delta).all():raise ValueError('Finite adjacent time differences required')
    rho=np.exp(-delta/tau);u=r/s
    if not np.isfinite(u).all():raise FloatingPointError('Unrepresentable residual/scale')
    constant=float(n*(math.log(nu-2.)+2*betaln(nu/2.,.5)))
    if f==0 or n==1:
        z=u.copy();penalty,psi=_student_terms(z,nu)
        B=np.zeros((2,n));B[0]=1.;B[1,:-1]=-rho
        rhs=np.r_[0.,rho*u[:-1]]
        history=np.zeros(1) if n==1 else solve_banded((1,0),B,rhs,check_finite=False)
        gf=-float(psi@history);gu=psi;log_tau=0.;diagonal=np.ones(n)
        logdet=float(2*np.log(s).sum());method='EXACT_SINGLETON' if n==1 else 'EXACT_FRACTION_ZERO_BANDED_ONE_SIDED_LIMIT'
    else:
        T=np.zeros((2,n));T[0]=1.;T[0,1:]+=(1.-2*f)*rho*rho;T[1,:-1]=-(1.-f)*rho
        try:L=cholesky_banded(T,lower=True,check_finite=False)
        except np.linalg.LinAlgError as error:raise FloatingPointError('Unresolved nonpositive Cholesky pivot; no floor substituted') from error
        diagonal=L[0];q=L[1,:-1]
        w=np.r_[u[0],u[1:]-rho*u[:-1]]
        z=solve_banded((1,0),L,w,check_finite=False)
        if not np.isfinite(z).all():raise FloatingPointError('Unrepresentable innovations')
        penalty,psi=_student_terms(z,nu)
        transpose=np.zeros((2,n));transpose[1]=diagonal;transpose[0,1:]=q
        gw=solve_banded((0,1),transpose,psi,check_finite=False)
        gl=2./diagonal-gw*z;gq=-gw[1:]*z[:-1]
        rhs=gl/(2*diagonal);rhs[:-1]-=q*gq/(2*diagonal[:-1]**2)
        U=np.zeros((2,n));U[1]=1.;U[0,1:]=-(q/diagonal[:-1])**2
        ga=solve_banded((0,1),U,rhs,check_finite=False)
        gc=(gq-2*q*ga[1:])/diagonal[:-1]
        gu=gw.copy();gu[:-1]-=rho*gw[1:]
        grho=-u[:-1]*gw[1:]+2*(1.-2*f)*rho*ga[1:]-(1.-f)*gc
        gf=float(np.sum(-2*rho*rho*ga[1:]+rho*gc))
        log_tau=float(np.sum(grho*rho*delta/tau))
        logdet=float(2*np.log(diagonal).sum()+2*np.log(s).sum());method='BANDED_CHOLESKY_WHITENING_AND_ELIMINATED_REVERSE_ADJOINT'
    gr=gu/s;gls=2.-gu*u;innovation=float(penalty.sum());deviance=innovation+logdet+constant
    if not np.isfinite([deviance,gf,log_tau,constant]).all() or not np.isfinite(gr).all() or not np.isfinite(gls).all():
        raise FloatingPointError('Unrepresentable normalized density or analytical score')
    _pin()
    return {'schema':'bhsm.synthetic_student_ou_banded_score.v1','negative_two_log_density':deviance,
        'innovation_deviance':innovation,'log_determinant':logdet,'normalizing_deviance_constant':constant,
        'whitened_innovations':z,'innovation_score':psi,'residual_score':gr,'log_scale_score':gls,
        'fraction_score':gf,'log_tau_score':log_tau,'fixed_nu':nu,'nu_score':None,'method':method,
        'row_ids_in_generative_order':row_ids,'provider_source_sha256':PIN,
        'ordering_contract':'Unchanged chronological stable input order; ties scientifically material. No sorting.',
        'scope':'Synthetic numerical prototype only; unchanged Student law, no physical fitting, calibration or adoption.'}
