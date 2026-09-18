# Every Rank-Six Output Projection of the Eight-Bit Inverse Has Differential Uniformity Ten

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

Let I be inversion on the field with 256 elements, extended by I(0)=0. We give a finite exact certificate that every surjective binary linear output projection from eight to six dimensions makes I differentially 10-uniform. Equivalently, for every two-dimensional binary output subspace, the maximum inverse differential count in one of its affine cosets equals ten. The lower bound is certified by eight semilinear subspace orbits covering all 10,795 two-dimensional subspaces; the upper bound follows from the inverse map's differential multiplicities. Consequently, adding to I any function whose image lies in a binary affine subspace of dimension at most two cannot produce an APN function, without any degree or bijectivity assumption. The certificate consists of a field convention, eight orbit representatives, eight directions, and a complete finite verification prescription. The global maximum value ten already appears in work on subspace differential uniformity. The claim isolated here has the stronger quantifier that every two-dimensional output kernel attains that value; priority for this universal statement is not asserted.

## 1. Problem and precise scope

For a function F between binary vector spaces define

$$D_aF(x)=F(x+a)+F(x),\qquad
\delta(F)=\max_{a\ne0,b}\#\{x:D_aF(x)=b\}.$$

A function from an n-dimensional binary space to itself is almost perfect nonlinear, or APN, when δ(F)=2. This paper studies a local obstruction around the inverse function on K=F_256. It does not settle existence of an eight-bit APN permutation and does not exclude modifications with higher-dimensional images.

For a binary subspace W of K, set

$$C_I(W)=\max_{a\in K^*,\ b\in K}\#\{x\in K:D_aI(x)\in b+W\},$$

where I(0)=0 and I(x)=x^{-1} for x≠0.

**Theorem 1.** For every two-dimensional binary linear subspace W of K,

$$C_I(W)=10.$$

**Corollary 2.** Every surjective binary linear map L:K→F_2^6 satisfies

$$\delta(L\circ I)=10.$$

**Corollary 3.** If H:K→K has image contained in an affine binary subspace of dimension at most two, then I+H is not APN. The function H may be arbitrary, and I+H need not be a permutation.

Theorem 1 combines an elementary upper bound with an exhaustive finite orbit certificate. All data needed to repeat the finite part are given below. It is a statement in dimension eight; the proof does not extrapolate a pattern from small dimensions.

## 2. Differential capacity and output projection

Suppose G=I+H with image(H) contained in a linear subspace W. For every a,x,

$$D_aG(x)\in D_aI(x)+W.$$

Therefore each input assigned by D_aI to a coset b+W remains in that coset after modification. If G were APN, at most two inputs could occupy each of its |W| output values, giving the necessary capacity bound

$$\#\{x:D_aI(x)\in b+W\}\le2|W|. \tag{1}$$

For a surjection L with kernel W, the fibers of L are exactly these cosets. Consequently

$$\delta(L\circ I)=C_I(W). \tag{2}$$

If dim W=2, Theorem 1 contradicts the capacity eight in (1). Every subspace of smaller dimension is contained in one of dimension two. If the image of H is contained in c+W, replace H by H+c and observe that a constant output translation leaves all derivatives unchanged. This proves both corollaries once Theorem 1 is established.

A permutation would impose an additional capacity restriction on the zero coset because its nonzero-direction derivatives cannot equal zero. No such restriction is needed here: the obstruction already rules out arbitrary APN functions in the specified modification class.

## 3. Differential support of the inverse

At direction one, the exceptional inputs 0 and 1 both yield D_1I(x)=1. For x outside {0,1},

$$D_1I(x)=\frac{1}{x(x+1)}.$$

Thus a nonzero output y has two nonexceptional preimages exactly when the equation x²+x=1/y is solvable, equivalently when the absolute trace Tr(1/y) vanishes. Put

$$S=\{y\in K^*: \operatorname{Tr}_{K/\mathbb F_2}(1/y)=0\}.$$

The trace-zero space has 128 elements, so |S|=127. As the extension degree is even, Tr(1)=0: output 1 has the two nonexceptional preimages as well as 0 and 1. Hence D_1I has one output of multiplicity four, 126 outputs of multiplicity two, and no other outputs.

For a≠0 the scaling identity is

$$D_aI(at)=a^{-1}D_1I(t). \tag{3}$$

Every derivative has exactly one fourfold output, namely a^{-1}; all other positive multiplicities are two. A two-dimensional coset contains four outputs, so its total differential count is at most

$$4+2+2+2=10. \tag{4}$$

Equality occurs precisely when the coset contains a^{-1} and its four elements all belong to a^{-1}S. In particular, the coset a^{-1}+W has count ten if and only if

$$1+aW\subseteq S. \tag{5}$$

Thus a direction satisfying (5) is a short lower-bound witness for a given W.

## 4. Field convention and the eight witnesses

Represent K as

$$\mathbb F_2[T]/(T^8+T^4+T^3+T+1).$$

Integers 0 through 255 encode the coefficients of 1,T,…,T^7 as their binary digits. Addition is bitwise XOR; multiplication is polynomial multiplication reduced by the displayed modulus, whose binary encoding is 0x11b. Decimal 3 represents T+1 and has multiplicative order 255.

The following table gives all required orbit representatives W=span{1,c}. The last column is the four-element set 1+aW, with the field arithmetic just specified. All its entries are in S.

| c | Semilinear orbit size | Direction a | Set 1+aW |
|---:|---:|---:|---|
| 2 | 2040 | 4 | {1,5,9,13} |
| 6 | 2040 | 9 | {1,8,55,62} |
| 8 | 1020 | 2 | {1,3,17,19} |
| 12 | 510 | 8 | {1,9,97,105} |
| 24 | 2040 | 4 | {1,5,97,101} |
| 32 | 2040 | 8 | {1,9,18,26} |
| 46 | 1020 | 2 | {1,3,93,95} |
| 188 | 85 | 2 | {1,3,96,98} |

Each row may be checked either by the eight-term field trace of 1/y for its four entries, or by directly counting the 256 values of I(x+a)+I(x) in a^{-1}+W. The latter count is ten in every row. These witnesses certify existence of a suitable differential direction; they are not inferred from a search timeout.

## 5. Why the orbit certificate covers every subspace

Consider the transformations

$$W\longmapsto3W,\qquad W\longmapsto W^2=\{w^2:w\in W\}.$$

They generate the scalar-and-Frobenius action because 3 generates K* and Frobenius generates the Galois group. Both preserve C_I(W). For scalar c≠0 this follows from

$$D_{a/c}I(x/c)=cD_aI(x);$$

for Frobenius it follows from

$$D_{a^2}I(x^2)=(D_aI(x))^2.$$

All maps on inputs and outputs in these identities are bijective. Hence a witness for one representative transports to every member of its orbit.

For completeness, here is a finite verification prescription with explicit stopping rules and without relying on a preexisting list of subspaces:

1. Enumerate all pairs of distinct nonzero field elements u,v. Each pair is binary linearly independent. Store the sorted four-element set {0,u,v,u+v}, deduplicating identical sets.
2. From each table representative, take closure under scalar multiplication by 3 and squaring. Maintain a set of visited four-element sets and stop when there is no new set.
3. Check that all visited sets are valid two-dimensional subspaces, that the eight closures are pairwise disjoint, and that their sizes equal the table.
4. Check that their union equals the complete set in step 1. Independently compare the number of sets with the Gaussian binomial coefficient

$${8\brack2}_2=\frac{(256-1)(256-2)}{(4-1)(4-2)}=10795.$$

5. Verify the witness condition (5) for each representative by exact field arithmetic.

Each closure is finite. Because its generators are permutations, closure under their forward applications is closure under the group they generate. The reported orbit sizes sum to 10,795, and the set comparison checks coverage as well as that numerical sum. This prevents an incomplete or overlapping enumeration from being mistaken for a proof.

These operations were rerun for this manuscript using an independent field-arithmetic routine. They produced the eight stated orbit sizes, an exact disjoint union of all 10,795 spaces, and count ten at every displayed witness. The direction-one differential histogram was independently checked to contain one fourfold and 126 twofold outputs. Equation (4), orbit invariance, and these finite checks prove Theorem 1. □

## 6. Consequences and comparison with earlier work

Equation (2) concerns every rank-six linear projection, not an average projection or the best projection found by search. It is invariant under invertible affine changes of input and output: input changes permute derivative directions, while the output linear part permutes two-dimensional kernels. Accordingly, the same universal statement holds for affine equivalents of inversion, including the AES S-box.

Rønjom, Sandrib, and Sunde [1] introduce subspace differential uniformity. Their AES calculation already gives the global maximum ten for the corresponding two-dimensional output-coset statistic. Thus the numerical value ten is not claimed as a discovery. The distinction addressed by this paper is between

$$\max_{\dim W=2}C_I(W)=10$$

and the universal statement

$$\min_{\dim W=2}C_I(W)=\max_{\dim W=2}C_I(W)=10.$$

A maximum alone does not imply the latter. The orbit certificate makes the quantifier explicit. The present comparison is limited to the cited definitions and reported calculation; it is not a proof that this universal statement never appeared elsewhere.

Switching methods and modifications supported in output subspaces have a substantial history, including Edel and Pott [2]. The capacity argument here is a restriction on one specific neighborhood of the inverse function. It does not claim switching as a new method, and it does not transfer automatically to other seeds or to a composition of several modifications whose combined image has higher dimension.

Three-dimensional modifications have capacity sixteen, and their behavior cannot be settled from the two-dimensional witness table. Nor does a capacity test passing imply that compatible derivative assignments come from a single function. Such compatibility is a separate constraint. Statements about larger subspaces or unrestricted eight-bit APN permutations are therefore outside the theorem.

## 7. Reproducibility and limitations

This is a finite computational result with an analytic reduction. The field modulus, the representative table, the closure rules, the exhaustive subspace construction, and the direct differential-count test are all included in the manuscript. An implementation can reproduce them using only binary polynomial arithmetic and finite sets. No randomized numerical calculation, database classification of APN functions, or SAT unsatisfiability claim is required for the theorem.

The publication-time check independently reconstructed the orbit partition and all eight differential witnesses. Earlier development also investigated general graph switching and higher-dimensional search spaces, but those additional results and their large certificate collections are not assertions of this paper. Its scientific claim is exactly Theorem 1 and its projection and modification corollaries.

## AI assistance and license

OpenAI GPT-6 through the Codex client assisted with manuscript preparation, consistency checks, the independent finite verification, and submission. The exact model build is unknown, and complete model provenance for earlier working sessions is unavailable. Finite verification of the certificate is distinct from establishing bibliographic priority.

Copyright 2026 Kaiyi Zhang. Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Sondre Rønjom, Arne Sandrib, and Joakim Sunde. *Subspace differential uniformity*. Cryptography and Communications, 2026. [Published article](https://doi.org/10.1007/s12095-026-00896-w), [authors' computational repository](https://github.com/arnesandrib/subspace_equivalence). See the definition of subspace differential uniformity and the AES calculation.
2. Yves Edel and Alexander Pott. *A new almost perfect nonlinear function which is not quadratic*. Advances in Mathematics of Communications 3(1), 59–81, 2009. [Publisher](https://doi.org/10.3934/amc.2009.3.59), [author manuscript](https://www.yvesedel.de/Papers/switch.pdf). Cited for switching background rather than the universal kernel statement proved here.
