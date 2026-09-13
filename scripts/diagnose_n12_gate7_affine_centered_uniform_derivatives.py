"""Diagnostic mean-value integration of centered residuals on unchanged domains."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import diagnose_n12_gate7_centered_uniform_derivatives as diagnostic
import numpy as np
from flint import arb
from bhsm.interface import centered_variation_state_derivative as derivatives
from bhsm.interface import affine_hs_midpoint_domain as grouped

original_evaluate=diagnostic.evaluate


def evaluate(engine,source,start,stop):
    p=engine.p;cert=p.values.cert;paired=source['paired'];count=stop-start
    for file in (Path(__file__),Path(derivatives.__file__),Path(grouped.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    groups=source.get('groups')
    if groups is None:
        groups=[dict(start=0,stop=1,norm='interval',radius=source['tube']['radius_longitudinal']),
                dict(start=1,stop=75,norm='euclidean',radius=source['tube']['radius_transverse'])]
    domain=paired['directions'];center=paired['center']
    old_line=diagnostic.signed.line_residual;old_response=diagnostic.signed.physical_response_residual
    base_integrand=cert._integrand;records=[]

    def at_center(callback):
        active=cert._integrand
        try:
            cert._integrand=base_integrand
            with diagnostic.use_ball_factored_integrand(cert,center):
                return callback(cert._arb_action_jets(center).dense_maps)
        finally:cert._integrand=active

    def combine(anchor,ds,which):
        if ds.shape!=(62,count,domain.shape[1]):raise ArithmeticError('all affine derivative columns required')
        bound=grouped.group_row_bounds(ds.reshape(62*count,domain.shape[1]),groups).reshape(62,count)
        result=anchor+np.array([arb(0,b) for b in bound.flat],dtype=object).reshape(62,count)
        records.append(dict(which=which,domain_columns=domain.shape[1],
            maximum_state_contribution=float(max(bound.flat)),
            maximum_anchor_absolute=float(max(abs(a).upper() for a in anchor.flat))))
        print(diagnostic.json.dumps(dict(phase='AFFINE_CENTERED_RESIDUAL',**records[-1])),flush=True)
        return result

    def line(action,x,psi,lam,R,u,v,maps):
        anchor,_=at_center(lambda center_maps:old_line(action,center,psi,lam,R,u,v,center_maps))
        ds=derivatives.line_state_derivative(action,x,psi,lam,R,u,v,domain,maps)
        raw_p=np.concatenate((np.full(37,arb(0)),psi))
        slopes=np.asarray(action(x,[raw_p[:,None,None],raw_p[:,None,None],v[:,None,:]],maps),dtype=object).reshape(count)
        return combine(anchor,ds,'line'),slopes

    def response(action,x,psi,lam,hard,border,dp,slopes,R,u,qw,rw,weights,v,maps):
        raw_p=np.concatenate((np.full(37,arb(0)),psi))
        def centered(center_maps):
            center_slopes=np.asarray(action(center,[raw_p[:,None,None],raw_p[:,None,None],v[:,None,:]],center_maps),dtype=object).reshape(count)
            return old_response(action,center,psi,lam,hard,border,dp,center_slopes,R,u,qw,rw,weights,v,center_maps)
        anchor=at_center(centered)
        ds=derivatives.response_state_derivative(action,x,psi,lam,hard,R,u,qw,rw,weights,v,domain,maps)
        return combine(anchor,ds,'response')

    try:
        diagnostic.signed.line_residual=line;diagnostic.signed.physical_response_residual=response
        arrays,proof=original_evaluate(engine,source,start,stop)
    finally:
        diagnostic.signed.line_residual=old_line;diagnostic.signed.physical_response_residual=old_response
    if len(records)!=2:raise ArithmeticError('complete affine residuals for both variations required')
    proof['affine_centered_residuals']=records
    proof['same_paired_domain_groups_used']=True
    return arrays,proof


diagnostic.evaluate=evaluate
if __name__=='__main__':diagnostic.main()
