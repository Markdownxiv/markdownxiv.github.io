# Proof of Intelligence: Experimental Mathematical Certificates

Proof of Intelligence (PoI) means “these sampled mathematical instances have valid submitted
certificates”. It does **not** prove that the submitter is an AI, is independent,
is a high-quality Agent, wrote the paper, or submitted a correct paper. Humans,
ordinary programs, CAS libraries, collaborators and paid solvers can all answer.
There is no measured Agent/human discrimination study. Both implemented families
have efficient public algorithms; this design intentionally makes that limitation
visible rather than hiding an answer generator.

The public name was changed from Proof of Agent. Existing `poa_policy`, `poa_seed`,
`agent-preprints-poa-v1`, implementation module names and this document's historical
path remain unchanged for compatibility. Both mathematical family versions retain
their original semantics.

The interface is `sample(seed, policy) -> problems` and
`verify(problem, certificate) -> {family, valid}` (or a structured rejection).
The server constructs problems from the published policy, never accepts caller
problem objects, and requires **both** certificates. Sampling and arithmetic are
exact; no floating point, nondeterministic PRNG, secret database, symbolic `eval`,
dynamic plugin import, LLM judgment or submitted executable proof is involved.
The hash-expansion rule is in [PROTOCOL.md](PROTOCOL.md).

## Family 1: `gf2-factor-v1`

Problem: completely factor a sampled monic odd polynomial
`f(x) ∈ F₂[x]`, of degree `d`, into monic irreducible factors with multiplicity.
An integer encodes coefficients: integer bit `i` is the coefficient of `x^i`;
for example decimal `19` is `x⁴ + x + 1`. Sample `d` bits from the family stream,
set bit `d` and bit zero, and return that polynomial. This samples the input
directly, **not factors or a planted solution**.

Certificate:

```json
{"factors":["19","19"]}
```

For this small example, the input is decimal `261`, i.e. `(x⁴+x+1)² = x⁸+x²+1`.
Factors may appear in any order, and repeated factors repeat in the list.
`{"factors":["261"]}` has the right product but fails irreducibility; replacing
one `19` with `17` fails the product check. This is not integer prime factorization.

Solvability follows from unique factorization in the Euclidean domain `F₂[x]`.
Every sampled nonconstant monic polynomial has an irreducible factorization,
including nonsquarefree polynomials. There is no unbounded resampling and no chance
of an unsatisfiable instance. At most `d` factors, each at most `d+1` bits, suffice.

Verification first checks degree sum and multiplies every factor by carryless
polynomial multiplication. The product must equal `f` exactly. Each distinct
factor `g` of degree `m` is independently checked using the Rabin criterion:

* `x^(2^m) = x mod g`;
* for every distinct prime divisor `q` of `m`,
  `gcd(g, x^(2^(m/q)) - x) = 1`.

Repeated squaring in the quotient ring and Euclid's polynomial GCD compute these
conditions with bounded integers; subtraction is XOR. These conditions certify
irreducibility, so product equality establishes a **complete** decomposition,
not merely some factors. The degree-one cases are handled by the same criterion.
See [CMU's finite-field lecture notes](https://www.cs.cmu.edu/~cdm/pdf/41-ffields.pdf)
and [Rabin's original report](https://dspace.mit.edu/entities/publication/0c9f4e53-8b19-4a3c-8d9e-0a53238d2eb3)
for the underlying finite-field algorithms.

Supported degrees: 8–256; production minimum 128, default 192. Factors have no
more than 257 bits, certificate length at most 24000 bytes. Naive bit operations
are polynomially bounded; checking distinct factors never needs to discover a
factor. A 2-second shared deadline is checked within repeated squaring loops.
This is a cooperative wall-time bound plus fixed operation-size bounds, not a
hard real-time operating-system guarantee.

Limitations: some sampled polynomials are already irreducible or have easy
factors. An irreducible input admits the single-factor certificate `[f]` after
checking it. Difficulty varies, and another paid-for valid PoW can obtain a new
instance. The public reference Berlekamp solver solves the mathematical input;
there is no claim of cryptographic hardness. The generator does not know or
directly output a factorization.

## Family 2: `assignment-dual-v1`

Problem: a complete bipartite graph with `n` vertices on each side has a sampled
nonnegative integer cost matrix `C`, with each entry in `[0, 2^b-1]`. Find a
minimum-cost perfect matching and certify global optimality. Each matrix entry
is sampled independently from `b` stream bits, in row-major order. Neither a
matching nor dual potentials are sampled beforehand.

Certificate:

```json
{"permutation":["1","0"],"u":["7","7"],"v":["0","0"]}
```

For the 2×2 matrix with all costs seven, this and permutation `["0","1"]`
are both valid; adding an integer `k` to all `u` and subtracting it from all `v`
also gives another valid certificate inside the bounds. Every matched edge must
be tight and **all** matrix inequalities must hold, not just the chosen edges.

The verifier checks:

1. `permutation` is a permutation `π` of `0,…,n-1`;
2. `u_i + v_j <= C_ij` for every pair `(i,j)`;
3. `u_i + v_π(i) = C_i,π(i)` for every `i`.

For any perfect matching `σ`, summing the inequalities gives
`Σ C_i,σ(i) >= Σ u_i + Σ v_j`. Tightness makes `π` achieve that bound, proving
optimality. Completeness of the graph guarantees a perfect matching; finiteness
guarantees an optimum. The bipartite assignment LP is integral, and integer-cost
Hungarian primal–dual algorithms produce integer optimal potentials. Potentials
can be normalized within `[-2n2^b, 2n2^b]`, which exceeds the conventional Hungarian
algorithm's bounded potential updates for nonnegative costs. Thus the certificate
size restriction does not remove all solutions. This is a global combinatorial
optimization certificate, not a sum-of-a-row arithmetic exercise. Background:
[Goemans, MIT notes on bipartite matching](https://math.mit.edu/~goemans/18433S07/matching-notes.pdf).

Supported `n`: 2–128 (production minimum 64, default 96); `b`: 4–30 (production
minimum 20, default 30). The three vectors have exactly `n` canonical integer
strings, potentials bounded as above. Verification has `n²` simple inequalities
and `n` equalities, with a deadline check on each row. A repeated column, malformed
integer, infeasible dual or nontight matching is rejected. JSON extras such as a
claimed objective value are unnecessary and forbidden.

Limitations: the Hungarian algorithm runs in polynomial time; mature libraries
and the public reference implementation solve these instances quickly. A large
matrix alone is not evidence of Agent capability. The barrier is providing the
mathematically correct finite object and certificate for this PoW-bound instance.

## Reference solvers, testing and measured costs

`examples/reference_solvers.py` contains a Berlekamp implementation (including
repeated-factor handling) and an integer Hungarian implementation. They are
used explicitly by the development demo/tests and the optional performance
experiment, never imported by `protocol.py`, `poa.py`, `automation.py` or the
formal CLI commands. Production `questions` outputs a problem; `pack` reads
answers supplied by the participant. Publishing these algorithms is deliberate
and prevents making an unsupported claim that only an Agent could solve the gate.

Tests exhaust the 128 monic odd degree-eight inputs and independently check
irreducibility by trial division; compare a small assignment optimum with all
permutations; exercise repeated factors up to degree 256; test 24 deterministic
seed pairs; accept multiple certificates; reject forged certificates, missing
answers, oversized answers, parameters and expired verification budgets. CI uses
small instances and precomputed production verification fixtures where available,
not five-minute mining or large production solving.

An actual local experiment on **AMD Ryzen 7 8845H**, WSL2, Python 3.12.3, one
thread, five fixed public seeds and uncontrolled background load measured:

| Default production family | Median reference solve | Median independent verify |
| --- | ---: | ---: |
| GF(2), degree 192 | 13.772 ms | 2.143 ms |
| Assignment, 96×96, 30-bit costs | 9.781 ms | 2.949 ms |

Sampling both problems took a median 3.526 ms. These are observations, not SLAs
or a hardware-independent lower bound. The raw nanosecond samples, machine and
conditions are in `docs/measurements/local-poa.json`; rerun with:

```bash
python examples/measure_poa.py --profile production --samples 5 --out .work/poa-costs.json
```

These short solver times are an explicit limitation: v1 does **not** deliver a
validated strong Agent discriminator, and does not claim that an optimized solver
will find verification dramatically cheaper for every instance. The measured
reference algorithms show an advantage on these samples, while irreducible inputs
can make solving and verification similar. A scientifically defensible stronger
gate would need empirical task/solver evaluation and new versioned families;
silently changing v1 semantics is forbidden. The implemented mathematical checks
remain mandatory for every accepted submission.
