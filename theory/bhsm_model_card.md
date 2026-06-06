# Berger-Hopf Standard Model Working Model Card

This card assembles the current executable low-energy reinterpretation. It is not a completed first-principles proof.

Model level: `BHSM_WORKING_LOW_ENERGY_REINTERPRETATION`
Theorem complete: `False`
Geometry config: `ALPHA_ANCHORED` (`a=1.157054135733433`, status `CANONICAL`)
Geometry source: alpha^{-1}/(12*pi^2) Hopf/electroweak residual
Geometry notes:
- Selected as canonical only when BHSM assumptions include epsilon_alpha = alpha^{-1}/(12*pi^2) - 1.
- This selection rule does not inspect empirical mass or CKM residuals.
- Adopted because the BHSM scale sector contains epsilon_alpha = alpha^{-1}/(12*pi^2) - 1.
- Not chosen by fitting residuals.

## Gauge Group

SU(3)_c x SU(2)_L x U(1)_Y

## Field and Representation Ledger

| Field | Chirality | SU(3) | SU(2) | Y | Generations |
| --- | --- | --- | --- | --- | --- |
| `Q_L` | left | `3` | `2` | `1/6` | 3 |
| `u_R` | right | `3` | `1` | `2/3` | 3 |
| `d_R` | right | `3` | `1` | `-1/3` | 3 |
| `L_L` | left | `1` | `2` | `-1/2` | 3 |
| `e_R` | right | `1` | `1` | `-1` | 3 |
| `H` | scalar | `1` | `2` | `1/2` | profile `Phi(y)` |

## Hypercharge and Anomalies

Anomalies cancel: `True`

## Generation and Mode Ledger

| Sector | Rank | Mode (k,j) | Hopf q | Action |
| --- | --- | --- | --- | --- |
| charged_leptons | heavy | `(0,0)` | 0 | 0.0 |
| charged_leptons | middle | `(5,2)` | 1 | 35.33877427301784 |
| charged_leptons | light | `(9,3)` | 3 | 102.04896845716057 |
| up_quarks | heavy | `(0,0)` | 0 | 0.0 |
| up_quarks | middle | `(6,0)` | 6 | 60.1958738286423 |
| up_quarks | light | `(10,1)` | 8 | 141.68155347314186 |
| down_quarks | heavy | `(0,0)` | 0 | 0.0 |
| down_quarks | middle | `(6,3)` | 0 | 48.0 |
| down_quarks | light | `(8,2)` | 4 | 85.42038836828547 |

## Yukawa Hierarchy Outputs

```json
{
  "charged_leptons": {
    "heavy": 1.0,
    "light": 0.00029729106456492414,
    "middle": 0.06007447093260976
  },
  "down_quarks": {
    "heavy": 1.0,
    "light": 0.0011165200546001757,
    "middle": 0.021933971495439474
  },
  "up_quarks": {
    "heavy": 1.0,
    "light": 1.2690463017606151e-05,
    "middle": 0.008310500554068288
  }
}
```

## CKM and PMNS Outputs

CKM status: `BHSM_CANONICAL_FLAVOR_SCREEN`, CP phase: `HOPF_PHASE_CP_SCREEN`
PMNS status: `EFFECTIVE_EXTENSION_SCREEN`, alpha: `0.0072973525692838015`

## Coupling Outputs

alpha_1 = `0.01688686394038963`
alpha_2 = `0.03377372788077926`
alpha_3 = `0.1182080475827274`

## Higgs/Electroweak Outputs

v_gev = `246.16986520825228`
m_lift_gev = `9718.396740299762`

## H_T Proxy Gap Output

Status: `PROXY_AUDIT`
Model level: `DIRAC_PROXY_LEVEL_2`
First complement eigenvalue: `1.4630400252994733`
First H_T complement gap: `19586.72266333732`
Passes proxy target: `True`

## Scalar Decoupling Output

Status: `FINITE_BASIS_SCAFFOLD`
Passes scaffold: `True`
Light Higgs projections: `1`

## Symbolic Lagrangian Blocks

```text
{
  "effective_neutrino": "\\frac{c_{ij}}{\\Lambda}(L_i H)(L_j H)",
  "fermion_kinetic": "\\bar{Q_L} i\\gamma^\\mu D_\\mu Q_L + \\bar{u_R} i\\gamma^\\mu D_\\mu u_R + \\bar{d_R} i\\gamma^\\mu D_\\mu d_R + \\bar{L_L} i\\gamma^\\mu D_\\mu L_L + \\bar{e_R} i\\gamma^\\mu D_\\mu e_R",
  "gauge_kinetic": "-\\frac14 G_{\\mu\\nu}^a G^{a\\mu\\nu} -\\frac14 W_{\\mu\\nu}^i W^{i\\mu\\nu} -\\frac14 B_{\\mu\\nu} B^{\\mu\\nu}",
  "higgs": "(D_\\mu H)^\\dagger(D^\\mu H) -[-\\mu^2 H^\\dagger H + \\lambda(H^\\dagger H)^2]",
  "topographic_internal": "\\mathcal L_{\\rm topo/int}",
  "yukawa": "-\\bar Q_L Y_d H d_R -\\bar Q_L Y_u \\tilde H u_R -\\bar L_L Y_e H e_R + h.c."
}
```

## Remaining Open Action-Level Derivations

- derive Omega_f from the full twisted Dirac/bundle action
- compute the full analytic twisted Dirac H_T spectrum
- prove assumptions A1-A7 in the full internal action
- complete two-/three-loop threshold RG matching
- prove scalar/topographic decoupling from the full action
