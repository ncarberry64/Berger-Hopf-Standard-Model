"""Run actual joint-workspace handlers through failed/reopened/new-input states."""
from pathlib import Path
import json
import shutil
import subprocess
import pytest


@pytest.mark.parametrize('mode',['requested_starts','numerical_fallback','default_fallback'])
def test_saved_joint_result_restores_controls_and_clears_stale_job_state(mode):
    node=shutil.which('node')
    if node is None:pytest.skip('Node unavailable for joint UI behavior fixture')
    tests=Path(__file__).resolve().parent
    completed=subprocess.run([node,str(tests/'joint_browser_state_fixture.js'),
        str(tests.parent/'bhtracker/web/joint.js'),mode],capture_output=True,text=True,timeout=20)
    assert completed.returncode==0,completed.stdout+completed.stderr
    assert json.loads(completed.stdout)=={'mode':mode,'passed':True,
        'restored_starts':12 if mode=='numerical_fallback' else 16}
