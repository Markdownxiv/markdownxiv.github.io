# Convex Polyhedra from Unordered Edge Lengths: Structural Forcing and a Restricted Hardness Result

Kaiyi Zhang

September 22, 2026

## Abstract

We study the following realization problem: given a multiset of positive rational numbers, decide whether it is exactly the multiset of lengths of the actual edges of a bounded, full-dimensional convex polytope in three-dimensional Euclidean space. No graph is supplied, and subdivisions do not count as edges. We give a polynomial-size existential-real formulation that certifies both edges and nonedges. We then prove that six suitably separated dominant lengths force a tetrahedral quotient, and that a hierarchy of separated three-edge groups forces successive expansions of quotient vertices into triangles. These statements constrain every convex realization using lengths alone. Separately, we prove NP-hardness when admissible realizations are restricted to right prisms of fixed height and equilateral base side length, with nonadjacent corners of one base truncated. This reduction outputs the entire edge multiset, uses only rational lengths of polynomial bit length, and does not supply cut depths or corner angles. We also give a full-polyhedron counterexample showing why that restricted reduction cannot simply be used for unrestricted realization, and an obstruction to repairing a subdivision-based construction with a small total length of auxiliary edges. The unrestricted problem is not classified by these results: neither a polynomial-time algorithm nor a hardness reduction to it is established.

## 1. Problem and scope

An instance is a list $\ell_1,\ldots,\ell_n\in\mathbb Q_{>0}$, encoded in binary. We ask whether there is a bounded, full-dimensional convex polytope $P\subset\mathbb R^3$ and a bijection from the input occurrences to the one-dimensional faces of $P$ preserving length. We call this problem **unordered edge realization**. Equal values remain separate occurrences. Vertices inserted into an existing straight edge and diagonals drawn inside a facet are not additional polytope vertices or edges.

This distinction matters for complexity. Lucier's subdivision-allowing construction proves a related hardness result, while his discussion separates the nondegenerate problem considered here [1, Theorem 6.5.8 and Section 6.5.4]. That historical statement is not a claim about the present literature's complete state. Our results below are self-contained arguments about the specified rational-input problem and one explicitly restricted variant.

We use the standard fact that the graph of a convex three-dimensional polytope is simple and three-vertex-connected, hence three-edge-connected [2]. A graph with $n$ edges arising this way has at most $\lfloor2n/3\rfloor$ vertices. Moreover, every edge of length $L$ has two edge-disjoint alternative endpoint paths along its incident facets, each strictly longer than $L$. Therefore

$$
3\max_i\ell_i<\sum_i\ell_i
$$

is necessary. It is not sufficient. A six-edge polytope must be a tetrahedron, and the multiset $\{1,1,1,1,1,d\}$ is realizable precisely for $0<d<\sqrt3$. Indeed, the two endpoints of the $d$ edge lie on the intersection circle of two unit spheres whose centers are distance one apart; that circle has diameter $\sqrt3$. The maximum is attained only in a flat configuration. Conversely every strictly smaller positive chord length admits a nonflat choice. Taking $d=9/5$ satisfies the displayed total-length condition but is impossible.

The main results have different logical scopes:

| Result | Problem to which it applies |
| --- | --- |
| Polynomial-size existential-real formulation, Section 2 | Unrestricted unordered edge realization |
| Tetrahedral quotient and hierarchical triangle forcing, Section 3 | Every unrestricted realization satisfying the stated length inequalities |
| Exact triangular-cap criterion, Section 4 | A specified trihedral cone |
| Rational NP-hardness reduction, Section 5 | A specified family of admissible geometric realizations |
| Alternative-prism and small-auxiliary-length obstructions, Section 6 | Particular attempts to transfer hardness to unrestricted realization |

In particular, restricting the *allowed outputs* can make a decision problem harder without proving the unrestricted problem hard. Section 6 supplies an explicit example of the lost implication.

## 2. An existential-real upper bound

The class $\exists\mathbb R$ consists of problems polynomial-time reducible to feasibility of existential formulas over the real numbers with polynomial equalities and inequalities and rational coefficients. Membership is an upper bound; it is not a polynomial-time decision procedure.

**Lemma 2.1 (nonedge certificate).** Let $p_i,p_j$ be distinct vertices of a convex polytope with vertex set $V$. Then

$$
[p_i,p_j]\text{ is not an edge}
\quad\Longleftrightarrow\quad
\operatorname{relint}[p_i,p_j]\cap
\operatorname{conv}(V\setminus\{p_i,p_j\})\ne\varnothing.
$$

**Proof.** An exposing functional for an edge is constant on its endpoints and strictly smaller at all other vertices, so an edge cannot have the indicated intersection. Conversely, suppose the whole segment is disjoint from the hull of the other vertices. Strict separation gives a functional $f$ whose values at both endpoints exceed its values at every other vertex. If the endpoint values tie, it already exposes the edge. Otherwise relabel so that $f(p_i)>f(p_j)$. Interpolate $f$ with a functional uniquely exposing $p_j$. At the parameter where the endpoint values first tie, the value at $p_j$ remains strictly above all other vertex values, because this inequality holds at both ends of the interpolation. The resulting functional exposes the edge. Finally, either endpoint lying in the hull of the other vertices would contradict extremality. Thus any intersection is in the relative interior. $\square$

**Theorem 2.2.** Unordered edge realization belongs to $\exists\mathbb R$.

**Proof.** Take a disjunction over the possible vertex counts $4\le v\le\lfloor2n/3\rfloor$. For a fixed $v$, introduce coordinates $p_1,\ldots,p_v\in\mathbb R^3$ and exposing vectors $u_i\in\mathbb R^3$, with

$$
u_i\cdot(p_i-p_j)>0\qquad(i\ne j).
$$

These constraints make the points distinct exposed vertices of their hull. Enforce full dimension by

$$
\det(p_2-p_1,p_3-p_1,p_4-p_1)^2>0.
$$

A realization may always label four affinely independent vertices first.

For every pair $i<j$, use a Boolean real variable $e_{ij}$, constrained by $e_{ij}(e_{ij}-1)=0$. If $e_{ij}=1$, require a vector $s_{ij}$ satisfying

$$
s_{ij}\cdot(p_i-p_j)=0,
\qquad s_{ij}\cdot(p_i-p_h)>0\quad(h\notin\{i,j\}).
$$

If $e_{ij}=0$, require variables $t_{ij}$ and $\mu_{ij,h}$ with

$$
\begin{aligned}
&0<t_{ij}<1,\qquad \mu_{ij,h}\ge0,
\qquad \sum_{h\ne i,j}\mu_{ij,h}=1,\\
&t_{ij}p_i+(1-t_{ij})p_j
=\sum_{h\ne i,j}\mu_{ij,h}p_h.
\end{aligned}
$$

The lemma makes $e_{ij}$ exactly the adjacency indicator, including the exclusion of extra hull edges.

Finally introduce Boolean variables $z_{ij,k}$ assigning edge occurrences to the input, with

$$
\sum_{k=1}^n z_{ij,k}=e_{ij},
\qquad
\sum_{i<j}z_{ij,k}=1\quad(1\le k\le n),
$$

and impose $z_{ij,k}=1\Rightarrow\|p_i-p_j\|^2=\ell_k^2$. All implications can be written as disjunctions of polynomial sign conditions.

A satisfying assignment gives precisely the required full-dimensional finite convex hull and edge multiset. Conversely, a realization supplies all the witnesses, including the nonedge witnesses from Lemma 2.1. For fixed $v=O(n)$ there are $O(n^3)$ variables and polynomially many bounded-degree conditions. The disjunction over $v$ is also polynomial in size. The largest degree is six, and clearing positive denominators preserves polynomial coefficient bit length. $\square$

No assertion of NP membership is made: this formulation need not have short rational coordinate witnesses.

## 3. Graph structure forced by length separation

For a set of edges called short, retain all graph vertices, including isolated vertices, when taking its connected components. The sum of all short lengths bounds the length of any simple path in a short component.

**Lemma 3.1 (metric separation).** Let $H$ be the total length of the short edges. A distinguished edge longer than $H$ cannot have both endpoints in one short component. If two distinguished edges connect the same pair of short components, their lengths differ by at most $H$.

**Proof.** The first assertion follows by comparing the distinguished edge with a short path between its endpoints. For the second, join their endpoints by a path in each of the two components and use the triangle inequality in both directions. The total length of those two paths is at most $H$. $\square$

**Theorem 3.2 (six-edge frame).** Suppose six designated input occurrences have lengths $L_1,\ldots,L_6$, the total of all other lengths is $H$, and

$$
\min_iL_i>H,
\qquad |L_i-L_j|>H\quad(i\ne j).
$$

In every convex realization, deleting the six designated edges leaves exactly four connected components. There is one designated edge between each pair, so contracting these components gives $K_4$. Each component has exactly three external edges. A nontrivial component is bridgeless and has three distinct attachment vertices; a singleton has degree three.

**Proof.** The quotient is loopless and simple by Lemma 3.1. Every nontrivial cut in it is a cut of the original graph, so it has size at least three. With six edges its minimum degree is at least three, forcing at most four vertices. Simplicity and minimum degree three force at least four. Thus it is $K_4$.

If a component had an internal bridge, each side of that bridge would require at least two of its three external edges to have a cut of size at least three. This is impossible. If all external edges attach at one vertex, deleting that vertex disconnects the full graph unless the component is that singleton. If they attach at exactly two vertices, deleting those two disconnects the graph unless they constitute the entire component. In the latter case their degree sum is at most $2+3=5$, contradicting minimum degree three. $\square$

The theorem forces a combinatorial quotient; it does not automatically make representative points a nonflat tetrahedron. For representatives $p_i$ of the components, each coarse distance differs from its designated edge length by at most $H$. A separate metric margin is required whenever a construction needs a nondegenerate coarse tetrahedron.

The next result avoids incorrectly assuming three-connectivity inside a component.

**Theorem 3.3 (hierarchical triangle forcing).** Partition the input occurrences into a six-element group $A$, triples $T_1,\ldots,T_k$, and an optional residual multiset $R$. Put

$$
H_0=\sum_{i=1}^k\sum_{t\in T_i}t+\sum_{r\in R}r,
\qquad
H_i=\sum_{j=i+1}^k\sum_{t\in T_j}t+\sum_{r\in R}r.
$$

Assume the hypotheses of Theorem 3.2 for $A$ with budget $H_0$, and assume

$$
\min T_i>H_i,
\qquad \max T_i-\min T_i>H_i
\quad(1\le i\le k).
$$

For each $i$, retain $A,T_1,\ldots,T_i$ and contract the connected components formed by the remaining smaller edges. The initial quotient is $K_4$. At each subsequent step exactly one quotient vertex is replaced by a triangle, with one old incident edge attached to each new vertex. If $R$ is empty, this is the full graph; it is cubic and has

$$
V=4+2k,\qquad E=6+3k,\qquad F=4+k.
$$

Two entries of a triple may be equal; the range condition is sufficient.

**Proof.** Inductively, each current component is connected and has exactly three external edges. Its internal graph is bridgeless by the bridge argument in Theorem 3.2. Delete the next three distinguished edges and contract each remaining smaller-edge component inside it. No distinguished edge becomes a loop, since it is longer than $H_i$. Each nonempty quotient is connected and bridgeless: contraction preserves the absence of bridges.

A loopless connected bridgeless multigraph with an edge has at least two edges. There are only three distinguished edges altogether, so all three must be in the same old component. A connected loopless bridgeless multigraph with three edges is either a triangle or three parallel edges between two vertices. The latter is excluded by applying Lemma 3.1 to its longest and shortest edges.

For a vertex $D$ of the resulting triangle let $r_D$ count old external edges incident to its component. Its cut in the full graph has size $2+r_D$, so $r_D\ge1$. Since the three $r_D$ sum to three, each equals one. Every new component again has exactly three external edges, completing the induction. When $R$ is empty every final component is a singleton. The counts follow by adding two vertices and three edges at each step and then applying Euler's formula. $\square$

A geometrically decreasing sequence of scales for any fixed positive non-equilateral triple satisfies these inequalities when the ratio is sufficiently large. Its binary descriptions have length linear in the number of levels. This observation concerns the cost of encoding the hypotheses, not the existence of a realization.

![A tetrahedral quotient on the left and its expansion at D into a triangle on the right. The three orange edges form the next distinguished triple; the six blue edges persist.](figures/hierarchical-expansion.png)

*Figure 1. One step of Theorem 3.3. These are combinatorial quotient graphs; the drawing is not a spatial metric realization. The theorem does not specify which vertex is expanded.*

Theorem 3.3 leaves open which vertex is expanded, the shape of its cone, and the feasibility of prescribed triangle lengths there. Quotient triangles need not remain actual triangular facets after later expansions. These distinctions prevent interpreting the theorem as a complete reduction by itself.

## 4. A local cap criterion and a grouping obstruction

Let $e_1,e_2,e_3$ be unit cone generators with $e_1\perp e_2,e_3$ and $e_2\cdot e_3=c$, where $-1<c\le0$. A triangular truncation has intercepts $ae_1,be_2,de_3$ with $a,b,d>0$. Let $p,q$ be the two sides incident to $ae_1$, and let $r$ be the remaining side.

**Proposition 4.1.** Such a truncation exists if and only if

$$
|p^2-q^2|<r^2<p^2+q^2-2cpq.
$$

**Proof.** Set $x=a^2$. The first two side equations give $b=\sqrt{p^2-x}$ and $d=\sqrt{q^2-x}$, so

$$
r^2=f(x)=p^2+q^2-2x-2c\sqrt{(p^2-x)(q^2-x)},
\quad 0<x<\min(p^2,q^2).
$$

Its derivative is

$$
f'(x)=-2+c\frac{p^2+q^2-2x}{\sqrt{(p^2-x)(q^2-x)}}\le-2.
$$

The endpoint limits are exactly the stated upper and lower bounds. Thus the inequalities are necessary and sufficient and determine $x$ uniquely. A plane through the three positive intercepts cuts the cone. $\square$

For rational $c,p,q,r$ the criterion is a polynomial-time rational test. If the three lengths are unordered, try each choice for $r$.

At $c=-1/2$, the rational lengths

$$
\epsilon=\frac1{100B^2},\quad
p=3+\frac{\epsilon u}{11},\quad
q=5+\frac{\epsilon v}{13},\quad
r=7+\frac{\epsilon(w-1/2)}{14}
$$

encode the comparison $u+v\ge w$ for integers $0\le u,v,w\le B$. Here $r^2>p^2+q^2$, forcing the largest length into the $r$ role even when the triple is unordered. The decisive expression is

$$
\begin{aligned}
p^2+q^2+pq-r^2
={}&\epsilon(u+v-w+1/2)\\
&+\epsilon^2\left(\frac{u^2}{121}+\frac{v^2}{169}
+\frac{uv}{143}-\frac{(w-1/2)^2}{196}\right).
\end{aligned}
$$

The absolute quadratic coefficient is below $B^2/32$, so its contribution is below $\epsilon/3200$, while the linear term has magnitude at least $\epsilon/2$.

Nevertheless, pooling many such triples does not enforce the intended comparison groups. Every acute triangle satisfies Proposition 4.1 for every $-1<c\le0$, when its largest side is assigned to $r$. For $m$ lengths in each of the bands

$$
P:[3,3.001],\qquad Q:[5,5.001],\qquad R:[6.999,7.001],
$$

every triple of type $PQQ$ or $PRR$ is acute, as are $PPP,QQQ,RRR$. If $m$ is even, use $m/2$ groups of type $PQQ$ and $m/2$ of type $PRR$. If $m\ge3$ is odd, first use one homogeneous triple of each type, then apply the even construction. Thus for every $m\ge2$ the uncolored local grouping is feasible, independently of the encoded integers. Tiny distinct perturbations within these bands do not remove the obstruction.

This is a local statement. It does not claim that any additional prescribed scaffold edges can simultaneously be realized.

## 5. Rational hardness for a restricted geometric family

### 5.1. The family and the numerical source

Let $\mathcal F$ consist of polytopes obtained as follows. Start with a right prism of height $10$ over any strictly convex equilateral polygon of side length $100$. Truncate some pairwise nonadjacent vertices of one base, each by a plane meeting its three incident edges in their relative interiors and removing only that corner. The number of base vertices, base shape, selected corners and cut depths are unspecified.

The restricted decision problem asks whether the entire input multiset is realized by some member of $\mathcal F$. This definition constrains the admissible geometry; it is absent from unordered edge realization.

**Theorem 5.1.** Realization in $\mathcal F$ is NP-hard for positive rational lengths encoded in binary.

We reduce from Numerical Three-Dimensional Matching, which is NP-hard even when all source integers are distinct [3, Theorem 3.3]. Given positive integer lists $X,Y,Z$ of size $m$ and target $T$, replace $z$ by $w=T-z$. Reject immediately if a resulting $w$ is nonpositive or if $\sum X+\sum Y\ne\sum W$; such an input may map to the impossible one-length list $\{1\}$.

Let $B_0$ bound the values in $X,Y,W$ and set $M=10B_0$. Form the $2m$ item occurrences

$$
\{M+x:x\in X\}\;\cup\;\{3M+y:y\in Y\}
$$

and the $m$ targets $\{4M+w:w\in W\}$. Two items adding to a target must use one from each item class: two from the first class are too small, and two from the second are too large. Thus pairing these uncolored items into the targets is equivalent to the source problem. Their total sums agree. Let $B$ be the maximum shifted item or target.

### 5.2. The complete rational edge list

Set

$$
\eta=\frac1{10^6m^2B},\qquad
\epsilon=\frac1{10^6m^2B^3},\qquad
t_j=\frac{\epsilon j}{2}.
$$

For an item $j$ define

$$
b(j)=\frac{2t_j}{1-t_j^2},\qquad
P(j)=\frac{1+t_j^2}{1-t_j^2},\qquad Q(j)=100-b(j),
$$

and for a target $w$ define $R(w)=\epsilon(w-\eta)$. The identity

$$
P(j)^2=1+b(j)^2
$$

is exact. Output the following $15m$ lengths:

| Length | Multiplicity |
| --- | --- |
| $P(j)$ | One for each of the $2m$ items |
| $Q(j)$ | One for each of the $2m$ items |
| $R(w)$ | One for each of the $m$ targets |
| $100$ | $6m$ |
| $9$ | $m$ |
| $10$ | $3m$ |

This is the *entire* multiset, computable without a matching. Each number has $O(\log m+\log B)$ bits. The reduction is polynomial even for a binary numerical source; strong NP-hardness is not needed for this encoding argument.

We record bounds used in both directions. For $1\le j,w\le B$, write $d_j=\epsilon^2j^2/4$ and $y_j=P(j)-1$. Then $0<d_j<1/4$ and

$$
\begin{aligned}
\epsilon j&\le b(j)\le\epsilon j+\tfrac12\epsilon^3j^3,\\
|b(j)^2-\epsilon^2j^2|&\le\epsilon^4j^4,\\
y_j&=\frac{\epsilon^2j^2}{2(1-d_j)},\\
|18y_j-y_j^2-9\epsilon^2j^2|&<4\epsilon^4j^4.
\end{aligned}
$$

For the last two error comparisons, the ratios to $\epsilon^4j^4$ are respectively

$$
\frac{2-d_j}{4(1-d_j)^2},\qquad
\frac{32-36d_j}{16(1-d_j)^2},
$$

which are bounded by $1$ and $4$ on this interval. In particular,

$$
\begin{aligned}
&0<b(j)<0.001,\quad 1<P(j)<1.001,\quad99.999<Q(j)<100,\\
&\epsilon/2<R(w)<0.001,\quad
\epsilon^2B^3<\eta,\quad5\epsilon^2B^4<1.
\end{aligned}
$$

### 5.3. A realization from a matching

Suppose the items are paired so that $u_i+v_i=w_i$. The three horizontal lengths $b=b(u_i)$, $c=b(v_i)$, $r=R(w_i)$ form a nondegenerate triangle. Indeed,

$$
b+c-r\ge\epsilon\eta>0,
\qquad
|b-c|\le\epsilon(w_i-2)+\tfrac12\epsilon^3B^3<r.
$$

Let the angle opposite $r$ be $\pi-\gamma_i$. Thus

$$
\cos\gamma_i=\frac{r^2-b^2-c^2}{2bc}.
$$

The estimates above give $b+c-r<2\epsilon\eta$, $b+c+r<3\epsilon B$, and $bc\ge\epsilon^2$. Consequently

$$
0<1-\cos\gamma_i<3\eta B=\frac3{10^6m^2}.
$$

The inequality $1-\cos\gamma\ge2\gamma^2/\pi^2$ on $[0,\pi]$ implies

$$
0<\gamma_i<\frac1{100m}.
$$

For $i=0,\ldots,m-1$, choose two unit directions of arguments

$$
\beta_i=2\arctan(i/m),\qquad \beta_i+\gamma_i,
$$

where the matching triples have been indexed from zero. Append the negatives of these $2m$ directions. Consecutive $\beta_i$ differ by more than $1/m$, and the last displayed direction is below $\pi/2$. All $4m$ directions are therefore strictly ordered cyclically, with consecutive gaps below $\pi$, and their vectors sum to zero. Multiplying by $100$ and taking partial sums gives a strictly convex equilateral $4m$-gon. One elementary way to verify convexity is to project successive edge vectors onto the left normal of a fixed edge: the contributions first have positive sign and then negative sign, with total zero, so all other vertices lie strictly on the left of that supporting edge.

Make the right prism of height $10$. At each top corner between the designated pair of directions, truncate vertical distance $1$ and horizontal distances $b(u_i),b(v_i)$. The horizontal rays form angle $\pi-\gamma_i$, so the new face has sides $P(u_i),P(v_i),R(w_i)$. The selected corners are nonadjacent. Their small top corner triangles are disjoint; their cut planes retain every bottom vertex, so the cuts yield a genuine convex polytope with positive volume.

The surviving top edges consist of $2m$ lengths $Q(j)$ and $2m$ copies of $100$. The bottom contributes $4m$ copies of $100$. The vertical edges give $m$ copies of $9$ and $3m$ copies of $10$. Together with the new triangles these are exactly the prescribed $15m$ lengths.

The directions have rational cosines and algebraic sines. Coordinates may therefore be algebraic, as allowed by the realization problem. Only the rational edge list is output by the reduction; no expanded number field or coordinate certificate is needed for its polynomial size.

### 5.4. Every admissible cut has depth one

Now suppose a member of $\mathcal F$ realizes the output list. At a cut let $v$ be the surviving vertical edge and $a=10-v$ its depth. Since $0<v<10$, the available values for $v$ are $9$, a value $P(j)$, or a value $R(w)$; hence $1\le a<10$.

For a neighboring surviving top edge $e$, its horizontal cut distance is $100-e$. This uses nonadjacency of the selected corners. The connecting cap side $S$ obeys

$$
S^2=a^2+(100-e)^2.
$$

The value gaps force $e=Q(n)$ for an item $n$:

- $e=100$ would give a zero horizontal cut.
- $e=9$ or $10$ puts $S$ between $90$ and $92$, where there is no input value.
- $e=P(j)$ puts $S$ between $98.999$ and $\sqrt{99^2+100}<99.51$, also absent.
- $e=R(w)<0.001$ makes $S^2\ge1+(100-e)^2>100^2$, larger than the maximum input length squared.

Thus each horizontal cut distance is $b(n)$. If $v=9$, then $a=1$ and $S=P(n)$, as intended. We exclude the other possibilities exactly.

If $v=P(j)$, then $8.999<a<9$ and $8.999<S<9.001$. The only possible input value of $S$ is $9$. It would imply

$$
b(n)^2=81-(10-P(j))^2=18y_j-y_j^2.
$$

The error bounds in Section 5.2 yield

$$
|n^2-9j^2|<5\epsilon^2B^4<1.
$$

These are integers, so $n=3j$. But the defining rational function gives $b(3j)>3b(j)$, whereas

$$
\frac{18y_j-y_j^2}{b(j)^2}=\frac{18-y_j}{2+y_j}<9,
$$

a contradiction.

If $v=R(w)$, then $9.999<a<10$ and $9.999<S<10.001$, so the only possible input value is $S=10$. This would require

$$
b(n)^2=20R(w)-R(w)^2>9\epsilon.
$$

Instead $b(n)^2<2\epsilon^2B^2<9\epsilon$, again a contradiction.

Every cut therefore has depth exactly one, side lengths $P(u),P(v)$, and top remainders $Q(u),Q(v)$. Its base is shorter than $b(u)+b(v)<0.002$, so it must use a target length $R(w)$. Every $P$ occurrence lies on a cap side, since all other edge roles have been determined. There are $2m$ such occurrences, forcing exactly $m$ cuts. A prism with an $N$-gon base and $m$ nonadjacent corner truncations has $3N+3m$ edges; hence $N=4m$.

### 5.5. Recovering the numerical matching

The horizontal triangle at a cut satisfies $R(w)<b(u)+b(v)$. If $u+v\le w-1$, however,

$$
b(u)+b(v)\le\epsilon(u+v)+\epsilon^3B^3
<\epsilon(w-\eta)=R(w),
$$

since $\eta+\epsilon^2B^3<1$. Thus $u+v\ge w$ at every cut. All item and target occurrences are used and their global sums agree, so equality holds at every cut. The offsets from Section 5.1 recover one original item from each class, and hence the required numerical matching. This proves Theorem 5.1. $\square$

The proof does not assert NP membership of the restricted problem on arbitrary inputs, nor that recognizing membership in $\mathcal F$ from an arbitrary geometric representation is free. The family is part of the restricted problem's definition.

## 6. Obstructions to transferring the reduction

### 6.1. A NO matching instance with a full convex realization

Take $m=4$ with item occurrences $31$ four times and $91$ four times, and targets $121$ twice and $123$ twice. Both totals are $488$. Possible pair sums are $62,122,182$, so no pair can equal a target.

Nevertheless, the rational list in Section 5.2 is the full edge list of a right $20$-gonal prism of height $100$. Use $20$ of the $24$ copies of $100$ for its vertical edges. Every remaining multiplicity is even. Halve them to obtain $20$ base side lengths, including two sides of length $100$, with every other side positive and at most $100$.

For completeness, a strictly convex polygon with these sides exists by a direct cyclic construction. If its prospective circumradius is $r\ge50$, the sum of the minor central angles is

$$
\Phi(r)=\sum_s2\arcsin\frac{s}{2r},
$$

where the sum is over the base side occurrences. At $r=50$, the two maximal sides already contribute $2\pi$, and the others contribute positively. As $r\to\infty$, the sum tends to zero. Continuity gives a radius $r>50$ with $\Phi(r)=2\pi$. Placing the chords in the prescribed cyclic order yields a strictly convex polygon.

The resulting prism uses every output occurrence exactly once as an actual edge. Its counts are $V=40,E=60,F=22$, all vertices have degree three, and these are also the counts of the intended truncated-prism construction. Thus neither Euler counts nor cubicity repairs the reduction.

This counterexample has repeated source integers. The NP-hard distinct-source restriction from [3] avoids this particular parity construction, but that observation does not exclude other convex realizations. No unrestricted soundness result follows from it.

### 6.2. Small auxiliary lengths do not repair a subdivision construction

We next give a different obstruction, for the numerical family underlying the subdivision construction in [1]. It illustrates why replacing subdivision points by tiny polyhedral features requires a new argument.

**Proposition 6.1.** Let positive integers $v_1,\ldots,v_m$ sum to $2S$, put $T=10S$, and consider the lengths

$$
10v_1,\ldots,10v_m,\qquad a=2T-5,\qquad b=T-4,\qquad b=T-4.
$$

Add any positive auxiliary lengths of total $H<3$. If the resulting multiset is the actual edge multiset of a convex three-polytope, every value among the $v_i$ occurs with even multiplicity.

**Proof.** Orient an edge $AB$ of length $a$ along the $x$ axis, with $x(A)=0$ and $x(B)=a$. Its two incident facets give internally vertex-disjoint alternative boundary paths $P_1,P_2$, each longer than $a$.

If one path contained neither $b$ edge, its item lengths, being multiples of $10$, would have total at least $2T$: their total exceeds $a-H>2T-8$. It would consume every item. The other path would then have length at most $2b+H<a$, a contradiction. Thus each path contains exactly one $b$ edge. Its item total exceeds

$$
a-b-H=T-1-H>T-4,
$$

so it is at least $T$. Equality of the global item total forces each path's item total to be exactly $T$. Every item edge and both $b$ edges lie on the two paths; every edge outside the paths and $AB$ is auxiliary.

Let $h_j$ be the total auxiliary length on $P_j$. Its long-edge total is $a+1$. For a vertex $v$ on $P_j$, let $q_j(v)$ be the long-edge prefix length, omitting auxiliary edges. The sum of all projection defects along that path is $1+h_j$, and each individual defect is nonnegative. Hence

$$
-h_j\le q_j(v)-x(v)\le1+h_j.
$$

Assume first $S\ge2$, so every long edge has length at least $10$. Distinct prefix values on one path differ by at least $10$. If $v,w$ have successive distinct prefix values in the path order, then

$$
x(w)-x(v)\ge9-2H>H.
$$

They cannot belong to one auxiliary-edge component, whose diameter is at most $H$. Conversely all vertices with the same prefix value on that path are connected by auxiliary edges.

If an auxiliary component meets both paths, choose an auxiliary connector between successive contacts on different paths, with its interior meeting neither path. If its length is $d$, then $d+h_1+h_2\le H$. At its endpoints the preceding bounds give

$$
|q_1-q_2|\le1+d+h_1+h_2\le1+H<4.
$$

Every prefix has the form $10k+\delta b$ with $\delta\in\{0,1\}$. Prefixes with different $\delta$ differ by at least $4$, since $b=10S-4$; prefixes with equal $\delta$ differ by a multiple of $10$. Thus connected contacts have identical prefix values and identical $\delta$.

Every auxiliary component meets at least one path, since the full graph is connected and all nonauxiliary edges are on the paths or $AB$. A component away from $A,B$ meeting only one path would have exactly two edges leaving it: the long edge entering and the long edge leaving its constant-prefix interval. Three-edge-connectivity forbids this. Therefore the two paths have the same increasing list of long prefixes. Their long-edge sequences coincide. Removing the $b$ edge from each leaves identical item sequences, proving the even multiplicities.

For $S=1$, the first path-count argument already forces the only possible item list to be $(1,1)$, so the conclusion also holds. $\square$

For example $(1,2,4,7)$ is a YES instance of equal-sum partition, but its multiplicities violate Proposition 6.1. Thus small auxiliary additions cannot turn this particular source map into a reduction for general instances.

With just the original single auxiliary edge of length one, the failure is stronger: for $m>2$ no genuine convex polytope realizes the output. Ignoring auxiliary edges, the two paths and $AB$ have $m$ internal vertices of degree two. An off-path auxiliary edge supplies additional incidence to at most two of them; putting it on a path only creates an extra internal vertex and uses up the auxiliary edge. Minimum degree three is impossible.

## 7. Exact checks and reproducibility

The arguments above are uniform proofs. Finite computations were used to audit identities and complete geometric witnesses, not to turn unsuccessful numerical searches into nonexistence claims.

The Python program in Appendix A is self-contained and uses only the standard library. Equalities are reduced formally in products of positive square roots using rational coefficients. Strict signs use outward rational intervals obtained by integer square roots. No floating-point residual is accepted as an exact length or convexity certificate.

The program checks two matched instances, with pairs $(1,4),(2,5)$ and $(1,4),(2,5),(3,6)$ and their corresponding sum targets. The resulting witnesses have $(V,E,F)=(20,30,12)$ and $(30,45,17)$. It checks the complete supporting-facet description, strict convexity within each facet, the full edge-length multiset, and Euler's formula. It also checks $1,250$ exact comparisons for the two unintended vertical-edge roles in Section 5.4 at $m=2,B=25$, and the complete alternative-prism multiset of Section 6.1. These examples use the pairing formulation directly; the offsets in Section 5.1 are needed for the reduction's source equivalence, not for constructing these test witnesses.

These checks all pass. They do not independently certify the universal structural theorems; those rest on their proofs. The manuscript makes no claim of independent peer review or exhaustive literature novelty.

## 8. What remains unresolved

The results do not supply a polynomial-time algorithm or an NP-hardness reduction for unrestricted unordered edge realization. The existential-real formulation gives an upper bound. The hierarchy theorem forces graph operations but leaves the locations and geometry of those operations open. The rational reduction proves hardness only with the geometric family restriction, and the alternative prism demonstrates that omitting that restriction can destroy soundness.

A possible next direction is to use the forced hierarchy to encode choices of expanded vertices, together with a numerical state whose feasible transitions are controlled by actual edge lengths. Such an argument would have to exclude every unintended vertex choice, cone configuration and metric branch, and provide both polynomial encoding bounds and complete YES realizations. No such transition or acceptance construction is established here.

## AI disclosure

The mathematical exploration, draft proofs, verification code and manuscript were developed with assistance from OpenAI through the Codex agent client. The exact underlying model identifier and model version were not available for this submission and are declared `unknown`. The mathematical claims and their limitations are stated explicitly above; automated archive admission is not a correctness certificate for them.

## References

1. Brendan Lucier. *Unfolding and Reconstructing Polyhedra*. University of Waterloo, 2006. See Theorem 6.5.8 and Section 6.5.4. [Repository record](https://uwspace.uwaterloo.ca/items/69b70b9e-d3ba-4e86-98fc-042f61dea62f); [full text](https://dspacemainprd01.lib.uwaterloo.ca/server/api/core/bitstreams/a6fcf674-1587-4f72-a74f-ca50ece1d230/content).
2. M. L. Balinski. On the graph structure of convex polyhedra in $n$-space. *Pacific Journal of Mathematics* **11**(2), 431–434, 1961. [DOI: 10.2140/pjm.1961.11.431](https://doi.org/10.2140/pjm.1961.11.431); [publisher PDF](https://msp.org/pjm/1961/11-2/pjm-v11-n2-p03-s.pdf).
3. MIT Hardness Group, Erik D. Demaine, Holden Hall, and Jeffery Li. *Tetris with Few Piece Types*. arXiv:2404.10712v1, 2024. Section 3, Theorem 3.3 establishes the numerical matching source used here. [Version cited](https://arxiv.org/html/2404.10712v1#S3).

## Appendix A. Reproducible exact audit

Save the following block as `polyhedron_audit.py` and run `python3 polyhedron_audit.py`. It needs Python 3.10 or later and no external packages. The square-root algebra only uses its formal reduction as a sufficient equality certificate; it does not assume algebraic independence of the radicands. Interval uncertainty causes a strict inequality check to fail rather than accepting an unproved sign.

```python
"""Exact checks for the RATIONAL truncated-prism-family reduction.

Save as polyhedron_audit.py and run with Python 3.10 or later.
The output-family restriction is essential.  This is NOT a hardness proof
for arbitrary convex polyhedra: duplicate_source_escape checks a counterexample.
"""

from collections import Counter
from fractions import Fraction as F
from math import isqrt

class I:
    def __init__(self, lo, hi=None):
        self.lo = F(lo)
        self.hi = F(lo if hi is None else hi)
        assert self.lo <= self.hi

    @staticmethod
    def of(x):
        return x if isinstance(x, I) else I(x)

    def __add__(self, other):
        other = I.of(other)
        return I(self.lo + other.lo, self.hi + other.hi)
    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo)

    def __sub__(self, other):
        return self + (-I.of(other))

    def __rsub__(self, other):
        return I.of(other) - self

    def __mul__(self, other):
        other = I.of(other)
        p = [a*b for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        return I(min(p), max(p))
    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I.of(other)
        assert other.hi < 0 or other.lo > 0, "division interval includes zero"
        return self * I(1/other.hi, 1/other.lo)

    def sqrt(self, places=30):
        assert self.lo >= 0
        scale = 10**places
        def lower(x):
            return F(isqrt((x.numerator*scale*scale)//x.denominator), scale)
        return I(lower(self.lo), lower(self.hi) + F(1, scale))

    def excludes_zero(self):
        return self.lo > 0 or self.hi < 0

    def absolute_lower(self):
        return min(abs(self.lo), abs(self.hi)) if self.excludes_zero() else F(0)

def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))

def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))



class R:
    """Exact sums of products of specified positive square roots.

    Equality is certified by formal reduction using sqrt(d_i)^2=d_i.
    Strict inequalities use outward rational intervals, never floats.
    Algebraic independence is unnecessary: formal zero is always real zero.
    """

    radicands = []
    root_intervals = []

    def __init__(self, value=0):
        self.terms = value if isinstance(value, dict) else {0: F(value)}
        self.terms = {mask: c for mask, c in self.terms.items() if c}

    @classmethod
    def root(cls, value):
        value = F(value)
        assert value > 0
        mask = 1 << len(cls.radicands)
        cls.radicands.append(value)
        cls.root_intervals.append(I(value).sqrt(places=80))
        return cls({mask: F(1)})

    @staticmethod
    def of(value):
        return value if isinstance(value, R) else R(value)

    def __add__(self, other):
        result = self.terms.copy()
        for mask, c in R.of(other).terms.items():
            result[mask] = result.get(mask, F(0))+c
        return R(result)
    __radd__ = __add__

    def __neg__(self):
        return R({mask: -c for mask, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-R.of(other))

    def __rsub__(self, other):
        return R.of(other) - self

    def __mul__(self, other):
        result = {}
        for a, ca in self.terms.items():
            for b, cb in R.of(other).terms.items():
                coefficient = ca*cb
                overlap = a & b
                while overlap:
                    bit = overlap & -overlap
                    coefficient *= self.radicands[bit.bit_length()-1]
                    overlap -= bit
                mask = a ^ b
                result[mask] = result.get(mask, F(0))+coefficient
        return R(result)
    __rmul__ = __mul__

    def __eq__(self, other):
        return not (self-R.of(other)).terms

    def interval(self):
        result = I(0)
        for mask, c in self.terms.items():
            term = I(c)
            while mask:
                bit = mask & -mask
                term *= self.root_intervals[bit.bit_length()-1]
                mask -= bit
            result += term
        return result

    def __gt__(self, other):
        return (self-other).interval().lo > 0

    def __lt__(self, other):
        return (self-other).interval().hi < 0

    def rational(self):
        assert set(self.terms) <= {0}, 'Nonrational formal expression'
        return self.terms.get(0, F(0))


def parameters(m, B):
    return F(1, 10**6 * m*m * B), F(1, 10**6 * m*m * B**3)


def edge_multiset(items, targets):
    m = len(targets)
    assert m >= 1 and len(items) == 2*m
    assert min(items + targets) > 0 and sum(items) == sum(targets)
    B = max(items + targets)
    eta, eps = parameters(m, B)
    b, p = {}, {}
    for j in set(items):
        t = eps*j/2
        b[j] = 2*t/(1-t*t)
        p[j] = (1+t*t)/(1-t*t)
        assert p[j]**2 == 1+b[j]**2
        assert eps*j <= b[j] <= eps*j+eps**3*j**3/2
        assert 0 < b[j] < F(1, 1000)
        assert 1 < p[j] < F(1001, 1000)
    r = {w: eps*(w-eta) for w in set(targets)}
    assert all(0 < v < F(1, 1000) for v in r.values())
    wanted = Counter()
    wanted.update(p[j] for j in items)
    wanted.update(100-b[j] for j in items)
    wanted.update(r[w] for w in targets)
    wanted[100] += 6*m
    wanted[9] += m
    wanted[10] += 3*m
    assert sum(wanted.values()) == 15*m
    return eta, eps, b, p, r, wanted


def witness(pairs, targets):
    """Verify supporting facets and ALL actual edges using exact radicals."""
    assert all(u+v == w for (u, v), w in zip(pairs, targets))
    items = [j for pair in pairs for j in pair]
    eta, eps, b, _, r, wanted = edge_multiset(items, targets)
    m = len(targets)
    R.radicands, R.root_intervals = [], []
    directions = []
    for i, ((u, v), w) in enumerate(zip(pairs, targets)):
        t = F(i, m)
        x, y = R((1-t*t)/(1+t*t)), R(2*t/(1+t*t))
        cosine = (r[w]**2-b[u]**2-b[v]**2)/(2*b[u]*b[v])
        assert 0 < cosine < 1
        assert 1-cosine <= 3*eta*max(items+targets)
        sine = R.root(1-cosine*cosine)
        directions += [(x, y), (x*cosine-y*sine, x*sine+y*cosine)]
    directions += [(-x, -y) for x, y in directions]
    n = len(directions)
    base = []
    x = y = R(0)
    for dx, dy in directions:
        assert dx*dx+dy*dy == 1
        base.append((x, y))
        x += 100*dx
        y += 100*dy
    assert x == y == 0

    points = [(x, y, R(0)) for x, y in base]
    top, caps = {}, {}
    selected = {2*i+1: i for i in range(m)}
    for i, (x, y) in enumerate(base):
        if i not in selected:
            top[i] = len(points)
            points.append((x, y, R(10)))
        else:
            u, v = pairs[selected[i]]
            left, right = directions[i-1], directions[i]
            a = len(points)
            points.append((x, y, R(9)))
            bb = len(points)
            points.append((x-b[u]*left[0], y-b[u]*left[1], R(10)))
            c = len(points)
            points.append((x+b[v]*right[0], y+b[v]*right[1], R(10)))
            caps[i] = (a, bb, c)

    faces = [list(reversed(range(n)))]
    topface = []
    for i in range(n):
        topface.extend(caps[i][1:] if i in caps else [top[i]])
    faces.append(topface)
    for i in range(n):
        j = (i+1) % n
        if i in caps:
            a, bb, c = caps[i]
            faces.append([i, j, top[j], c, a])
        elif j in caps:
            a, bb, c = caps[j]
            faces.append([i, j, a, bb, top[i]])
        else:
            faces.append([i, j, top[j], top[i]])
    faces.extend([a, c, bb] for a, bb, c in caps.values())

    edges = Counter()
    for face in faces:
        p0, p1, p2 = [points[i] for i in face[:3]]
        normal = cross(sub(p1, p0), sub(p2, p0))
        assert dot(normal, normal) > 0
        assert all(dot(normal, sub(points[i], p0)) == 0 for i in face)
        values = [dot(normal, sub(p, p0)) for i, p in enumerate(points) if i not in face]
        assert all(v > 0 for v in values) or all(v < 0 for v in values)
        for a, bb in zip(face, face[1:]+face[:1]):
            # Each listed boundary segment is an exposed edge of the facet;
            # this excludes interior points, diagonals and collinear splits.
            assert all(dot(normal, cross(sub(points[bb], points[a]),
                                         sub(points[k], points[a]))) > 0
                       for k in face if k not in (a, bb))
            edges[tuple(sorted((a, bb)))] += 1
    assert all(count == 2 for count in edges.values())
    actual = Counter(dot(sub(points[i], points[j]), sub(points[i], points[j])).rational()
                     for i, j in edges)
    expected = Counter({length*length: count for length, count in wanted.items()})
    assert actual == expected
    assert len(points)-len(edges)+len(faces) == 2
    return len(points), len(edges), len(faces)


def check_depth_exclusion(B=25, m=2):
    """Check exact small instances of the two unintended vertical roles.

    Uniform estimates, rather than these finite checks, prove the theorem.
    """
    eta, eps = parameters(m, B)
    assert 5*eps*eps*B**4 < 1
    assert eps*eps*B**3 < eta
    b, p = {}, {}
    for j in range(1, B+1):
        t = eps*j/2
        b[j] = 2*t/(1-t*t)
        p[j] = (1+t*t)/(1-t*t)
        y = p[j]-1
        assert abs(b[j]**2-eps**2*j*j) <= eps**4*j**4
        assert abs(18*y-y*y-9*eps**2*j*j) < 4*eps**4*j**4
        assert (18-y)/(2+y) < 9
    for j in range(1, B//3+1):
        assert b[3*j] > 3*b[j]
    for n in range(1, B+1):
        for j in range(1, B+1):
            assert b[n]**2 != 81-(10-p[j])**2
        for w in range(1, B+1):
            r = eps*(w-eta)
            assert b[n]**2 < 20*r-r*r
    return B*B*2


def duplicate_source_escape():
    items = [31]*4+[91]*4
    targets = [121]*2+[123]*2
    assert sum(items) == sum(targets)
    assert all(a+b not in targets for a in set(items) for b in set(items))
    *_, wanted = edge_multiset(items, targets)
    leftover = wanted.copy()
    leftover[100] -= 20
    assert all(count >= 0 and count % 2 == 0 for count in leftover.values())
    base = Counter({length: count//2 for length, count in leftover.items() if count})
    assert sum(base.values()) == 20
    assert max(base) == 100 and base[100] >= 2
    assert max(base) < sum(length*count for length, count in base.items())-max(base)
    actual = Counter({length: 2*count for length, count in base.items()})
    actual[100] += 20
    assert actual == wanted
    return sum(wanted.values())


def main():
    print('Exact unintended-depth checks:', check_depth_exclusion(), flush=True)
    for pairs in [[(1, 4), (2, 5)], [(1, 4), (2, 5), (3, 6)]]:
        targets = [u+v for u, v in pairs]
        print('Exact rational-length YES witness (V,E,F):', witness(pairs, targets), flush=True)
    print('Exact NO-source / alternative prism edge count:', duplicate_source_escape(), flush=True)
    print('NP-hardness applies only with the output-family restriction.', flush=True)


if __name__ == '__main__':
    main()
```
