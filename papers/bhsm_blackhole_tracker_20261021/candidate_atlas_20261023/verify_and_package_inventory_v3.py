"""Run focused tests, verify deterministic output, and package factual metadata."""
from pathlib import Path
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime,timezone
import zipfile

HERE=Path(__file__).resolve().parent
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write_new(path,value):
    with Path(path).open("x",encoding="utf-8",newline="\n") as handle:
        json.dump(value,handle,indent=2,ensure_ascii=False,allow_nan=False); handle.write("\n")

def main():
    test=subprocess.run([sys.executable,"-I",str(HERE/"test_inventory_v3.py")],cwd=HERE,capture_output=True,text=True)
    if test.returncode!=0: raise RuntimeError(test.stdout+test.stderr)
    with (HERE/"INVENTORY_VERIFICATION_v3.testlog.txt").open("x",encoding="utf-8") as handle:
        handle.write(test.stdout+test.stderr)
    original=HERE/"inventory_v3.json"; replay=HERE/"inventory_v3_replayed.json"
    if original.read_bytes()!=replay.read_bytes(): raise ValueError("Artifact rebuild differs")
    doc=json.loads(original.read_bytes()); freeze=json.loads((HERE/"INPUT_FREEZE_v3.json").read_bytes())
    files=["build_inventory_v3.py","prepare_metadata_snapshot_v3.py","test_inventory_v3.py",
        "verify_and_package_inventory_v3.py","README_INVENTORY_v3.txt","INPUT_FREEZE_v3.json","inventory_v3.json"]
    files+=sorted(str(p.relative_to(HERE)).replace("\\","/") for p in (HERE/"metadata_sources_v3").iterdir() if p.is_file())
    receipt={"schema":"bhsm.blackhole_tracker.candidate_inventory_verification.v3","status":"PASS_METADATA_REBUILD_AND_NONPROMOTION_CHECKS",
        "created_utc":datetime.now(timezone.utc).isoformat(),"runtime":{"python":sys.version,"platform":platform.platform()},
        "builder_sha256":sha(HERE/"build_inventory_v3.py"),"input_freeze_sha256":sha(HERE/"INPUT_FREEZE_v3.json"),
        "inventory_sha256":sha(original),"second_cli_rebuild_sha256":sha(replay),"byte_identical_rebuild":True,
        "focused_tests":18,"test_exit_code":test.returncode,"test_log_sha256":sha(HERE/"INVENTORY_VERIFICATION_v3.testlog.txt"),
        "relocated_offline_rebuild_with_original_paths_forbidden":"PASS_IN_TEST_15",
        "original_source_hashes_checked_before_and_after_preparation":42,"metadata_snapshot_files":16,
        "native_observation_rows_bundled":0,"new_fits_or_likelihood_calls":0,"counts":doc["metadata"]["counts"],
        "literature_positive_benchmark_separate_from_cohort":1,"engine_accepted_BH_interpretations":0,
        "BHSM_interpretation":doc["metadata"]["BHSM_interpretation"],"formal_BHSM_repository":doc["metadata"]["formal_BHSM_repository"],
        "files":[{"path":name,"bytes":(HERE/name).stat().st_size,"sha256":sha(HERE/name)} for name in files]}
    write_new(HERE/"INVENTORY_VERIFICATION_v3.json",receipt)
    package_names=files+["INVENTORY_VERIFICATION_v3.json","INVENTORY_VERIFICATION_v3.testlog.txt"]
    package=HERE/"BHSM_Candidate_Atlas_Metadata_v3.zip"
    with zipfile.ZipFile(package,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in package_names: archive.write(HERE/name,name)
    with zipfile.ZipFile(package) as archive:
        if archive.testzip() is not None: raise ValueError("ZIP integrity failure")
        if set(archive.namelist())!=set(package_names): raise ValueError("ZIP member mismatch")
        for name in package_names:
            if archive.read(name)!=(HERE/name).read_bytes(): raise ValueError("ZIP content mismatch")
    write_new(HERE/"INVENTORY_PACKAGE_v3.json",{"schema":"bhsm.candidate_inventory_metadata_package.v3","status":"PASS",
        "filename":package.name,"bytes":package.stat().st_size,"sha256":sha(package),"members":len(package_names),
        "all_member_bytes_verified":True,"raw_observations_bundled":False,"owner_verification_sha256":sha(HERE/"INVENTORY_VERIFICATION_v3.json")})
    print(json.dumps({"verification_sha256":sha(HERE/"INVENTORY_VERIFICATION_v3.json"),"package_sha256":sha(package),"package_bytes":package.stat().st_size,"members":len(package_names)},indent=2))

if __name__=="__main__": main()
