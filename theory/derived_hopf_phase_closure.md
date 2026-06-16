# Derived Hopf Phase Closure

Let the Hopf fiber coordinate satisfy

```text
psi ~ psi + 2*pi
```

and let an admissible boundary mode be

```text
Phi_d(psi) = exp(i d psi) Phi_0
```

Global single-valuedness requires

```text
Phi_d(psi+2*pi)=Phi_d(psi)
```

therefore

```text
exp(i 2*pi d)=1
```

so `d` is an integer. For positive closure dimensions,

```text
d in Z_{>0}
```

Status: `PO_BH_2_PHASE_CLOSURE_DERIVED_CONDITIONAL`.

Guardrail: this derives integer admissibility, not the full `{1,2,3}` spectrum.
