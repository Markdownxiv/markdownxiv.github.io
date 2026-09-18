# A Python Reference Implementation of Babai's Graph Isomorphism Framework

**Zhang Kaiyi**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

We describe a pure-Python reference implementation of Babai's graph and string isomorphism framework, together with its representation invariants, a handwritten complexity audit, and independent finite validation. The graph interface returns a representative isomorphism and generators for the full isomorphism coset. The implementation tracks nonfaithful action kernels, uniform subset models, transported noncanonical choices, and the corrected primitive-right branch of Split-or-Johnson. We explain how these choices enter a conservative phase recurrence giving exp(O((log n)^5)) for graphs on n vertices under the cited structural lemmas and stated input-cost assumptions. The exponent is an implementation accounting bound, not an improvement over the published quasipolynomial result. Validation includes 98 unit tests, complete small-graph automorphism counts, rejection of matched nonisomorphic atlas pairs, independent full-coset comparisons, and choice replay. The large-parameter certificate-aggregation regime has not been exercised end to end at its unmodified threshold, so finite tests must not be read as an empirical certification of the asymptotic theorem. The source is publicly available at a pinned revision.

## 1. Purpose, attribution, and artifact

The algorithmic framework and its quasipolynomial breakthrough are due to Babai [1]. This work contributes a reference implementation, an explicit account of how its state representations preserve all isomorphisms, and a ledger connecting implementation choices to the complexity argument. The exposition and correction in [2,3] are mathematical dependencies. The paper does not claim a new general graph-isomorphism upper bound, a practical performance record, or first implementation priority.

The scope of the graph interface is finite simple undirected graphs. The more general string interface accepts an explicitly generated permutation group acting on positions. Its answer is the full set of allowed isomorphisms in a compact coset representation, including the empty case. This makes completeness of returned generators as important as checking an individual witness.

The pinned public artifact is [kzoacn/graph-isomorphism, revision 902843f0e820f3e1fffbcfccf07ba8b1d6da1e99](https://github.com/kzoacn/graph-isomorphism/tree/902843f0e820f3e1fffbcfccf07ba8b1d6da1e99). Python 3.11 or newer and the standard library suffice at runtime. NetworkX, SymPy, and pytest are used for independent validation. Large constants and slow research implementations are expected; there is no measured claim of practical scalability.

The documentation and validation records identify the algorithm source by the combined filename-and-content SHA-256 digest `15c0f489ea85a549ae7373d3098a91ba582a5ba00aaa03ababd22458476ae986`. The digest convention is implemented in the artifact's `scripts/verify_atlas.py`. The sections below consolidate that artifact's implementation and complexity notes. Results inherited from Babai's framework remain attributed to their mathematical sources.

## 2. Computational interface and invariants

### Scope and Entry Points

The default entry point, `graph_isomorphisms`, handles general finite simple
undirected graphs and returns the full isomorphism coset. The general string
isomorphism entry point is `BabaiSolver.solve`, which proceeds from Luks reductions
to the complete subset-model recursion.

The implementation follows the orbital-configuration route in Section 13 of
Babai's paper to reduce non-giant image groups, avoiding a dependency on an
unimplemented Cameron group recognizer. Local certificates use the paper's
Unaffected Stabilizer Theorem, and the combinatorial recursion incorporates the
2017 correction. See Section 3 for the worst-case analysis
and the more generous thresholds used in this implementation.

### Key Invariants

#### Permutations and Cosets

`compose(p, q)[v] = q[p[v]]`. String isomorphisms satisfy `x[v] == y[g[v]]`.
`Coset(H, r)` denotes `{compose(h, r): h in H}`.

The window chain rule uses `y[r[v]]` as the aligned target. It first solves the
restricted action, then takes the homomorphism preimage to restore the full
domain and retain the kernel. `merge_isomorphism_cosets` requires that the union
of branches is known to be an isomorphism coset. `coset_hull` explicitly constructs
the smallest containing coset and is used for the generator fibers in TopAction;
the union of those fibers need not itself be a coset.

#### Group Operations

Schreier-Sims constructs a deterministic stabilizer chain without enumerating the
entire group. The group order is the product of the basic orbit sizes, and
membership is tested by sifting. Group objects are immutable so that changing
generators cannot leave a stale stabilizer chain in use.

Homomorphisms use the joint action of the original and image representations,
checking that the generator images respect the group relations. Stabilizer chains
of the joint group provide kernels and constructive lifts. `preimage(H)` accepts
only a subgroup of the image; it does not hide a general subgroup-intersection
operation. Every enumeration of group elements or cosets requires an explicit bound.

#### Block Systems and Subset Models

`BlockTower` retains existing block systems. New Luks block systems must coarsen
the existing tower, and the whole tower is restricted when descending to a window.
A fresh initial tower is created for a new representation only when complete
constant fibers are compressed and the actual degree decreases by at least half.

`subset_action` verifies that the actual domain consists of uniform fibers over
all `t`-subsets of the ideal domain:

- Each actual point has a nonempty proper support subset. Complements are taken
  when necessary to ensure `t <= m/2`.
- Every `t`-subset occurs, with the same fiber size.
- The support map commutes with every group generator and its image.

This model does not require the current group to be transitive or its image to be
giant. After a structural reduction, the new support is the set of blocks touched
or the union of Johnson subsets. The actual domain is partitioned by support size.
Each new model is checked again for completeness, uniformity, and equivariance.
`descend_action` checks that the ideal action factors through the restriction to
the actual window.

#### Configurations and Noncanonical Choices

F2 retains equality patterns and all coordinate maps, including noninjective maps.
Higher-arity WL uses the joint color distribution for replacements at the same
point in every coordinate. Signatures are compared by their complete values;
hash collisions do not change equality decisions.

Local relations use shared color meanings. Every noncanonical choice in the
Design Lemma and Split-or-Johnson is recorded in `Choice`. The main recursion
enumerates its possible images and replays the choices on the target structure.
The corresponding point-mapping constraints are explicitly enforced after
structural alignment. Binary WL after individualization only prunes this already
bounded choice family; it introduces no new branches.

Orbital color integers from different certificate groups do not automatically
have shared meanings. `_nongiant_certificate_orbit` fixes one source orbital
relation and compares it with every possible target orbital relation.

#### Johnson and Split-or-Johnson

Johnson recognition reconstructs the underlying set and then verifies every pair
color; intersection numbers alone are insufficient. For a complete uniform
hypergraph with `m = 2k`, complementary pairs give blocks of size two.

The corrected coherent primitive-right branch produces a single recursive
instance whose right side is at most half as large. Other combinatorial steps
that introduce noncanonical choices also shrink the right side by a constant
factor. Only canonical steps that add no choices may decrease it by just one
point. The enlarged small-right threshold and its index cost are included in
the complexity analysis.

#### Local Certificates and TopAction

The default locality parameter is `max(9, N.bit_length() + 2)`, satisfying the
strict Unaffected Stabilizer threshold. Certificate aggregation is used only when
`10*k < m`; other cases fall under enumeration of a small ideal action. General
local updates recurse on windows of size at most `floor(N/k)`. Natural symmetric
and alternating actions can be solved directly in polynomial time.

A full certificate fixes the complement of its window. Its generators are checked
to be global string automorphisms, and its image must contain the alternating
group on the test set. Certificate comparison replays both windows together and
can impose an ordered test-tuple constraint. Local-guide colors are equivalence
classes of local isomorphisms across the two inputs.

TopAction checks that image-group generators lift to actual isomorphisms. Failure
to lift a generator establishes only a failure of surjectivity, not nonisomorphism.
The source automorphism projection must first be verified to contain the
alternating group before a subsequent failure can establish nonisomorphism.

### Main Recursion Branches

| Branch | Progress or result |
| --- | --- |
| Natural `S_m` / `A_m` action | Solve by color classes and handle parity |
| Intransitive Luks action | Apply the window chain rule without increasing total subdomain size |
| Small quotient or ideal domain | Enumerate a bounded image group; kernel orbits strictly reduce the actual domain |
| Constant fibers | At least halve the actual domain and retain the full kernel in the preimage |
| Intransitive ideal action | Color by orbits; descent to a large orbit introduces no exponential branching |
| Imprimitive ideal action | The block action at least halves the ideal domain |
| Non-giant, doubly transitive action | Individualize within the Wielandt bound, then reduce an action that is no longer doubly transitive |
| Non-giant, uniprimitive action | Apply Split-or-Johnson to the orbital configuration |
| Orbit partition from full certificates | Align and pull back to actual windows and a smaller block action |
| Large alternating symmetry | Use TopAction and lifting on short windows |
| Large non-giant certificate orbit | Reduce transitivity, match orbital relations, and apply Split-or-Johnson |
| Small support of full certificates | Build non-full local relations, apply joint WL, the Design Lemma, and Split-or-Johnson |

All of these branches are implemented in the default `BabaiSolver`.
`GiantActionRequired` remains only in the standalone `LuksSolver` component to
indicate that its caller has not installed a continuation. The default graph
interface uses `BabaiSolver`.

## 3. Correctness and conservative complexity accounting

Let `N` be the actual string-domain size, `m` the current ideal-domain size,
and `n` the number of vertices in the original graph. The graph reduction uses
unordered vertex pairs, so `N = binom(n,2)`. The graph interface uses `0/1` colors.
The general string API requires hashable symbols with stable equality semantics:
it uses `Counter` and dictionaries. A time bound in the domain size alone assumes
polynomial-size symbols with polynomial-time hashing and equality, and a
polynomial-size input generating set. Otherwise their input size and operation
costs must also be included. The graph reduction satisfies these assumptions.

This analysis accounts for the more generous thresholds used in the code. It does
not claim the optimized exponent of the paper. The group-theoretic and
combinatorial results on which it relies are listed at the end. This is a
handwritten implementation analysis, not a machine-checked proof. The
correctness and complexity review records its audit and test coverage.

### 3.1 The Subset-Action Model

The main recursion maintains a surjection `phi: G -> P <= S_m` and an equivariant map

$$
s:\Omega\longrightarrow\{T\subseteq\Gamma:|T|=t\},\qquad1\le t\le m/2.
$$

Each `t`-subset has exactly `b` preimages, so `N = b * binom(m,t)`. The code checks
coverage, uniformity, and equivariance on generators. It does not require `P` to
be giant or `G` to act transitively on `Omega`.

The inequalities `binom(m,t) >= m` and `binom(m,t) >= 2^t` give

$$
m\le N,\qquad t\le\log_2N.
$$

The kernel `ker(phi)` fixes every support subset, so its actual orbits have size
at most `b <= N/m <= N/2`. The action on proper subsets is faithful: an ideal
permutation fixing every `t`-subset also fixes every ideal point. This establishes
that subsequent model actions factor through the corresponding actual windows.

The initial Luks quotient action uses `t=1`. The graph entry point uses unordered
vertex pairs directly, taking complements when needed. Cases with `n<3` are
handled separately by preimages, retaining the kernel of the potentially
nonfaithful action on vertex pairs.

### 3.2 Structural Reductions Preserve the Model

For ideal color classes `C_1,...,C_r`, partition the actual domain by the vector
`(|s(v) intersect C_i|)_i`. Babai's Lemma 5.2.1 states that every window has size
at most `2N/3`, except possibly a single pure window

$$
\Omega(C)=\{v:s(v)\subseteq C\}.
$$

A pure window larger than `2N/3` requires `|C| > 2m/3`. It still consists of
uniform fibers over all `t`-subsets of `C`.

There are two structural reductions on a dominant color class:

- An equipartition: the new ideal points are its blocks, and an actual point's
  support becomes the set of blocks touched by its old support.
- A Johnson embedding: the vertices of the color class are `k`-subsets of a new
  set, and an actual point's support becomes the union of those `k`-subsets.

Partition the actual domain by the new support size `u`. Each size that occurs
covers every `u`-subset with uniform fibers. The full symmetric group on the new
ideal domain induces bijections preserving the entire combinatorial point set
and its counts. This counting argument does not require the current search group
to contain that full symmetric group. The code checks the resulting property
again through `subset_action`.

The new ideal domain is at most half as large as the old one. Blocks of an
equipartition have size at least two. A Johnson embedding satisfies
`|C| = binom(m',k) >= binom(m',2)` and `m'>=5`, giving `m'<=|C|/2`.

For small `m'`, the new image group can be enumerated directly. Write `c=|C|`
and `W=b*binom(c,t)` for the pure-window size. In the partition case, the kernel
fixes every block, so each of its orbits lies in one block-count profile. For
`t<=c/2`, mixed profiles have size at most `2W/3` by Lemma 5.2.1. A profile wholly
inside one of the `m'>=2` equally sized blocks occupies at most
`W*(1/m')^t<=W/2`. If `t>c/2`, the complement bijection inside `C` gives the
same conclusion with `c-t`. In the Johnson case, the kernel fixes every old
Johnson vertex and hence every old support fiber, giving orbit size at most
`b<=W/c`. Here `0<t<c`: dominance and `t<=m/2` imply `t<3c/4`.

These small-parameter calls use the entire pure window before partitioning by
new support size. Fixing this window pointwise fixes every old `t`-subset of
`C`, hence every old vertex of `C`, and therefore the new blocks or Johnson
atoms. This proves that the auxiliary action factors through the window even
when some new union supports are the entire ideal domain. Such supports are
not passed to `subset_action`.

The small-parameter threshold here uses the pure-window size `W=|Omega(C)|`.
If `m' > 10*max(9, floor(log2 W)+3)`, the new support cannot be the entire ideal
domain. Write `c=|C|`. Dominance gives `t<3c/4`; if `t>c/2`, then
`W>=binom(c,t)>=2^(c/4)` and thus `m'<=c<=4 log2 W`, contradicting the threshold.
Consequently, the large-parameter branch has `t<=c/2`, and hence `t<=log2 W`.
The partition case has `u<=t`. In the Johnson case, the threshold also gives
`t<=log2 W<m'/10`, and `c=binom(m',k)>=binom(m',2)` implies
`m'/10<sqrt(c)`. Moreover, `k<=m'/2` gives `c>=2^k`. Consequently,
`log2 W >= t log2(c/t) >= (t/2) log2 c >= tk/2`.
Therefore `u<=tk<=2 log2 W<m'/2`.
The small-image branch covers the remaining small parameters. When needed,
nontrivial supports are complemented to normalize their size to at most half
of the ideal domain.

### 3.3 Each Branch Returns All Isomorphisms

The Luks window chain rule and small-quotient enumeration are exact coset
decompositions. When constant fibers are compressed, the kernel of the block
action is retained in the returned preimage.

In the giant case, isomorphisms of partitions and Johnson structures can be
constructed directly. `align_splits` finds structural isomorphisms and enforces
all selected point correspondences; `preimage_coset` lifts them to the actual
domain. The subsequent chain rule checks all actual coordinates.

The non-giant case uses orbits, blocks, and orbital configurations obtained from
the current group itself. Noncanonical choices are handled by taking their point
stabilizer and enumerating all its cosets. The code checks that this stabilizer
is contained in the structure's automorphism group, avoiding a general subgroup
intersection.

Local certificates provide global automorphisms or evidence of local
non-fullness. Aggregation uses equivalence classes of local isomorphisms across
the two inputs, so every actual global isomorphism preserves these colors. For a
large non-giant certificate orbit, one source relation is compared against every
possible target orbital relation.

In the small-support branch, every test set in the complement of the full
certificate group's support is non-full: a full test would move every point of
that test set in the projected group. The local-guide relation cannot have a
twin class of size at least `k`. Otherwise, for a test set inside that class,
all its ordered tuples would have the same color; the local comparison group
would induce every permutation of the test set, contradicting non-fullness.
Thus the Design Lemma's twin hypothesis holds when `10k<m` and the selected
domain has more than `2m/3` points.

TopAction generates the full coset from isomorphism fibers of image-group
generators. A failed test establishes only a failure of surjectivity. The
alternating automorphism projection is verified first, allowing a subsequent
failure to establish that a target branch is empty.

All possible images of noncanonical choices are covered, so the final union of
branches is exactly `Iso_G(x,y)`. When nonempty, the closure of its coset generators
stays within this isomorphism set and generates the entire coset.

### 3.4 Cost of Individual Subroutines

Every residual generator added by deterministic Schreier-Sims enlarges a basic
orbit, with at most `D(D-1)/2` such enlargements for an action of degree `D`.
Joint actions used for homomorphisms have degree `O(N)`. Group operations take
polynomial time in the degree and the supplied generator-list length, and
output generating sets are compressed to polynomial size. Homomorphisms, kernels,
lifts, and point stabilizers do not enumerate large groups.

F2 and higher-arity WL take `m^O(k)` time. All arities used in the main recursion
are `O(log N)`: they arise from the model's `t`, the locality parameter `k`, or
the design arity in the bipartite reduction. These steps therefore take at most
`N^O(log N)` time.

The small-right threshold in Split-or-Johnson is `64 ceil(log2 L)^2`, where `L`
is the left-side size. This case fixes every right point or fiber, using
`O(log^2 N)` original ideal points. Other steps that incur individualization cost
shrink the right side by a constant factor and fix at most `O(log N)` points each.
The full choice record therefore has length `O(log^2 N)`. Steps that decrease the
right side by only one point are canonical and introduce no additional group index.

The bipartite structure has arity `d<=6 ceil(log_R L)` with `R<L`, so
`R^d<=L^6 R^6<=L^12`. Tuple construction, F2, WL, and twin checks remain polynomial
in `L`.

The enlarged cutoff also supplies the counting hypothesis used to build this
relation. Let `L'<=L` be the retained twin-free left class, `r<=R/2` its
neighborhood size, and `d=min(r,6 ceil(log_R L'))`. The complete hypergraph is
handled separately. If `d=r`, a missing neighborhood distinguishes the tuple
colors. Otherwise put `s=d/2=3 ceil(log_R L')`. If every injective tuple had the
same color, the incidence counts would define a nonempty `d`-design. The
[Ray-Chaudhuri-Wilson inequality as stated in Section 2.6 of the exposition](https://arxiv.org/html/1710.04574#S2.SS6)
would give `L'>=binom(R,s)`. But the active branch has
`R>64 ceil(log2 L)^2`, so `s<=6 log2 L'<sqrt(R)` and

$$
\binom Rs\ge(R/s)^s>R^{s/2}\ge(L')^{3/2}>L'.
$$

This contradiction excludes an all-vertex twin class. A proper large twin
class can cause a canonical reduction by just one right point; it adds no
individualization. The other continuing reductions after a choice shrink the
right side to at most `2R/3` or `R/2`. A choice that immediately returns a
partition is a terminal stage and needs no further size decrease.

All noncanonical matches and computation in one structure-discovery stage are
bounded by

$$
Q(N)=N^{O((\log N)^2)}=\exp(O((\log N)^3)).
$$

Naive coset traversal squares the index cost but stays within the same form of
bound. Binary WL pruning after individualization adds only polynomial work and
no additional choices.

### 3.5 Actual-Domain Descent for Local Certificates and Small Images

The default is `k=max(9, floor(log2 N)+3)`, and aggregation is used only when
`10k<m`. This satisfies the strict threshold of the Unaffected Stabilizer Theorem.
Each general window update enumerates at most `k!` test images and recurses on
kernel orbits. The Affected Orbit Lemma bounds every recursive window by `N/k`.

A certificate expands its window at most `N` times. There are at most `m^k` test
sets and `m^(2k)` pairs of test sets. Including all comparisons, the total number
of recursive calls is still `N^O(log N)`, with subproblems of size at most `N/k`.
Shortcuts for natural symmetric and alternating actions may inspect larger
windows, but solve them directly in polynomial time without invoking difficult
recursion.

The small-image branch satisfies one of the following conditions:

- `m=O(log N)`, allowing enumeration of at most
  `m! = exp(O(log N log log N))` image elements.
- The image-group order is at most `m^(1+ceil(log2 m))`.

The kernel fixes model fibers, so actual subproblems have size at most
`N/m<=N/2`. Small-parameter structural cases with trivial union supports use the
`2/3` window bound from Section 3.2. These conditions are checked at the call sites;
`m!` cannot be used arbitrarily as an enumeration bound for a general large group.

### 3.6 The Combined Recurrence

Fix a phase's starting actual degree `N`, and expand recursive calls until all
remaining actual subproblems have size at most `2N/3`. Actual orbit chains are
additive: their windows are disjoint and their total length does not increase.
Before entering a model they can require polynomially many steps, including
successive descents from degree `q` to `q-1`, with polynomial overhead.

Inside a model, at most one color window, and then at most one union-size
window, can exceed `2N/3`. The code processes windows in decreasing size order.
Consequently, any such continuing window is processed before the subgroup can
be changed by solving a different window. This matters for the transitivity
argument below. Other windows already end the phase.

Each continuing block or Johnson stage at least halves the ideal domain.
An ideal coloring without a dominant class ends the phase by the induced
`2/3` window bound. The step that must be analyzed together with its successor
is individualization in a non-giant
doubly transitive group. The Wielandt bound requires `O(log m)` points. The action
on the remaining large orbit is transitive but no longer doubly transitive, so
the next step is block reduction or Split-or-Johnson on an orbital configuration.
If the parameters are already small, enumeration proceeds through short kernel
orbits. Canonical ideal-orbit descent introduces no matching index. Its image
is transitive after restriction to the selected large orbit; a subsequent
complete-subset window has the same image because the ideal action factors
faithfully through that window. Thus orbit descent cannot repeatedly restart
the costly double-transitivity step without an intervening structural decrease.

On a continuing path there are therefore `O(log N)` charged stages. The calls
that start a fresh Luks problem or compress constant fibers already decrease
the actual degree by a constant factor, apart from natural symmetric or
alternating actions which are solved directly. In particular, the ideal degree
is not reset to a larger value along a continuing path within this phase.

The total multiplier from expanding this part of the model recursion is at most

$$
Q(N)^{O(\log N)}=\exp(O((\log N)^4)).
$$

Certificate construction and unsuccessful TopAction tests may do recursive
work before a structural outcome is known. Their recursive windows already
have size at most `N/k` or a model fiber; the polynomial natural-action
shortcuts require no difficult recursion. Count these calls as additional
leaves of the phase, rather than assuming that every TopAction test terminates
the whole problem.

Including those leaves, bounded image enumeration, and the disjoint short
windows, both the phase overhead and its number of leaves are at most
`A(N)=exp(O((log N)^4))`. For the nondecreasing worst-case envelope `T`, this gives

$$
T(N)\le A(N)\bigl(1+T(\lfloor2N/3\rfloor)\bigr).
$$

outside a fixed finite base range. Iterating through `O(log N)` phases bounds
`log T(N)` by a constant times
`sum_j (log N - j*log(3/2))^4 = O((log N)^5)`, and hence

$$
T(N)\le\exp(O((\log N)^5)).
$$

Purely additive orbit chains, even when an orbit has size `N-1`, add only
polynomial work and sums whose total subdomain length does not increase. They
do not introduce the exponential multiplier above at every level. Polynomial
costs of large integers and complete signatures are absorbed by the bound; the
analysis does not assume collision-free hashing.

Finally, `N=binom(n,2)<=n^2`, so the graph interface still has the bound
`exp(O((log n)^5))`, which is quasipolynomial.

## 4. Finite validation and what it checks

The September 13 development review records the following executed checks against the source digest above. These checks target both soundness and finite-case completeness.

| Check | Recorded result |
|---|---|
| Unit and regression suite | 98 passed |
| NetworkX atlas graphs through six vertices | 209 relabelings and complete automorphism counts passed |
| Nonisomorphic atlas pairs with equal vertex and edge counts | 1,340 correctly rejected |
| Independent subset-model coset oracle | 240 comparisons: 152 nonempty and 88 empty |
| Uniform-hypergraph relabeling and choice replay | 84 passed |

The unit suite was rerun during preparation of this manuscript: all 98 tests passed. The other counts in the table are the preserved development review results; they are not newly claimed large-instance benchmarks.

The coset oracle independently closes a small generator set by breadth-first traversal and compares the entire returned set with the expected set. It does not use the implementation's own membership or enumeration methods for that comparison. Tested actions include symmetric, alternating, cyclic, dihedral, and intransitive groups, subset ranks one through three, balanced supports, and nontrivial fiber kernels. Both solver strategies are checked without changing their thresholds. Separate replay checks lower the small-right cutoff to exercise deeper reductions on tractable inputs; those modified-threshold checks are recorded as such.

The atlas validation compares with NetworkX's graph atlas and VF2. It checks complete automorphism counts as well as witness validity. Equal-vertex and equal-edge negative pairs prevent trivial size tests from explaining the rejection counts. The source and verifier hashes in the public artifact tie each saved record to its implementation. Passing finite cases does not establish the recurrence or the structural lemmas for arbitrary size.

The public artifact supports these reproduction commands:

```bash
python3 -m pip install -e '.[validation]'
python3 -m pytest -q
python3 -m scripts.verify_atlas --max-n 6 --report atlas-report.json
python3 -m scripts.verify_models --report models-report.json
```

Here the two output paths are disposable report destinations. The complete implementation, dependencies, tests, and report schemas are available at the pinned source link in Section 1; they are separate from the Markdown manuscript deposited in the archive.

## 5. Limits of the audit

There has been no end-to-end aggregation run at the unmodified large-parameter condition `10*max(9, N.bit_length()+2)<m`. Some aggregation tests instead use lowered thresholds or directly constructed branch fixtures. Those tests establish behavior on their finite inputs, not the theorem governing the full large-parameter regime.

Checking a returned vertex bijection establishes soundness of that witness. Checking each returned generator establishes that the generated subgroup consists of automorphisms. Neither alone proves that every automorphism was returned or that a negative result is correct. The small independent coset oracles test these stronger properties only on their enumerated inputs. The mathematical completeness argument in Section 3 remains necessary.

The conservative running-time analysis is handwritten and depends on the cited group-theoretic and combinatorial results. It is not a machine-checked proof, and the review was AI-assisted rather than an independent expert review. No sampled recursion trace, threshold-adjusted branch test, or favorable timing has been used as a substitute for a worst-case recurrence.

Specific implementation obligations deserve continued attention: preservation of kernels after representation changes; faithful action factorization through pure windows; replay of every possible image of a noncanonical choice; coherent color meanings across the two inputs; and accounting for unsuccessful TopAction tests. The audit spells out these obligations because omitting them can preserve some valid witnesses while silently losing completeness or the claimed cost bound.

The code is intended for inspection, teaching, and further validation of a complex framework. Practical graph-isomorphism solvers optimize different objectives, and no competitiveness claim against them follows from this implementation's asymptotic accounting. Related earlier implementation work includes [4]; this paper makes no claim to be the first public code associated with Babai's algorithm.

## AI assistance and license

The development repository records OpenAI Codex with GPT-6-Astra as generating and revising the implementation, tests, and analysis. OpenAI GPT-6 through the Codex client assisted with this English manuscript, its consistency checks, the unit-test replay, and submission. Exact model builds are unknown. Automated validation is not independent human peer review or formal verification.

Copyright 2026 Zhang Kaiyi. This manuscript is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/). Software licensing is governed by the separately linked source repository.

## References

1. László Babai. *Graph Isomorphism in Quasipolynomial Time*. [arXiv record](https://arxiv.org/abs/1512.03547), [author version 2.5, November 2018](https://people.cs.uchicago.edu/~laci/quasi25.pdf). Mathematical source for local certificates, affected and unaffected stabilizers, subset-window bounds, and the orbital-configuration route.
2. Harald Andrés Helfgott. *Graph isomorphisms in quasi-polynomial time*. [Corrected exposition](https://arxiv.org/abs/1710.04574). Used for the Design Lemma, Split-or-Johnson, aggregation, and detailed complexity arguments.
3. László Babai. *Graph Isomorphism Update*, 2017. [Author's correction page](https://people.cs.uchicago.edu/~laci/update.html). The corrected primitive-right step is included in the implementation.
4. MadPidgeon. *Babai-Graph-Isomorphism*. Source code accompanying a bachelor's thesis. [Public repository](https://github.com/MadPidgeon/Babai-Graph-Isomorphism). Acknowledged as related implementation work; no equivalence of coverage is asserted.
