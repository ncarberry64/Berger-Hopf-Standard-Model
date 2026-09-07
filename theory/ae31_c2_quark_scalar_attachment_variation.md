# AE3.1 current-C2 quark scalar-attachment variation

BHSM already contains the scalar-state factorization

```text
H(x,y)=H(x) Phi(y)
```

and a Higgs-selected internal profile `Phi0` in the historical parent-action
scaffold. Neither fact by itself makes `Phi` an active coordinate of the
versioned AE3.1 action. In AE3.1, `H` is an intrinsic M4 field and the only
added LR--Higgs term is the charged-lepton term. Therefore
`delta S_AE3.1/delta Phi` is not presently defined.

The possible historical source can be decided by chirality grading. In the
current quark basis

```text
Gamma_chi=diag(-1,-1,+1,+1).
```

A `U(1)` connection is representation diagonal and chirality even:

```text
[Gamma_chi,A_U1]=0,
P_L A_U1 P_R=P_R A_U1 P_L=0.
```

The transported quark--Higgs supports are chirality odd:

```text
{Gamma_chi,I_up}=0,
{Gamma_chi,I_down}=0.
```

Consequently variation of the Higgs-selected `U(1)` connection cannot equal
the missing LR scalar vertex. Its valid historical role—charge and boundary
orientation selection—survives unchanged.

The scalar profile action also has a precise but different role. Substitution
of `H(x,y)=H(x)Phi(y)` into the scalar kinetic term gives

```text
integral_B |Phi|^2 dmu_Berger * integral_M4 |D H|^2.
```

Canonical profile normalization conditionally fixes that kinetic factor to
one. But a scalar-only functional contains no `Q_L,u_R,d_R`, so both mixed
third variations with quark fields vanish. Profile normalization can
normalize an already action-owned odd vertex; it cannot create one.

The symbolic historical boundary term `S_boundary[Psi,Phi0]` does not rescue
the vertex. The repository explicitly records that it has not been obtained
by varying the full internal action. Its target values `6` and `12` select
family/winding boundary data and are not quark Yukawa residues.

The exact missing action class is therefore an odd internal Dirac or
superconnection endomorphism

```text
S_odd = integral bar(Psi) E_H[H,Htilde] Psi,
{Gamma_chi,E_H}=0,
E_H=V_u(Htilde) I_up + V_d(H) I_down.
```

This statement introduces no new representation channel: `I_up,I_down` are
the already transported BHSM supports. It introduces no independent contact
coefficient: the squared-pencil contacts remain fixed by the first vertices.
It identifies the parity and action location of the object that the parent
theory must derive. This unit does not add `E_H` to AE3.1 or choose its
residues.

The next constructive calculation must derive, from one parent action, the
odd endomorphism, its universal-profile attachment and retained trace, and
the two residues on the existing supports. Once obtained, the projector
responses, contact closure, family shapes, and current-C2 domain transport
are already available downstream.

Promoted:

- exclusion of the chirality-even Higgs-selected U(1) connection as the LR
  Yukawa owner;
- exclusion of scalar profile normalization as a generator of a mixed
  fermion vertex;
- the chirality-odd Dirac/superconnection class and support required of the
  missing parent object.

Not promoted:

- action ownership or normalization of that odd endomorphism;
- numerical `c_u,c_d`, quark poles, masses, or CKM mixing.

`FULL_BHSM_COMPLETE = FALSE`.
