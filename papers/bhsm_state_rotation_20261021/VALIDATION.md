# Validation record

The geometry and numerical checks validate stated identities and equations.
They do not establish microscopic closure, a physical state selection,
continuum stability, a measured signal or a unique astronomical inference.

- Recovered starting package: all **71 original file members** preserved byte
  for byte (72 archive entries include a directory). All six inherited source
  hashes verified. Its full nine-stage replay passed in a separate recovery
  copy; the original timing example reproduced. See results/starting_*.
- New package: all **seven replay stages passed**. Exact symbolic trace,
  projector, differential spectrum, scalar Euler equation/current elimination
  and nodal rigidity checks passed. The geometric numerical check includes
  258 cases covering both complex orientations and both sharp endpoints.
- Ordered optical response: independent quadrature, tighter temporal provider,
  direct finite matrix ODE, common-profile null, state-swap sign, symmetric
  second-order test forcing, fixed-lens derivative and Fermat symmetrizer passed.
  Exact numerical values and limits are in results/rotation_response.json.
- A direct swapped-state matrix subtraction initially failed an unnecessarily
  tight numerical threshold: its tiny antisymmetric coefficient suffered
  cancellation between much larger off-diagonal entries (absolute coefficient
  difference 7.62e-24). The value is retained in the JSON. Integrating the same
  original finite ODE in I,Z,X,J components avoids that subtraction and gives
  state-swap error 2.96e-31. No physical state, uncertainty or result threshold
  was adjusted to obtain a positive physical conclusion.
- New manuscript: 13-page PDF compiled with MiKTeX/pdflatex + BibTeX/latexmk;
  no undefined citations/references or overfull boxes. All 13 actual rendered
  pages visually inspected; both figure pairs, equations, references and
  footers readable. Hash-labelled visual reports are in results/pdf_render/.
- Separate skeptical mathematical, novelty and numerical/physical-chain
  reviews completed. Reported corrections were incorporated and the targeted
  resolution addendum is included. These are internal AI-assisted reviews,
  not external peer review.
- Repository gate: code/figures.py passed; original root manuscript compiled;
  scripts/package_submission.py verified 54 archive entries. Generated changes
  to original tracked PDFs/ZIPs were restored in this new worktree.
- Fresh focused repository pytest: **39 passed**, covering all three current
  action/environment/gradient test files outside the historical snapshot plus
  the documented optical, low-rank and prediction gates. Exact command and
  JUnit record are in results/focused_repository_pytest.*.
- Historical full repository evidence: **87 passed, 1 strict expected failure**
  in 6699.65 seconds. All **45/45** scientific snapshot files match their
  recorded LF-normalized SHA256 values, with fingerprint
  ac34e2f45e3eab1e9317db88d97288cd8fcfac7595b436cd4b1438a2b50039a2.
  This is reused baseline evidence, not a new full-suite result for this paper.
  A redundant fresh broad run was stopped during the documented long nested
  distance integrals after this exact snapshot verification. It is not counted
  as passed. Initial plain collection had failed because one inherited test
  imports background without adding code/; the fresh scoped run explicitly
  initially used PYTHONPATH=<worktree>/code. A minimal repository conftest.py
  now supplies that same import path for ordinary pytest and CI. With no
  PYTHONPATH override, the 39 scoped tests pass and all 102 tests collect.
  No existing scientific test, equation or acceptance rule changed.
- Portable release: the unpacked source ZIP's complete seven-stage offline
  replay passed. Five scientific JSON outputs matched byte for byte across
  the working tree and independent extraction. See portable replay receipt.

The package's independent scientific replay has no network or observational
dependencies. The original failed observational/microscopic flags, frozen
manifest and PR #23 remain preserved.
