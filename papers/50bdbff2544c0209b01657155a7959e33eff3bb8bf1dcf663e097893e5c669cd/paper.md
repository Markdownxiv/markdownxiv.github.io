# The Zero-Minor Problem Is NP-Complete

**Kaiyi Zhang**  
Author homepage: [github.com/kzoacn](https://github.com/kzoacn)  
September 23, 2026

## Abstract

Given a square matrix with binary-encoded rational entries, the zero-minor problem asks whether some nonempty square submatrix has determinant zero. Its row and column sets may be arbitrary and need not coincide. We give a self-contained proof that this decision problem is NP-complete, even when all entries are integers. The reduction encodes a positive-integer Subset Sum instance by distinct nodes with positional markers, uses a modified Vandermonde determinant to recognize a prescribed sum, and converts the resulting rectangular matrix to systematic form. An adjugate construction produces an integer square matrix directly, with polynomially bounded output length. The complementary problem of recognizing totally nonsingular square matrices is therefore coNP-complete. We also describe an exact depth-first search based on bordered-minor identities. After clearing denominators, it uses $O(\binom{2n}{n})$ arithmetic operations and $O(n^3)$ stored integers; all intermediate integers have polynomial bit length. The same bounds hold for finding a zero minor of minimum order. Independent exact computations check small reduction instances, compare the search with exhaustive enumeration, and confirm the operation counts on Cauchy matrices. The complexity result is presented in relation to established hardness results for singular maximal minors and full spark, without a priority claim or a claim of an optimal exponential base.

**Keywords:** zero minor; total nonsingularity; NP-completeness; full spark; Subset Sum; fraction-free elimination.

## 1. Problem and scope

Let $[n]=\{1,\ldots,n\}$. For $I,J\subseteq[n]$ with $|I|=|J|$, let $A[I,J]$ denote the submatrix with the selected rows and columns in increasing index order. Write

$$
\Delta_A(I,J)=\det A[I,J],\qquad
\Delta_A(\varnothing,\varnothing)=1.
$$

The decision problem studied here is

$$
\begin{aligned}
\text{Zero-Minor}_{\mathbb Q}:\quad
&\text{Input: } A\in\mathbb Q^{n\times n},\ n\ge1,\text{ in binary encoding};\\
&\text{Question: does there exist }I,J\subseteq[n]\text{ such that}\\
&\hspace{2em}1\le |I|=|J|\le n\text{ and }\Delta_A(I,J)=0?
\end{aligned}
\tag{1}
$$

Restricting the input entries to integers defines $\text{Zero-Minor}_{\mathbb Z}$. The dimension is part of the input. All statements concern exact zero testing in the usual bit model of computation.

The row and column sets may be nonconsecutive and need not be equal. Both one-by-one minors and the determinant of the whole matrix are allowed. An input without a zero minor is called **totally nonsingular**. For example,

$$
\begin{pmatrix}1&1\\1&2\end{pmatrix}
$$

is totally nonsingular. Conversely, invertibility alone is insufficient: the matrix

$$
A_0=\begin{pmatrix}1&2&3\\2&4&7\\3&5&8\end{pmatrix}
\tag{2}
$$

has determinant $1$, but its upper-left two-by-two minor vanishes. Testing the determinant of one specified matrix is polynomial-time; the existential choice of a submatrix changes the complexity.

**Theorem 1.** Both $\text{Zero-Minor}_{\mathbb Z}$ and $\text{Zero-Minor}_{\mathbb Q}$ are NP-complete under deterministic polynomial-time many-one reductions. Recognizing totally nonsingular square matrices over either input domain is coNP-complete.

**Theorem 2.** After clearing rational denominators, an exact algorithm finds a zero minor or certifies total nonsingularity using

$$
O\!\left(\binom{2n}{n}\right)
=O\!\left(\frac{4^n}{\sqrt n}\right)
\tag{3}
$$

arithmetic operations and $O(n^3)$ stored integers. If the resulting integer entries have absolute value at most $H\ge1$, the stored determinants and the arithmetic temporaries have $O(n(\log H+\log(n+1)))$ bits. A modification finds a minimum-order zero minor with the same worst-case bounds.

These statements distinguish a decision problem, a certificate-producing search problem, and an optimization problem. NP-completeness in Theorem 1 refers to the decision problem. Theorem 2 is an upper bound for the search and optimization problems, with polynomial overhead in input bit length.

### 1.1. Relation to existing work

Chistov, Fournier, Gurvits, and Koiran proved NP-completeness of detecting a zero maximal minor in a rectangular integer matrix, using Vandermonde constructions [2]. Tillmann and Pfetsch state the coNP-completeness of rational full-spark recognition in Corollary 3 [3]. The connection between full-spark systems and totally nonsingular matrices is developed by Arambašić and Bakić [4].

The proof below gives an explicit route from positive-integer Subset Sum to the precise **square-matrix, arbitrary-order** problem in (1). In particular, it constructs an invertible prescribed block and supplies the encoding-length argument needed to normalize that block. We do not claim that the general hardness phenomenon or the Vandermonde technique is new. Similarly, the algorithm uses the classical Sylvester identity underlying Bareiss elimination [5]; the analysis concerns its organization as a depth-first search over increasing row and column prefixes.

## 2. Two equivalent formulations

### 2.1. Systematic form and full spark

For $A\in\mathbb Q^{n\times n}$, define

$$
G=[\,I_n\mid A\,]\in\mathbb Q^{n\times2n}.
$$

An $n$-row matrix is **full spark** when every set of $n$ columns is linearly independent.

**Lemma 3.** The matrix $A$ has a nonempty zero minor if and only if $G$ has a singular $n$-column submatrix.

**Proof.** A choice of $n$ columns of $G$ consists of some columns $J$ from $A$ and some identity columns $K$, where $|J|+|K|=n$. Set $I=[n]\setminus K$. Expanding along the identity columns gives

$$
\det G[:,K\cup(n+J)]=\pm\det A[I,J].
\tag{4}
$$

Every equal-size pair $(I,J)$ arises this way. If $J=\varnothing$, the selected matrix is the identity and its determinant is $1$; hence a singular selection necessarily corresponds to a nonempty minor. This proves both directions. $\square$

In particular, $A$ is totally nonsingular exactly when $[I_n\mid A]$ is full spark. The latter matrix always has full row rank; testing its overall rank does not test full spark.

### 2.2. Joint support size

For a vector $x$, let $\|x\|_0$ denote the number of nonzero coordinates.

**Lemma 4.** For $A\in\mathbb Q^{n\times n}$,

$$
A\in\text{Zero-Minor}_{\mathbb Q}
\quad\Longleftrightarrow\quad
\exists x\in\mathbb Q^n\setminus\{0\}:
\|x\|_0+\|Ax\|_0\le n.
\tag{5}
$$

**Proof.** If $A[I,J]$ is singular of order $k$, extend a nonzero rational null vector by zeros outside $J$. The resulting $x$ satisfies $\|x\|_0\le k$, and $Ax$ vanishes on $I$, so $\|Ax\|_0\le n-k$.

Conversely, put $J=\operatorname{supp}(x)$ and $s=|J|$. Condition (5) implies that $Ax$ has at least $s$ zero coordinates. Choose any $s$ of them as $I$. Then $A[I,J]x_J=0$ with $x_J\ne0$, proving singularity. $\square$

This is also the support condition for the null vector $(-Ax,x)$ of $[I_n\mid A]$.

## 3. NP-completeness

### 3.1. Membership in NP

A certificate consists of the two index sets $I,J$, encoded with $O(n\log(n+1))$ bits. A verifier checks their validity and equal positive size, and tests the selected determinant for zero by exact rational or fraction-free integer elimination. Clearing the denominators in each selected row multiplies its determinant by a nonzero integer and has polynomial encoding length. Determinant computation has polynomial bit complexity, for example by fraction-free elimination and Hadamard bounds [5]. Thus both problems belong to NP.

### 3.2. Encoding Subset Sum with paired nodes

We reduce from positive-integer **Subset Sum**: given $a_1,\ldots,a_m>0$ and $t>0$ in binary, decide whether some subset sums to $t$. This is the standard NP-complete problem [1]. Take $m\ge1$ and define

$$
D=1+\max\left\{2,t,\sum_{i=1}^m a_i\right\},
\qquad
x_i=D^i,\quad x_{m+i}=D^i+a_i\quad(1\le i\le m),
\tag{6}
$$

and

$$
T=\sum_{i=1}^m D^i+t.
\tag{7}
$$

All $2m$ nodes are distinct: the two nodes in a pair differ by $a_i>0$, and they lie in disjoint intervals $[D^i,D^i+D)$ for different $i$.

**Lemma 5.** There exists an $m$-element set $S\subseteq[2m]$ with $\sum_{j\in S}x_j=T$ if and only if the Subset Sum instance is affirmative.

**Proof.** For an arbitrary selection, let $c_i\in\{0,1,2\}$ count the selected nodes in pair $i$, and let $e_i\in\{0,1\}$ indicate whether $D^i+a_i$ is selected. Its sum is

$$
\sum_i c_iD^i+\sum_i e_i a_i.
$$

The final summand lies in $[0,D)$, and every $c_i<D$. There are consequently no carries in this base-$D$ representation. Equality with (7) forces $c_i=1$ for every $i$ and $\sum_i e_i a_i=t$. Conversely, any subset summing to $t$ determines one node from each pair and hence an $m$-element selection with sum $T$. $\square$

### 3.3. A modified Vandermonde matrix

Construct an $m\times2m$ integer matrix $H$ whose rows are

$$
H_{r+1,j}=x_j^r\quad(0\le r\le m-2),
\qquad
H_{m,j}=x_j^m-Tx_j^{m-1}.
\tag{8}
$$

When $m=1$, the first group of rows is empty and $H_{1,j}=x_j-T$; thus the definition also covers this boundary case.

**Lemma 6.** If $S=\{s_1<\cdots<s_m\}\subseteq[2m]$, then

$$
\det H[:,S]
=\prod_{1\le p<q\le m}(x_{s_q}-x_{s_p})
\left(\sum_{j\in S}x_j-T\right).
\tag{9}
$$

**Proof.** Write $\sigma=\sum_{j\in S}x_j$. At every selected node, the identity

$$
\prod_{j\in S}(z-x_j)
=z^m-\sigma z^{m-1}+q(z),\qquad \deg q\le m-2,
$$

gives $x_j^m=\sigma x_j^{m-1}-q(x_j)$. Subtracting the appropriate linear combination of the first $m-1$ rows transforms the last row of $H[:,S]$ into $(\sigma-T)x_j^{m-1}$. Factoring out $\sigma-T$ leaves the ordinary Vandermonde determinant in the selected column order. For $m=1$ the same calculation holds with $q=0$ and the empty product equal to $1$. $\square$

The first factor in (9) is nonzero. Lemmas 5 and 6 therefore show that $H$ has a singular maximal minor exactly when the original Subset Sum instance is affirmative.

### 3.4. Producing a square integer matrix

Partition $H=[B\mid C]$ into its first and last $m$ columns. Since the first $m$ nodes sum to $T-t$, (9) gives

$$
\det B=-t\prod_{1\le p<q\le m}(D^q-D^p)\ne0.
\tag{10}
$$

The prescribed block $B$ is invertible on every input, regardless of its answer. Set

$$
A=B^{-1}C,\qquad
M=\operatorname{adj}(B)C=(\det B)A.
\tag{11}
$$

Left multiplication by $B^{-1}$ preserves which maximal column selections are singular, and

$$
B^{-1}H=[I_m\mid A].
$$

By Lemma 3, $H$ has a singular maximal minor if and only if $A$ has a nonempty zero minor. Finally, for every order $k$,

$$
\det M[I,J]=(\det B)^k\det A[I,J],
\tag{12}
$$

so $M$ has precisely the same zero-minor pattern as $A$. Unlike $A$, the matrix $M$ has integer entries. The reduction outputs $M$.

### 3.5. Polynomial encoding length and running time

Let $L$ be the bit length of the Subset Sum input. Then $m\le L$ and $\log D=O(L)$. The nodes and target have $O(m\log D)$ bits. Each entry of $H$ has

$$
b=O(m^2\log D)
$$

bits. Each entry $M_{ij}$ is, by Cramer's rule, the determinant of $B$ after replacing its $i$th column by the $j$th column of $C$. Hadamard's inequality bounds its bit length by

$$
O\bigl(m(b+\log(m+1))\bigr).
\tag{13}
$$

Consequently all $m^2$ entries of $M$ have total encoding length polynomial in $L$. Integer powers, the entries of $H$, and these $m^2$ determinants can all be computed in polynomial bit time. No unit-cost assumption for unbounded integers is used.

We have proved the deterministic polynomial-time equivalence

$$
(a_1,\ldots,a_m;t)\in\text{Subset-Sum}
\quad\Longleftrightarrow\quad
M\in\text{Zero-Minor}_{\mathbb Z}.
\tag{14}
$$

This proves NP-hardness for integer inputs and hence for rational inputs. Together with membership in NP it proves Theorem 1; taking complements gives the total-nonsingularity statement. $\square$

This reduction establishes ordinary NP-completeness with binary encoding. It does not establish strong NP-completeness, a lower bound of $4^n$, or an impossibility result for a particular smaller exponential base.

## 4. An exact algorithm with shared minor computations

### 4.1. Number of candidates

There are

$$
N_n=\sum_{k=1}^n\binom nk^2=\binom{2n}{n}-1
\tag{15}
$$

nonempty square submatrices. Computing each determinant separately by cubic elimination gives the direct arithmetic bound

$$
O\!\left(\sum_{k=1}^n k^3\binom nk^2\right)
=O(n^3N_n).
$$

The following search shares determinant computations between different candidates.

### 4.2. State invariant and exact extension

A state contains increasing row and column prefixes $I,J$ of equal length, a nonzero determinant $d=\Delta_A(I,J)$, and the increasing lists $R,C$ of indices greater than the last selected row and column, respectively. It stores the rectangular array

$$
D_{rc}=\Delta_A(I\cup\{r\},J\cup\{c\}),
\qquad r\in R,\ c\in C.
\tag{16}
$$

At the root, $I=J=\varnothing$, $d=1$, and $D=A$.

Choose $r\in R,c\in C$, and put $p=D_{rc}$. If $p=0$, this entry already identifies a zero minor of the original input. If $p\ne0$, extend the prefixes by $r,c$. For $u>r,v>c$, Sylvester's bordered-minor identity gives

$$
D'_{uv}
=\frac{D_{rc}D_{uv}-D_{uc}D_{rv}}{d}
=\Delta_A(I\cup\{r,u\},J\cup\{c,v\}).
\tag{17}
$$

This identity underlies fraction-free elimination [5]. One way to prove (17) is to take the Schur complement of the invertible block $A[I,J]$ in the twice-bordered matrix. Each once-bordered determinant is $d$ times a Schur-complement entry, while the twice-bordered determinant is $d$ times its two-by-two determinant. For the empty prefix, (17) is the ordinary two-by-two determinant formula.

The denominator is never zero: the root uses $1$, and every descendant is entered only when its parent pivot $p$ is nonzero. For integer input the division in (17) is exact, because the quotient is an integer determinant.

### 4.3. Depth-first search

In the following pseudocode, appending indices preserves their increasing order.

```text
Search(D, d, R, C, I, J):
    for each a in 0,...,len(R)-1:
        for each b in 0,...,len(C)-1:
            p = D[a,b]
            if p == 0:
                return (I appended with R[a], J appended with C[b])
            if a+1 < len(R) and b+1 < len(C):
                form E on u>a, v>b by
                    E[u,v] = (p*D[u,v] - D[u,b]*D[a,v]) / d
                answer = Search(E, p, R[a+1:], C[b+1:],
                                I appended with R[a],
                                J appended with C[b])
                discard E
                if answer exists:
                    return answer
    return none
```

The initial call is `Search(A, 1, [1,...,n], [1,...,n], [], [])`. Discarding a completed child array before constructing the next one enforces the space bound.

### 4.4. Correctness and arithmetic count

**Lemma 7.** The search returns a valid zero minor if one exists and otherwise returns `none`. It performs $O(N_n)$ arithmetic operations.

**Proof.** The invariant (16) and identity (17) show that every returned zero is a determinant of the original matrix. For completeness, let

$$
I=\{i_1<\cdots<i_k\},\qquad
J=\{j_1<\cdots<j_k\}
$$

be a target pair. Its unique increasing generation path is

$$
(i_1,j_1),\ldots,(i_k,j_k).
$$

If an earlier prefix on this path has zero determinant, the algorithm already has a valid answer. Otherwise the path remains available, and the target is eventually generated and checked. Skipped indices introduce arbitrary gaps, so this is not a restriction to consecutive submatrices.

Each minor of order at least two has exactly one immediate prefix, obtained by deleting its largest row and largest column. Its value is therefore generated at most once by (17), using two multiplications, one subtraction, and one division. First-order minors are the input entries. The number of generated entries, zero tests, and state transitions is $O(N_n)$. On a totally nonsingular input, exactly $N_n$ entries are checked and exactly $N_n-n^2$ higher-order entries are generated. $\square$

The count is an upper bound for this particular algorithm. It is not an assertion that every possible algorithm must inspect all minors.

### 4.5. Storage and bit complexity

At prefix length $t$, the candidate array has at most $(n-t)^2$ entries. Depth-first traversal retains only arrays along the active path. Their total size is at most

$$
\sum_{s=1}^n s^2=\frac{n(n+1)(2n+1)}6=O(n^3).
\tag{18}
$$

The prefixes, loop indices, and recursion records require polynomially fewer additional slots. Implementations must release a completed child before allocating its replacement.

For rational input, multiply each row by the least common multiple of its positive denominators. These factors have polynomial bit length in the original input, and every minor is multiplied by a nonzero factor. Let $H\ge1$ bound the absolute values of the resulting integer entries. Hadamard's inequality gives, for a minor of order $k$,

$$
|\Delta_A(I,J)|\le k^{k/2}H^k.
\tag{19}
$$

Thus every stored determinant has $O(n(\log H+\log(n+1)))$ bits. Products and differences in the numerator of (17) have at most twice this bound plus a constant. Exact division does not introduce fractions. The total bit complexity is consequently

$$
\binom{2n}{n}\operatorname{poly}(n,L_A),
\tag{20}
$$

including polynomial preprocessing, where $L_A$ is the original input bit length. The storage bound in bits is polynomial as well. Arithmetic-operation counts in (3) do not suppress an exponential growth of operand lengths.

### 4.6. Minimum-order zero minors

Maintain the best order $K$, initially $n+1$, and its witness. On encountering a zero of order $k<K$, record it and set $K=k$. Continue other branches, but skip any state that can generate only orders at least $K$. Do not extend through a zero pivot.

A zero pivot of order $k$ cannot lead to an improvement by extension, because every extension has larger order. Furthermore, every proper prefix of a globally minimum-order zero minor is nonzero. Such a path is either visited or pruned only after a witness of no larger order is already known. This proves correctness of minimum-order search. Each candidate is still generated at most once, so the time and space bounds are unchanged. This finishes the proof of Theorem 2. $\square$

The argument does not authorize pruning at a smaller zero pivot when the task asks for a zero minor of **exactly** a specified larger order. A singular smaller submatrix can have a nonsingular extension.

## 5. Useful reductions and boundary cases

### 5.1. Low-order and complementary checks

Scanning for zero entries detects first-order minors in $O(n^2)$ operations. A determinant computation checks order $n$ in $O(n^3)$ arithmetic operations. If all entries are nonzero, then for fixed rows $r<s$,

$$
\det A[\{r,s\},\{p,q\}]=0
\quad\Longleftrightarrow\quad
\frac{a_{rp}}{a_{sp}}=\frac{a_{rq}}{a_{sq}}.
\tag{21}
$$

Sorting these ratios for every row pair gives a deterministic $O(n^3\log n)$ comparison bound for second-order detection. Hashing normalized rational ratios gives an expected $O(n^3)$ dictionary-operation bound under the usual hashing assumptions. Reduction and comparison of large integers contribute additional bit costs.

For invertible $A$, Jacobi's complementary-minor formula [6, Proposition 4.1] states

$$
\det A[I,J]
=(-1)^{\sum_{i\in I}i+\sum_{j\in J}j}
\det A\,\det A^{-1}[J^c,I^c].
\tag{22}
$$

Hence order-$k$ zeros of $A$, for $1\le k<n$, correspond to order-$(n-k)$ zeros of $A^{-1}$. The swapped row and column complements are essential. Checking zero entries and second-order ratio collisions in $A^{-1}$ treats orders $n-1$ and $n-2$ of $A$. For small $n$, only distinct valid orders are retained.

These are optional accelerations for finding an arbitrary zero minor. A large-order witness is only an upper bound on the answer when minimum order is required. Our reference implementation below uses the general search directly, so its verification exercises the recurrence without these accelerations.

### 5.2. Fixed orders and fixed finite fields

For a fixed order $k$, direct enumeration with elimination uses

$$
O\!\left(\binom nk^2k^3\right)
$$

arithmetic operations, polynomial in $n$. For finding a zero minor of order at most $r$, truncating the prefix search gives $O(\sum_{k=1}^r\binom nk^2)$ arithmetic operations.

The rational-field hardness statement also cannot simply be transferred to a fixed finite field. Suppose $A\in\mathbb F_q^{n\times n}$ and $n\ge q$. A zero entry is already a witness. If there is none, fix two rows. Their $n$ column ratios belong to the $q-1$ nonzero field elements, so two are equal. Equation (21) then gives a second-order zero minor. Scanning the entries and finding a ratio collision takes $O(n^2)$ field operations, even by comparing all pairs of ratios. For fixed $q$, the remaining dimensions $n<q$ are bounded.

### 5.3. Exactness and transformations

Ordinary row reduction preserves rank but not the zero-minor pattern of the input: it transforms the totally nonsingular two-by-two example in Section 1 into an identity matrix with zero entries. In contrast, (16) identifies every search entry with a specific original minor. The left multiplication in Section 3.4 is used only to preserve **maximal minors of the rectangular matrix**, after which Lemma 3 transfers their meaning to a different square matrix.

For integer determinants, nonzero reduction modulo a prime certifies nonvanishing over the integers, whereas zero reduction modulo that prime does not certify an integer zero. A modular implementation of (17) must also handle a denominator that vanishes modulo the chosen prime; discarding that branch would be invalid. Finally, approximate singularity of noisy floating-point data is a different problem and is outside the exact decision problem (1).

## 6. Exact computational verification

The mathematical arguments above do not depend on experiments. We nevertheless implemented the search using Python integers, `fractions.Fraction`, row-wise denominator clearing, and an explicit remainder check on every division in (17). A separate verifier uses rational Gaussian elimination with row pivoting and increasing-order exhaustive enumeration. It does not use the bordered-minor recurrence to compute its reference determinants.

All checks below completed with Python 3.12.12 and random seed `20260923`:

| Check family | Instances | Verification |
|---|---:|---|
| Exhaustive small integer matrices | 596 | All one-by-one and two-by-two matrices over $\{-1,0,1\}$, and all three-by-three matrices over $\{1,2\}$ |
| Random integer matrices | 400 | 80 matrices of each order 1 through 5; entries sampled uniformly from $[-7,7]\cap\mathbb Z$ |
| Random rational matrices | 150 | 30 matrices of each order 1 through 5; numerators in $[-7,7]$, denominators in $[1,9]$ |
| Subset Sum reductions | 243 | Every $m\in\{1,2,3\}$, every ordered tuple in $\{1,2,3\}^m$, and every target from 1 through $1+\sum_i a_i$ |
| Modified Vandermonde determinants | 4,068 | Every maximal column selection for each of the 243 reduction instances |
| Cauchy matrices | 8 | $a_{ij}=1/(i+j+1)$ for zero-based $i,j$, in orders 1 through 8 |

For each exhaustive or random matrix, the verifier checked both existence and minimum-order mode against independent enumeration and verified every returned witness. For each reduction instance it enumerated all subsets of the original integers, independently enumerated all minors of the integer output $M$, and checked (9) for every maximal column selection of $H$. All comparisons passed.

The Cauchy matrices have no zero minors. Full traversal produced the following counts; the last column counts entries in live search arrays after denominator clearing and excludes scalar temporaries and the caller's input storage.

| $n$ | Minors checked | Higher-order determinants generated | Peak live array entries |
|---:|---:|---:|---:|
| 4 | 69 | 53 | 30 |
| 5 | 251 | 226 | 55 |
| 6 | 923 | 887 | 91 |
| 7 | 3,431 | 3,382 | 140 |
| 8 | 12,869 | 12,805 | 204 |

These counts equal $N_n$, $N_n-n^2$, and $\sum_{s=1}^n s^2$, respectively. Independent enumeration was also performed on the Cauchy cases through order 5. The complete search implementation and the verification script are included as executable Python code in Appendices A and B, so the checks do not depend on a separate code-hosting service.

## 7. Consequences and limitations

The existential zero-minor problem for binary-encoded integer or rational square matrices is NP-complete, and its universal complement is coNP-complete. The explicit reduction accounts for square shape, arbitrary minor order, a guaranteed invertible normalization block, and output bit length. It places the requested formulation within the established complexity theory of singular maximal minors and full spark.

The prefix search supplies an exact certificate or a complete negative answer with $O(\binom{2n}{n})$ arithmetic work and polynomial storage. Its exponential base is an upper bound, not a proved optimum. Unless $\mathrm P=\mathrm{NP}$, no polynomial-time exact algorithm solves all inputs of (1); this leaves open improvements in exponential algorithms and algorithms for restricted matrix classes. Principal minors, proper minors only, a specified variable order, and approximate singularity require their own formulations and arguments.

## AI assistance and license

OpenAI GPT-6, accessed through Codex, assisted with manuscript preparation from supplied mathematical notes, checking the arguments and references, implementing and running the exact verification, and preparing the submission. An exact model version was not exposed and is recorded as unknown. These disclosures are not independent authentication or peer review. No affiliation is asserted.

Copyright © 2026 Kaiyi Zhang. This manuscript, including its code listings, is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Richard M. Karp. “Reducibility among Combinatorial Problems.” In *Complexity of Computer Computations*, pp. 85–103, 1972. [Publisher and DOI](https://doi.org/10.1007/978-1-4684-2001-2_9).

2. Alexander Chistov, Hervé Fournier, Leonid Gurvits, and Pascal Koiran. “Vandermonde Matrices, NP-Completeness, and Transversal Subspaces.” *Foundations of Computational Mathematics* **3**, 421–427, 2003. [Publisher and DOI](https://doi.org/10.1007/s10208-002-0076-4).

3. Andreas M. Tillmann and Marc E. Pfetsch. “The Computational Complexity of the Restricted Isometry Property, the Nullspace Property, and Related Concepts in Compressed Sensing.” arXiv:1205.2081v6, 2013; see Corollary 3. [Versioned preprint](https://arxiv.org/abs/1205.2081v6).

4. Ljiljana Arambašić and Damir Bakić. “Full spark frames and totally positive matrices.” *Linear and Multilinear Algebra* **67**(8), 1685–1700, 2019. [Publisher and DOI](https://doi.org/10.1080/03081087.2018.1466864).

5. Erwin H. Bareiss. “Sylvester's Identity and Multistep Integer-Preserving Gaussian Elimination.” *Mathematics of Computation* **22**(103), 565–578, 1968. [Publisher and DOI](https://doi.org/10.1090/S0025-5718-1968-0226829-0).

6. Eoghan McDowell. “Flagged Schur Polynomial Duality via a Lattice Path Bijection.” *The Electronic Journal of Combinatorics* **30**(1), P1.5, 2023; see Proposition 4.1 for Jacobi's complementary-minor formula. [Open-access article](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v30i1p5).

## Appendix A. Exact search implementation

Save the following as `zero_minor.py`. It accepts a nonempty square matrix of Python `int` or `Fraction` entries, rejects floating-point inputs, and returns zero-based row and column tuples or `None`. `minimum_order=True` requests a witness of minimum order. Its recursive implementation requires sufficient Python recursion depth for the input dimension; the theoretical space bound refers to the algorithm, not a particular interpreter limit.

```python
"""Exact zero-minor search. Python 3.10+, standard library only.

The returned row/column tuples use zero-based indices. None certifies that
every nonempty square submatrix is nonsingular. Floats are rejected.
"""

from fractions import Fraction
from math import lcm


def integer_rows(matrix):
    """Clear denominators independently in each row; preserve zero minors."""
    rows = [list(row) for row in matrix]
    n = len(rows)
    if not n or any(len(row) != n for row in rows):
        raise ValueError("expected a nonempty square matrix")
    result = []
    for row in rows:
        if any(not isinstance(x, (int, Fraction)) for x in row):
            raise TypeError("entries must be int or Fraction")
        values = [Fraction(x) for x in row]
        scale = lcm(*(x.denominator for x in values))
        result.append([x.numerator * (scale // x.denominator) for x in values])
    return result


def find_zero_minor(matrix, minimum_order=False, *, stats=None):
    """Return a zero minor, optionally of minimum order, using exact division.

    Optional stats records visited minors, generated bordered determinants,
    and the peak number of stored matrix entries (excluding temporaries).
    """
    initial = integer_rows(matrix)
    n = len(initial)
    if stats is None:
        stats = {}
    stats.clear()
    stats.update(checked=0, generated=0, peak_matrix_entries=n * n)
    best = None
    bound = n + 1
    rows, cols = [], []

    def visit(D, denominator, row_start, col_start, live_entries):
        nonlocal best, bound
        order = len(rows) + 1
        if order >= bound:
            return False
        nr, nc = len(D), len(D[0])
        for a in range(nr):
            for b in range(nc):
                if order >= bound:
                    return False
                p = D[a][b]
                stats["checked"] += 1
                r, c = row_start + a, col_start + b
                if p == 0:
                    best = (tuple(rows + [r]), tuple(cols + [c]))
                    bound = order
                    if not minimum_order or bound == 1:
                        return True
                    continue
                if a + 1 == nr or b + 1 == nc or order + 1 >= bound:
                    continue
                E = []
                for u in range(a + 1, nr):
                    new_row = []
                    for v in range(b + 1, nc):
                        numerator = p * D[u][v] - D[u][b] * D[a][v]
                        value, remainder = divmod(numerator, denominator)
                        if remainder:
                            raise ArithmeticError("bordered-minor division was not exact")
                        new_row.append(value)
                        stats["generated"] += 1
                    E.append(new_row)
                child_live = live_entries + (nr - a - 1) * (nc - b - 1)
                stats["peak_matrix_entries"] = max(
                    stats["peak_matrix_entries"], child_live
                )
                rows.append(r)
                cols.append(c)
                stop = visit(E, p, r + 1, c + 1, child_live)
                rows.pop()
                cols.pop()
                del E, new_row
                if stop:
                    return True
        return False

    visit(initial, 1, 0, 0, n * n)
    return best


if __name__ == "__main__":
    example = [[1, 2, 3], [2, 4, 7], [3, 5, 8]]
    print(find_zero_minor(example))
    print(find_zero_minor(example, minimum_order=True))
```

## Appendix B. Independent verification script

Save the following as `verify_results.py` in the same directory and run `python verify_results.py`. It uses only the Python standard library, regenerates every case reported in Section 6, and writes `verification.json`, including source-file SHA-256 digests. Assertions must remain enabled. The Cramer's-rule construction used here is intended for these small validation instances; the polynomial-time proof allows any exact polynomial-time determinant routine.

```python
"""Independent exact checks of the paper; no submission credentials needed."""

import hashlib
import itertools
import json
import platform
import random
from fractions import Fraction
from math import comb, prod
from pathlib import Path

from zero_minor import find_zero_minor


def det(matrix):
    """Independent rational Gaussian elimination with row pivoting."""
    a = [[Fraction(x) for x in row] for row in matrix]
    n = len(a)
    value = Fraction(1)
    for k in range(n):
        pivot = next((r for r in range(k, n) if a[r][k]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != k:
            a[k], a[pivot] = a[pivot], a[k]
            value = -value
        p = a[k][k]
        value *= p
        for r in range(k + 1, n):
            factor = a[r][k] / p
            for c in range(k + 1, n):
                a[r][c] -= factor * a[k][c]
            a[r][k] = 0
    return value


def submatrix(a, rows, cols):
    return [[a[i][j] for j in cols] for i in rows]


def brute_minimum(a):
    for k in range(1, len(a) + 1):
        for rows in itertools.combinations(range(len(a)), k):
            for cols in itertools.combinations(range(len(a)), k):
                if det(submatrix(a, rows, cols)) == 0:
                    return rows, cols
    return None


def check_search(a):
    expected = brute_minimum(a)
    for minimum in (False, True):
        actual = find_zero_minor(a, minimum_order=minimum)
        assert (actual is None) == (expected is None)
        if actual is not None:
            rows, cols = actual
            assert rows and len(rows) == len(cols)
            assert det(submatrix(a, rows, cols)) == 0
            if minimum:
                assert len(rows) == len(expected[0])


def reduction(values, target):
    m = len(values)
    base = 1 + max(2, sum(values), target)
    nodes = [base**i for i in range(1, m + 1)]
    nodes += [base**i + a for i, a in enumerate(values, 1)]
    total = sum(nodes[:m]) + target
    h = [[x**r for x in nodes] for r in range(m - 1)]
    h.append([x**m - total * x**(m - 1) for x in nodes])
    b = [row[:m] for row in h]
    # Cramer's rule computes adj(B) C without an inverse or rational rounding.
    output = []
    for i in range(m):
        row = []
        for j in range(m):
            replaced = [r[:] for r in b]
            for r in range(m):
                replaced[r][i] = h[r][m + j]
            d = det(replaced)
            assert d.denominator == 1
            row.append(d.numerator)
        output.append(row)
    return output, h, nodes, total


def run():
    rng = random.Random(20260923)
    counts = {"exhaustive_integer_matrices": 0, "random_integer_matrices": 0,
              "random_rational_matrices": 0, "subset_sum_instances": 0,
              "vandermonde_determinants": 0}
    for n, alphabet in [(1, (-1, 0, 1)), (2, (-1, 0, 1)), (3, (1, 2))]:
        for entries in itertools.product(alphabet, repeat=n * n):
            check_search([list(entries[r*n:(r+1)*n]) for r in range(n)])
            counts["exhaustive_integer_matrices"] += 1
    for n in range(1, 6):
        for _ in range(80):
            a = [[rng.randint(-7, 7) for _ in range(n)] for _ in range(n)]
            check_search(a)
            counts["random_integer_matrices"] += 1
        for _ in range(30):
            a = [[Fraction(rng.randint(-7, 7), rng.randint(1, 9))
                  for _ in range(n)] for _ in range(n)]
            check_search(a)
            counts["random_rational_matrices"] += 1
    for m in range(1, 4):
        for values in itertools.product(range(1, 4), repeat=m):
            for target in range(1, sum(values) + 2):
                a, h, nodes, total = reduction(values, target)
                attainable = {sum(values[i] for i in range(m) if mask >> i & 1)
                              for mask in range(1 << m)}
                expected = target in attainable
                assert (brute_minimum(a) is not None) == expected
                assert (find_zero_minor(a) is not None) == expected
                for cols in itertools.combinations(range(2*m), m):
                    vandermonde = prod(nodes[q] - nodes[p]
                                       for p, q in itertools.combinations(cols, 2))
                    rhs = vandermonde * (sum(nodes[j] for j in cols) - total)
                    assert det(submatrix(h, range(m), cols)) == rhs
                    counts["vandermonde_determinants"] += 1
                counts["subset_sum_instances"] += 1
    cauchy = []
    for n in range(1, 9):
        a = [[Fraction(1, i + j + 1) for j in range(n)] for i in range(n)]
        stats = {}
        assert find_zero_minor(a, stats=stats) is None
        count = comb(2*n, n) - 1
        assert stats["checked"] == count
        assert stats["generated"] == count - n*n
        assert stats["peak_matrix_entries"] == sum(k*k for k in range(1, n+1))
        if n <= 5:
            check_search(a)
        cauchy.append({"n": n, **stats})
    example = [[1, 2, 3], [2, 4, 7], [3, 5, 8]]
    assert det(example) == 1
    assert find_zero_minor(example, True) == ((0, 1), (0, 1))
    counts["cauchy_matrices"] = len(cauchy)
    report = {"status": "passed", "seed": 20260923,
              "python": platform.python_version(), "counts": counts,
              "cauchy_counts": cauchy,
              "source_sha256": {name: hashlib.sha256(Path(name).read_bytes()).hexdigest()
                                for name in ("zero_minor.py", "verify_results.py")}}
    Path("verification.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()
```
