# Resume after the non-cut temporal element milestone

Start from PR465's new published revision, preserving newer work. Scientific
reference524ed90689bd5923c249bba2e699abf627e703cd; calculation began at
58e5941b38faae24e67be87aa55537aadeec656e. Read report.md, checkpoint.json,
semantic_scope.json and assembly_run_1/result.json. The previous cut and
endpoint calculations are preserved and were not replayed.

New arrays: run_1/prefix_time_element.npz is the evaluated degree4 prefix
weak-density element. run_3/result.json is its completed receipt;
run_3/point_volume_and_Cauchy.npz supplies point pairing measures.
future_run_2 has actual retained future node1/2 actions, their field/clock
inputs, and degree1 element. assembly_run_1 contains the cut-to-future1
connecting density element and the144x144 partial K/M assembly,48 joining
trace constraints, original source load and hierarchical form cotangent.

The original source satisfies joining constraints exactly in this
representation. The three model-scoped source contractions are
1.5928499679389998e-29,1.907643448553739e-5 and5.221547643364169e-5.
No stationary exterior equation, native heat or physical Pauli extraction
was solved. Interpolation/continuum remainders remain unevaluated. The
prefix proper-duration enclosure does not certify its quadratic form.

Preserve the common-A connection, daughter eta/radial inclusion, original
independent photon source, source-frame factors, full connected n1/n3
outputs, differentiated bulk/Cauchy projections, volume versus Cauchy
pairings, all-time updates and frozen locals. Add no lapse-only correction
to an already combined jet. The trial conormals are not stationary returns;
the prefix sampled endpoint trial conormal is also distinct from the
interior-node interpolant conormal.

NEXT: evaluate the source-reached inherited tail weak/conormal action
at retained future node2/action_arc4, using its total W/p trace injection
i2. Required contraction is i2^sharp Gamma1^owner u_s, where
Gamma0 u_s=i2 g and q_tail,0^owner(v,u_s)+s<v,u_s>_tail=0 on owned
zero-trace variations. Retain full relation if a graph chart fails,
connected response, material/reset/canonical-stop and same-owner
constraint/completion terms. Later point/clock records already exist;
do not call them missing or introduce a new physical boundary datum.
Do not invert this partial local Dirac assembly and call it the full
stratified source solve. The native shift/length prescription is unchanged.

No old guard, cut contraction, eigenbranch-selection campaign,98-direction
derivative campaign or broad audit is needed. Ten new readonly checks
already passed. Replay only if a scientific discrepancy requires it.

Reproduction from the publication worktree, using fresh output directories:

```powershell
C:\Python314\python.exe scripts/replay_muon_prefix_time_element.py --output <fresh-prefix>
C:\Python314\python.exe scripts/replay_muon_retained_arc_time_element.py --retained-input artifacts/muon_prefix_time_element_20261004/future_run_2 --output <fresh-future>
C:\Python314\python.exe scripts/connect_muon_temporal_elements.py --prefix <fresh-prefix> --future <fresh-future> --clock artifacts/muon_prefix_time_element_20261004/retained_connecting_clock.npz --output <fresh-assembly>
```

For the saved original prefix result, use run_1 together with the final
run_3 receipt; no receipt repair replay is needed. The current replay
fixes the wide-Arb display-string receipt parser and delivers point
pairings directly. Exact executed scientific code snapshots and hashes
are retained. The initial future attempt stopped before field actions at
an overly strict byte identity; its inputs were reused after recognizing
the tiny weighted-coordinate roundtrip. Neither historical state changed.

Targeted checks, if changed code or new evidence justifies them:

```powershell
C:\Python314\python.exe -m pytest --noconftest -q tests/test_muon_prefix_time_element.py tests/test_muon_retained_arc_time_element.py
```

Physical a_mu, g_mu, native uncertainty and physical transfer directions
remain unevaluated. Frozen local contributions are not added again or
refitted. This is the muon-specific realization, not a second universal
framework; generic interface extraction still follows an actual native
contraction.
