import numpy as np
from bhsm.interface.muon_endpoint_second_domain_germ import endpoint_trace_first_germ,endpoint_second_from_first_germs


def test_second_endpoint_contact_includes_vector_field_derivative():
    # Complex nonlinear coframe; independently compare value second
    # differences on a parabolic trajectory, not a frozen straight slope.
    raw=np.zeros((2,268),complex);raw[:,0]=[.04+.02j,.05-.01j]
    raw[:,98]=[.003+.001j,.004-.002j];raw[:,99]=[.01+.003j,.008-.002j]
    raw[:,74]=[.02+.01j,-.01+.02j];raw[:,37]=[.03-.01j,.02+.01j]
    R=np.zeros((536,504));P=np.zeros((268,252))
    # Only the geometry coordinates are needed for this independent control.
    P[:100,:100]=np.eye(100)
    R[:100,:100]=np.eye(100);R[268:368,252:352]=np.eye(100)
    norm=np.eye(4);offset=np.zeros_like(raw);offset[:,0]=[.03+.01j,.04-.02j]
    offset[:,98]=[.006+.001j,-.003+.002j];offset[:,99]=[.004+.003j,.002-.001j]
    offset[:,74]=[.01+.002j,-.02+.004j];diagonal=.07+.02j
    rate=lambda z:offset+diagonal*z
    r=rate(raw);acc=diagonal*r;h=2e-4
    base=endpoint_trace_first_germ(raw,r,R,P,norm)
    plus=endpoint_trace_first_germ(raw+h*r,rate(raw+h*r),R,P,norm)
    minus=endpoint_trace_first_germ(raw-h*r,rate(raw-h*r),R,P,norm)
    a=endpoint_second_from_first_germs(plus,minus,np.arange(504)*h,np.zeros(504),normalized_step=h,rate_magnitude=1)
    zp=raw+h*r+.5*h*h*acc;zm=raw-h*r+.5*h*h*acc
    pp=endpoint_trace_first_germ(zp,rate(zp),R,P,norm);mm=endpoint_trace_first_germ(zm,rate(zm),R,P,norm)
    for value,second in(('moving_geometric_trace','moving_geometric_trace_time_second'),('proper_normal_rows','proper_normal_rows_time_second')):
        independent=(pp[value]-2*base[value]+mm[value])/(h*h)
        np.testing.assert_allclose(a[second],independent,atol=2e-7,rtol=5e-4)
    # Omitting the derivative of the canonical vector would change this jet.
    frozen_plus=endpoint_trace_first_germ(raw+h*r,r,R,P,norm)
    frozen_minus=endpoint_trace_first_germ(raw-h*r,r,R,P,norm)
    frozen=endpoint_second_from_first_germs(frozen_plus,frozen_minus,np.zeros(504),np.zeros(504),normalized_step=h,rate_magnitude=1)
    assert np.linalg.norm(a['proper_normal_rows_time_second']-frozen['proper_normal_rows_time_second'])>1e-5
