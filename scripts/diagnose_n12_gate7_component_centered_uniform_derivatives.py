"""Diagnostic componentwise refinement of signed centered variation solves."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import diagnose_n12_gate7_centered_uniform_derivatives as diagnostic
from bhsm.interface import componentwise_weighted_response as rows

original_evaluate=diagnostic.evaluate


def evaluate(engine,source,start,stop):
    p=engine.p
    for file in (Path(__file__),Path(rows.__file__)):
        p.geometry.residual.merge(source['binding']['files'],{p.df.file_key(file):p.values.sha(file)})
    p.verify_sources(source['binding'])
    previous=diagnostic.enclose_response
    try:
        diagnostic.enclose_response=rows.enclose_response_rows
        return original_evaluate(engine,source,start,stop)
    finally:diagnostic.enclose_response=previous


diagnostic.evaluate=evaluate
if __name__=='__main__':diagnostic.main()
