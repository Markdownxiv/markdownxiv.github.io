# The Zero-Minor Problem Is NP-Complete

**Kaiyi Zhang**  
Author homepage: [github.com/kzoacn](https://github.com/kzoacn)  
September 23, 2026. Version 2.

## Abstract

The zero-minor problem asks whether a square matrix contains a nonempty square submatrix with determinant zero, with arbitrary row and column sets. We give self-contained deterministic polynomial-time reductions proving NP-completeness for binary-encoded integer and rational matrices and for finite fields supplied as part of the input through an irreducible polynomial and polynomial-basis coordinates. The finite-field problem remains NP-complete separately in characteristics two and three when the extension degree can grow. In characteristic two, an exact-cover reduction uses a cardinality constraint to turn parity of coverage into exact coverage. In characteristic three, paired nodes encode positive one-in-three satisfiability. Modified Vandermonde determinants and systematic form convert both constructions to square matrices. In contrast, the problem over each fixed finite field is in P. The complementary total-nonsingularity problems are coNP-complete in the hard input models. We also describe a depth-first bordered-minor algorithm using $O(\binom{2n}{n})$ arithmetic operations and $O(n^3)$ stored coefficients, including for minimum-order search. Integer intermediate values have polynomial bit length, and finite-field arithmetic has polynomial cost in the compact field description. Exact verification scripts check the reductions, worked examples, and search counts. The results are placed alongside established work on singular maximal minors and full spark, without a priority claim or an optimality claim for the exponential bound.

**Keywords:** zero minor; total nonsingularity; NP-completeness; finite fields; characteristic two; characteristic three; full spark; exact cover; fraction-free elimination.

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

Restricting the input entries to integers defines $\text{Zero-Minor}_{\mathbb Z}$. The dimension is part of the input. Section 5 defines a further uniform problem in which a finite field is also supplied as input. All statements concern exact zero testing in the usual bit model of computation.

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

**Theorem 3 (Finite fields supplied as input).** With the compact representation in Section 5.1, the uniform finite-field zero-minor problem is NP-complete under deterministic polynomial-time many-one reductions. This remains true when the characteristic is fixed to $2$, and separately when it is fixed to $3$, while the extension degree is part of the input. The corresponding total-nonsingularity recognition problems are coNP-complete. For each fixed finite field, however, the zero-minor problem is in P.

These statements distinguish a decision problem, a certificate-producing search problem, and an optimization problem. NP-completeness in Theorems 1 and 3 refers to the decision problems. Theorem 2 is an upper bound for the search and optimization problems, with polynomial overhead in input bit length. Section 5.6 extends its arithmetic and storage bounds to finite fields.

### 1.1. Relation to existing work

Chistov, Fournier, Gurvits, and Koiran proved NP-completeness of detecting a zero maximal minor in a rectangular integer matrix, using Vandermonde constructions [2]. Tillmann and Pfetsch state the coNP-completeness of rational full-spark recognition in Corollary 3 [3]. The connection between full-spark systems and totally nonsingular matrices is developed by Arambašić and Bakić [4].

The proof below gives an explicit route from positive-integer Subset Sum to the precise **square-matrix, arbitrary-order** problem in (1). In particular, it constructs an invertible prescribed block and supplies the encoding-length argument needed to normalize that block. We do not claim that the general hardness phenomenon or the Vandermonde technique is new. Similarly, the algorithm uses the classical Sylvester identity underlying Bareiss elimination [5]; the analysis concerns its organization as a depth-first search over increasing row and column prefixes.

The finite-field arguments use deterministic construction of irreducible polynomials in fixed characteristic [7], positive one-in-three satisfiability [8], and Exact Cover by 3-Sets [9]. We give the reductions explicitly, including the balancing step in characteristic two and the treatment of repeated variable occurrences in characteristic three. Fixing the characteristic does not fix the field when its extension degree is allowed to grow.

## 2. Two equivalent formulations

### 2.1. Systematic form and full spark

Let $K$ be any field. For $A\in K^{n\times n}$, define

$$
G=[\,I_n\mid A\,]\in K^{n\times2n}.
$$

An $n$-row matrix is **full spark** when every set of $n$ columns is linearly independent.

**Lemma 4.** The matrix $A$ has a nonempty zero minor if and only if $G$ has a singular $n$-column submatrix.

**Proof.** A choice of $n$ columns of $G$ consists of some columns $J$ from $A$ and some identity columns $L$, where $|J|+|L|=n$. Set $I=[n]\setminus L$. Expanding along the identity columns gives

$$
\det G[:,L\cup(n+J)]=\pm\det A[I,J].
\tag{4}
$$

Every equal-size pair $(I,J)$ arises this way. If $J=\varnothing$, the selected matrix is the identity and its determinant is $1$; hence a singular selection necessarily corresponds to a nonempty minor. This proves both directions. $\square$

In particular, $A$ is totally nonsingular exactly when $[I_n\mid A]$ is full spark. The latter matrix always has full row rank; testing its overall rank does not test full spark.

### 2.2. Joint support size

For a vector $x$, let $\|x\|_0$ denote the number of nonzero coordinates.

**Lemma 5.** For $A\in K^{n\times n}$,

$$
A\text{ has a nonempty zero minor}
\quad\Longleftrightarrow\quad
\exists x\in K^n\setminus\{0\}:
\|x\|_0+\|Ax\|_0\le n.
\tag{5}
$$

**Proof.** If $A[I,J]$ is singular of order $k$, extend a nonzero null vector over $K$ by zeros outside $J$. The resulting $x$ satisfies $\|x\|_0\le k$, and $Ax$ vanishes on $I$, so $\|Ax\|_0\le n-k$.

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

**Lemma 6.** There exists an $m$-element set $S\subseteq[2m]$ with $\sum_{j\in S}x_j=T$ if and only if the Subset Sum instance is affirmative.

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

**Lemma 7.** If $S=\{s_1<\cdots<s_m\}\subseteq[2m]$, then

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

The first factor in (9) is nonzero. Lemmas 6 and 7 therefore show that $H$ has a singular maximal minor exactly when the original Subset Sum instance is affirmative.

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

By Lemma 4, $H$ has a singular maximal minor if and only if $A$ has a nonempty zero minor. Finally, for every order $k$,

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

**Lemma 8.** The search returns a valid zero minor if one exists and otherwise returns `none`. It performs $O(N_n)$ arithmetic operations.

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

## 5. Finite fields supplied as part of the input

### 5.1. Compact representation and membership in NP

The uniform finite-field problem has input

$$
(p,f,A),\qquad
K=\mathbb F_p[X]/(f(X)),\qquad
A\in K^{n\times n},
\tag{21}
$$

where $p$ is a binary-encoded prime, $f$ is a monic irreducible polynomial of degree $d\ge1$, and each matrix entry is given by its $d$ coefficients in the basis $1,\alpha,\ldots,\alpha^{d-1}$, with $\alpha=X\bmod f$. Coefficients lie in $\{0,\ldots,p-1\}$. Both $p$ and $d$ may vary. The field order is $q=p^d$, but neither the elements of the field nor its multiplication table are enumerated in the input. The field description and matrix occupy $O((n^2+1)d\log p)$ bits apart from size headers.

The question is whether $A$ has a nonempty zero minor. Invalid field or matrix encodings are rejected. Primality and polynomial irreducibility can be checked in deterministic polynomial time. For example, irreducibility uses Frobenius powers modulo $f$ and polynomial gcds; factoring the integer $d$ by trial division is polynomial in the length of the dense polynomial representation. Thus field validity does not require a promise that is expensive to verify.

Given a valid input, addition, multiplication, inversion, and equality in $K$ take time polynomial in $d$ and $\log p$. The certificate $(I,J)$ is therefore checked by finite-field elimination in polynomial bit time. This proves membership in NP, including for the restrictions $p=2$ and $p=3$.

For the hardness constructions we must also produce $f$, not merely assume that the desired field is available. Shoup gives a deterministic algorithm constructing a degree-$d$ irreducible polynomial in time polynomial in $d$ for each fixed prime characteristic [7]. This suffices for both constructions below. No deterministic construction polynomial in $\log p$ for unrestricted varying $p$ is needed.

### 5.2. A common algebraic construction over any field

**Lemma 9.** Let $K$ be a field, let $x_1,\ldots,x_{2r}\in K$ be distinct, and let $T\in K$. From these data one can construct a square matrix $A\in K^{r\times r}$ in polynomially many field operations such that $A$ has a nonempty zero minor if and only if some $r$ of the nodes sum to $T$.

**Proof.** Form the $r\times2r$ matrix $H$ by (8), with $m=r$. The proof of Lemma 7 uses polynomial identities and row additions only, so (9) holds over every field, including characteristic two. Its Vandermonde factor is nonzero. Hence an $r$-column submatrix is singular precisely when its nodes sum to $T$.

The matrix $H$ has full row rank. Otherwise every $r$-column determinant would vanish, so every $r$-element selection of nodes would sum to $T$. For any different indices $a,b$, choose $r-1$ other indices. Comparing their union with $\{a\}$ and their union with $\{b\}$ would give $x_a=x_b$, a contradiction. This argument includes $r=1$, when the common selection is empty.

Gaussian elimination finds $r$ independent columns in polynomial time. Permute them to obtain $[B\mid C]$ with $B$ invertible, and set $A=B^{-1}C$. Left multiplication preserves singularity of each maximal column selection. Lemma 4, applied to $[I_r\mid A]$, gives the required equivalence. There is no exhaustive basis search in this construction. $\square$

### 5.3. Characteristic three: positive one-in-three satisfiability

Positive one-in-three satisfiability asks for Boolean values such that exactly one of the three variable occurrences in each constraint is true. This problem is NP-complete [8]. Repeated occurrences are allowed here, as in Schaefer's formulation. An instance without constraints is immediately affirmative. A constraint with three occurrences of the same variable is immediately impossible. Map these cases to fixed one-by-one yes and no matrices, respectively, and remove unused variables. In the remaining instances, let $m$ be the number of variables and $c\ge1$ the number of constraints.

Let $a_{\ell i}$ be the number of occurrences of variable $i$ in constraint $\ell$. Then $\sum_i a_{\ell i}=3$. No $a_{\ell i}$ equals $3$ after preprocessing, and each remaining variable has a nonzero occurrence count in some constraint.

Construct $K=\mathbb F_{3^{m+c}}$ and choose the polynomial-basis elements, in order, as

$$
e_1,\ldots,e_c,g_1,\ldots,g_m.
$$

Set

$$
\begin{aligned}
v_i&=\sum_{\ell=1}^c a_{\ell i}e_\ell,
&\tau&=\sum_{\ell=1}^c e_\ell,\\
x_i&=g_i,
&x_{m+i}&=g_i+v_i,\\
T&=\sum_{i=1}^m g_i+\tau.
\end{aligned}
\tag{22}
$$

Each $v_i\ne0$, so the two nodes in a pair differ. Different pairs have different $g_i$ coordinates, so all $2m$ nodes are distinct. Also $\tau\ne0$ by linear independence of the basis, even when $c$ is divisible by $3$.

Consider a selection of $m$ nodes with sum $T$. Comparing the coefficient of $g_i$ forces exactly one node from pair $i$: the possible counts $0,1,2$ are distinct modulo $3$. Let $z_i\in\{0,1\}$ indicate selection of $g_i+v_i$. The remaining coordinates require

$$
\sum_i a_{\ell i}z_i\equiv1\pmod3
\qquad(1\le\ell\le c).
\tag{23}
$$

As an ordinary integer, the sum on the left belongs to $\{0,1,2,3\}$. Thus (23) is equivalent to the integer equality $\sum_i a_{\ell i}z_i=1$. Conversely, a satisfying Boolean assignment selects one node from each pair and gives the target sum. We have proved an equivalence between satisfiability and an $m$-node target sum.

Lemma 9 converts this instance to a square zero-minor instance. Here the first $m$ columns can be used as the normalization block without pivot selection: their node sum differs from $T$ by $-\tau$, so

$$
\det B=-\tau\prod_{1\le i<j\le m}(g_j-g_i)\ne0.
\tag{24}
$$

Each field element has $m+c$ ternary coefficients, and the output matrix has $m^2$ entries. Its encoding length is $O(m^2(m+c))$ bits. Field construction, powering, and elimination are deterministic polynomial-time operations. This proves NP-hardness, and hence NP-completeness, for characteristic three with variable extension degree.

### 5.4. Characteristic two: exact cover and a counting constraint

The characteristic-three Boolean construction cannot be transferred by simply changing the modulus to $2$, because one and three true occurrences then have the same residue. Instead we use **Exact Cover by 3-Sets (X3C)**, an NP-complete problem [9]. Its input is a universe of $3k$ elements and $N$ distinct three-element subsets; the question is whether $k$ of these subsets cover every element exactly once. We may assume $k\ge1$, since the empty instance is trivial.

**Lemma 10 (Balancing the number of candidates).** In deterministic polynomial time, an X3C instance can be replaced by an equivalent instance with $3r$ elements and exactly $2r$ distinct candidate triples.

**Proof.** Track $\delta=N-2k$. Components introduced below use fresh elements and no triple meets two components, so an exact cover exists after adjoining a component if and only if it existed before, provided the component itself has an exact cover.

If $\delta>0$, add $\delta$ disjoint components consisting of three new elements and their unique candidate triple. Each step increases $N$ and $k$ by one, decreasing $\delta$ by one.

If $\delta<0$, add $-\delta$ disjoint copies of a component on six new elements with these five triples:

$$
\{1,2,3\},\quad\{4,5,6\},\quad
\{1,2,4\},\quad\{1,2,5\},\quad\{1,2,6\}.
$$

Its first two triples give an exact cover. Each step increases $N$ by five and $k$ by two, increasing $\delta$ by one. At termination the new counts satisfy $N'=2r$ and $|U'|=3r$. There are at most $|N-2k|$ additions, so the output has size polynomial in the original explicit input. $\square$

Apply the lemma and index the resulting universe by $[3r]$, with candidate triples $S_1,\ldots,S_{2r}$. Construct $K=\mathbb F_{2^{3r}}$ with an $\mathbb F_2$-basis $e_1,\ldots,e_{3r}$. Define

$$
x_j=\sum_{i\in S_j}e_i,
\qquad
T=\sum_{i=1}^{3r}e_i.
\tag{25}
$$

Distinct triples give distinct nodes. For a selection $J$ of exactly $r$ candidates, let $b_i$ be the ordinary integer number of selected triples containing element $i$. Then

$$
\sum_{j\in J}x_j=T
\iff b_i\equiv1\pmod2\text{ for every }i,
\qquad
\sum_{i=1}^{3r}b_i=3r.
\tag{26}
$$

The parity requirement implies $b_i\ge1$ for all $3r$ elements. Their total is exactly $3r$, so every $b_i$ equals $1$. Conversely, an exact cover satisfies (26). The cardinality constraint therefore turns odd coverage into exact coverage; cancellation modulo two creates no additional affirmative instances.

Apply Lemma 9 to the nodes and target. In characteristic two, the last row in (8) is $x_j^r+Tx_j^{r-1}$, and the determinant identity remains valid. The lemma supplies a full-rank rectangular matrix and a square matrix $A=B^{-1}C$ with the required zero-minor equivalence. In this construction the first $r$ columns need not be independent, so the normalization block must be found by elimination.

Every field element has $3r$ binary coefficients, and the output matrix occupies $O(r^3)$ bits. The balancing step, fixed-characteristic field construction [7], and matrix operations are all deterministic polynomial-time procedures. This proves NP-hardness, and hence NP-completeness, for characteristic two with variable extension degree. Either characteristic restriction already proves NP-hardness of the uniform problem in (21).

### 5.5. Why fixing the field changes the answer

Fix a finite field $\mathbb F_q$ once and for all. A zero entry gives a first-order witness. If there is none and $n\ge q$, choose any two rows. Their $n$ column ratios take values in the $q-1$ nonzero field elements. Two ratios coincide, giving a second-order zero minor. Hence

$$
n\ge q\quad\Longrightarrow\quad
\text{a zero minor of order one or two exists}.
\tag{27}
$$

The scan and a pairwise ratio comparison use $O(n^2)$ field operations. If $n<q$, exhaustive enumeration is bounded by a constant depending only on the fixed field. The complete fixed-field decision problem is therefore in P. In particular, every matrix of order at least two over $\mathbb F_2$ has a zero minor.

For the reductions above, $q$ grows exponentially with the extension degree while its representation grows only linearly in that degree for fixed characteristic. Thus (27) does not apply to their output dimensions, which are smaller than $q$. Fixing $p=2$ or $p=3$ fixes the characteristic, not the field. The distinction is between one fixed field and an unbounded family of compactly represented extension fields.

Together with Section 5.1 and the two reductions, this proves the zero-minor claims of Theorem 3. The total-nonsingularity statements follow by complementation on valid inputs; invalid descriptions are polynomial-time recognizable and do not affect the complexity classification. $\square$

### 5.6. Exact search over the supplied field

The state invariant (16), identity (17), and the increasing-prefix argument hold over every field. In a finite-field implementation, division in (17) means multiplication by the inverse of the nonzero prefix determinant. A zero pivot already gives a valid zero minor in the supplied field, and minimum-order pruning works as in Section 4.6.

Consequently the search uses $O(N_n)$ field operations and $O(n^3)$ stored field elements, with bit time $O(N_n)\operatorname{poly}(n,d,\log p)$ and polynomial bit storage under (21). The integer-only reference search in Appendix A does not implement extension-field arithmetic; Appendix C implements the finite-field arithmetic and exhaustive checks needed to reproduce the reductions.

### 5.7. Two worked finite-field examples

For characteristic two, take the balanced instance on six elements with triples

$$
S_1=\{1,2,3\},\quad S_2=\{4,5,6\},\quad
S_3=\{1,2,4\},\quad S_4=\{1,3,5\}.
$$

The first two triples form an exact cover. Work in $K=\mathbb F_2[\alpha]/(\alpha^6+\alpha+1)$, using the basis $1,\alpha,\ldots,\alpha^5$. Formula (25) gives

$$
\begin{aligned}
(x_1,x_2,x_3,x_4)
={}&(1+\alpha+\alpha^2,\ \alpha^3+\alpha^4+\alpha^5,\\
&1+\alpha+\alpha^3,\ 1+\alpha^2+\alpha^4),\\
T={}&1+\alpha+\alpha^2+\alpha^3+\alpha^4+\alpha^5.
\end{aligned}
$$

The first two columns of $H$ are dependent, illustrating why an arbitrary first block cannot be assumed invertible. Taking columns $1,3$ as $B$ and columns $2,4$ as $C$ gives

$$
A=B^{-1}C=\begin{pmatrix}1&1+\beta\\0&\beta\end{pmatrix},
\qquad \beta=\alpha+\alpha^2+\alpha^4+\alpha^5.
\tag{28}
$$

The entry $A_{21}=0$ is a zero minor, while $\det A=\beta\ne0$.

For characteristic three, take one constraint on three different variables, requiring exactly one of them to be true. In $K=\mathbb F_3[\alpha]/(\alpha^4+\alpha+2)$, put $e_1=1$ and $(g_1,g_2,g_3)=(\alpha,\alpha^2,\alpha^3)$. The six nodes are

$$
\alpha,\alpha^2,\alpha^3,\alpha+1,\alpha^2+1,\alpha^3+1,
\qquad T=1+\alpha+\alpha^2+\alpha^3.
$$

Using the first three columns as $B$ gives

$$
A=\begin{pmatrix}
0&2\alpha+2\alpha^2&\alpha^2+2\alpha^3\\
\alpha+2\alpha^2+\alpha^3&0&1+2\alpha^2+\alpha^3\\
1+2\alpha+\alpha^2+2\alpha^3&1+\alpha+\alpha^2&0
\end{pmatrix}.
\tag{29}
$$

Each of the three possible satisfying assignments produces the corresponding diagonal zero. Both displayed moduli are irreducible, and Appendix C checks that fact and reproduces the matrices exactly. These small examples illustrate the constructions; Theorem 3 concerns the families with unbounded extension degree.

## 6. Useful reductions and boundary cases

### 6.1. Low-order and complementary checks

Scanning for zero entries detects first-order minors in $O(n^2)$ operations. A determinant computation checks order $n$ in $O(n^3)$ arithmetic operations. If all entries are nonzero, then for fixed rows $r<s$,

$$
\det A[\{r,s\},\{p,q\}]=0
\quad\Longleftrightarrow\quad
\frac{a_{rp}}{a_{sp}}=\frac{a_{rq}}{a_{sq}}.
\tag{30}
$$

Sorting these ratios for every row pair gives a deterministic $O(n^3\log n)$ comparison bound for second-order detection. Hashing normalized rational ratios gives an expected $O(n^3)$ dictionary-operation bound under the usual hashing assumptions. Reduction and comparison of large integers contribute additional bit costs.

For invertible $A$, Jacobi's complementary-minor formula [6, Proposition 4.1] states

$$
\det A[I,J]
=(-1)^{\sum_{i\in I}i+\sum_{j\in J}j}
\det A\,\det A^{-1}[J^c,I^c].
\tag{31}
$$

Hence order-$k$ zeros of $A$, for $1\le k<n$, correspond to order-$(n-k)$ zeros of $A^{-1}$. The swapped row and column complements are essential. Checking zero entries and second-order ratio collisions in $A^{-1}$ treats orders $n-1$ and $n-2$ of $A$. For small $n$, only distinct valid orders are retained.

These are optional accelerations for finding an arbitrary zero minor. A large-order witness is only an upper bound on the answer when minimum order is required. Our reference implementation below uses the general search directly, so its verification exercises the recurrence without these accelerations.

### 6.2. Fixed orders

For a fixed order $k$, direct enumeration with elimination uses

$$
O\!\left(\binom nk^2k^3\right)
$$

arithmetic operations, polynomial in $n$. For finding a zero minor of order at most $r$, truncating the prefix search gives $O(\sum_{k=1}^r\binom nk^2)$ arithmetic operations.

These fixed-order bounds are separate from the fixed-field tractability established in Section 5.5.

### 6.3. Exactness and transformations

Ordinary row reduction preserves rank but not the zero-minor pattern of the input: it transforms the totally nonsingular two-by-two example in Section 1 into an identity matrix with zero entries. In contrast, (16) identifies every search entry with a specific original minor. The left multiplication in Sections 3.4 and 5 is used only to preserve **maximal minors of the rectangular matrix**, after which Lemma 4 transfers their meaning to a different square matrix.

For integer determinants, nonzero reduction modulo a prime certifies nonvanishing over the integers, whereas zero reduction modulo that prime does not certify an integer zero. A modular implementation of (17) must also handle a denominator that vanishes modulo the chosen prime; discarding that branch would be invalid. Finally, approximate singularity of noisy floating-point data is a different problem and is outside the exact decision problem (1).

## 7. Exact computational verification

### 7.1. Integer and rational matrices

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

### 7.2. Finite-field reductions and examples

Appendix C supplies a separate standard-library script. It uses polynomial-basis arithmetic over small explicitly represented extension fields, checks each modulus by Frobenius powers and polynomial gcds, and evaluates determinants by the Leibniz permutation expansion. Systematic-form conversion uses Gaussian elimination. Every node selection is checked against its combinatorial interpretation, every maximal determinant is checked against (9), and every square output is checked by independent minor enumeration, stopping if a witness is found. This separation checks the conversion to square matrices as well as the target-sum encoding.

The new checks used Python 3.12.12 and seed `20260923`:

| Characteristic | Source instances | Affirmative / negative | Maximal-minor identities | Fields in nontrivial reductions |
|---:|---:|---:|---:|---|
| 2 | 84 | 42 / 42 | 2,688 | $\mathbb F_{2^6}$, $\mathbb F_{2^9}$, $\mathbb F_{2^{12}}$ |
| 3 | 100 | 48 / 52 | 1,370 | $\mathbb F_{3^d}$ with $3\le d\le8$ |

For characteristic two, 60 cases contain $2r$ candidate triples on $3r$ elements, with 20 cases for each $r=2,3,4$. The cases include collections generated from planted covers and unconstrained random collections, with one six-element case fixed to reproduce (28). Another 24 cases start with six elements and three, four, or five candidate triples, eight cases per candidate count. These exercise both padding operations and the case requiring no padding. The answer before padding is compared with the complete maximal-minor search in $H$ and the independent zero-minor search in the final square matrix.

For characteristic three, the script enumerates all multisets of zero, one, or two constraints drawn from the three-occurrence variable multisets on one, two, or three declared variables. This gives 84 instances. It adds all 16 subsets of the four distinct-variable triples on four variables. Repeated variable occurrences, repeated constraints, unused variables, empty conjunctions, and impossible single-variable constraints are thereby included. The prescribed first block is checked for invertibility on every nontrivial instance. Forty-five instances are handled by the explicit trivial-case preprocessing, leaving 55 nontrivial reductions and 1,370 maximal-minor identities. The one-constraint three-variable instance reproduces (29).

All comparisons passed. The script writes `verification-finite-fields.json`, including the source hash, field moduli, and the worked-example matrices. Its fixed small moduli and exhaustive checks are for reproducibility; the polynomial-time reductions use the general field-construction result cited in Section 5.1.

## 8. Consequences and limitations

The existential zero-minor problem for binary-encoded integer or rational square matrices is NP-complete, and its universal complement is coNP-complete. The same classifications hold for the uniform compactly represented finite-field problem, even with characteristic restricted to two or to three. Over each fixed finite field the problem is in P. The explicit reductions account for square shape, arbitrary minor order, invertible normalization blocks, and polynomial output length. In characteristic two the exact number of selected triples is what prevents parity cancellation from producing false positives.

The prefix search supplies an exact certificate or a complete negative answer with $O(\binom{2n}{n})$ arithmetic work and polynomial storage. Its exponential base is an upper bound, not a proved optimum. Unless $\mathrm P=\mathrm{NP}$, no polynomial-time exact algorithm solves every input in either of the hard models. This leaves open improvements in exponential algorithms and algorithms for restricted matrix classes. The finite-field theorem uses an explicit irreducible polynomial and polynomial-basis coordinates; it makes no claim for an input model that explicitly lists every field element or its multiplication table. Principal minors, proper minors only, a specified variable order, and approximate singularity require their own formulations and arguments.

## AI assistance and license

OpenAI GPT-6, accessed through Codex, assisted with manuscript preparation from supplied mathematical notes, developing and checking the finite-field reductions, checking references, implementing and running the exact verification, and preparing the submission and revision. An exact model version was not exposed and is recorded as unknown. These disclosures are not independent authentication or peer review. No affiliation is asserted.

Copyright © 2026 Kaiyi Zhang. This manuscript, including its code listings, is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Richard M. Karp. “Reducibility among Combinatorial Problems.” In *Complexity of Computer Computations*, pp. 85–103, 1972. [Publisher and DOI](https://doi.org/10.1007/978-1-4684-2001-2_9).

2. Alexander Chistov, Hervé Fournier, Leonid Gurvits, and Pascal Koiran. “Vandermonde Matrices, NP-Completeness, and Transversal Subspaces.” *Foundations of Computational Mathematics* **3**, 421–427, 2003. [Publisher and DOI](https://doi.org/10.1007/s10208-002-0076-4).

3. Andreas M. Tillmann and Marc E. Pfetsch. “The Computational Complexity of the Restricted Isometry Property, the Nullspace Property, and Related Concepts in Compressed Sensing.” arXiv:1205.2081v6, 2013; see Corollary 3. [Versioned preprint](https://arxiv.org/abs/1205.2081v6).

4. Ljiljana Arambašić and Damir Bakić. “Full spark frames and totally positive matrices.” *Linear and Multilinear Algebra* **67**(8), 1685–1700, 2019. [Publisher and DOI](https://doi.org/10.1080/03081087.2018.1466864).

5. Erwin H. Bareiss. “Sylvester's Identity and Multistep Integer-Preserving Gaussian Elimination.” *Mathematics of Computation* **22**(103), 565–578, 1968. [Publisher and DOI](https://doi.org/10.1090/S0025-5718-1968-0226829-0).

6. Eoghan McDowell. “Flagged Schur Polynomial Duality via a Lattice Path Bijection.” *The Electronic Journal of Combinatorics* **30**(1), P1.5, 2023; see Proposition 4.1 for Jacobi's complementary-minor formula. [Open-access article](https://www.combinatorics.org/ojs/index.php/eljc/article/view/v30i1p5).

7. Victor Shoup. “New Algorithms for Finding Irreducible Polynomials over Finite Fields.” *Mathematics of Computation* **54**(189), 435–447, 1990. [Author's manuscript](https://www.shoup.net/papers/detirred.pdf), [DOI](https://doi.org/10.1090/S0025-5718-1990-0993933-0).

8. Thomas J. Schaefer. “The Complexity of Satisfiability Problems.” In *Proceedings of the Tenth Annual ACM Symposium on Theory of Computing*, pp. 216–226, 1978. [Publisher and DOI](https://doi.org/10.1145/800133.804350), [paper](https://www.khoury.northeastern.edu/home/lieber/courses/csg260/f06/materials/papers/max-sat/p216-schaefer.pdf).

9. Burkhard Monien and Ivan Hal Sudborough. “Bandwidth Constrained NP-Complete Problems.” *Theoretical Computer Science* **41**, 141–167, 1985. [Publisher and DOI](https://doi.org/10.1016/0304-3975(85)90068-4).

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

Save the following as `verify_results.py` in the same directory and run `python verify_results.py`. It uses only the Python standard library, regenerates the integer and rational cases reported in Section 7.1, and writes `verification.json`, including source-file SHA-256 digests. Assertions must remain enabled. The Cramer's-rule construction used here is intended for these small validation instances; the polynomial-time proof allows any exact polynomial-time determinant routine.

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

## Appendix C. Finite-field verification script

Save the following as `verify_finite_fields.py` and run `python verify_finite_fields.py` with assertions enabled. It requires only the standard library. Field elements in the generated JSON use radix-$p$ integer encoding: the integer $\sum_i a_i p^i$ represents $\sum_i a_i\alpha^i$, not the image of that integer in the prime subfield. The reduction proofs use polynomial-time elimination and field construction; this small-instance verifier deliberately uses exhaustive enumeration and permutation determinants.

```python
"""Exact checks of the finite-field reductions. Python standard library only.

Integers encode polynomial-basis coefficients in radix p, least degree first.
The fixed small moduli are checked for irreducibility before use. This exhaustive
test program is not the polynomial-time field-construction algorithm in the proof.
"""

from functools import lru_cache
from itertools import combinations, combinations_with_replacement, permutations, product
from pathlib import Path
import hashlib
import json
import platform
import random


def trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def remainder(a, b, p):
    a, b = trim(a), trim(b)
    while a and len(a) >= len(b):
        offset = len(a) - len(b)
        scale = a[-1] * pow(b[-1], -1, p) % p
        for j, value in enumerate(b):
            a[offset + j] = (a[offset + j] - scale * value) % p
        a = trim(a)
    return a


def polynomial_product(a, b, f, p):
    out = [0] * max(0, len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] = (out[i + j] + x * y) % p
    return remainder(out, f, p)


def irreducible(f, p):
    """Frobenius/gcd check; checking every degree up to d/2 is sufficient."""
    d = len(f) - 1
    h = [0, 1]
    for i in range(1, d + 1):
        out = [1]
        for _ in range(p):
            out = polynomial_product(out, h, f, p)
        h = out
        if i <= d // 2:
            difference = h + [0] * max(0, 2 - len(h))
            difference[1] = (difference[1] - 1) % p
            a, b = list(f), trim(difference)
            while b:
                a, b = b, remainder(a, b, p)
            if len(a) != 1:
                return False
    return h == remainder([0, 1], f, p)


MODULI = {
    (2, 6): (1, 1, 0, 0, 0, 0, 1),
    (2, 9): (1, 1, 0, 0, 0, 0, 0, 0, 0, 1),
    (2, 12): (1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1),
    (3, 3): (1, 2, 0, 1),
    (3, 4): (2, 1, 0, 0, 1),
    (3, 5): (1, 2, 0, 0, 0, 1),
    (3, 6): (2, 1, 0, 0, 0, 0, 1),
    (3, 7): (2, 0, 1, 0, 0, 0, 0, 1),
    (3, 8): (2, 0, 1, 0, 0, 0, 0, 0, 1),
}


class Field:
    def __init__(self, p, d):
        self.p, self.d = p, d
        self.f = MODULI[p, d]
        assert irreducible(self.f, p)
        self.size = p**d
        self.binary_modulus = sum(c << i for i, c in enumerate(self.f))

    def digits(self, a):
        out = []
        for _ in range(self.d):
            out.append(a % self.p)
            a //= self.p
        return out

    def encode(self, a):
        return sum((c % self.p) * self.p**i for i, c in enumerate(a))

    @lru_cache(maxsize=65536)
    def add(self, a, b):
        if self.p == 2:
            return a ^ b
        return self.encode([x + y for x, y in zip(self.digits(a), self.digits(b))])

    def total(self, values):
        out = 0
        for value in values:
            out = self.add(out, value)
        return out

    @lru_cache(maxsize=65536)
    def neg(self, a):
        return a if self.p == 2 else self.encode([-x for x in self.digits(a)])

    def sub(self, a, b):
        return self.add(a, self.neg(b))

    @lru_cache(maxsize=65536)
    def mul(self, a, b):
        if self.p == 2:
            out = 0
            while b:
                if b & 1:
                    out ^= a
                b >>= 1
                a <<= 1
                if a & self.size:
                    a ^= self.binary_modulus
            return out
        out = polynomial_product(self.digits(a), self.digits(b), self.f, self.p)
        return self.encode(out)

    def power(self, a, exponent):
        out = 1
        while exponent:
            if exponent & 1:
                out = self.mul(out, a)
            a = self.mul(a, a)
            exponent >>= 1
        return out

    @lru_cache(maxsize=65536)
    def inverse(self, a):
        assert a != 0
        return self.power(a, self.size - 2)


@lru_cache(maxsize=None)
def field(p, d):
    return Field(p, d)


def determinant(a, F):
    """Leibniz expansion, independent of systematic-form elimination."""
    n = len(a)
    out = 0
    for perm in permutations(range(n)):
        value = 1
        for i, j in enumerate(perm):
            value = F.mul(value, a[i][j])
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        out = F.add(out, F.neg(value) if inversions % 2 else value)
    return out


def zero_minor(a, F):
    n = len(a)
    for k in range(1, n + 1):
        for rows in combinations(range(n), k):
            for cols in combinations(range(n), k):
                if determinant([[a[i][j] for j in cols] for i in rows], F) == 0:
                    return rows, cols
    return None


def systematic(h, basis, F):
    n = len(h)
    remaining = [j for j in range(2 * n) if j not in basis]
    order = list(basis) + remaining
    a = [[row[j] for j in order] for row in h]
    for k in range(n):
        pivot = next(i for i in range(k, n) if a[i][k])
        a[k], a[pivot] = a[pivot], a[k]
        inverse = F.inverse(a[k][k])
        a[k] = [F.mul(x, inverse) for x in a[k]]
        for i in range(n):
            if i != k:
                scale = a[i][k]
                a[i] = [F.sub(x, F.mul(scale, y)) for x, y in zip(a[i], a[k])]
    assert [row[:n] for row in a] == [[int(i == j) for j in range(n)] for i in range(n)]
    return [row[n:] for row in a]


def check_template(nodes, target, F, predicate, expected, prescribed_basis=None):
    n = len(nodes) // 2
    assert len(set(nodes)) == len(nodes)
    h = [[F.power(x, i) for x in nodes] for i in range(n - 1)]
    h.append([F.sub(F.power(x, n), F.mul(target, F.power(x, n - 1))) for x in nodes])
    basis = None
    count = 0
    any_zero = False
    for selected in combinations(range(2 * n), n):
        value = determinant([[row[j] for j in selected] for row in h], F)
        vandermonde = 1
        for i, j in combinations(selected, 2):
            vandermonde = F.mul(vandermonde, F.sub(nodes[j], nodes[i]))
        difference = F.sub(F.total(nodes[j] for j in selected), target)
        assert value == F.mul(vandermonde, difference)
        assert (difference == 0) == predicate(selected)
        any_zero |= value == 0
        if value != 0 and basis is None:
            basis = selected
        count += 1
    assert basis is not None and any_zero == expected
    if prescribed_basis is not None:
        assert determinant([[row[j] for j in prescribed_basis] for row in h], F) != 0
        basis = prescribed_basis
    a = systematic(h, basis, F)
    witness = zero_minor(a, F)
    assert (witness is not None) == expected
    return count, {"p": F.p, "degree": F.d, "modulus_low_first": F.f,
                   "nodes": nodes, "target": target, "basis_columns_zero_based": basis,
                   "matrix_radix_encoded": a, "zero_minor_zero_based": witness}


def cover(k, triples, selected):
    return all(sum(i in triples[j] for j in selected) == 1 for i in range(3 * k))


def pad_cover(k, triples):
    triples = list(dict.fromkeys(tuple(sorted(s)) for s in triples))
    difference = len(triples) - 2 * k
    if difference >= 0:
        for _ in range(difference):
            triples.append(tuple(range(3 * k, 3 * k + 3)))
            k += 1
    else:
        for _ in range(-difference):
            b = 3 * k
            triples.extend(tuple(b + i for i in s) for s in
                           [(0, 1, 2), (3, 4, 5), (0, 1, 3), (0, 1, 4), (0, 1, 5)])
            k += 2
    assert len(triples) == 2 * k
    return k, triples


def run():
    rng = random.Random(20260923)
    counts = {"characteristic_2_instances": 0, "characteristic_2_padding_instances": 0,
              "characteristic_2_identities": 0, "characteristic_2_yes": 0,
              "characteristic_3_instances": 0, "characteristic_3_trivial_instances": 0,
              "characteristic_3_identities": 0, "characteristic_3_yes": 0}
    examples = {}
    cases2 = []
    for k in (2, 3, 4):
        pool = list(combinations(range(3 * k), 3))
        for trial in range(20):
            if trial % 2:
                triples = [tuple(range(i, i + 3)) for i in range(0, 3 * k, 3)]
                triples += rng.sample([s for s in pool if s not in triples], k)
            else:
                triples = rng.sample(pool, 2 * k)
            if k == 2 and trial == 0:
                triples = [(0, 1, 2), (3, 4, 5), (0, 1, 3), (0, 2, 4)]
            cases2.append((k, triples, False))
    pool = list(combinations(range(6), 3))
    for size in (3, 4, 5):
        for _ in range(8):
            cases2.append((2, rng.sample(pool, size), True))
    for original_k, original, padding_test in cases2:
        expected = any(cover(original_k, original, s)
                       for s in combinations(range(len(original)), original_k))
        k, triples = pad_cover(original_k, original)
        F = field(2, 3 * k)
        nodes = [sum(1 << i for i in s) for s in triples]
        target = (1 << (3 * k)) - 1
        count, data = check_template(nodes, target, F, lambda s: cover(k, triples, s), expected)
        counts["characteristic_2_instances"] += 1
        counts["characteristic_2_padding_instances"] += int(padding_test)
        counts["characteristic_2_identities"] += count
        counts["characteristic_2_yes"] += int(expected)
        examples.setdefault("characteristic_2", data)

    cases3 = []
    for variables in (1, 2, 3):
        pool = list(combinations_with_replacement(range(variables), 3))
        for length in range(3):
            cases3.extend((variables, clauses) for clauses in combinations_with_replacement(pool, length))
    pool = list(combinations(range(4), 3))
    for length in range(5):
        cases3.extend((4, clauses) for clauses in combinations(pool, length))
    for variables, clauses in cases3:
        expected = any(all(sum(bits[i] for i in clause) == 1 for clause in clauses)
                       for bits in product((0, 1), repeat=variables))
        counts["characteristic_3_instances"] += 1
        counts["characteristic_3_yes"] += int(expected)
        if not clauses or any(len(set(clause)) == 1 for clause in clauses):
            a = [[0 if not clauses else 1]]
            assert (zero_minor(a, field(3, 3)) is not None) == expected
            counts["characteristic_3_trivial_instances"] += 1
            continue
        used = sorted(set().union(*(set(c) for c in clauses)))
        index = {v: i for i, v in enumerate(used)}
        clauses = [tuple(index[v] for v in clause) for clause in clauses]
        m, c = len(used), len(clauses)
        F = field(3, m + c)
        markers = [3**(c + i) for i in range(m)]
        vectors = [F.total(3**j for j, clause in enumerate(clauses) for v in clause if v == i)
                   for i in range(m)]
        nodes = markers + [F.add(a, b) for a, b in zip(markers, vectors)]
        target = F.total(markers + [3**j for j in range(c)])

        def satisfies(selected):
            selected = set(selected)
            return (all((i in selected) + (m + i in selected) == 1 for i in range(m))
                    and all(sum(m + i in selected for i in clause) == 1 for clause in clauses))

        count, data = check_template(nodes, target, F, satisfies, expected, tuple(range(m)))
        counts["characteristic_3_identities"] += count
        if m == 3 and clauses == [(0, 1, 2)]:
            examples["characteristic_3"] = data
    # Independent coefficient arithmetic also checks the optimized binary path.
    for p, d in MODULI:
        F = field(p, d)
        for _ in range(20):
            a, b = rng.randrange(1, F.size), rng.randrange(F.size)
            oracle = F.encode(polynomial_product(F.digits(a), F.digits(b), F.f, p))
            assert F.mul(a, b) == oracle
            assert F.mul(a, F.inverse(a)) == 1
            assert F.power(a, F.size) == a
    report = {"status": "passed", "python": platform.python_version(), "seed": 20260923,
              "counts": counts, "examples": examples,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    Path("verification-finite-fields.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    run()
```
