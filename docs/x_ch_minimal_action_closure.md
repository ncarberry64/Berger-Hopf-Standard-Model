# X_ch Minimal Action Decision

Status: `CONDITIONAL_ACTION_THEOREM`.

The controlling ontology defines BHSM modes as physical boundary fields and
defines `X_ch` as a charged boundary-response operator:

```text
Psi_boundary -> P_ch Psi_boundary -> X_ch(P_ch Psi_boundary)
             -> charged-current response
```

The conditional source and response rule are

```text
S_charged_response = integral_boundary
  <J_ch, X_ch(P_ch Psi_boundary)> + h.c.

delta S_charged_response / delta J_ch = X_ch(P_ch Psi_boundary)
```

`C_ch_boundary` remains the artifact-backed boundary source. The theorem is
conditional because the operator interpretation is author supplied. It does
not identify `X_ch` as a standalone four-dimensional production field, and it
does not close numerical coupling normalization or external HEP runtime gates.
