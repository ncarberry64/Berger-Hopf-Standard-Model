import numpy as np
from bhsm.interface.aether_n3_sbp_redirect_audit_v16_57 import trapezoid_sbp_difference
from bhsm.interface.aether_n3_replacement_global_kkt_v16_11 import NODES,trapezoid_weights
def test_trapezoid_pair_satisfies_exact_sbp_identity():
    d=trapezoid_sbp_difference();w=np.diag(trapezoid_weights());b=np.zeros((NODES,NODES));b[0,0]=-1;b[-1,-1]=1
    assert np.linalg.norm(w@d+d.T@w-b)<1e-12
