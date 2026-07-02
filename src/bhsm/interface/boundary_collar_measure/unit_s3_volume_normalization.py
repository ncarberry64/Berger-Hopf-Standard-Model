from .common import build_gate

def audit_unit_s3_volume_normalization():
    return build_gate("unit_s3_volume_normalization")
