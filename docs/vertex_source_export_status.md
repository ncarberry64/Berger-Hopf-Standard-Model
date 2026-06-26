# BHSM Vertex-Source Export Status v0.2

The vertex-source ledger is not a Feynman-rule export.

It lists source categories that may later feed a Feynman-rule layer:

- charged boundary response;
- neutral operator kernel;
- CKM mixing source;
- PMNS mixing source;
- CP holonomy source;
- boundary transport identity.

Current artifact:

```text
artifacts/BHSM_vertex_source_ledger_v0_2.json
```

Current status: symbolic source ledger only. Lorentz structures, gauge-fixed
interaction terms, field normalization, and vertex normalization remain missing.

## Phase Three-A Extension

Phase Two-A exports vertex-source categories. Phase Three-A adds a vertex
normalization ledger:

```text
artifacts/BHSM_vertex_normalization_ledger_v0_3.json
```

Current status:

```text
vertex_normalization_complete = false
complete_vertex_table_present = false
```

No source category is upgraded to a production Feynman rule.
