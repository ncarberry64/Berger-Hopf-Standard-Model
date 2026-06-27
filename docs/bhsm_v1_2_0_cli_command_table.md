# BHSM v1.2.0 CLI command table

| Command | Purpose | Internet? | PDG? | Wolfram/FeynRules? | MadGraph? | Claim status | Output |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `registry` | List registry entries | no | no | no | no | metadata only | text/JSON |
| `status KEY` | Inspect one entry | no | no | no | no | metadata only | text/JSON |
| `predict` | Run placeholder interface demo | no | no | no | no | conditional on calibration/formula | text/JSON |
| `report` | Build reviewer report | no | no | no | no | comparison and blocker aware | text/JSON |

No CLI command promotes open theorems or disabled runtime gates.
