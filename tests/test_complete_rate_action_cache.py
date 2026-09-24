import sys
from pathlib import Path
from flint import arb,ctx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import derive_n12_gate7_complete_endpoint_rate_jet as driver
from bhsm.interface.shared_action_taylor import TaylorDomain


def test_exact_leg_symmetry_and_parameter_swap_reuse_one_contraction(tmp_path,monkeypatch):
    old=ctx.prec;ctx.prec=256
    try:
        d=TaylorDomain([(0,225,'box')],225)
        a=[arb(0)]*225;a[75]=arb(1);u=d.affine(0,a);v=driver.base.swap(u)
        one=d.affine(1);calls=[]
        def contract(module,state,legs,progress):
            calls.append(1);result=d.affine(2)
            for leg in legs:result*=leg[0]
            return result,arb(1)
        monkeypatch.setattr(driver.base,'contract',contract)
        (tmp_path/'immutable_inputs.json').write_text('{}')
        source=dict(domain=d,state=[one],sources={},radius_exact=['1','1'])
        evaluate=driver.SymmetricEvaluator(source,tmp_path)
        result_u=evaluate([[u],[one]])
        result_v=evaluate([[one],[v]])
        assert len(calls)==1
        assert result_u.a[0,75]==2 and result_u.a[0,150].is_zero()
        assert result_v.a[0,150]==2 and result_v.a[0,75].is_zero()
        assert result_u.r.is_zero() and result_v.r.is_zero()
    finally:ctx.prec=old
