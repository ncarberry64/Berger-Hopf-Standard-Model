"""Consume full-campaign DF without overwriting selected-pilot local evidence."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import derive_n12_gate7_full_direct_physical_jacobians as backend
import certify_n12_gate7_direct_physical_local_defects as assembler


def main():
    backend.install_backend()
    assembler.WORK=backend.ROOT/'artifacts/flagship_integration/.full_direct_physical_local_defect_work'
    original=assembler.load_inputs
    def load_inputs(indices):
        source=original(indices)
        assembler.residual.merge_verified_raw_sources(source['inputs'],source['raw_inputs'],
            {backend.producer.file_key(Path(__file__)):backend.producer.values.sha(Path(__file__))})
        return source
    assembler.load_inputs=load_inputs
    assembler.main()


if __name__=='__main__':main()
