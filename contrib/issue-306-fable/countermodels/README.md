# Finite countermodels for issue #306 (Uniform Collar Projection Gap) — machine verification

Angle: the acceptance item "a finite countermodel demonstrates failure when each mixing
or locality hypothesis is removed." Everything here is confirm-and-extend of the proof
packet that closed #306 on origin/main; nothing rivals an existing lane (all four #306
comments are by muellerberndt; no external Lean lane is claimed there, and this work is
Python-only).

Pinned upstream: `origin/main` commit `ae6eccd113213c51cb44dc93c525452fd3679556`.
All `file:line` citations below refer to that commit (the local checkout of the repo is
on an older branch that predates the packet; nothing here was read from memory).

Run:

```
python verify.py     # exit 0 iff all countermodel checks PASS (verified: 5/5 PASS)
```

Requires Python 3.10+ and numpy (numpy is used only for full-spectrum cross-checks;
every load-bearing identity is exact-rational `fractions.Fraction`).

## Grounding (source-defined objects, pinned citations)

| Object | Citation (at ae6eccd1) |
|---|---|
| Admissible atomic collar tower, hypotheses (G1)-(G4) | `extra/yang_mills_gap_clay_problem.tex:492-521` |
| Finite collar classification / rate floor `c_*` | `extra/yang_mills_gap_clay_problem.tex:523-533` |
| Theorem: uniform gap `delta_* = c_*(1-eta_*)` | `extra/yang_mills_gap_clay_problem.tex:543-557` |
| Paper-stated finite countermodels (both) | `extra/yang_mills_gap_clay_problem.tex:572-592` |
| "complete source signature" premise | `extra/yang_mills_gap_clay_problem.tex:536` |
| Certificate contract (vendored here) | `code/yang_mills_gap/collar_gap_certificate.py` (blob `cad9d83b`) |
| Witness verifier (vendored here) | `code/yang_mills/verify_collar_gap_certificate.py` (blob `3055eb52`) |
| Contract witness data (copied here) | `code/yang_mills/certificates/issue_306_theorem_contract_witness.json` (blob `b5b9de93`) |
| tex blob | `6fcf1139` |

## What this adds over the repo's own tests (the gap this fills)

1. `code/yang_mills/test_collar_gap_certificate.py::test_no_mixing_local_countermodel_has_zero_gap`
   (at ae6eccd1) is **vacuous**: it asserts a hand-set literal `0 == 0` and constructs no
   operator. The paper's claimed heat-bath spectrum `{0, 2e, 2(1-e), 2}` (tex:580) was not
   machine-checked anywhere in the repo. CM1 here checks it as an exact polynomial identity.
2. `test_product_mixing_nonlocal_gray_cycle_gap_vanishes` verifies **one eigenvector**
   only; it does not verify that `1 - cos(2*pi/2^m)` is the *minimal* positive eigenvalue
   (i.e. the gap). CM2 confirms this over the full spectrum.
3. The repo's certificate tests cover mixing/rate/float rejections but **not** the two
   locality-side fail-closed paths (refinement escaping the finite type table; influence
   on an unlisted type). CM3 covers them.

## Countermodels and honest status labels

### CM1 — uniform mixing removed, locality kept  [newly-machine-checked-here]
The paper's two-site family (tex:574-581): `pi_e(00)=pi_e(11)=(1-e)/2`,
`pi_e(01)=pi_e(10)=e/2`, collar generator `L = (I-E_1)+(I-E_2)` with the two exact
single-site heat-bath conditional expectations (the `P_{v,r,b}` of tex:498).

Machine check (exact, no floats): the characteristic polynomial of `L`, computed by
Faddeev-LeVerrier over the polynomial ring Q[e], **equals** `x(x-2e)(x-(2-2e))(x-2)`
as a polynomial identity in `e`. Hence the spectrum is `{0, 2e, 2-2e, 2}` for *every*
epsilon, the gap is `2e -> 0`, and the exact Dobrushin coefficient is
`eta(e) = 1-2e -> 1`. At the frozen endpoint `e = 0`, `L` restricted to the support is
verified to be the exact zero matrix (kernel dimension 2, gap exactly 0). Locality holds
throughout (two sites, radius-1, one bounded collar type); only the *uniform* bound
`eta_* < 1` of (G3) fails across the family, and no uniform positive modulus exists.
Note the certified bound `c_*(1-eta(e)) = 2e` is *tight* on this family.

### CM2 — locality removed, mixing kept  [exact structure + numerical spectrum]
The paper's Gray-cycle family (tex:581-591): product fair-bit law on `{0,1}^m`, states
listed in cyclic reflected-Gray order, `E_0, E_1` the conditional expectations onto the
two alternating perfect matchings.

Machine checks:
- **Exact (rational):** each matched pair block is `[[1/2,1/2],[1/2,1/2]]` (idempotent,
  symmetric, stochastic: a genuine conditional expectation), and for every cyclic
  position the two matching partners are exactly the two cyclic neighbours, which is
  entrywise the identity `(I-E_0)+(I-E_1) = I - (S+S^{-1})/2` (m = 3..10).
- **Numerical (tolerance 1e-9, numpy eigvalsh):** the FULL spectrum confirms the
  minimal positive eigenvalue is `1 - cos(2*pi/2^m)`, strictly decreasing, reaching
  `1.882e-05` at m = 10. This extends the repo's single-eigenvector check to an actual
  gap statement. (The analytic identification of the full cycle spectrum is classical
  Fourier, as the paper itself says at tex:585; the numeric check is the machine
  confirmation, and it is the one non-exact step in this packet.)
- **Nonlocality witness (exact):** `parity(gray(k)) == k mod 2` for every state, so
  matching-side membership reads the parity of ALL m bits (this is tex:584 made
  computable), and the `E_1` matching uses m-1 distinct flip positions at size m —
  unbounded across the family, violating the finite printed type table (G1).
- **Positive control (numerical):** restoring locality (all m single-bit heat baths on
  the same law, rate 1, influence 0) gives gap exactly 1 uniformly in m = 3..8,
  matching the theorem's `delta_* = c_*(1-eta_*) = 1`.

### CM0 — reproduction  [reproduced-from-repo]
The vendored witness verifier recomputes the packet witness's announced exact values
`c_floor = 3/4, eta_upper = 1/2, gap_lower = 3/8` from
`data/issue_306_theorem_contract_witness.json`.

### CM3 — certificate fail-closed on hypothesis removal  [newly-machine-checked-here]
Four manifests in `data/` are each rejected by the vendored `validate()` with the
expected message: eta = 1 (mixing removed), refinement escaping the finite type table
(locality removed), influence on an unlisted type (locality removed), rate_lower = 0
(rate floor removed). The two locality rejections are not exercised by the repo's own
test file at ae6eccd1.

### CM3b — misdeclared nonlocal family  [demonstration, by-design boundary]
`data/cm2_gray_cycle_misdeclared_manifest.json` describes the CM2 Gray family with a
*false* string-level `rooted_neighborhood` (claiming radius-1 locality). The arithmetic
validator accepts it and emits `gap_lower = 1`, while the true operator gap at m = 10
is `1.882e-05`. This is not a soundness bug: the packet explicitly makes the type table
a source-supplied "complete source signature" (tex:536) and labels the executable layer
a data-model calibration, not a physical receipt (tex:601-608). CM3b makes precise
*where* the locality hypothesis lives: in the faithfulness of the declared source
signature, outside the arithmetic checks. That faithfulness is exactly the hypothesis
whose removal the countermodel demonstrates.

## What this does NOT show (claim boundary)

- Nothing here touches the physical compact-gauge Yang-Mills source, continuum,
  transfer/vacuum, OS regularity, or noncollapse obligations; per the #306 closure
  comment those remain gated under #294 and #295.
- CM2's "for all m" statement is machine-checked for m = 3..10 plus the classical
  analytic formula; the minimal-eigenvalue confirmation is numerical with stated
  tolerance, not exact-rational.
- No Lean artifact is produced here; this packet is pure data + Python, deliberately,
  to avoid opening a rival Lean lane.

## Files

```
verify.py                                     main verification script (PASS/FAIL per countermodel)
vendored/collar_gap_certificate.py            vendored from ae6eccd1 (blob cad9d83b), unmodified
vendored/verify_collar_gap_certificate.py     vendored from ae6eccd1 (blob 3055eb52), unmodified
vendored/PROVENANCE.md                        pinning record
data/issue_306_theorem_contract_witness.json  copied from ae6eccd1 (blob b5b9de93), unmodified
data/cm3_*.json                               fail-closed fixtures (must be rejected)
data/cm2_gray_cycle_misdeclared_manifest.json accepted-but-refuted fixture (CM3b)
verify_output.txt                             captured run (5/5 PASS, exit 0)
```
