"""Run the unchanged Hessian producer with a status-only I/O retry policy."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]


def main():
    import derive_n12_gate7_direct_physical_hessians as h
    from bhsm.interface.status_file_retry import retry_status_writes
    def event(path,attempt,error):
        if attempt==1:print(json.dumps(dict(status_write_retry=str(path),winerror=error.winerror)),flush=True)
    with retry_status_writes(h,[h.WORK/'active_state.json'],on_retry=event):
        h.main()


if __name__=='__main__':main()
