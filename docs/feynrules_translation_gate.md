# BHSM FeynRules Translation Gate v0.3

Machine-readable gate:

```text
artifacts/BHSM_feynrules_translation_gate_v0_3.json
```

The gate checks:

- complete 4D Lagrangian;
- field normalization;
- vertex normalization;
- mass/width scheme;
- renormalization scheme;
- gauge fixing;
- complete vertex table;
- production parameter card.

Current result:

```text
feynrules_ready = false
ufo_ready = false
```

The gate is intentionally strict. Candidate ledgers do not count as production
FeynRules readiness.

Phase Three-C does not open this gate. It adds explicit target maps and
candidate parameter-card entries while leaving production FeynRules readiness
blocked.

Phase Three-D also leaves this gate closed. Canonical target conventions and
current-attachment maps are not production FeynRules readiness.

Phase Three-E exports vector/fermion normalization theorem-status artifacts,
gauge-fixing/coupling scheme candidates, and mass-width/renormalization
candidate ledgers. The FeynRules gate remains closed because target
normalization conventions are not BHSM-derived field-strength theorems and the
mass-width, renormalization, complete 4D Lagrangian, and production vertex
tables remain open.

Phase Three-F clears the interface normalization sub-gate by defining
canonical production-basis fields with `Z_A,prod = Z_psi,prod = 1`. The
FeynRules gate remains closed because complete 4D Lagrangian export,
mass-width closure, renormalization closure, and production vertex tables
remain open.

Phase Three-G exports the candidate vertex table and symbolic Lagrangian
assembly ledger, but the FeynRules gate remains closed because the table is
incomplete and multiple blocker rows remain open.
