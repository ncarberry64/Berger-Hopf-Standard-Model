"""Independent quadrature of the public alphaQEDc26 standard-ee spectrum.

Only the five-flavor two-current contribution is provided. No anomalous
moment is used as an input. Covariance follows alphaQED26 printed p17.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
from numpy.polynomial.legendre import leggauss

ALPHA_REF_INV = 137.0359991657  # intRdatx.f frozen R normalization.
BACKGROUND_RANGES = [(.27914036,.318),(.318,1.05),(1.05,1.4),(1.4,2.),
                     (2.,3.2),(3.2,3.6),(3.6,5.2),(5.2,9.46),(9.46,11.5)]

def load_alphaqed26_spectrum(path,*,verify=True):
    path = Path(path)
    if verify:
        provenance=json.loads((path/'provenance.json').read_text(encoding='utf8'))
        for entry in provenance['input_records']:
            data=(path/entry['path']).read_bytes()
            if len(data)!=entry['bytes'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
                raise ValueError('frozen spectral input identity mismatch: '+entry['path'])
    raw = np.genfromtxt(path/'raw_spectrum.csv',delimiter=',',names=True,dtype=None,encoding=None)
    p = np.genfromtxt(path/'pqcd_spectrum.csv',delimiter=',',names=True)
    res = np.genfromtxt(path/'resonance_parameters.csv',delimiter=',',names=True)
    u = np.genfromtxt(path/'resonance_undressing.csv',delimiter=',',names=True)
    us = np.genfromtxt(path/'resonance_spacelike_undressing.csv',delimiter=',',names=True)
    blocks = {}
    specs = [('CHPT',.27914036,.318),('LOW_BG',.318,1.4),('R1_4',1.4,3.2),
             ('R3_2',3.2,3.6),('R3_6',3.6,5.2),('R9_5',9.46,11.5),
             ('OMEGA',.757,.8107),('PHI',1.00001,1.04)]
    for name,lo,hi in specs:
        d=raw[raw['block']==name]; x=d['E_GeV']; y=d['R']; st=d['stat_abs']
        # frome/frphi return column 3 directly: ABSOLUTE, unlike background.
        sy=d['sys_component'] if name in ('OMEGA','PHI') else d['sys_component']*y
        keep=(x<=hi)|(np.arange(len(x))==np.searchsorted(x,hi))
        x,y,st,sy=x[keep],y[keep],st[keep],sy[keep]
        if np.any(np.diff(x)<=0) or np.any(y<0) or not np.all(np.isfinite(np.stack([x,y,st,sy]))):
            raise ValueError('malformed consumed spectral block '+name)
        blocks[name]={'x':x,'y':y,'stat':st,'sys':sy,'lo':lo,'hi':hi,'type':'data'}
    for group,lo,hi in [(1,5.2,9.46),(2,11.5,1e6)]:
        d=p[p['block']==group]
        blocks['PQCD_'+str(group)]={'x':d['E_GeV'],'y':d['R'],'stat':d['stat_abs'],
                                  'sys':d['sys_abs'],'lo':lo,'hi':hi,'type':'pqcd'}
    undress={}
    for idx in [4,5,6,10,11,12,13,14,15]:
        d=us[us['resonance']==idx] if idx in [4,5,10,11,12] else u[(u['resonance']==idx)&(u['index']>=2)]
        # The source's psi2 grid has one reversed pair. Spacelike factors
        # are evaluations of a smooth source function, so order the samples.
        # The same pair in psi3 lies below its consumed resonance domain.
        d=d[np.argsort(d['E_GeV'],kind='stable')]
        if np.any(np.diff(d['E_GeV'])<=0): raise ValueError('duplicate undressing sample')
        undress[idx]=(d['E_GeV'],d['factor'],d['frac_error'])
    return {'blocks':blocks,'resonances':res,'undressing':undress,'path':str(path)}

def _weights(block,kernel,order):
    x=block['x'];lo=block['lo'];hi=block['hi']
    knots=np.unique(np.r_[lo,x[(x>lo)&(x<hi)],hi])
    z,w=leggauss(order);left=knots[:-1];right=knots[1:]
    e=(left[:,None]+right[:,None])/2+(right-left)[:,None]/2*z
    values=np.asarray(kernel(e),dtype=float)
    if not np.all(np.isfinite(values)):raise ValueError('nonfinite consumed spectral kernel')
    wx=(right-left)[:,None]/2*w*values
    i=np.clip(np.searchsorted(x,e,side='right')-1,0,len(x)-2)
    t=(e-x[i])/(x[i+1]-x[i]);weights=np.zeros(len(x))
    np.add.at(weights,i.ravel(),(wx*(1-t)).ravel())
    np.add.at(weights,(i+1).ravel(),(wx*t).ravel())
    return weights

def _resonance_value(spectrum,idx,kernel_s,order):
    r=spectrum['resonances'][idx-1];M=r['M_MeV']*.001;G=r['G_MeV']*.001;B=r['Br_ee']
    lo=r['Elo_GeV'];hi=r['Ehi_GeV'];x,y,ye=spectrum['undressing'][idx]
    energy=np.unique(np.r_[lo,x[(x>lo)&(x<hi)],hi])
    t=np.arctan((energy**2-M*M)/(M*G));z,w=leggauss(order)
    ti=(t[:-1,None]+t[1:,None])/2+(t[1:,None]-t[:-1,None])/2*z
    s=M*M+M*G*np.tan(ti);e=np.sqrt(s)
    d=(t[1:,None]-t[:-1,None])/2*w
    values=np.asarray(kernel_s(s),dtype=float)
    if not np.all(np.isfinite(values)):raise ValueError('nonfinite consumed resonance kernel')
    density=9*ALPHA_REF_INV**2*B*G*s*s/(M**3)*values*np.interp(e,x,y)
    val=float(np.sum(d*density))
    undressing_error=float(np.sum(d*density*np.interp(e,x,ye)))
    return val,undressing_error

def _integral(spectrum,kernel_E,kernel_s,order=20):
    components={};stats=[];syss=[];undressing_errors=[];pqcd_errors=[]
    for name,b in spectrum['blocks'].items():
        w=_weights(b,kernel_E,order);components[name]=float(w@b['y'])
        if name in ('OMEGA','PHI'):
            stats.extend(w*b['stat']);syss.append(float(w@b['sys']))
        elif b['type']=='pqcd':
            pqcd_errors.append(float(w@b['sys']))
        else:
            stats.extend(w*b['stat'])
            for ilo,ihi in BACKGROUND_RANGES:
                blo=max(ilo,b['lo']);bhi=min(ihi,b['hi'])
                if blo>=bhi:continue
                wb=_weights(dict(b,lo=blo,hi=bhi),kernel_E,order)
                syss.append(float(wb@b['sys']))
    staps=[.057,.112,.114];sysps=[.042,.148,.152]
    stayp=[.034,.159,.133,.092,.118,.202];sysyp=[.067,.160,.093,.208,.250,.313]
    for idx in [4,5,6,10,11,12,13,14,15]:
        value,underr=_resonance_value(spectrum,idx,kernel_s,order)
        components['RESONANCE_'+str(idx)]=value
        k=idx-4 if idx<10 else idx-10
        stats.append(value*(staps if idx<10 else stayp)[k])
        syss.append(value*(sysps if idx<10 else sysyp)[k])
        undressing_errors.append(underr)
    # Both perturbative intervals consume the same alpha_s parameter.
    # Its source finite-difference sensitivity is fully correlated.
    syss.append(sum(pqcd_errors))
    stat=float(np.linalg.norm(stats));syst=float(np.linalg.norm(syss))
    return {'value':sum(components.values()),'statistical_error':stat,'systematic_error':syst,
            'spectral_error':float(np.hypot(stat,syst)),'components':components,
            'statistical_error_vector':stats,'systematic_error_vector':syss,
            'quadrature_order':order,'scope':'standard-ee five-flavor two-current source; IUNMIX=0, iomegaphidat=2',
            'undressing_error_estimate':sum(abs(x) for x in undressing_errors),
            'undressing_error_policy':'separate conservative sum; not an independent covariance row',
            'tail_beyond_E_GeV':1e6,'tail_not_included':True,
            'status':'NUMERICALLY_EVALUATED_MEASURED_FIVE_FLAVOR_TWO_CURRENT_COMPONENT',
            'complete_native_remainder':False,
            'uncertainty_scope':'source point/range errors, common alpha_s sensitivity; no full experimental joint covariance or higher-QCD-order enclosure'}

def integrate_spectral_kernel(spectrum,kernel_s,*,order=20):
    """Integrate R(s)*kernel_s(s) ds with shared spectral uncertainty rows.

    The callback includes its physical normalization factors. The spectrum
    includes source resonance domains once and source pQCD intervals. The
    result excludes s>1e12; a caller must retain its own tail contribution
    or bound. This evaluates a spectral contraction, not the native vertex.
    """
    if not callable(kernel_s):raise ValueError('kernel_s callback required')
    return _integral(spectrum,lambda e:2*e*kernel_s(e*e),kernel_s,order)

def delta_alpha_had_spacelike(spectrum,Q_squared,alpha0,*,order=20):
    Q=float(Q_squared);a=float(alpha0)
    if not np.isfinite(Q) or Q<0 or not np.isfinite(a) or a<=0:
        raise ValueError('finite Q_squared>=0 and alpha0>0 required')
    f=a/(3*np.pi)*Q
    result=_integral(spectrum,lambda e:f*2/(e*(e*e+Q)),lambda s:f/(s*(s+Q)),order)
    result['Q_squared_GeV2']=Q
    result['tail_asymptotic_estimate']=a/(3*np.pi)*(11/3)*np.log1p(Q/1e12)
    return result

def delta_alpha_had_spacelike_jet(spectrum,Q_squared,alpha0,*,order=20):
    """Value and first two derivatives with respect to positive Q^2.

    dDelta/dQ^2=(alpha/3pi)*int R(s)/(s+Q^2)^2 ds;
    d2Delta/d(Q^2)^2=-(2alpha/3pi)*int R(s)/(s+Q^2)^3 ds.
    These are physical spectral operator applications with the same rows.
    """
    value=delta_alpha_had_spacelike(spectrum,Q_squared,alpha0,order=order)
    Q=float(Q_squared);f=float(alpha0)/(3*np.pi)
    first=integrate_spectral_kernel(spectrum,lambda s:f/(s+Q)**2,order=order)
    second=integrate_spectral_kernel(spectrum,lambda s:-2*f/(s+Q)**3,order=order)
    # Asymptotic tail estimates are explicit, separate from the finite integral.
    first['tail_asymptotic_estimate']=f*(11/3)/(1e12+Q)
    second['tail_asymptotic_estimate']=-f*(11/3)/(1e12+Q)**2
    return {'value':value,'first':first,'second':second,'variable':'Q_squared_GeV2'}

def leading_hvp_pauli(spectrum,alpha0,m_mu,*,order=20,kernel_order=96):
    a=float(alpha0);m=float(m_mu)
    if not np.isfinite(a) or a<=0 or not np.isfinite(m) or m<=0:
        raise ValueError('finite positive alpha0 and m_mu required')
    def kernel(s):
        return pauli_kernel(s,m,kernel_order=kernel_order)
    f=a*a/(3*np.pi*np.pi)
    result=_integral(spectrum,lambda e:f*2*kernel(e*e)/e,lambda s:f*kernel(s)/s,order)
    result['alpha0']=a;result['m_mu_GeV']=m
    result['tail_asymptotic_estimate']=f*(11/3)*m*m/(3*1e12)
    result['kernel_quadrature_order']=kernel_order
    return result

def pauli_kernel(s,m_mu,*,kernel_order=96):
    """Positive LO dispersion kernel; stable source analytic formula above threshold.

    For x<0.5 the log1p remainder is evaluated as a convergent series,
    avoiding cancellation at high energy. Sixty terms suffice in the
    actual muon/pion-threshold domain (x<0.21); the omitted positive bound
    is below 1e-42 for the elementary series there.
    """
    s=np.asarray(s,dtype=float);q=s/(float(m_mu)**2)
    if np.any(~np.isfinite(q)) or np.any(q<=0):raise ValueError('positive finite s/m_mu^2 required')
    result=np.empty_like(q);mask=q>4.5
    v=q[mask];x=2/(v-2+np.sqrt(v*(v-4)))
    p=x.copy();series=np.zeros_like(x)
    for j in range(1,61):
        series+=((-1)**(j+1))/(j+2)*p;p*=x
    result[mask]=x*x*(2-x*x)/2+(1+x)**2*(1+x*x)*series+(1+x)/(1-x)*x*x*np.log(x)
    if np.any(~mask):
        z,w=leggauss(kernel_order);u=(z+1)/2;w=w/2
        result[~mask]=np.sum(w*u*u*(1-u)/(u*u+(1-u)*q[~mask,None]),axis=-1)
    return result
