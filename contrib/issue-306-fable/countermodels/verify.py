#!/usr/bin/env python3
"""Machine-checked finite countermodels for OPH issue #306 (Uniform Collar Projection Gap).

Acceptance item covered (issue #306): "A finite countermodel demonstrates failure when
each mixing or locality hypothesis is removed."

Grounding (all citations pinned to origin/main ae6eccd113213c51cb44dc93c525452fd3679556):
  * Theorem target and hypotheses (G1)-(G4):
      extra/yang_mills_gap_clay_problem.tex:492-521 (admissible atomic collar tower),
      :523-533 (finite classification / rate floor c_*),
      :543-557 (Uniform collar-projection and transfer gap, delta_* = c_*(1-eta_*)).
  * Paper-stated countermodels (this script machine-checks and extends them):
      extra/yang_mills_gap_clay_problem.tex:572-592
      (two-site epsilon family with heat-bath spectrum {0, 2e, 2(1-e), 2};
       Gray-cycle pair family with gap 1 - cos(2*pi/2^m)).
  * Certificate contract (vendored, blob cad9d83b):
      code/yang_mills_gap/collar_gap_certificate.py
  * Witness verifier (vendored, blob 3055eb52):
      code/yang_mills/verify_collar_gap_certificate.py
  * Contract witness data (blob b5b9de93):
      code/yang_mills/certificates/issue_306_theorem_contract_witness.json

What this script ADDS over the repo's own tests (confirm-and-extend, not rival):
  1. code/yang_mills/test_collar_gap_certificate.py::test_no_mixing_local_countermodel_has_zero_gap
     is vacuous (it asserts a hand-set literal 0 == 0 and constructs no operator).
     CM1 here builds the two-site heat-bath collar generator exactly and proves its
     characteristic polynomial equals x(x-2e)(x-(2-2e))(x-2) as a POLYNOMIAL IDENTITY
     in e over Q (exact rational coefficient comparison), so the paper's stated spectrum
     holds for ALL epsilon, and the gap 2e -> 0 with eta(e) = 1-2e -> 1.
  2. The Gray-cycle test verifies ONE eigenvector only; it does not verify that
     1 - cos(2*pi/2^m) is the MINIMAL positive eigenvalue. CM2 here verifies the exact
     operator identity (I-E_0)+(I-E_1) = I - (S+S^{-1})/2 in exact rationals and then
     computes the FULL spectrum numerically, confirming the minimum positive eigenvalue.
  3. CM2 also machine-checks the nonlocality witness behind tex line 584 ("deciding
     which bit to change reads the whole configuration"): block membership in the
     matchings is determined by the parity of ALL m bits (parity(gray(k)) == k mod 2).
  4. CM2 includes the positive control: the LOCAL rate-1 family (all m single-bit
     heat baths on the product law) has gap exactly 1, uniformly in m, matching the
     theorem's delta_* = c_*(1-eta_*) = 1*(1-0) = 1 prediction.
  5. CM3 exercises the vendored certificate validator fail-closed on four hypothesis
     removals, including the two LOCALITY-side rejections (refinement escaping the
     finite type table; influence on an unlisted type) that the repo's own test file
     does not cover.
  6. CM3b demonstrates that the arithmetic validator ACCEPTS a string-level
     misdeclaration of the Gray family (emitting gap_lower = 1) while the true
     operator gap at m = 10 is < 2e-5: the faithfulness of the declared source
     signature (tex:536, "complete source signature") is load-bearing and is exactly
     the locality hypothesis the countermodel removes.

Numeric policy: every load-bearing identity is exact-rational (fractions.Fraction).
numpy is used ONLY for full-spectrum cross-checks of operators whose exact structure
has already been established rationally; those checks carry explicit tolerances.

Run:  python verify.py     (exit code 0 iff every countermodel PASSes)
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

RESULTS: list[tuple[str, bool, str]] = []


def record(name: str, ok: bool, detail: str) -> None:
    RESULTS.append((name, ok, detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    for line in detail.splitlines():
        print(f"       {line}")


# ---------------------------------------------------------------------------
# Exact univariate polynomial arithmetic over Q (coefficients low -> high).
# ---------------------------------------------------------------------------

Poly = tuple[Fraction, ...]


def p_const(c) -> Poly:
    return (Fraction(c),)


def p_trim(p: Poly) -> Poly:
    q = list(p)
    while len(q) > 1 and q[-1] == 0:
        q.pop()
    return tuple(q)


def p_add(a: Poly, b: Poly) -> Poly:
    n = max(len(a), len(b))
    return p_trim(tuple(
        (a[i] if i < len(a) else Fraction(0)) + (b[i] if i < len(b) else Fraction(0))
        for i in range(n)))


def p_neg(a: Poly) -> Poly:
    return tuple(-c for c in a)


def p_mul(a: Poly, b: Poly) -> Poly:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            out[i + j] += ca * cb
    return p_trim(tuple(out))


E_VAR: Poly = (Fraction(0), Fraction(1))  # the indeterminate e


def mat_mul(A, B):
    n = len(A)
    out = []
    for i in range(n):
        row = []
        for j in range(n):
            acc = p_const(0)
            for k in range(n):
                acc = p_add(acc, p_mul(A[i][k], B[k][j]))
            row.append(acc)
        out.append(row)
    return out


def mat_add(A, B):
    n = len(A)
    return [[p_add(A[i][j], B[i][j]) for j in range(n)] for i in range(n)]


def mat_scale_id(c: Poly, n: int):
    return [[c if i == j else p_const(0) for j in range(n)] for i in range(n)]


def char_poly_faddeev(A) -> list[Poly]:
    """Coefficients [c1, ..., cn] of det(xI - A) = x^n + c1 x^{n-1} + ... + cn over Q[e].

    Faddeev-LeVerrier: M_1 = A, c_1 = -tr(M_1); M_k = A M_{k-1} + c_{k-1} I,
    c_k = -tr(M_k)/k.
    """
    n = len(A)
    coeffs: list[Poly] = []
    M = mat_scale_id(p_const(1), n)  # M_1 = I
    for k in range(1, n + 1):
        AM = mat_mul(A, M)
        trace = p_const(0)
        for i in range(n):
            trace = p_add(trace, AM[i][i])
        ck = p_mul(p_const(Fraction(-1, k)), trace)
        coeffs.append(ck)
        M = mat_add(AM, mat_scale_id(ck, n))
    return coeffs


# ---------------------------------------------------------------------------
# CM1: mixing removed, locality kept (two-site epsilon family, tex:574-581).
# ---------------------------------------------------------------------------

def cm1() -> None:
    # States ordered [00, 01, 10, 11]. pi(00)=pi(11)=(1-e)/2, pi(01)=pi(10)=e/2.
    # Single-site heat-bath conditional expectations (exact Gibbs conditionals):
    #   P(x1=0|x2=0)=1-e, P(x1=0|x2=1)=e, symmetric in the sites.
    one, e = p_const(1), E_VAR
    ome = p_add(one, p_neg(e))  # 1 - e
    z = p_const(0)
    # E1: condition on x2 (columns are (y1, x2))
    E1 = [[ome, z, e, z],
          [z, e, z, ome],
          [ome, z, e, z],
          [z, e, z, ome]]
    # E2: condition on x1 (columns are (x1, y2))
    E2 = [[ome, e, z, z],
          [ome, e, z, z],
          [z, z, e, ome],
          [z, z, e, ome]]
    # Collar generator with unit rates: L = (I - E1) + (I - E2) = 2I - E1 - E2.
    L = mat_add(mat_scale_id(p_const(2), 4), mat_add(
        [[p_neg(c) for c in row] for row in E1],
        [[p_neg(c) for c in row] for row in E2]))

    got = char_poly_faddeev(L)  # [c1, c2, c3, c4] of det(xI - L)

    # Expected det(xI - L) = x (x - 2e) (x - (2-2e)) (x - 2), expanded in Q[e][x].
    # Multiply the three nontrivial monic linear factors as polynomials in x with Q[e] coeffs.
    def lin(root: Poly) -> list[Poly]:
        return [p_neg(root), p_const(1)]  # x - root, low->high in x

    def xmul(a: list[Poly], b: list[Poly]) -> list[Poly]:
        out = [p_const(0)] * (len(a) + len(b) - 1)
        for i, ca in enumerate(a):
            for j, cb in enumerate(b):
                out[i + j] = p_add(out[i + j], p_mul(ca, cb))
        return out

    two_e = p_mul(p_const(2), e)
    two_m2e = p_add(p_const(2), p_neg(two_e))
    expected_x = xmul(xmul(xmul(lin(p_const(0)), lin(two_e)), lin(two_m2e)), lin(p_const(2)))
    # expected_x has degree 4: coeffs low->high in x; convert to [c1..c4] convention:
    # det(xI-L) = x^4 + c1 x^3 + c2 x^2 + c3 x + c4
    exp_c = [expected_x[3], expected_x[2], expected_x[1], expected_x[0]]

    ident = all(p_trim(g) == p_trim(x) for g, x in zip(got, exp_c))

    # Frozen endpoint e = 0: measure supported on {00, 11}; heat bath fixes both
    # configurations, so L restricted to the support is the exact 2x2 zero matrix
    # and the kernel is 2-dimensional: gap above the vacuum projector is exactly 0.
    def at0(p: Poly) -> Fraction:
        return p[0]
    support = [0, 3]
    L0 = [[at0(L[i][j]) for j in support] for i in support]
    frozen_zero = all(c == 0 for row in L0 for c in row)

    # Dobrushin influence for this family, exact: a_12 = TV(P(.|x2=0), P(.|x2=1))
    #   = |(1-e) - e| = 1 - 2e for e <= 1/2, so eta(e) = 1 - 2e -> 1 as e -> 0,
    # and the certified bound c_*(1-eta) = 2e coincides exactly with the true gap.
    eps_list = [Fraction(1, 2 ** k) for k in range(1, 13)]
    gaps = [2 * eps for eps in eps_list]
    etas = [1 - 2 * eps for eps in eps_list]
    mono = all(b < a for a, b in zip(gaps, gaps[1:])) and all(b > a for a, b in zip(etas, etas[1:]))

    ok = ident and frozen_zero and mono and gaps[-1] == Fraction(1, 2048)
    record(
        "CM1 mixing-removed (two-site heat-bath family, tex:574-581)",
        ok,
        "char poly of L equals x(x-2e)(x-(2-2e))(x-2) as a polynomial identity in e over Q: "
        f"{ident}\n"
        f"frozen endpoint e=0: L|support is the exact zero 2x2 matrix (gap exactly 0): {frozen_zero}\n"
        f"exact family: eta(e)=1-2e -> 1, true gap 2e -> 0 (last tested gap = {gaps[-1]}); "
        "no uniform positive modulus exists once uniform mixing (G3) is dropped.\n"
        "Locality is KEPT throughout: two sites, radius-1 conditionals, one bounded collar type.",
    )


# ---------------------------------------------------------------------------
# CM2: locality removed, mixing kept (Gray-cycle pair family, tex:581-591).
# ---------------------------------------------------------------------------

def gray(k: int) -> int:
    return k ^ (k >> 1)


def cm2() -> None:
    if np is None:
        record("CM2 locality-removed (Gray-cycle family)", False, "numpy unavailable")
        return
    half = Fraction(1, 2)
    exact_ok = True
    parity_ok = True
    flip_positions_by_m: dict[int, int] = {}
    gap_rows: list[str] = []
    gaps: list[float] = []
    ms = list(range(3, 11))
    for m in ms:
        n = 2 ** m
        order = [gray(k) for k in range(n)]
        pos = {s: k for k, s in enumerate(order)}
        # Matching E0 pairs cyclic positions (0,1),(2,3),...; E1 pairs (1,2),...,(n-1,0).
        # Exact structural identity: 2I - E0 - E1 must equal I - (S + S^{-1})/2
        # in the cyclic-position basis (S = cyclic shift). Verify entrywise in Q.
        for k in range(n):
            # row of A = (I-E0)+(I-E1) at cyclic position k:
            # diagonal 2 - 1/2 - 1/2 = 1; off-diagonal -1/2 at k-1 and k+1; zero elsewhere.
            # E0 block containing k: partner p0 = k^1 (positions); E1 partner p1 = ((k-1)^1)+1 mod n
            p0 = k ^ 1
            p1 = (k - 1) % n if k % 2 == 0 else (k + 1) % n
            partners = {p0, p1}
            if partners != {(k - 1) % n, (k + 1) % n}:
                exact_ok = False
        # blocks of both matchings are 2x2 [[1/2,1/2],[1/2,1/2]]: exactly idempotent,
        # symmetric, stochastic (conditional expectation onto the pair sigma-algebra
        # of the uniform product law); verified once algebraically:
        B = [[half, half], [half, half]]
        idem = all(
            sum(B[i][k] * B[k][j] for k in range(2)) == B[i][j]
            for i in range(2) for j in range(2))
        if not idem:
            exact_ok = False
        # Nonlocality witness (tex:584): block membership parity. parity(gray(k)) == k mod 2,
        # so deciding whether a configuration is a left or right member of an E0 block
        # requires the parity of ALL m bits. Exact check for every state:
        for k in range(n):
            if bin(order[k]).count("1") % 2 != k % 2:
                parity_ok = False
        # Distinct bit positions flipped inside the E1 matching (collar-type witness):
        flips = set()
        for k in range(1, n, 2):
            a, b = order[k], order[(k + 1) % n]
            flips.add((a ^ b).bit_length() - 1)
        flip_positions_by_m[m] = len(flips)
        # Full spectrum (numeric cross-check of the exactly-established cycle operator):
        A = np.eye(n)
        for k in range(n):
            A[k, (k - 1) % n] -= 0.5
            A[k, (k + 1) % n] -= 0.5
        eig = np.linalg.eigvalsh(A)
        positive = eig[eig > 1e-12]
        gap = float(positive.min())
        predicted = 1 - math.cos(2 * math.pi / n)
        if abs(gap - predicted) > 1e-9:
            exact_ok = False
        gaps.append(gap)
        gap_rows.append(f"m={m:2d} n={n:4d}: full-spectrum gap={gap:.3e} "
                        f"(=1-cos(2pi/n) within 1e-9), E1 flip positions used={len(flips)}")
    shrinking = all(b < a for a, b in zip(gaps, gaps[1:])) and gaps[-1] < 2e-5
    unbounded_types = all(flip_positions_by_m[m] >= m - 1 for m in ms) and \
        flip_positions_by_m[ms[-1]] > flip_positions_by_m[ms[0]]

    # Positive control: the LOCAL rate-1 family (all m single-bit heat baths on the
    # uniform product law) has gap exactly 1 uniformly in m: theorem prediction
    # delta_* = c_*(1-eta_*) = 1*(1-0) = 1 (tex:543-557).
    control_ok = True
    for m in range(3, 9):
        n = 2 ** m
        A = np.zeros((n, n))
        for s in range(n):
            A[s, s] = m / 2
            for i in range(m):
                A[s, s ^ (1 << i)] -= 0.5
        eig = np.linalg.eigvalsh(A)
        positive = eig[eig > 1e-12]
        if abs(float(positive.min()) - 1.0) > 1e-9:
            control_ok = False

    ok = exact_ok and parity_ok and shrinking and unbounded_types and control_ok
    record(
        "CM2 locality-removed (Gray-cycle pair family, tex:581-591)",
        ok,
        "exact identity (I-E0)+(I-E1) = I - (S+S^-1)/2 and exact idempotent pair blocks: "
        f"{exact_ok}\n" + "\n".join(gap_rows) + "\n"
        f"minimal positive eigenvalue confirmed over the FULL spectrum (extends the\n"
        "single-eigenvector check in code/yang_mills/test_collar_gap_certificate.py): "
        f"{shrinking}\n"
        f"nonlocality witness: parity(gray(k)) == k mod 2 for every state ({parity_ok}); "
        "block membership reads the parity of ALL m bits, and the E1 matching uses "
        f"{flip_positions_by_m[ms[-1]]} distinct flip positions at m={ms[-1]} "
        f"(unbounded across the family: {unbounded_types}), violating (G1) finite type table.\n"
        "Mixing is KEPT: every pair kernel is uniform (rate 1, perfectly mixing), the law "
        "is the product fair-bit law.\n"
        f"positive control (locality restored, all m single-bit heat baths): gap = 1 "
        f"uniformly in m = 3..8 ({control_ok}), matching delta_* = c_*(1-eta_*) = 1.",
    )


# ---------------------------------------------------------------------------
# CM3: certificate-contract fail-closed checks on the vendored validators.
# ---------------------------------------------------------------------------

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cm3() -> None:
    cert = load_module("collar_gap_certificate",
                       HERE / "vendored" / "collar_gap_certificate.py")
    wit = load_module("verify_collar_gap_certificate",
                      HERE / "vendored" / "verify_collar_gap_certificate.py")

    # CM0 reproduction: the packet's own witness recomputes to the announced values.
    witness = json.loads((HERE / "data" / "issue_306_theorem_contract_witness.json").read_text())
    res = wit.verify(witness)
    repro = (res["c_floor"], res["eta_upper"], res["gap_lower"]) == ("3/4", "1/2", "3/8")
    record(
        "CM0 reproduction (issue_306_theorem_contract_witness.json)",
        repro,
        f"vendored verifier recomputes c_floor=3/4, eta_upper=1/2, gap_lower=3/8: {repro}",
    )

    cases = [
        ("cm3_mixing_removed_eta_ge_1.json", "must be < 1",
         "uniform mixing (G3) removed: eta = 1"),
        ("cm3_locality_removed_refinement_escape.json", "leaves the finite",
         "locality (G1/G4) removed: refinement escapes the printed type table"),
        ("cm3_locality_removed_unknown_influence_target.json", "unknown type",
         "locality removed: influence targets an unlisted type"),
        ("cm3_rate_floor_removed.json", "must be positive",
         "rate floor (G2) removed: rate_lower = 0"),
    ]
    all_ok = True
    lines = []
    for fname, needle, label in cases:
        payload = json.loads((HERE / "data" / fname).read_text())
        try:
            cert.validate(payload)
            all_ok = False
            lines.append(f"{label}: NOT rejected (fail-open!) [{fname}]")
        except ValueError as exc:
            hit = needle in str(exc)
            all_ok = all_ok and hit
            lines.append(f"{label}: rejected ({exc}) [{fname}] expected-msg={hit}")
    record("CM3 certificate fail-closed on hypothesis removal", all_ok, "\n".join(lines))

    # CM3b: the arithmetic validator accepts a string-level MISDECLARATION of the
    # Gray family and emits gap_lower = 1, while CM2 shows the true gap at m=10 is
    # 1 - cos(2pi/1024) < 2e-5. Faithfulness of the declared source signature
    # (tex:536) is therefore load-bearing: it IS the locality hypothesis.
    payload = json.loads(
        (HERE / "data" / "cm2_gray_cycle_misdeclared_manifest.json").read_text())
    try:
        receipt = cert.validate(payload)
        accepted = receipt["gap_lower"] == "1"
    except ValueError:
        accepted = False
    true_gap = 1 - math.cos(2 * math.pi / 1024)
    ok = accepted and true_gap < 2e-5
    record(
        "CM3b misdeclared nonlocal family: certificate accepts, operator refutes",
        ok,
        f"validator emits gap_lower = 1 for the misdeclared manifest: {accepted}\n"
        f"true operator gap at m=10 is 1-cos(2pi/1024) = {true_gap:.3e} << 1\n"
        "=> the arithmetic checks alone do not certify the gap; the source-locality\n"
        "   declaration (rooted_neighborhood faithfulness) is the load-bearing hypothesis.",
    )


def main() -> int:
    print("OPH issue #306 finite countermodels: machine verification")
    print("pinned upstream: origin/main ae6eccd113213c51cb44dc93c525452fd3679556")
    print("-" * 76)
    cm1()
    cm2()
    cm3()
    print("-" * 76)
    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} countermodel checks PASS")
    if failed:
        print("FAILED: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
