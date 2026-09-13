"""Diagnostic selected-line projection inside the centered action residual."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import diagnose_n12_gate7_component_centered_uniform_derivatives as component
from bhsm.interface import projected_coupled_variation_residual as projected

diagnostic=component.diagnostic


def evaluate(engine,source,start,stop):
    p=engine.p
    for file in (Path(__file__),Path(projected.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    old=diagnostic.signed.line_residual
    try:
        diagnostic.signed.line_residual=projected.line_residual
        arrays,proof=component.evaluate(engine,source,start,stop)
    finally:diagnostic.signed.line_residual=old
    proof['selected_line_projection_contracted_before_interval_evaluation']=True
    return arrays,proof


diagnostic.evaluate=evaluate
if __name__=='__main__':diagnostic.main()
