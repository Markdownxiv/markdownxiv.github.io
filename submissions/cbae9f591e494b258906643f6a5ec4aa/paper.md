# Equitable Quotients and Two-Root Refinement in Doubly Regular Tournaments

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

We study equitable vertex partitions of doubly regular tournaments after two vertices are individualized. The signed quotient matrix satisfies a weighted skew-symmetry identity and a rank-one quadratic identity, which impose arithmetic restrictions on cell sizes. We classify the possible seven-cell quotient matrices by pairwise coprime positive odd integers α, β, γ satisfying α(β+γ)=βγ+1. A seven-cell rooted quotient without an extreme triple through its roots requires at least 143 vertices. We also prove that every doubly regular tournament with more than seven vertices has a pair of individualized vertices whose stable ordinary color refinement has at least nine cells. The argument combines the quotient classification, vanishing first and third moments of triple correlations, and connectivity of arcs through directed triangles. We give complete proofs and describe finite exact checks. These are structural results for restricted refinement configurations; they do not establish a polynomial-time algorithm for general tournament isomorphism, and no priority claim is made relative to the full association-scheme literature.

## 1. Definitions and main results

A tournament has exactly one directed edge between every pair of distinct vertices. It is doubly regular if it has n=4ℓ+3 vertices, every vertex has 2ℓ+1 out-neighbors, and every pair has ℓ common out-neighbors. Let A be its adjacency matrix and let S=A−Aᵀ. Then

$$S\mathbf1=0,\qquad S^\top=-S,\qquad S^2=J-nI. \tag{1}$$

Here J is the all-ones matrix. These familiar rank-three identities are also used in the association-scheme treatment of doubly regular tournaments; see Herman [1].

A partition into nonempty cells F_1,…,F_f is equitable if the number of out-neighbors in F_j is constant on F_i, for every i,j. Ordinary directed color refinement repeatedly separates vertices with different out-neighbor counts into the current cells. When started with two distinct singleton colors and one color for all remaining vertices, it stabilizes at an equitable partition. Stable two-dimensional Weisfeiler–Leman refinement induces a vertex partition at least as fine.

Our first result classifies a smallest exceptional possibility: a rooted equitable partition with exactly seven cells. It is a classification of quotient matrices satisfying the stated equations and integer conditions. It is not a realization theorem for tournaments.

**Theorem 1.** Suppose a doubly regular tournament of order n=4ℓ+3≥7 has an equitable partition into seven cells, with two vertices a→b as singleton cells. Then ℓ is odd. After naming the other cells as below and orienting the last two by a sign convention, there are pairwise coprime positive odd integers α,β,γ with

$$\ell=\beta\gamma,\qquad |X|=\alpha\gamma,\qquad |Y|=\alpha\beta,$$

$$\alpha(\beta+\gamma)=\beta\gamma+1. \tag{2}$$

The signed quotient is uniquely determined by these parameters. If the root pair belongs to no triple with correlation of absolute value n−3, then α>1 and n≥143.

**Theorem 2.** Every doubly regular tournament of order n>7 has two vertices whose individualization followed by ordinary color refinement produces at least nine cells.

The lower bound in Theorem 2 is constant. In particular it gives no bound of the form n^δ and does not close an isomorphism recursion.

## 2. Arithmetic constraints on equitable quotients

Put n_i=|F_i| and D=diag(n_1,…,n_f). Equitability makes the signed quotient

$$R_{ij}=\sum_{y\in F_j}S_{xy}\quad(x\in F_i)$$

well-defined. Each induced tournament on a cell is regular, so every n_i is odd and R_{ii}=0. For i≠j, R_{ij} is a sum of an odd number of signs and is therefore a nonzero odd integer. Restricting (1) to vectors constant on cells gives

$$R\mathbf1=0,\qquad DR=-R^\top D,\qquad R^2=\mathbf1d^\top-nI,\quad d=(n_i)_i. \tag{3}$$

For g_{ij}=gcd(n_i,n_j), weighted skew-symmetry implies

$$R_{ij}=\frac{n_j}{g_{ij}}s_{ij},\qquad R_{ji}=-\frac{n_i}{g_{ij}}s_{ij}, \tag{4}$$

where s_{ij} is a nonzero odd integer. Set Q=D^{1/2}RD^{-1/2} and w=(√n_i)_i. Then

$$Q^\top=-Q,\qquad Q^2=ww^\top-nI.$$

Comparing diagonal entries of QQᵀ yields

$$\sum_{j\ne i}\frac{n_i n_j}{g_{ij}^2}\le\sum_{j\ne i}Q_{ij}^2=n-n_i. \tag{5}$$

For example, if there are c singleton cells, every other cell satisfies (c+1)n_i≤n.

There is also a square constraint. The kernel of Q is spanned by w, and its other eigenvalues are ±i√n. Consequently f is odd. For f≥3, deleting row and column i gives a principal minor of Q equal to n^{(f−3)/2}n_i. The corresponding principal minor of the integer skew-symmetric matrix DR is

$$n^{(f-3)/2}\prod_{j=1}^f n_j. \tag{6}$$

An even-order integer skew-symmetric determinant is the square of its integer Pfaffian. Thus (6) must be a perfect square. These necessary conditions use equitability alone; no coherent-configuration hypothesis is required.

## 3. The seven-cell case

Fix a→b. The four adjacency-pattern classes outside the roots have sizes

| Cell | Directions | Size |
|---|---|---:|
| O | a→x and b→x | ℓ |
| M | a→x→b | ℓ |
| I | x→a and x→b | ℓ |
| C | b→x→a | ℓ+1 |

Every equitable partition retaining the root singletons refines these sets. Because all cells have odd size, an even ℓ forces at least two cells in each of O,M,I and at least one in C, giving at least nine cells in total. For odd ℓ the corresponding minimum is seven: O,M,I stay whole and C splits as X∪Y, with positive odd sizes u,v satisfying u+v=ℓ+1.

Order the seven cells as a,b,O,M,I,X,Y. The root rows are

$$R_{a,*}=(0,1,\ell,\ell,-\ell,-u,-v),$$

$$R_{b,*}=(-1,0,\ell,-\ell,-\ell,u,v).$$

Weighted skew-symmetry determines the first two columns. The remaining block is forced to have the form

$$
\begin{array}{c|rrrrr}
 &O&M&I&X&Y\\\hline
O&0&1&1&H/\ell&-H/\ell\\
M&-1&0&1&-H/\ell&H/\ell\\
I&-1&-1&0&H/\ell&-H/\ell\\
X&-H/u&H/u&-H/u&0&H/u\\
Y&H/v&-H/v&H/v&-H/v&0
\end{array},\qquad H^2=\ell uv. \tag{7}
$$

Here is an algebraic derivation that also establishes uniqueness. Introduce the ten flows n_iR_{ij} for unordered pairs of nonroot cells. The five nonroot row-sum equations and the ten equations (R²)_{a,j}=(R²)_{b,j}=n_j form a linear system with constant coefficients. In the pair order OM,OI,OX,OY,MI,MX,MY,IX,IY,XY, eliminating its variables gives

$$ (\ell,\ell,H,-H,\ell,-H,H,H,-H,H). \tag{8}$$

For a direct check of uniqueness, the coefficient system has rank nine, with a constant nine-by-nine minor of determinant −32; equivalently, its homogeneous solution is the scalar multiple of (0,0,1,−1,0,−1,1,1,−1,1). The row equations remain valid for every admissible ℓ,u,v, not just generic symbolic choices. The diagonal equation for O then reads

$$-2\ell-2-\frac{H^2(u+v)}{\ell uv}=-3\ell-3,$$

and gives H²=ℓuv. Conversely, substitution into (3) verifies every entry of the quadratic identity. Thus there is no omitted quotient parameter.

Exchange X and Y if needed to make H>0. Define

$$\alpha=H/\ell,\qquad\beta=H/u,\qquad\gamma=H/v.$$

These are positive odd integers. From H²=ℓuv we obtain H=αβγ and then (2). A divisor common to any pair of α,β,γ divides the final equation's constant 1, so they are pairwise coprime. Conversely, parameters satisfying (2) yield the integral signed quotient (7), with the required parity and size bounds. This converse only establishes feasibility of the quotient equations.

For fixed ℓ, all parameters can be enumerated by the ordered factor pairs βγ=ℓ and the test that α=(ℓ+1)/(β+γ) is an odd positive integer. The ordering records the sign convention in Section 4.

## 4. Triple correlations and the first nonextreme parameter

For three distinct vertices define the symmetric correlation

$$\tau(a,b,c)=\sum_z S_{az}S_{bz}S_{cz}.$$

Its absolute value is at most n−3. Call a triple extreme if equality holds. Expanding the indicators of common out-neighbors gives

$$|N^+(a)\cap N^+(b)\cap N^+(c)|=
\begin{cases}
(n-7+\tau(a,b,c))/8,&\text{the triple is transitive},\\
(n-3+\tau(a,b,c))/8,&\text{the triple is cyclic}.
\end{cases} \tag{9}$$

To verify the constants, expand the product of the three factors 1+S_{az}. The three row sums vanish and the three pairwise row inner products are −1. The vertices in the triple contribute a total of 4 in the transitive case and zero in the cyclic case; they must be removed because the diagonal signs are zero rather than −1. This gives (9).

For a seven-cell quotient, common out-neighbors can also be counted as the out-neighbors of c in O. Equations (7) and (9) give

$$\tau(a,b,c)=\begin{cases}
0,&c\in O\cup M\cup I,\\
-4\beta,&c\in X,\\
4\gamma,&c\in Y.
\end{cases} \tag{10}$$

Since n−3=4ℓ and βγ=ℓ, the root pair belongs to an extreme triple exactly when β=ℓ or γ=ℓ, equivalently α=1. In that case (2) becomes (β−1)(γ−1)=0 and one of X,Y is a singleton.

If α>1, then α≥3. Equation (2) implies β,γ>α: for example β(γ−α)=αγ−1>0. The pairwise coprime odd β and γ are distinct, so

$$\ell=\beta\gamma\ge(\alpha+2)(\alpha+4)\ge35.$$

Therefore n≥143. Equality in this arithmetic bound has parameters (3,5,7) or (3,7,5), with cell sizes (1,1,35,35,35,21,15), up to the last exchange. No realization of such a 143-vertex tournament is asserted. If ℓ is an odd prime power, coprimality already forces β=1 or γ=1, so every seven-cell root pair at that order is extreme. This proves Theorem 1.

## 5. First and third moments

**Lemma 3.** In any regular tournament, without assuming double regularity,

$$\sum_{\{a,b,c\}}\tau(a,b,c)=0,\qquad
\sum_{\{a,b,c\}}\tau(a,b,c)^3=0. \tag{11}$$

The sums are over unordered triples of distinct vertices.

**Proof.** First extend τ to ordered triples allowing repetitions. The total first moment is zero by the zero column sums. Expanding the cube and interchanging summations gives

$$\sum_{a,b,c}\tau(a,b,c)^3
=\sum_{x,y,z}\left(\sum_aS_{ax}S_{ay}S_{az}\right)^3
=-\sum_{x,y,z}\tau(x,y,z)^3.$$

Thus the ordered third moment is zero. The last equality uses only skew-symmetry. To remove repeated indices use regularity: τ(a,a,a)=0, while for a≠b,

$$\tau(a,a,b)=S_{ab},\qquad\tau(a,b,b)=-S_{ab}.$$

These repeated-index contributions cancel in both odd moments. Each remaining unordered triple occurs six times, proving (11). □

If all distinct-triple values belong to {0,−s,t}, with s,t>0 and some value nonzero, then s=t. Indeed, on this set the identity z³=(t−s)z²+stz holds. Summing and applying (11) leaves (t−s) times a strictly positive sum of squares.

## 6. Proof of the nine-cell theorem

If ℓ is even, Section 3 proves the result for every root pair. Suppose ℓ is odd and, towards a contradiction, no root pair gives nine cells. Every stable partition is equitable, has an odd number of cells by Section 2, and has at least seven cells. It must therefore have exactly seven.

Attach the ordered parameters (α,β,γ) to each arc. For a directed triangle the correlation in (10) is nonzero. If it is negative, the β parameters of all three arcs coincide; if it is positive, their γ parameters coincide. As βγ=ℓ, either equality determines the entire parameter triple.

All arcs in a doubly regular tournament are connected by chains of directed triangles. To see this, fix x and form a bipartite graph between N⁺(x) and N⁻(x), joining y to z when y→z. Each part has size 2ℓ+1, and double regularity gives degree ℓ+1 at every vertex. Two vertices in the same part have a common neighbor because their degrees sum to more than the other part's size. The bipartite graph is connected, and every one of its edges represents the triangle x→y→z→x. Consequently all arcs incident with x belong to the same triangle-chain component. Doing this at every x connects all arcs of the original tournament.

It follows that all arcs have a common parameter triple. Every distinct-triple correlation is therefore in {0,−4β,4γ}, and nonzero values occur. Lemma 3 implies β=γ. Pairwise coprimality forces β=γ=1; equation (2) then gives α=1 and n=7. This contradicts n>7 and proves Theorem 2. □

An equivalent final check is to sum (10) cubed over each arc's third vertex. The sum is

$$64\alpha\beta\gamma(\gamma^2-\beta^2).$$

Every unordered triple is counted three times over arcs, so its total must vanish by (11).

## 7. Finite validation and interpretation

The development implementation uses exact integer signed quotients. Symbolic checks verify the rank-nine flow system, the determinant −32 minor, and all 49 entries of (3) after the substitution H²=ℓuv. A separate parameter enumeration through ℓ≤1001 agrees with the factor-pair description, finding 1,037 ordered feasible quotients, including 36 with α>1. Arithmetic feasibility in this enumeration is not evidence of graph realization.

The recorded catalogue audit covers 765 nonbase doubly regular tournaments through order 27, using McKay's published catalogue [2]. It checks 263,411 unordered root pairs, including 615 seven-cell outcomes. Including supplementary instances, independent triple-correlation comparisons cover 2,674,259 triples, and a separate two-dimensional WL implementation supplies 300 comparisons. These are finite consistency checks, not the proof of Theorem 2. For this manuscript preparation, the symbolic and parameter calculations were rerun, together with all root pairs in Paley tournaments of orders 7, 11, 19, and 23.

The formulas and quotient table above specify the mathematical calculations independently of the larger development files. Those full files and catalogue certificates are not deposited within this manuscript version. No claim is made that the catalogue audit establishes a new enumeration of isomorphism classes.

The results exclude one particular small-refinement scenario. They give neither an asymptotically growing lower bound on cell count nor a general polynomial bound on isomorphism search. In particular, multiplying a polynomial root-enumeration cost through logarithmically many constant-factor reductions can still give a quasipolynomial recurrence. The structural and algorithmic questions beyond that boundary remain separate. The novelty of the stated quotient and moment combination has not been established by an exhaustive literature audit.

## AI assistance and license

OpenAI GPT-6 through the Codex client assisted with English manuscript preparation, consistency checks, local validation, and submission. The exact model build is unknown; complete model provenance for earlier working sessions is unavailable. The proofs are handwritten mathematical arguments, not formally verified theorems.

Copyright 2026 Kaiyi Zhang. Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Allen Herman. *The Terwilliger algebras of doubly regular tournaments*. 2024. [Author preprint](https://arxiv.org/abs/2404.11560), [published article](https://doi.org/10.1007/s10801-024-01319-w). Used for background on the signed adjacency identities and the association-scheme setting.
2. Brendan D. McKay. *Digraphs* data catalogue, including doubly regular tournaments. [Author's catalogue](https://users.cecs.anu.edu.au/~bdm/data/digraphs.html). Used for finite input data, not for an infinite-family theorem.
