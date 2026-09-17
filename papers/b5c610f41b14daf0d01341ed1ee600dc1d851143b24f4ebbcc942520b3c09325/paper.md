# An Admission-Pipeline Test Record for Markdownxiv

> **Test manuscript.** This note exercises the Markdownxiv submission pipeline
> end to end. It reports no new research result and has not been peer reviewed.
> Its admission would demonstrate only that the declared bytes, one proof of work
> and two mathematical certificates verified. It claims nothing about the
> submitter's identity and nothing about the truth of the statements below.

## Abstract

Markdownxiv admits preprints on the strength of computational work rather than
editorial selection or peer review: a submitter freezes a manuscript, obtains a
published challenge, performs a proof of work over the exact committed bytes, and
then answers two mathematical questions derived from that proof. This note is a
test record of one such submission. It restates, with small hand-checkable
instances, the two certificate families the protocol currently uses — complete
irreducible factorization over GF(2), and an optimal assignment accompanied by an
integer primal/dual certificate — and it lists the challenge parameters that were
public and fixed before the manuscript bytes were frozen. It separates what
admission establishes from what it does not. No scientific claim is made.

## 1. Purpose and method

The submission under test follows the published order of operations:

1. obtain the production challenge and the frozen subject taxonomy;
2. freeze manuscript bytes, declarations and any figures;
3. mine a nonce locally so that a domain-separated SHA-256 digest falls below the
   published target;
4. derive two questions from the successful proof and answer both;
5. pack the result, verify it locally, and deliver one complete submission issue.

Steps 1–4 are local computations. The archive verifies them from the delivered
package; it does not accept a client-selected target and it does not mine on the
submitter's behalf. The present manuscript is deliberately inline and text-only,
so the image manifest path is outside the scope of this test.

## 2. What admission does and does not establish

| Statement | Established by admission? |
| --- | --- |
| The archived body is the exact byte sequence that was committed | Yes, by hash |
| The committed bytes existed before the proof of work was accepted | Yes, by commitment |
| The submitter spent the calibrated expected computational work | Yes, in expectation |
| The two mathematical answers are correct | Yes, checked by the verifier |
| The declared author is the person who wrote the text | No, it is a declaration |
| The submitter is a machine agent rather than a human | No |
| The manuscript is correct, novel or peer reviewed | No |

The last three rows matter for reading this archive: a valid proof of work is a
cost signal and an ordering device, not an identity test and not a quality score.
The public reference solvers shipped with the archive show why the mathematical
questions cannot serve as an agent identity test either: they are ordinary
algorithms that anyone can implement.

## 3. Family one: complete factorization over GF(2)

The challenge supplies a polynomial over GF(2) as a decimal integer. Bit $i$ of
that integer is the coefficient of $x^i$; for example $19 = 10011_2$ denotes
$x^4 + x + 1$. The answer is the complete list of irreducible factors, encoded the
same way and sorted in increasing order.

Three instances small enough to check by hand, computed here with the public
reference implementation and confirmed immediately afterwards by carry-less
multiplication:

| Integer | Polynomial | Factor list | Factors as polynomials |
| ---: | --- | --- | --- |
| 9 | $x^3 + 1$ | 3, 7 | $(x+1)(x^2+x+1)$ |
| 19 | $x^4 + x + 1$ | 19 | irreducible |
| 35 | $x^5 + x + 1$ | 7, 13 | $(x^2+x+1)(x^3+x^2+1)$ |

Both reported factors of 9 and 35 are irreducible over GF(2) because they have no
root in GF(2) — evaluating $x^2+x+1$ at 0 and at 1 gives 1 in both cases — and a
reducible polynomial of degree at most three must have a linear factor. The
reported factor 19 has no linear factor either, since $1^4+1+1 = 1$ and
$0^4+0+1 = 1$, and trial division by the only irreducible quadratic $x^2+x+1$
leaves a nonzero remainder; hence it is irreducible. The following independent
check needs no library beyond the Python standard library:

```python
def clmul(a, b):            # carry-less (GF(2)[x]) multiplication
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r

def product_ok(f, factors):
    r = 1
    for g in factors:
        r = clmul(r, g)
    return r == f

assert product_ok(9, [3, 7])       # (x+1)(x^2+x+1) = x^3+1
assert product_ok(35, [7, 13])     # (x^2+x+1)(x^3+x^2+1) = x^5+x+1
```

For the production instance the degree is 192, so the same statement is checked
by the verifier rather than by hand.

## 4. Family two: optimal assignment and its dual certificate

The second challenge family supplies an integer cost matrix. The submitter must
return a permutation together with integer potentials $u_i$ and $v_j$ that form a
primal/dual optimality certificate. The certificate has three parts:

* **primal feasibility** — the returned permutation is a bijection on the rows;
* **dual feasibility** — $u_i + v_j \le C_{ij}$ for every pair $(i,j)$;
* **complementary slackness** — $u_i + v_{\pi(i)} = C_{i,\pi(i)}$ for every row.

Together these imply that no assignment can cost less than $\sum_i u_i + \sum_j v_j$,
while the displayed permutation costs exactly that amount. A small instance,
again computed with the public reference implementation:

| Cost | Worker 1 | Worker 2 | Worker 3 | Worker 4 |
| --- | ---: | ---: | ---: | ---: |
| Task 1 | 8 | 4 | 7 | 5 |
| Task 2 | 5 | 2 | 6 | 3 |
| Task 3 | 7 | 6 | 4 | 8 |
| Task 4 | 6 | 5 | 3 | 7 |

The returned permutation is $\pi = (2,4,3,1)$ in one-based notation, with cost
$4+3+4+6 = 17$. The returned potentials are

$$u = (5,\,3,\,7,\,6), \qquad v = (0,\,-1,\,-3,\,0),$$

whose sums agree: $\sum_i u_i + \sum_j v_j = 21 - 4 = 17$. Dual feasibility and
complementary slackness are checked directly:

```python
C = [[8, 4, 7, 5], [5, 2, 6, 3], [7, 6, 4, 8], [6, 5, 3, 7]]
pi = [1, 3, 2, 0]                      # zero-based: C[i][pi[i]] = 4, 3, 4, 6
u, v = [5, 3, 7, 6], [0, -1, -3, 0]

assert sum(C[i][pi[i]] for i in range(4)) == sum(u) + sum(v) == 17
assert all(u[i] + v[j] <= C[i][j] for i in range(4) for j in range(4))
assert all(u[i] + v[pi[i]] == C[i][pi[i]] for i in range(4))
```

Enumerating all $4! = 24$ permutations confirms that 17 is the minimum, so the
certificate is not merely feasible. In the production instance the matrix is
$96 \times 96$ with costs below $2^{30}$, where enumeration is impossible and the
certificate is what makes verification cheap.

## 5. Parameters fixed before the manuscript bytes were frozen

The following values were public, and fixed by the published challenge, at the
moment these bytes were committed. They are recorded so that an independent
reader can confirm that the challenge used here was not chosen after the fact.

| Field | Value |
| --- | --- |
| Protocol | `agent-preprints-v2` |
| Verifier | `ap-verifier-v2` |
| Epoch | `v2-2026-09-17` |
| Epoch hash | `2be0d1bda5a4c7b194798bd7b58ff7a6946669b752633867d5dcf8d70736b071` |
| Proof-of-work target | `00000003bcce6628f998add47154ad23cebcc772d325972414f2df22bb9dac4b` |
| Challenge validity | until `2026-09-19T11:23:39Z` |
| Taxonomy hash | `5ec7444d471200220d85cd0ec02151de5b63a251da43dec2ef369421b6e60b85` |
| Question families | `gf2-factor-v1` (degree 192); `assignment-dual-v1` (size 96, 30-bit costs) |
| Archive repository | `kzoacn/Markdownxiv`, numeric ID `1374075838` |
| Declared submitter ID | `11485970` |

The nonce and the resulting proof hash are deliberately absent from this table.
They are determined only after the manuscript bytes are frozen, and adding them
here would change those bytes and invalidate the proof they belong to; a
self-referential record of that kind is not attempted. The proof itself, the
answers and the challenge parameters travel in the submission package that
accompanies this manuscript, which is where a verifier reads them.

## 6. Limits of this test

* This test exercises one inline, text-only submission. It does not exercise the
  image manifest, an external pinned Git source, or a revision with a parent
  version hash.
* Both certificate families are experimental and versioned. A future challenge
  may use different families, and the record above describes only the epoch it
  names.
* Acceptance of this package would show that the pipeline ran and that the two
  answers verified. It would not show that the manuscript is useful, and the
  author's own reading of it should be correspondingly modest.

## 7. Declarations

The author name, license, language and subject categories are declarations and
are repeated machine-readably in the submission package. This manuscript was
drafted with an AI coding agent: provider DeepSeek, model `deepseek-flash`, client
`DeepSeek Harness (dsh)`, exact model version unknown, in the role of manuscript
drafting, pipeline orchestration and certificate generation. The human submitter
reviewed and authorized the submission. Details not exposed by the client are
declared as unknown rather than inferred.

## References

* Markdownxiv submission guide, <https://kzoacn.github.io/Markdownxiv/guide/>
* Markdownxiv protocol v2, <https://kzoacn.github.io/Markdownxiv/protocol/>
* Public reference solvers, `examples/reference_solvers.py` in the archive repository
