# A Four-Vertex Counterexample to an Attractor-Based Parity-Game Algorithm

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

We give a loop-free, strongly connected parity game on four vertices that contradicts the soundness and minimal-dominion assertions for the attractor construction in version 1 of Attractors Is All You Need: Parity Games In Polynomial Time, arXiv:2511.03752v1. Every play in the game is won by Odd, yet the proposed construction returns the whole game for the Even threshold and the empty set for the relevant Odd threshold. The complete algorithm consequently assigns the wrong winner to all four vertices. The example is insensitive to a natural repair that refreshes an auxiliary reachability set. We trace the fixed-point computations explicitly, identify the incompatibility between the reachability strategies being combined, and distinguish the invalid dominion argument from a correct strong-connectivity property. Recorded exhaustive checks on normalized games with at most three vertices support vertex-minimality for the interpretation implemented here. The counterexample concerns the specified algorithm and version; it gives no general lower bound for solving parity games and makes no claim to the first discovery of an error in that preprint.

## 1. Scope and conventions

The object of this note is Rick van der Heijden's preprint [1], specifically arXiv:2511.03752v1, dated November 4, 2025, Section 3, Theorem 2, Lemma 3, and Algorithm 1. We use its minimum-priority convention: an infinite play is won by the parity of the least priority occurring infinitely often. The example has no self-loops and has at least one outgoing edge at every vertex, so it satisfies the stated arena restrictions without preprocessing.

A positional strategy chooses one outgoing edge at each vertex owned by its player. A region D is closed for player P under such a strategy when its selected edges stay in D and every edge from an opponent-owned vertex of D also stays in D. A P-dominion is a nonempty such region with a strategy winning from all its vertices. All statements below distinguish existential paths from reachability that one player can force against every opponent choice.

The notation in Section 2 restates just the part of [1] needed to check the example. The conclusions are about those formulas. They do not depend on access to an implementation supplied by the preprint's author.

## 2. The construction being tested

Let Attr_P(U) denote the usual P-attractor: the least set containing U that includes a P-owned vertex with some successor already in the set, and an opponent-owned vertex with all successors in the set.

For a priority threshold h, let P be its parity and let

$$U_h=\{v:\rho(v)\le h,\ \rho(v)\equiv h\pmod2\}.$$

The auxiliary set in [1] is, in equivalent notation,

$$B_h=\bigcup_{\substack{0\le k\le h\\k\not\equiv h\pmod2}}
\bigl(\{v:\rho(v)=k\}\cap\operatorname{Attr}_P(U_{k-1})\bigr).$$

Take U_{−1}=∅. For an attractor candidate A define

$$C_h(A)=\operatorname{Attr}_{1-P}\bigl(\{v\in A\setminus(B_h\cup U_h):\rho(v)<h\}\bigr).$$

The descending iteration starts with U⁰=U_h and A⁰=Attr_P(U⁰), and uses

$$U^{r+1}=U^r\setminus\operatorname{Attr}_{1-P}\bigl((V\setminus A^r)\cup C_h(A^r)\bigr),$$

$$A^{r+1}=\operatorname{Attr}_P(U^{r+1}),\qquad A(G,h)=\bigcap_{r\ge0}A^r.$$

The preprint asserts that the resulting region has the threshold player's dominion property, and uses these regions to assign winners. Our counterexample tests both parities of this construction.

## 3. The complete game

The arena has the following four vertices and five edges. The successor column is the full edge specification.

| Vertex | Priority | Owner | Successors |
|---|---:|---|---|
| a | 1 | Odd | b |
| b | 2 | Odd | c |
| c | 3 | Even | a, d |
| d | 4 | Odd | c |

It is strongly connected: a→b→c→a is a directed cycle, and c↔d connects the remaining vertex. There are no self-loops. Both players own vertices, and the only choice is Even's choice at c.

**Proposition 1.** Every infinite play from every vertex is won by Odd.

**Proof.** If a occurs infinitely often, the least infinitely recurring priority is 1. If a occurs only finitely often, then b also occurs only finitely often; eventually the play alternates between c and d, whose least priority is 3. Both outcomes favor Odd. This argument applies even when Even uses a history-dependent strategy. □

**Proposition 2.** The whole arena is the only nonempty Odd-closed set, and hence is an inclusion-minimal and cardinality-minimal Odd-dominion.

**Proof.** At the three Odd-owned vertices the successor is forced. Odd-closure also requires both successors of the Even-owned vertex c to remain in the set. Thus any nonempty Odd-closed set is closed under all graph edges. Strong connectivity makes it the whole arena. Proposition 1 then gives the dominion property. □

## 4. The Odd threshold removes the dominion

Set h=3, so P=Odd. The initial seed is U_3={a,c}. Both remaining vertices lead to c, so A⁰=V.

The only opposite-parity vertex eligible for B_3 is b, of priority 2. It would have to belong to Attr_Odd(U_1)=Attr_Odd({a}). It does not: from b, Even can stay on c→d→c forever. Hence B_3=∅.

The bad set inside C_3(V) is therefore {b}. Its Even-attractor is all of V: Even chooses c→a→b, a has its forced edge to b, and d has its forced edge to c. Thus

$$C_3(V)=V.$$

The first seed update removes both a and c, yielding U¹=∅ and A¹=∅. The iteration remains empty:

$$A(G,3)=\varnothing. \tag{1}$$

By Proposition 2, the game's minimal Odd-dominion is V. Therefore the minimal-dominion inclusion asserted in Lemma 3 of [1] fails on this graph.

The tempting smaller set {c,d} is not an Odd-dominion. Even owns c and can leave it through c→a. The existence of a play staying on the short cycle does not establish a trap for Even's choices.

## 5. The Even threshold accepts the losing arena

Set h=4, so P=Even. Now U_4={b,d}. Even can choose c→d, and a leads to b; consequently A⁰=V again.

Priority 1 contributes nothing to B_4 because there is no priority-zero seed. Vertex c, of priority 3, does belong to Attr_Even(U_2)=Attr_Even({b}), using c→a→b. Thus

$$B_4=\{c\}.$$

The remaining bad set is {a}. Its Odd-attractor is exactly {a}: Even can avoid a at c by choosing d, so neither c nor the forced predecessors b,d can be added. It follows that

$$C_4(V)=\{a\}.$$

Neither seed b nor d is removed. Therefore U¹=U⁰, A¹=V, and the fixed point is

$$A(G,4)=V. \tag{2}$$

Every vertex of V is won by Odd, so (2) contradicts the Even-dominion assertion of Theorem 2 in [1]. In this branch the seeds never change. Recomputing B_4 against the surviving seeds produces the same result, so simply refreshing the auxiliary reachability information does not repair the example.

The two reachability statements use incompatible decisions at c. Reaching b uses c→a, which visits the lower odd priority. Avoiding a uses c→d, which permits the losing cycle with priorities 3 and 4. Their individual existential guarantees do not imply one winning strategy satisfying both requirements.

## 6. Consequence for the complete algorithm

With maximum priority 4, Algorithm 1 of [1] first tests the opposite-parity maximum 3. Equation (1) gives no region. It then tests threshold 4, where (2) returns all vertices and labels them Even-winning. The correct winner partition is instead

$$W_{\mathrm{Even}}=\varnothing,\qquad W_{\mathrm{Odd}}=\{a,b,c,d\}.$$

Thus the counterexample concerns the final solver, not merely an intermediate candidate region. Both parity classes occur; no convention for a missing priority class is involved. No vertex deletion precedes the incorrect assignment, and the graph already satisfies the no-self-loop restriction.

## 7. A valid structural statement nearby

The failed argument should not be confused with the following standard and directly provable observation.

**Lemma 3.** Let D be an inclusion-minimal P-dominion. Fix any positional strategy σ that is closed and winning on D. Retain σ's edges at P-vertices and every opponent edge, obtaining a directed graph H on D. Then H is strongly connected.

**Proof.** A bottom strongly connected component B of H is nonempty. Its P-vertices retain their chosen successor inside B and all outgoing edges from opponent vertices stay in B. The restricted strategy remains winning there. Thus B is a P-dominion contained in D, and minimality gives B=D. □

Strong connectivity in this fixed-strategy graph is an existential path property. It does not say that P can force a visit to every particular vertex, and it does not justify combining separately chosen reachability strategies.

A useful independent certificate of this distinction can be stated without the challenged attractor operator. For each priority q unfavorable to P, assign a nonnegative rank r_q on D. Require, for every retained edge v→w with both priorities at least q,

$$r_q(v)\ge r_q(w)+\mathbf1[\rho(v)=q]. \tag{3}$$

All coordinates must refer to the same σ. Such ranks exist exactly when σ wins on D, and they can be bounded by the number of q-priority vertices. For soundness, sum (3) around a cycle whose least priority is q; at least one strict descent gives a contradiction. For completeness, in the subgraph on priorities at least q assign edge weight one when the source has priority q, and zero otherwise. A winning σ has no positive-weight cycle. The maximum accumulated weight of a finite walk from v defines r_q(v), and it is at most the number of q-priority vertices because repeating one would give a positive closed walk. This proves the stated rank bound and (3).

These ranks certify a supplied common strategy. Their polynomial encoding length does not yield a polynomial-time method for finding that strategy. They are included to make the missing quantifier explicit, without asserting novelty over the broader progress-measure literature [2].

## 8. Finite verification and minimality evidence

The four-vertex computation was checked in three ways: explicit enumeration of the players' positional strategies and eventual cycles, a Zielonka-style recursive oracle, and a fixed-strategy threshold-cycle certificate check. The tested candidate implementation is a literal interpretation of the published formulas, not code attributed to the preprint's author. A separate local variant refreshes the auxiliary reachability set. Both implementations give the erroneous all-Even assignment on this example. The trace was rerun during preparation of this manuscript.

The recorded small-game audit also compares the oracles on 576 two-vertex games and checks the candidate constructions on 3,912 normalized loop-free games: 24 with two vertices and 3,888 with three. It records 18,224 attractor checks without an error in those smaller cases. Priorities are normalized by their order, equality pattern, and parity, using minimum priority zero or one and consecutive increments zero, one, or two. This reduction preserves the predicates used in the tested formulas. The finite audit therefore supports vertex-minimality for that interpretation. The direct four-vertex disproof does not depend on the minimality claim.

A further recorded seven-vertex example has branching for both players and both parities of cycles, but it is not needed for the result here. We do not claim that four vertices is minimal under those additional restrictions.

The full four-vertex graph, every attractor set needed for its trace, and the winning argument are printed in this note. Readers can verify the disproof without the development implementation or the larger audit files. The complete historical audit files are not deposited within this manuscript version.

## 9. Interpretation

Equations (1) and (2) establish errors in the indicated assertions of the specified preprint version. They do not establish a superpolynomial lower bound for parity games, invalidate other attractor-based partial solvers, or rule out stronger repairs retaining compatible strategy information. No first-discovery claim is made. The example is presented as a compact, independently checkable correction to the public algorithmic claim.

## AI assistance and license

OpenAI GPT-6 through the Codex client assisted with English manuscript preparation, formula comparison, local replay, and submission. The exact model build is unknown, and complete model provenance for earlier working sessions is unavailable. The finite checks and mathematical arguments have not been represented as independent human peer review.

Copyright 2026 Kaiyi Zhang. Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Rick van der Heijden. *Attractors Is All You Need: Parity Games In Polynomial Time*. arXiv:2511.03752v1, November 4, 2025. [Version-specific text](https://arxiv.org/html/2511.03752v1), [record](https://arxiv.org/abs/2511.03752v1). The counterexample addresses this version's Section 3 definitions and statements.
2. Marcin Jurdziński and Ranko Lazić. *Succinct progress measures for solving parity games*. 2017. [Author preprint](https://arxiv.org/abs/1702.05051). Cited for the broader context of strategy-compatible ranking certificates, not as the source of the particular counterexample.
