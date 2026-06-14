# boundary_action

Status: `BOUNDARY_ACTION_STRUCTURAL_CANDIDATE`
Closed: `False`
Candidate only: `True`

Structural rule: `S_boundary contains lambda_f (Omega_f-Omega_f0)^2 |psi|^2`
Computed value: `{'lepton_middle': {'sector': 'lepton', 'mode': (5, 2), 'q': 1, 'omega': 3}, 'lepton_light': {'sector': 'lepton', 'mode': (9, 3), 'q': 3, 'omega': 3}, 'up_middle': {'sector': 'up', 'mode': (6, 0), 'q': 6, 'omega': 6}, 'up_light': {'sector': 'up', 'mode': (10, 1), 'q': 8, 'omega': 6}, 'down_middle': {'sector': 'down', 'mode': (6, 3), 'q': 0, 'omega': 12}, 'down_light': {'sector': 'down', 'mode': (8, 2), 'q': 4, 'omega': 12}}`

Evidence:
- current omega values recover lepton/up/down mode pairs
- previous status=BOUNDARY_MODE_PAIR_INVARIANT_DERIVED_ACTION_OPEN

Missing assumptions:
- derive the boundary penalty term by variation of the complete action
- derive sector signs and base/fiber coefficients rather than inserting them
- derive primitive constant boundary levels as stationary non-heavy modes
- link channel dimension d_f to Omega_f without circular use of selected modes
