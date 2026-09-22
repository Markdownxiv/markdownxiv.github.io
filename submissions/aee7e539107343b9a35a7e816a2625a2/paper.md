# Exact Prime Counting at the Square-Root Scale: Modular Reductions and Direct Local Integration

**Kaiyi Zhang**  
Research note, 22 September 2026  
License: CC-BY-4.0

## Abstract

We organize an exploratory study of exact computation of the prime-counting function $\pi(N)$ in the classical computational model. No algorithm with running time $O(N^{1/2-\delta})$, for fixed $\delta>0$, is obtained, either unconditionally or under the Riemann hypothesis. The useful outcomes are explicit reductions, local analytic constructions, and checks of several possible sources of hidden cost. For fixed $\alpha\in[1/3,1/2]$, we give exponent-preserving reductions between $\pi(N)\bmod 3$ and the ternary divisor summatory function $D_3(N)\bmod 9$. We record precision-lifting identities and a degree obstruction for a specified class of zeta-product representations. On the analytic side, a bounded two-variable representation of a local zeta batch permits controlled logarithm expansion and direct oscillatory integration. Cardinal B-spline windows reduce the required output to a polylogarithmic number of resonant frequencies; marked rational-function coefficient extraction computes these without first expanding the complete logarithm. The current construction still incurs essentially linear total work in the integration height. We also state a provisional time-space combination, explain its unverified interfaces, and separate it from established bounds. Reference computations and their source code accompany the note. They verify finite identities and numerical formulas, not the asymptotic performance of an optimized prime-counting implementation.

## 1. Scope, computational model, and status

The input is an integer $N\ge 2$ and the desired output is the complete integer

$$
\pi(N)=\#\{p\le N:p\text{ is prime}\}.
$$

The motivating objective is a fixed-power improvement over the square-root time exponent. Computing an approximation, a single residue, or a special family of inputs does not meet that objective. Input-dependent tables, zero lists, preprocessing, precision, and reconstruction are charged. Parallel depth is not substituted for total work.

We use the usual classical arithmetic/bit model with integers of $O(\log N)$ bits, or explicitly stated polylogarithmic working precision. Expressions $N^{a+o(1)}$ suppress subpower factors; bounds with $+\varepsilon$ are interpreted as algorithm families for each fixed $\varepsilon>0$.

Three levels of evidence are distinguished throughout:

1. **Identities and reductions:** algebraic statements with proofs, additionally checked on finite inputs.
2. **Working algorithmic constructions:** combinations of established subroutines with explicit cost and precision calculations. Their full interfaces and implementations are not independently certified here.
3. **Reference computations:** finite exact checks or high-precision, non-interval numerical comparisons. These are not performance measurements of the proposed asymptotic methods.

We do not claim novelty for the elementary identities or for recombining existing subroutines. In particular, the $5/11$ parity exponent below was already recorded in the 2009 Polymath discussion. The degree, rank, and cost observations in this note constrain specified representations or arguments; none is a lower bound for arbitrary algorithms computing $\pi(N)$.

### 1.1. Baselines used in the study

Lagarias and Odlyzko give an unconditional analytic algorithm with time $O_\varepsilon(N^{1/2+\varepsilon})$ and space $O_\varepsilon(N^{1/4+\varepsilon})$, together with a time-space tradeoff [LO]. Hirsch, Kessler, and Mendlovic provide elementary square-root-scale algorithms for prime counting and the Mertens function [HKM]. For the binary divisor sum we use the $x^{1/3+o(1)}$ subroutine discussed in [Polymath]; [Sladkey] is a related implementation-oriented reference. Gourdon's method as implemented in [primecount] is a practical comparison point, but this work contains no benchmark against that software.

The principal outcomes and their limits are:

| Object | Outcome | Limit |
|---|---|---|
| Full $\pi(N)$ | No fixed-power improvement obtained | The original time objective remains open in this study |
| $\pi(N)\bmod 2$ | Recovered the known $N^{5/11+o(1)}$ combination | One bit only; not a new result |
| $\pi(N)\bmod 3$ | Equivalent, in the stated exponent range, to $D_3(N)\bmod 9$ | The faster ternary primitive is missing |
| Local $\log\zeta$ integral | Direct coefficient-and-moment construction | Current total work remains $T N^{o(1)}$ |
| Resonant outputs | Only $O(\log N)$ frequencies per smooth window are needed | Input polynomial degree is still charged |
| Analytic storage | Provisional endpoint $N^{2/13+\varepsilon}$ at square-root time | Not a verified new record or complete implementation |

## 2. Modular information and complete reconstruction

If an integer $P$ is known to lie in $[L,U]$ and $P\equiv r\pmod Q$, its candidates are

$$
P=r+kQ,\qquad
\left\lceil\frac{L-r}{Q}\right\rceil\le k\le
\left\lfloor\frac{U-r}{Q}\right\rfloor.
$$

There is at most one candidate when $Q>U-L$. Under RH, the usual error interval around $\operatorname{Li}(N)$ has width $O(\sqrt N\log N)$. Thus a sufficiently large product of small prime moduli would determine $\pi(N)$, provided both the interval and all residues are correctly computed.

By the prime number theorem,

$$
\prod_{q\le c\log N\atop q\ {
m prime}}q=N^{c+o(1)}.
$$

Any fixed $c>1/2$ suffices for the RH interval; $c>1$ suffices with the crude unconditional interval $[0,N]$. The missing premise is a **uniform** fast residue algorithm up to $q=O(\log N)$. A bound $C(q)N^\alpha$ for every fixed $q$ is insufficient if $C(q)$ grows exponentially and restores a power of $N$. Polynomial overhead in $q$ would be sufficient. This reconstruction strategy is already part of the Polymath discussion [Polymath]. RH changes the required amount of modular information; it does not supply the residue algorithm.

### 2.1. The known parity combination

Write

$$
D_2(x)=\sum_{m\le x}\tau(m),\qquad
M(x)=\sum_{d\le x}\mu(d),\qquad
A(N)=\sum_{m\le N}2^{\omega(m)}.
$$

Checking prime powers and using multiplicativity gives

$$
A(N)=\sum_{d\le\sqrt N}\mu(d)D_2(\lfloor N/d^2\rfloor),
\qquad
A(N)\equiv1+2\sum_{a\ge1}\pi(\lfloor N^{1/a}\rfloor)\pmod4.
\tag{1}
$$

For an integer cutoff $Y$, put $K=\lfloor N/(Y+1)^2\rfloor$. The tail in the first sum can be grouped exactly as

$$
\sum_{k=1}^{K}D_2(k)
\left[
M(\lfloor\sqrt{N/k}\rfloor)-
M\bigl(\max(Y,\lfloor\sqrt{N/(k+1)}\rfloor)\bigr)
\right].
\tag{2}
$$

Using $D_2(x)$ in $x^{1/3+o(1)}$ time and deterministic $M(x)$ in $x^{1/2+o(1)}$ time [Polymath, HKM], the two main costs are

$$
N^{1/3}Y^{1/3}N^{o(1)}
\quad\hbox{and}\quad
NY^{-3/2}N^{o(1)}.
$$

They balance at $Y=N^{4/11+o(1)}$, giving $N^{5/11+o(1)}$. Sieving through $Y$ and preparing divisor sums through $K$ have smaller exponents. The higher-prime-power correction in (1) costs $N^{1/4+o(1)}$ using square-root-scale prime counting at smaller inputs. Division by $2$ requires the residue modulo $4$ before reduction modulo $2$.

The same $5/11$ exponent was explicitly mentioned in the 2009 research discussion [Nielsen]. This calculation is a verification of a known baseline, not a claim of a new sub-square-root algorithm for full prime counting.

### 2.2. Odd-prime residues

Let $q\ge3$ be prime and define formal Dirichlet series

$$
F_q(s)=\frac{\zeta(s)^q}{\zeta(qs)}
       =\sum_{m\ge1}\frac{f_q(m)}{m^s}.
$$

Its Euler factor satisfies

$$
\log\frac{1-t^q}{(1-t)^q}
=q\sum_{a\ge1,\ q\nmid a}\frac{t^a}{a}.
$$

Since $v_q(q^k/k!)\ge2$ for $k\ge2$, exponentiation modulo $q^2$ shows that the coefficient at $p^a$ is $q/a$ when $q\nmid a$ and is $0$ otherwise. Coefficients supported on two or more distinct primes vanish modulo $q^2$. Consequently,

$$
\pi(N)\equiv
\frac{F_q^\Sigma(N)-1}{q}
-\sum_{a\ge2,\ q\nmid a}a^{-1}\pi(\lfloor N^{1/a}\rfloor)
\pmod q,
\tag{3}
$$

where

$$
F_q^\Sigma(N)=\sum_{d\le N^{1/q}}\mu(d)D_q(\lfloor N/d^q\rfloor),
\qquad D_q(N)=\#\{(a_1,\ldots,a_q)\in\mathbb Z_{>0}^q:a_1\cdots a_q\le N\}.
$$

The division in (3) is performed after retaining modulus $q^2$; the remaining inverses are units modulo $q$. The argument fails for $q=2$, where the quadratic exponential term need not vanish modulo $4$; that case must use (1).

## 3. The first odd residue and a ternary counting problem

Set

$$
F=\frac{\zeta(s)^3}{\zeta(3s)}=1+3B(s).
$$

The coefficients of $B$ are integers. For any fixed $\alpha\in[1/3,1/2]$, an $N^{\alpha+o(1)}$ algorithm for either $\pi(N)\bmod3$ or $D_3(N)\bmod9$ gives one for the other, with no larger exponent.

**From $D_3$ to $\pi$.** Use

$$
1+3B^\Sigma(N)=\sum_{d\le N^{1/3}}\mu(d)D_3(\lfloor N/d^3\rfloor).
\tag{4}
$$

The total oracle work is $N^{\alpha+o(1)}\sum_{d\le N^{1/3}}d^{-3\alpha}$, with only an extra logarithm at $\alpha=1/3$. The Möbius sieve costs $N^{1/3+o(1)}$, and (3) removes higher prime powers.

**From $\pi$ to $D_3$.** Since $\zeta(s)^3=F\zeta(3s)$,

$$
D_3(N)\equiv\lfloor N^{1/3}\rfloor
+3\sum_{d\le N^{1/3}}B^\Sigma(\lfloor N/d^3\rfloor)\pmod9.
\tag{5}
$$

Recover $B^\Sigma(X)\bmod3$ from the prime-counting residue and its root corrections. Summing their costs gives at most $N^{1/3+o(1)}$ for the extra root calls when $\alpha\le1/2$. This proves the stated reduction. It still recovers only one ternary digit of the full answer.

### 3.1. Equal coordinates can be removed cheaply

Define

$$
A_3(N)=\#\{1\le a<b<c:abc\le N\},\qquad
E(N)=\#\{a,b\ge1:a\ne b,\ a^2b\le N\},\qquad
C(N)=\lfloor N^{1/3}\rfloor.
$$

Coordinate permutations give

$$
D_3(N)=6A_3(N)+3E(N)+C(N).
\tag{6}
$$

Also $E(N)+C(N)=\sum_{a\le\sqrt N}\lfloor N/a^2\rfloor$. With $u=C(N)$ and $K=\lfloor N/(u+1)^2\rfloor\le u$, this equals

$$
\sum_{a=1}^{u}\left\lfloor\frac N{a^2}\right\rfloor
+\sum_{v=1}^{K}v
\left[
\left\lfloor\sqrt{N/v}\right\rfloor
-\max\left(u,\left\lfloor\sqrt{N/(v+1)}\right\rfloor\right)
\right].
\tag{7}
$$

There are at most $2u$ terms. Thus the equal-coordinate part takes $N^{1/3+o(1)}$ time and subpower workspace. The remaining task is $A_3(N)\bmod3$; the orbit multiplicity $6$ does not vanish modulo $9$.

## 4. Precision lifting and its representation cost

Write $Z=\zeta(s)$, $Z_3=\zeta(3s)$ and $A_0=Z^2/Z_3$. Then $ZA_0=1+3B$. The finite geometric inverse is

$$
A_{[m]}=A_0\sum_{j=0}^{m-1}(1-ZA_0)^j
=\sum_{j=1}^{m}(-1)^{j+1}\binom mj\frac{Z^{3j-1}}{Z_3^j}
\equiv Z^{-1}\pmod{3^m}.
\tag{8}
$$

This is a coefficient identity in a Dirichlet-series ring. The prefix map is not a ring homomorphism, so Newton iteration cannot be applied to a single Mertens prefix value as if it were an ordinary scalar inverse.

Frobenius gives a useful low-precision reduction. Since $A_{[3]}=Z^{-1}(1+27B^3)$ and $B(s)^3\equiv B(3s)\pmod3$,

$$
Z^{-1}\equiv
12\frac{Z^2}{Z_3}-3\frac{Z^5}{Z_3^2}+\frac{Z^8}{Z_3^3}
-9\frac{Z^2Z_3^2}{\zeta(9s)}\pmod{81}.
\tag{9}
$$

The largest unscaled zeta power is $8$, rather than $11$ from a direct four-term geometric inverse. The added correction has cube-root-scale prefix cost using $D_2$. However, the prefix of $A_{[3]}$ is still needed modulo $81$; knowing only its value modulo $27$ does not supply that information. Equation (9) is not a cube-root algorithm for $M(N)\bmod81$.

The integral $3$-adic logarithm

$$
L_3(s)=\frac{3\log\zeta(s)-\log\zeta(3s)}3
=\frac{\log(1+3B)}3
=\sum_p\sum_{a\ge1,\ 3\nmid a}\frac{p^{-as}}a
\tag{10}
$$

directly recovers prime-counting residues after the root corrections. Its low-precision forms include

$$
\begin{aligned}
L_3&\equiv B &&\pmod3,\\
L_3&\equiv B+3B^2+3B(3s) &&\pmod9,\\
L_3&\equiv B+12B^2+3B^3 &&\pmod{27},\\
L_3&\equiv B+39B^2+3B^3+54B(s)B(3s) &&\pmod{81}.
\end{aligned}
\tag{11}
$$

Products in these formulas are Dirichlet convolutions. Their prefixes are additional computations, not products of already known prefixes.

### 4.1. A degree certificate for a specified class

Consider a finite expression

$$
G(s)=\sum_\nu c_\nu\zeta(s)^{a_\nu}H_\nu(s),\qquad 0\le a_\nu\le D,
$$

where $H_\nu$ consists of integer powers of $\zeta(ds)$ with $d\ge2$. On a squarefree integer having $r$ distinct prime factors, its coefficient is $g_r=\sum_\nu c_\nu a_\nu^r$. If $E$ shifts $r$, then

$$
P(E)g=0,\qquad P(X)=\prod_{a=0}^{D}(X-a).
$$

For the target Möbius sequence $(-1)^r$, coefficientwise congruence modulo $p^k$ therefore requires

$$
v_p((D+1)!)\ge k.
\tag{12}
$$

For $L_3$, the squarefree target is $\mathbf1_{r=1}$; the same argument gives

$$
v_3(D!)\ge k.
\tag{13}
$$

Thus the minimum possible unscaled degrees for $L_3$ modulo $3,9,27,81$ in this class are $3,6,9,9$, achieved by (11). For a restriction to indices at most $N$, the argument needs the product of the first $D+1$ primes to be at most $N$. It cannot be extrapolated to arbitrary growing $D$ without that condition. This is a representation certificate, not a general counting lower bound.

## 5. Why several apparent shortcuts do not give a time bound

### 5.1. Truncated logarithms and explicit coefficient tables

On $\Re s=2$, the series in $\zeta(s)-1$ converges absolutely. Nevertheless, truncating

$$
\log\zeta(s)=\sum_{k\ge1}\frac{(-1)^{k+1}}k(\zeta(s)-1)^k
$$

at a fixed degree $d$ leaves coefficient $(-1)^{d+1}d!$ on a product of $d+1$ distinct primes, instead of $0$. For example, the quadratic truncation leaves $-2$ at $30$.

Presieving changes which degrees are required, but does not make a large Euler-product expansion free. Likewise, if $M_y(s)=\sum_{d\le y}\mu(d)d^{-s}$, every nonzero summand in the coefficient of $M_y^k$ has the same sign, $(-1)^{\Omega(m)}$. There is no internal sign cancellation at a fixed product. For fixed $k$, its support contains $y^{k-o(1)}$ distinct products: use squarefree factors in a fixed proportional subinterval of $[1,y]$ and the standard subpower bound on divisor multiplicities. Explicitly generating the pair or triple table at $y=N^{1/3}$ therefore exceeds the target budget. This does not rule out direct prefix aggregation.

### 5.2. Carries are not removed by coefficient divisibility

For logarithmic bins $b(m)=\lfloor\log_{3/2}m\rfloor$, one has $b(2)=1$, $b(3)=2$, $b(5)=3$, and $b(6)=4$. In a three-factor convolution, the allocations of the two primes in $6$ contribute

$$
6z^3+3z^4.
$$

The sum of the coefficients vanishes modulo $9$, but a cutoff through degree $3$ retains $6$. Hence divisibility of the exact product coefficient does not justify omitting bin-boundary corrections.

The carry matrix

$$
C_q(u,v)=\left\lfloor\frac{u+v}{q}\right\rfloor,\qquad0\le u,v<q,
$$

has rank $q-1$ over $\mathbb F_3$. Indeed, rows $u=1,\ldots,q-1$ and reversed columns $v=q-j$ form a unit lower triangular matrix. The same minor is a unit modulo $9$. Consequently a uniform separable representation $\sum_{i=1}^r f_i(u)g_i(v)$ needs $r\ge q-1$.

There are explicit low-moment counterexamples. For $q>r$, the signed vector $v_u=(-1)^u\binom ru$, $0\le u\le r$, has zero moments of orders $0,\ldots,r-1$. Its positive and negative parts are nonnegative histograms with identical such moments. Pairing them with the single residue $q-r$ produces carry totals differing by $(-1)^r$. These statements concern general histograms or specified moment representations, not every algorithm for the structured distributions arising here.

### 5.3. Frobenius orbits retain arithmetic costs

For prime $q\ne3$, the nonzero Fourier frequencies split under multiplication by $3$ into $(q-1)/d$ orbits of length $d=\operatorname{ord}_q(3)$. Their sums can be written as traces in a degree-$d$ unramified $3$-adic extension. Expanding one representative per orbit still produces $d(q-1)/d=q-1$ base-ring coordinates. Fast trace arithmetic [Hubrechts] does not make the extension degree free. This observation does not rule out taking traces directly from a special sparse or circuit representation.

At precision $9$, lifted Frobenius is not ordinary cubing. With a primitive fifth root $\zeta$,

$$
(1+\zeta)^3-\sigma(1+\zeta)=3\zeta+3\zeta^2\ne0\pmod9.
$$

Nor does orbit length divisible by $3$ imply zero trace: in $\mathbb F_{27}=\mathbb F_3[u]/(u^3-u-1)$, one has $\operatorname{Tr}(u^2)=2$.

## 6. Local geometry: useful formulas and their domain of applicability

In a balanced box, write $f(a,b)=N/(ab)$, with $a_0,b_0,C=N/(a_0b_0)\asymp N^{1/3}$. For $u=(a-a_0)/a_0$, $v=(b-b_0)/b_0$, $0\le u,v\le\delta\le1/2$, put

$$
P_1=C(1-u-v),\qquad P_2=C(1-u-v+u^2+uv+v^2).
$$

Then

$$
P_1\le f\le P_2,\qquad
f-P_1\le4C\delta^2,\qquad P_2-f\le6C\delta^3.
\tag{14}
$$

The last inequality follows by expanding the exact numerator of $(P_2-f)/C$:

$$
\frac{u^3+u^2v+uv^2+v^3+u^3v+u^2v^2+uv^3}{(1+u)(1+v)}.
$$

If a quadratic patch of side $h=N^{1/3}\delta$ could be counted in $h^{\gamma+o(1)}$ time, then the balanced-box model would cost

$$
N^{\gamma/3}\delta^{\gamma-2}+N\delta^3,
$$

whose optimized exponent is $2/(5-\gamma)$. This needs $\gamma<1$ to beat $1/2$. Such a general patch primitive has not been constructed here, and unbalanced regions and modulus growth would still need treatment. Fixed-dimensional polytope counting does not apply directly to a quadratic boundary [Barvinok].

### 6.1. Complete quadratic periods

For a prime $q>3$, let $\chi$ be the Legendre symbol and $q\nmid a$. Define

$$
F_q(a,b,c)=\sum_{k=0}^{q-1}\left\lfloor\frac{ak^2+bk+c}{q}\right\rfloor,\qquad
d=\bigl(c-b^2(4a)^{-1}\bigr)\bmod q,\qquad
C_q(d)=\sum_{r=1}^{d}\chi(r).
$$

Here $0\le d<q$. Let $H_q=0$ for $q\equiv1\pmod4$ and $H_q=h(-q)$ for $q\equiv3\pmod4$. Completing the square and summing least nonnegative residues gives

$$
F_q(a,b,c)=\frac{a(q-1)(2q-1)}6+\frac{b(q-1)}2+c-\frac{q-1}2
+\chi(a)H_q+\chi(a)\chi(-1)C_q(d).
\tag{15}
$$

The class-number formula supplies $\sum r\chi(r)=-qh(-q)$ in the odd-character case. Booker provides a class-number algorithm with $q^{1/4+\varepsilon}$ running time under GRH [Booker]. This handles the special $d=0$ term, not arbitrary shifts: the remaining $C_q(d)$ is an incomplete character sum. In fact,

$$
C_q(d)=\chi(-1)\bigl(F_q(1,0,d)-F_q(1,0,0)-d\bigr).
$$

For $q=7,a=1,b=0,c=1$, omitting the character-prefix term gives $12$ instead of $11$. The powerful-modulus character-sum acceleration in [Hiary-characters] does not automatically cover prime modulus $q$.

For a nondegenerate binary quadratic polynomial

$$
Q(x,y)=ax^2+bxy+cy^2+dx+ey+f,\qquad \Delta=4ac-b^2\not\equiv0\pmod q,
$$

put $t=(f-(cd^2-bde+ae^2)\Delta^{-1})\bmod q$ and $\eta=\chi(-\Delta)$. With $S_1=q(q-1)/2$, $S_2=q(q-1)(2q-1)/6$ and

$$
P=(a+c)qS_2+bS_1^2+(d+e)qS_1+fq^2,
$$

one has

$$
\sum_{0\le x,y<q}\left\lfloor\frac{Q(x,y)}q\right\rfloor
=\frac{P-(q-\eta)q(q-1)/2-q\eta t}{q}.
\tag{16}
$$

Indeed, the completed quadratic form represents a nonzero value $q-\eta$ times and zero $q+(q-1)\eta$ times. Formula (16) is inexpensive, but it requires a complete period.

Replacing the local quadratic by a short-period approximation is not free. At $N=A^3$, $a_0=b_0=A$, the quadratic coefficient of $x^2$ is $1/A$. If even $h\le A/2$ and a replacement has common denominator $q\le h$, its $x^2$ coefficient $m/q$ differs by at least $1/A$. The second difference at $0,h/2,h$ forces uniform error at least $h^2/(8A)$, which exceeds the desired $O(h^3/A^2)$ scale when $h=o(A)$.

This is only an approximation-model obstruction. The symmetric block itself is easy when $3h^2<A$: its integer tangent plane gives

$$
\sum_{x,y=0}^{h}\left\lfloor\frac{A^3}{(A+x)(A+y)}\right\rfloor
=(h+1)^2(A-h).
$$

### 6.2. An exact convex-cap reduction

Let $U=P_1+\max Q$ be the affine upper plane, where $Q=P_2-P_1$. On an integer rectangle,

$$
\sum\lfloor f\rfloor=\sum\lfloor U\rfloor-\#(K_N\cap\mathbb Z^3),
$$

where

$$
K_N=\left\{(x,y,z):\frac{N+1}{(a_0+x)(b_0+y)}\le z\le U(x,y), (x,y)\text{ in the rectangle}\right\}.
\tag{17}
$$

The $+1$ is essential: $z>f(x,y)$ becomes $(a_0+x)(b_0+y)z\ge N+1$ on integer points. The lower graph is convex, so $K_N$ is a convex semialgebraic set. Integer feasibility in fixed dimension is not the same problem as counting all its integer points [Khachiyan-Porkolab].

For proportional side lengths $a_0\delta,b_0\delta$, the unshifted cap above $P_2$ has exact volume $(25/12)N\delta^4$, and $\operatorname{vol}(K_N)\le3N\delta^4$. A generic full-dimensional lattice-hull size bound is $O(\operatorname{vol}^{1/2})$ in dimension three [Barany-Larman]. Even granting a near-linear-cost hull construction, multiplication by the $O(\delta^{-2})$ patch count gives only $\sqrt N$ at the level of this estimate. Lower-dimensional integer hulls require separate treatment; they cannot be assigned a three-dimensional volume bound. This cost calculation is not a counting lower bound.

## 7. Direct local integration of the logarithm

We now give the principal constructive analytic step. Let $N^\eta\le T\le N^C$ for fixed positive constants, $t_0\in[T,2T]$, and $1\le U\le T^r$. Take $s_0=24+it_0$. We seek, to arbitrary fixed-power accuracy,

$$
I=\int_0^1 e^{i\lambda Uz}W(z)\log\zeta(s_0+iUz)\,dz,\qquad\lambda=\log N.
\tag{18}
$$

The factor $W$ is analytic and slowly varying, for example $1/(s_0+iUz)$ or that factor multiplied by the local Gaussian smoothing weight. The oscillation $e^{i\lambda Uz}$ is kept explicit.

### 7.1. A bounded two-variable representation

Euler-Maclaurin gives a Dirichlet main sum of length $M\asymp T$, elementary corrections, and a remainder smaller than any prescribed fixed power of $N$. Divide the main sum into blocks $[v,v+K)$ with $K/v\le1/(8T^r)$ and separate the term $1$. Set

$$
\ell_v=\operatorname{nint}\frac{U\log v}{2\pi},\qquad
\rho_v=2\pi\ell_v-U\log v,\qquad w=e^{-2\pi iz}.
$$

Each block is $w^{\ell_v}A_v(z)$, where

$$
A_v(z)=\sum_{m\in[v,v+K)}m^{-24-it_0}
\exp\bigl(i[\rho_v-U\log(m/v)]z\bigr).
$$

For $|z|\le3$,

$$
|A_v(z)|\le e^{3(\pi+1/8)}\sum_{m\in[v,v+K)}m^{-24}.
$$

The sum over $m\ge2$ is less than $1/32$, using

$$
e^{3(\pi+1/8)}(\zeta(24)-1)
<3^{10}\frac{25}{23\,2^{24}}<\frac1{32}.
$$

The Euler-Maclaurin corrections can be assigned the frequency $\ell_M$ and have sufficiently small analytic norm for the asymptotic parameter range. Thus

$$
\zeta(s_0+iUz)=1+G(z,e^{-2\pi iz})+E_{\rm EM}(z),
\qquad
\sup_{|z|\le3,\ |w|\le1}|G(z,w)|\le B_0<\frac1{16},
\tag{19}
$$

with $\deg_wG=O(U\log T)$. Small-height cases can be handled separately. The variables in the norm bound are independent; the identity for the original function is used on the real integration path.

All integer frequencies are retained. Reducing them modulo a sampling length is invalid for this integral: $1+a$ and $1+ae^{-2\pi iLz}$ agree at $z=j/L$, but their logarithms multiplied by $e^{2\pi iLz}$ integrate to $0$ and $a$, respectively, for $|a|<1$.

### 7.2. Controlled logarithm and oscillatory moments

Let $G_D$ be the $z$-Taylor truncation of degree $D$. Cauchy's bound gives

$$
|G-G_D|\le\frac{B_0}{2\,3^D}\quad(|z|\le1),\qquad
|G_D|\le3B_0=:\rho<\frac3{16}\quad(|z|\le2),
$$

uniformly for $|w|\le1$. Form

$$
L_J=\sum_{k=1}^{J}\frac{(-1)^{k+1}}kG_D^k
$$

and retain only $z$ degrees through $D$ after each multiplication. This preserves the exact retained jet. The three truncation errors on the real path are bounded by

$$
B_0 3^{-D},\qquad
\frac{\rho^{J+1}}{(J+1)(1-\rho)},\qquad
[-\log(1-\rho)]2^{-D},
\tag{20}
$$

in addition to the Euler-Maclaurin and arithmetic errors. Taking $D,J=O(\log N)$ gives arbitrary fixed-power accuracy. The earlier fixed-degree counterexample is not being bypassed: the logarithm degree explicitly grows with precision.

After incorporating the Taylor jet of $W$, write the retained polynomial as $\sum c_{j\ell}z^jw^\ell$. Then (18) is evaluated directly from

$$
\sum_{j,\ell}c_{j\ell}\,\mu_j(\lambda U-2\pi\ell),\qquad
\mu_j(\omega)=\int_0^1z^je^{i\omega z}\,dz.
\tag{21}
$$

For $|\omega|\ge2(D+1)$, the recurrence

$$
\mu_0=\frac{e^{i\omega}-1}{i\omega},\qquad
\mu_j=\frac{e^{i\omega}-j\mu_{j-1}}{i\omega}
$$

is stable in the forward direction. For $|\omega|=O(D)$, a convergent Taylor calculation, or $\mu_j={}_1F_1(j+1;j+2;i\omega)/(j+1)$, avoids a small-denominator problem. At resonance, $\mu_j(0)=1/(j+1)$.

The coefficient array has $U$ times polylogarithmically many entries. Fast bivariate polynomial multiplication and polylogarithmic precision suffice for the logarithm stage. Generating the block jets uses the weighted quadratic sums of [Hiary-theta], or the stated cubic subroutine of [Hiary-zeta]. The resulting working local cost is $(T^r+U)N^{o(1)}$, with $r=1/3$ in the quadratic version. The local numerical prototype verifies the formulas but generates the main sum by enumeration and does not implement those fast subroutines.

## 8. Smooth windows and selective resonant coefficients

Let $B_p$ be the $p$-fold convolution of $\mathbf1_{[0,1]}$, with $p\ge2$. It has support $[0,p]$, integral $1$, and

$$
\sum_{k\in\mathbb Z}B_p(t-k)=1.
$$

For windows of width $U$, use spacing $U/p$ and local weight $b_p(z)=B_p(pz)$. Boundary windows must be retained, and the remote tails are controlled by the original smoothing kernel. The overlap introduces only a factor $p$.

Define

$$
\nu_{p,j}(\omega)=\int_0^1z^jB_p(pz)e^{i\omega z}\,dz.
$$

The derivative identity

$$
B_p^{(k)}(t)=\sum_{r=0}^{k}(-1)^r\binom kr B_{p-k}(t-r)
$$

and $k$ integrations by parts yield, for $k\le p-1$,

$$
|\nu_{p,j}(\omega)|\le\frac1p
\min\left(1,\left(\frac{j+2p}{|\omega|}\right)^k\right).
\tag{22}
$$

The needed endpoint derivatives vanish. With $D,p=O(\log N)$ and $p$ a sufficiently large multiple of $\log N$, polynomial bounds on $\sum|c_{j\ell}|$ allow all frequencies outside

$$
|\lambda U-2\pi\ell|<R(D+2p),\qquad R>1\text{ fixed},
\tag{23}
$$

to be discarded within the global error budget. Only $O(\log N)$ frequencies remain per window. Their moments follow from

$$
\nu_{p,0}(\omega)=\frac{e^{i\omega/2}}p
\operatorname{sinc}(\omega/(2p))^p,\qquad
\nu_{p,j}=i^{-j}\partial_\omega^j\nu_{p,0}.
$$

### 8.1. Extracting the required logarithm coefficients

For $K\ge1$,

$$
[w^K]\log(1+G)=\frac1K[w^{K-1}]\frac{\partial_wG}{1+G}.
\tag{24}
$$

Bostan-Mori coefficient extraction [Bostan-Mori] repeatedly multiplies numerator and denominator by $Q(-w)$ and selects the relevant parity. The target index halves in each step, giving $O(\mathsf M(B)\log K)$ coefficient-ring operations for input degree $B=O(U\log T)$.

For a precision-aware version, work with a marker $u$ in

$$
\mathbb C[z,u]/(z^{D+1},u^{J+1})
$$

and extract from $u\partial_wG/(1+uG)$. Evaluating at $u=1$ afterwards gives exactly the logarithm truncated at order $J$. Constant terms are units because they equal $1$ modulo $u$. The marker limits every retained coefficient's degree in the original input coefficients to $J$. A conservative growth estimate is $(K+B+D+J)^{O(J)}$, so the additional guard precision is polylogarithmic in $N$ when $D,J=O(\log N)$. This is a working bit-budget argument, not an interval-certified implementation.

Despite the small output band, the method still costs $BN^{o(1)}$. For arbitrary dense input this dependence cannot simply be ignored. Let

$$
F(w)=1-\frac\rho B\sum_{j=1}^{B}w^j,\qquad 0<\rho<1/16,\qquad K=B+1.
$$

Increasing any one coefficient by $\rho/(2B)$ changes $[w^K]\log F$ by at least $\rho^2/(4B^2)$. Along this perturbation path the coefficients of $1/F$ are nonnegative and $[w^{K-j}]1/F\ge\rho/(2B)$. Thus a sufficiently accurate deterministic algorithm for arbitrary dense inputs may need to inspect all $B$ coefficients. This model does not exclude a specialized implicit algorithm for zeta-derived inputs.

## 9. Global costs and the provisional space calculation

The Gaussian Mellin kernel used in analytic counting is

$$
\frac{N^s}{s}\exp(\varepsilon^2s^2/2).
$$

The exact smoothed prime-power formulation is discussed in [Platt]. Choosing any fixed real part greater than $1$, including $24$, changes accuracy constants but not the power relation between integration height $T$ and local correction width $H=(N/T)N^{o(1)}$.

Our direct integration construction has about $T/U$ batches on one height scale, or an additional polylogarithmic factor with B-spline overlap. Its current total bound is

$$
\frac TU(T^r+U)N^{o(1)}.
$$

At the largest supported width $U=T^r$, this is $TN^{o(1)}$. Consequently the main cost still balances as $T+N/T$, with square-root scale at $T\asymp\sqrt N$. This is a limitation of the present construction and estimate, not an impossibility theorem.

The high-prime-power correction need not impose another square-root scan. From the weighted prime-power count $J(N)=\sum_{a\ge1}\pi(\lfloor N^{1/a}\rfloor)/a$,

$$
\pi(N)=J(N)-\sum_{a\ge2}\frac1a\pi(\lfloor N^{1/a}\rfloor).
$$

The classical subpower-space $x^{3/5+\varepsilon}$ algorithm [LO] evaluates all these smaller arguments in total $N^{3/10+o(1)}$ time and subpower space. This replaces an unnecessary square-root auxiliary scan; it is an application of existing algorithms, not a new full prime-counting exponent.

### 9.1. Provisional time-space combination

The research notes also contain a working combination of the Lagarias-Odlyzko integration framework with Hiary's cubic exponential-sum preprocessing. Its status is deliberately separate from the exact algebraic results above. The fast cubic table, a certified end-to-end counting implementation, a complete interface review, and a literature check establishing novelty have not been supplied.

The proposed batch model, for $4/13\le r\le1/3$, is the following, where $L$ is the number of returned batch values or a comparable coefficient-storage length:

$$
\text{time}=(T^r+L)N^{o(1)},\qquad
\text{space}=(T^{4-12r}+L)N^{o(1)}.
\tag{25}
$$

To account for preprocessing, choose block lengths from powers of two. If $W=T^{1-3r}$, the required cubic phases satisfy $cK^3\le W$. The cited cubic query construction has table scale $W^4$; only logarithmically many distinct $K$ occur. For short blocks $K\le W$, a direct parameter grid costs at most $K^3W\le W^4$. These costs cannot be omitted.

With height $T=N^a$ and space budget $N^{s+\varepsilon}$, the global integration model is $T+T^{1+r}/N^s$. Balancing it against $N/T$ and imposing $a(4-12r)=s$ gives

$$
a=\frac{12+13s}{28},\qquad
\text{time exponent}=\frac{16-13s}{28},\qquad
0\le s\le\frac2{13}.
\tag{26}
$$

Its endpoint is square-root time with candidate space $N^{2/13+\varepsilon}$. The comparison is with the original Lagarias-Odlyzko tradeoff, not a claim to beat all subsequent space bounds or the measured speed of `primecount`. Equation (26) should be read as the outcome of the stated provisional cost construction. It is not presented as an independently verified new record. The direct-integration and resonant-band refinements above do not improve its time exponent.

## 10. Validation, reproducibility, and remaining questions

The supplied programs are reference implementations. Exact tests use integer or rational arithmetic, or explicitly identified finite rings. Numerical tests use NumPy, SciPy, or mpmath and are not interval-certified. Neither successful tests nor platform admission certify a uniform complexity theorem.

Representative validation coverage is:

| Area | Finite checks |
|---|---|
| Parity and modular recovery | Integer-root grouping, prime-power corrections, and odd-prime moduli |
| Precision lifting | All coefficients and relevant prefixes through $4096$ |
| Quadratic periods | $31670$ univariate cases, $6333$ character-prefix recoveries, $416$ binary cases |
| Ternary symmetry | All inputs through $10000$ |
| Convex caps | $183$ patches, $5237$ grid points, $80$ volume checks |
| Fourier/Frobenius | $631$ floor identities and $11928$ frequency relations |
| Direct local integral | Three high-precision comparisons |
| Smooth resonant extraction | $935$ exact partitions, $108$ marked coefficient checks, $27$ moment comparisons |

For the direct local integral at real part $24$, Taylor degree $28$, logarithm order $10$, and eight Euler-Maclaurin terms, the stored comparisons are:

| $t_0$ | $U$ | Main-sum cutoff | Absolute difference from reference quadrature |
|---:|---:|---:|---:|
| $64$ | $1$ | $256$ | $4.69\times10^{-45}$ |
| $128$ | $2$ | $512$ | $1.10\times10^{-36}$ |
| $512$ | $3$ | $2048$ | $6.34\times10^{-33}$ |

These are observed differences, not certified enclosures. The prototype enumerates its main sum and uses ordinary polynomial convolution. It does not demonstrate the fast exponential-sum subroutines or the asymptotic storage claim.

The complete research reference programs are included as literal source in the reproducibility appendix. They write their own JSON results and can be run independently of Markdownxiv. They contain no publication-admission solver. Dependencies and source hashes are recorded with the publication rerun.

The outstanding task is to save a fixed power in the aggregate work, rather than only in the number of outputs. One concrete connection is

$$
\sum_{abc\le N\atop a,b,c\ge2}1=D_3(N)-3D_2(N)+3N-1.
$$

Thus a generic global logarithm method that also extracts its third Dirichlet power already encounters ternary counting. Cross-window aggregation, a usable dual expression for the smoothed ternary term, or a specialized implicit coefficient representation are possible next interfaces. None has been resolved here. A fixed-modulus improvement would still need controlled modulus growth and complete reconstruction to solve the original problem.

## AI-use disclosure

This note was developed with an OpenAI GPT-6-family assistant through the Codex client. The exact runtime model snapshot was not exposed and is declared unknown. AI assistance covered literature checking, exploratory derivations, reference programming, and manuscript preparation. These are provenance declarations, not authenticated identities. Independent human review, formal verification, and a certified optimized implementation are not claimed.

## References

- [LO] J. C. Lagarias and A. M. Odlyzko, *Computing $\pi(x)$: An Analytic Method*, Journal of Algorithms 8 (1987), 173–191. [Author-hosted paper](https://www-users.cse.umn.edu/~odlyzko/doc/arch/analytic.pi.of.x.pdf).
- [HKM] D. Hirsch, I. Kessler, and U. Mendlovic, *Computing $\pi(N)$: An Elementary Approach in $\widetilde O(\sqrt N)$ Time*. [arXiv:2212.09857](https://arxiv.org/abs/2212.09857).
- [Polymath] D. H. J. Polymath, *Deterministic Methods to Find Primes*. [arXiv:1009.3956](https://arxiv.org/abs/1009.3956).
- [Nielsen] M. Nielsen, *Finding Primes: A Fun Subproblem*, 1 September 2009. [Original research discussion](https://michaelnielsen.org/blog/finding-primes-a-fun-subproblem/).
- [Sladkey] R. Sladkey, *A Successive Approximation Algorithm for Computing the Divisor Summatory Function*. [arXiv:1206.3369](https://arxiv.org/abs/1206.3369).
- [primecount] K. Walisch and contributors, *primecount*. [Project source and documentation](https://github.com/kimwalisch/primecount).
- [Hiary-theta] G. A. Hiary, *A Nearly-Optimal Method to Compute the Truncated Theta Function, Its Derivatives, and Integrals*. [arXiv:0711.5002](https://arxiv.org/abs/0711.5002).
- [Hiary-zeta] G. A. Hiary, *Fast Methods to Compute the Riemann Zeta Function*, Annals of Mathematics 174 (2011), 891–946. [Published paper](https://annals.math.princeton.edu/wp-content/uploads/annals-v174-n2-p04-p.pdf).
- [Hiary-characters] G. A. Hiary, *Computing Dirichlet Character Sums to a Power-Full Modulus*. [arXiv:1205.4687](https://arxiv.org/abs/1205.4687).
- [Platt] D. J. Platt, *Computing $\pi(x)$ Analytically*. [arXiv:1203.5712](https://arxiv.org/abs/1203.5712).
- [Booker] A. R. Booker, *Quadratic Class Numbers and Character Sums*, Mathematics of Computation 75 (2006), 1481–1492. [Author institution record](https://research-information.bris.ac.uk/en/publications/quadratic-class-numbers-and-character-sums/).
- [Barvinok] A. I. Barvinok, *A Polynomial Time Algorithm for Counting Integral Points in Polyhedra When the Dimension Is Fixed*, Mathematics of Operations Research 19 (1994), 769–779. [Published paper](https://pubsonline.informs.org/doi/10.1287/moor.19.4.769).
- [Khachiyan-Porkolab] L. Khachiyan and L. Porkolab, *Computing Integral Points in Convex Semi-algebraic Sets*. [Author institution report](https://scholarship.libraries.rutgers.edu/esploro/outputs/technicalDocumentation/Computing-Integral-Points-In-Convex-Semi-algebraic/991031549975704646).
- [Barany-Larman] I. Bárány and D. G. Larman, *The Convex Hull of the Integer Points in a Large Ball*, Mathematische Annalen 312 (1998), 167–181. [Paper](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Barany/Baranyrpdcg.pdf).
- [Hubrechts] H. Hubrechts, *Fast Arithmetic in Unramified $p$-adic Fields*. [arXiv:0906.5510](https://arxiv.org/abs/0906.5510).
- [Bostan-Mori] A. Bostan and R. Mori, *A Simple and Fast Algorithm for Computing the $N$-th Term of a Linearly Recurrent Sequence*. [Author-hosted paper](https://mathexp.eu/bostan/publications/BoMo20.pdf).


## Reproducibility appendix

The following literal source files were rerun for this publication. All twelve programs exited successfully and produced JSON results with status `passed`. These programs concern the prime-counting research, not archive admission. The code is provided under the manuscript license; imported libraries retain their own licenses.

The rerun used Python 3.12.3, numpy 2.4.4, scipy 1.18.0, mpmath 1.3.0.

Save each block under its displayed filename in one directory. For the numerical programs, install the listed NumPy, SciPy, and mpmath versions. Run the Python files from that directory; they write their result JSON beside their source. The exact-identity programs use the standard library and the other supplied reference modules. Output JSON is not a certificate of asymptotic complexity.

| Source file | SHA-256 |
|---|---|
| `verify_identities.py` | `4c001cd86dcdb2b38f04d43587e7e14b9313ac406a98bda0e2af010f041f912c` |
| `verify_mod3_binning.py` | `d4e574d41f59269606c942a054d645b34dd3c6142407d5ee59a6b709a0be9ad4` |
| `zeta_batch_prototype.py` | `e7f398dffb8bc8045e8c496efbc4f41455fd7fa34080b6e56ebcc011a263db05` |
| `verify_log_zeta_series.py` | `6a29614eabc18bd343927b2261dc9bb9aaf5f8752a3ba48810db762a509e9972` |
| `verify_presieved_log.py` | `8884d540cd466038856eab1abf719b1580ee167c7fce2c38c05edd3bd2f65271` |
| `verify_heath_brown.py` | `4b69d54d1474ea87ffb2f4973e389dc78e5ccb76b40cb355def0cdf2a1f102f3` |
| `verify_padic_lifting.py` | `83bb7b4c903dd75881f479c486292894dc65aa4e6782bd9cadb6d75d2d47434d` |
| `verify_quadratic_periods.py` | `a6a9f4477b72fbc83af2585f735c90b425e66ed8f2bb3b5a916e66ecf870d7dd` |
| `verify_convex_caps.py` | `0393e7a2eacdc91d70b4cae32c4c3d18d3f93290829a2b1bbfac1a17e0d2b085` |
| `verify_fourier_traces.py` | `e0cad356d33c5527603c457f0f08d73d05b9502725486ddb1de8440cfe1d12bf` |
| `direct_log_integral.py` | `993a5735720e54857dd37970ecdd986b3e275c0985d0ee4056ac81b55ea5808a` |
| `verify_resonant_coefficients.py` | `8c9c931f9a56e09881e181685bc30075b733a5fa82b07ec2ba47b052da384c8f` |

### A.1. verify_identities.py

```python
"""Small exact checks of the research identities, not a fast pi(n) algorithm.

The test oracles deliberately use a full sieve. They must not be counted as free
preprocessing in a complexity claim. All comparisons are against independently
formed prime, divisor, and distinct-prime-factor tables.
"""

from fractions import Fraction
from math import isqrt
from pathlib import Path
import json
import random


def tables(limit):
    least = [0] * (limit + 1)
    mu = [0] * (limit + 1)
    omega = [0] * (limit + 1)
    primes = []
    mu[1] = 1
    for n in range(2, limit + 1):
        if least[n] == 0:
            least[n] = n
            primes.append(n)
            mu[n] = -1
            omega[n] = 1
        for p in primes:
            if n * p > limit:
                break
            least[n * p] = p
            if n % p == 0:
                mu[n * p] = 0
                omega[n * p] = omega[n]
                break
            mu[n * p] = -mu[n]
            omega[n * p] = omega[n] + 1

    tau = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for n in range(d, limit + 1, d):
            tau[n] += 1

    pi = [0] * (limit + 1)
    mertens = [0] * (limit + 1)
    divisor_sum = [0] * (limit + 1)
    omega_sum = [0] * (limit + 1)
    powers = [0] * (limit + 1)
    for p in primes:
        value = p
        while value <= limit:
            powers[value] += 1
            value *= p
    for n in range(1, limit + 1):
        pi[n] = pi[n - 1] + (n >= 2 and least[n] == n)
        mertens[n] = mertens[n - 1] + mu[n]
        divisor_sum[n] = divisor_sum[n - 1] + tau[n]
        omega_sum[n] = omega_sum[n - 1] + (1 << omega[n])
        powers[n] += powers[n - 1]
    return mu, pi, mertens, divisor_sum, omega_sum, powers


def integer_root(n, exponent):
    if exponent == 2:
        return isqrt(n)
    lo, hi = 0, 1 << ((n.bit_length() + exponent - 1) // exponent)
    while lo < hi:
        middle = (lo + hi + 1) // 2
        if middle ** exponent <= n:
            lo = middle
        else:
            hi = middle - 1
    return lo


def grouped_omega_sum(n, cutoff, mu, d_oracle, m_oracle):
    if not 1 <= cutoff <= isqrt(n):
        raise ValueError("cutoff must be in [1, floor(sqrt(n))]")
    result = sum(mu[d] * d_oracle(n // (d * d))
                 for d in range(1, cutoff + 1))
    maximum = n // ((cutoff + 1) ** 2)
    for k in range(1, maximum + 1):
        upper = isqrt(n // k)
        lower = max(cutoff, isqrt(n // (k + 1)))
        assert lower <= upper
        result += d_oracle(k) * (m_oracle(upper) - m_oracle(lower))
    return result


def parity_from_omega_sum(n, value, pi_oracle):
    assert value % 2 == 1
    correction = sum(pi_oracle(integer_root(n, a))
                     for a in range(2, n.bit_length()))
    return ((value - 1) // 2 - correction) % 2


def recover_integer(lower, upper, residue, modulus):
    residue %= modulus
    first = -((residue - lower) // modulus)
    last = (upper - residue) // modulus
    if first != last:
        raise ValueError("the interval and residue do not identify one integer")
    return residue + first * modulus


def generalized_divisor_prefix(limit, dimension):
    """Reference counts of ordered products of `dimension` positive integers."""
    coefficients = [0] + [1] * limit
    for _ in range(1, dimension):
        following = [0] * (limit + 1)
        for d in range(1, limit + 1):
            for multiple in range(d, limit + 1, d):
                following[multiple] += coefficients[d]
        coefficients = following
    result = [0] * (limit + 1)
    for n in range(1, limit + 1):
        result[n] = result[n - 1] + coefficients[n]
    return result


def odd_modulus_recovery(n, q, mu, divisor_prefix, pi_oracle):
    """Identity valid for odd prime q; its evaluation need not be fast."""
    value = sum(mu[d] * divisor_prefix[n // (d ** q)]
                for d in range(1, integer_root(n, q) + 1))
    assert (value - 1) % q == 0
    correction = sum(pow(a, -1, q) * pi_oracle(integer_root(n, a))
                     for a in range(2, n.bit_length()) if a % q)
    return ((value - 1) // q - correction) % q


def main():
    limit = 100_000
    mu, pi, mertens, ds, omega_sum, powers = tables(limit)
    for n in range(1, limit + 1):
        assert (omega_sum[n] - 1) % 4 == (2 * powers[n]) % 4
    grouped_cases = 0
    for n in range(1, 513):
        for cutoff in range(1, isqrt(n) + 1):
            actual = grouped_omega_sum(n, cutoff, mu, ds.__getitem__,
                                       mertens.__getitem__)
            assert actual == omega_sum[n], (n, cutoff, actual)
            grouped_cases += 1

    rng = random.Random(20260922)
    values = set(range(1, 4097))
    values.update(rng.randrange(1, limit + 1) for _ in range(2000))
    for r in range(2, isqrt(limit)):
        values.update([r * r - 1, r * r, r * r + 1])
    for n in sorted(values):
        actual = parity_from_omega_sum(n, omega_sum[n], pi.__getitem__)
        assert actual == pi[n] % 2, (n, actual, pi[n])
    for n in [rng.randrange(1, limit + 1) for _ in range(500)]:
        root = isqrt(n)
        for cutoff in {root, max(1, root - 1), max(1, int(n ** (4 / 11)))}:
            actual = grouped_omega_sum(n, cutoff, mu, ds.__getitem__,
                                       mertens.__getitem__)
            assert actual == omega_sum[n], (n, cutoff, actual)
            grouped_cases += 1

    for _ in range(1000):
        true_value = rng.randrange(-1000, 1000)
        lower = true_value - rng.randrange(100)
        upper = true_value + rng.randrange(100)
        modulus = upper - lower + rng.randrange(1, 100)
        actual = recover_integer(lower, upper, true_value % modulus, modulus)
        assert actual == true_value
    try:
        recover_integer(9, 13, 0, 2)
    except ValueError:
        pass
    else:
        raise AssertionError("parity cannot distinguish 10 and 12")

    odd_modulus_limit = 10_000
    odd_moduli = [3, 5, 7, 11]
    for q in odd_moduli:
        divisor_prefix = generalized_divisor_prefix(odd_modulus_limit, q)
        for n in range(1, odd_modulus_limit + 1):
            actual = odd_modulus_recovery(n, q, mu, divisor_prefix,
                                          pi.__getitem__)
            assert actual == pi[n] % q, (n, q, actual, pi[n] % q)
    # The odd-prime exponential argument cannot be reused at q=2: the
    # factorial 2! changes 2-adic divisibility. The smallest failure is n=4.
    false_q2_value = odd_modulus_recovery(4, 2, mu, ds, pi.__getitem__)
    assert false_q2_value != pi[4] % 2

    alpha = Fraction(1, 3)
    exponents = {}
    for beta in [Fraction(2, 3), Fraction(3, 5), Fraction(1, 2)]:
        denominator = 3 - 2 * alpha - beta
        y = (1 - alpha) / denominator
        head = alpha + (1 - 2 * alpha) * y
        tail = 1 - (2 - beta) * y
        assert head == tail == (1 - alpha * beta) / denominator
        assert y <= head and 1 - 2 * y <= head
        exponents[str(beta)] = {"cutoff_exponent": str(y),
                                "time_exponent": str(head)}

    result = {
        "status": "passed",
        "scope": "finite algebraic checks; no runtime-exponent benchmark",
        "prime_power_congruence_inputs": limit,
        "grouped_formula_cases": grouped_cases,
        "parity_recovery_inputs": len(values),
        "integer_recovery_cases": 1000,
        "ambiguous_parity_case_rejected": True,
        "odd_modulus_identity_inputs_per_modulus": odd_modulus_limit,
        "odd_moduli": odd_moduli,
        "invalid_odd_prime_formula_at_q2_counterexample": 4,
        "symbolic_cost_exponents": exponents,
    }
    destination = Path(__file__).with_name("identity_results.json")
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

### A.2. verify_mod3_binning.py

```python
"""Exact counterexamples and identities for the mod-3 research branch.

Only small inputs are enumerated. This is not a sub-square-root prime-counting
implementation. Rational bin boundaries and Taylor bounds avoid floating error.
"""

from collections import Counter
from fractions import Fraction
from math import isqrt
from pathlib import Path
import json
import random

from verify_identities import generalized_divisor_prefix, integer_root, tables


def log_bucket(n, numerator=3, denominator=2):
    assert 1 < Fraction(numerator, denominator) < 2
    k, a, b = 0, numerator, denominator
    while n * b >= a:
        k += 1
        a *= numerator
        b *= denominator
    return k


def truncated_product(left, right, degree):
    result = [0] * (degree + 1)
    for i, a in enumerate(left):
        for j in range(min(len(right), degree - i + 1)):
            result[i + j] += a * right[j]
    return result


def rounded_quotient_prefix(n, q):
    """The deliberately uncorrected A(z)^q/A(z^q) proposal."""
    degree = log_bucket(n)
    bins = [0] * (degree + 1)
    for m in range(1, n + 1):
        bins[log_bucket(m)] += 1
    numerator = [1] + [0] * degree
    for _ in range(q):
        numerator = truncated_product(numerator, bins, degree)
    denominator = [bins[j // q] if j % q == 0 else 0
                   for j in range(degree + 1)]
    assert denominator[0] == 1
    quotient = [0] * (degree + 1)
    for i in range(degree + 1):
        quotient[i] = numerator[i] - sum(
            denominator[j] * quotient[i - j] for j in range(1, i + 1))
    return sum(quotient), bins, numerator, quotient


def ordered_factorizations(n, slots):
    if slots == 1:
        yield (n,)
        return
    for d in range(1, n + 1):
        if n % d == 0:
            for tail in ordered_factorizations(n // d, slots - 1):
                yield (d,) + tail


def direct_local_f3(n):
    if n == 1:
        return 1
    value = 1
    p = 2
    while p * p <= n:
        exponent = 0
        while n % p == 0:
            n //= p
            exponent += 1
        if exponent:
            value *= 3 * exponent
        p += 1
    if n > 1:
        value *= 3
    return value


def floor_sum(n, bound):
    return sum(n // j for j in range(1, bound + 1))


def divisor2(n):
    root = isqrt(n)
    return 2 * floor_sum(n, root) - root * root


def divisor3_by_slices(n):
    root = integer_root(n, 3)
    return (3 * sum(divisor2(n // a) - floor_sum(n // a, root)
                    for a in range(1, root + 1)) + root ** 3)


def main():
    limit = 1000
    mu, pi, *_ = tables(limit)
    reference_d3 = generalized_divisor_prefix(limit, 3)
    reference_b3 = [0] * (limit + 1)
    for n in range(1, limit + 1):
        reference_b3[n] = reference_b3[n - 1] + direct_local_f3(n)
        assert divisor3_by_slices(n) == reference_d3[n]
        convolution = sum(mu[d] * reference_d3[n // d ** 3]
                          for d in range(1, integer_root(n, 3) + 1))
        assert convolution == reference_b3[n]

    failures = []
    for n in range(1, limit + 1):
        approximation, *_ = rounded_quotient_prefix(n, 3)
        # This necessary divisibility test still passes for the wrong answer.
        assert (approximation - 1) % 3 == 0
        correction = sum(a * pi[integer_root(n, a)]
                         for a in range(2, n.bit_length()))
        recovered = ((approximation - 1) // 3 - correction) % 3
        if recovered != pi[n] % 3:
            failures.append(n)
    assert failures[0] == 3

    rounded_five, bins, numerator, quotient = rounded_quotient_prefix(5, 3)
    assert reference_b3[5] == 16 and rounded_five == 22
    tuple_polynomial = Counter(sum(log_bucket(t) for t in triple)
                               for triple in ordered_factorizations(6, 3))
    assert tuple_polynomial == Counter({3: 6, 4: 3})
    assert sum(tuple_polynomial.values()) % 9 == 0
    assert sum(value for degree, value in tuple_polynomial.items()
               if degree <= log_bucket(5)) % 9 == 6

    rng = random.Random(20260922)
    taylor_checks = 10000
    for _ in range(taylor_checks):
        u = Fraction(rng.randrange(501), 1000)
        v = Fraction(rng.randrange(501), 1000)
        delta = max(u, v)
        actual = 1 / ((1 + u) * (1 + v))
        linear = 1 - u - v
        quadratic = linear + u * u + u * v + v * v
        assert linear <= actual <= quadratic
        remainder_numerator = (u ** 3 + u * u * v + u * v * v + v ** 3
                               + u ** 3 * v + u * u * v * v + u * v ** 3)
        assert quadratic - actual == remainder_numerator / ((1 + u) * (1 + v))
        assert actual - linear <= 4 * delta ** 2
        assert quadratic - actual <= 6 * delta ** 3

    models = {}
    for gamma in [Fraction(0), Fraction(1, 2), Fraction(9, 10),
                  Fraction(1), Fraction(3, 2), Fraction(2)]:
        delta_exponent = (1 - gamma / 3) / (5 - gamma)
        patch = gamma / 3 + (2 - gamma) * delta_exponent
        correction = 1 - 3 * delta_exponent
        assert patch == correction == 2 / (5 - gamma)
        models[str(gamma)] = str(patch)

    result = {
        "status": "passed",
        "scope": "exact small-input identities and rejected shortcut; no new pi algorithm",
        "divisor3_slice_inputs": limit,
        "cube_mobius_convolution_inputs": limit,
        "uncorrected_binning_test_inputs": limit,
        "uncorrected_binning_wrong_pi_mod3_count": len(failures),
        "first_uncorrected_failure": failures[0],
        "semiprime_counterexample": {
            "N": 5, "base": "3/2", "product": 6,
            "exact_B3": reference_b3[5], "uncorrected_B3": rounded_five,
            "bins_A": bins, "truncated_A_cubed": numerator,
            "truncated_A_cubed_over_A_zcubed": quotient,
            "product6_tuple_bucket_counts": dict(sorted(tuple_polynomial.items())),
            "truncated_semiprime_residue_mod9": 6,
        },
        "rational_taylor_bound_checks": taylor_checks,
        "balanced_box_hypothetical_exponents_by_patch_gamma": models,
        "quadratic_patch_solver_constructed": False,
    }
    destination = Path(__file__).with_name("mod3_binning_results.json")
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
```

### A.3. zeta_batch_prototype.py

```python
"""Prototype of streamed zeta batches using polynomial moments and an FFT.

The quadratic/cubic-moment oracle is evaluated NAIVELY here. Thus this file checks
the representation and error behavior, not the proposed asymptotic runtime.
NumPy complex128 arithmetic is not an interval-arithmetic certificate.
"""

import cmath
from fractions import Fraction
import json
from math import ceil, factorial, log, pi
from pathlib import Path

import mpmath as mp
import numpy as np

from verify_identities import integer_root


def analytic_coefficients(delta, height, width, sigma, y_degree, z_degree,
                          phase_degree):
    """Taylor coefficients of the residual after removing the main phase."""
    a = np.zeros(y_degree + 1, dtype=complex)
    b = np.zeros(y_degree + 1, dtype=complex)
    for k in range(1, y_degree + 1):
        coefficient = (-1) ** (k + 1) * delta ** k / k
        a[k] = -sigma * coefficient
        if k > phase_degree:
            a[k] -= 1j * height * coefficient
        b[k] = -1j * width * coefficient
    exponential = np.zeros(y_degree + 1, dtype=complex)
    exponential[0] = 1
    for k in range(1, y_degree + 1):
        exponential[k] = sum(j * a[j] * exponential[k - j]
                             for j in range(1, k + 1)) / k
    coefficients = np.zeros((z_degree + 1, y_degree + 1), dtype=complex)
    coefficients[0] = exponential
    for j in range(1, z_degree + 1):
        coefficients[j] = np.convolve(coefficients[j - 1], b)[:y_degree + 1] / j
    return coefficients


def block_coefficients(v, length, height, width, sigma, y_degree, z_degree,
                       phase_degree):
    prefactor = v ** (-sigma) * cmath.exp(-1j * height * log(v))
    if length == 1:
        result = np.zeros(z_degree + 1, dtype=complex)
        result[0] = prefactor
        return result
    delta = length / v
    y = np.arange(length, dtype=float) / length
    phase_polynomial = sum((-1) ** (k + 1) * (delta * y) ** k / k
                           for k in range(1, phase_degree + 1))
    phase = np.exp(-1j * height * phase_polynomial)
    # Replace this direct sum by the appropriate Hiary algorithm in a fast realization.
    moments = np.array([np.sum(y ** k * phase) for k in range(y_degree + 1)])
    coefficients = analytic_coefficients(delta, height, width, sigma,
                                         y_degree, z_degree, phase_degree)
    return prefactor * (coefficients @ moments)


def zeta_main_sum_batch(height, length, width, sigma=1.5,
                        y_degree=60, z_degree=20, grid_degree=40,
                        phase_degree=2, block_exponent=Fraction(1, 3)):
    scale_root = integer_root(height ** block_exponent.numerator,
                              block_exponent.denominator)
    assert 0 < width <= scale_root
    block_scale = 8 * (scale_root + 1)
    needed = max(16, ceil(4 * width * log(max(length, 3))))
    sample_count = 1 << (needed - 1).bit_length()
    accum = np.zeros((z_degree + grid_degree + 1, sample_count), dtype=complex)
    v, blocks = 1, 0
    while v <= length:
        maximum = min(max(1, v // block_scale), length - v + 1)
        # Powers of two permit reuse of only O(log T) moment tables in the
        # theoretical cubic construction; the prototype still uses direct sums.
        count = 1 << (maximum.bit_length() - 1)
        p = block_coefficients(v, count, height, width, sigma,
                               y_degree, z_degree, phase_degree)
        frequency = -width * log(v)
        nearest = round(frequency / (2 * pi))
        residual = frequency - 2 * pi * nearest
        assert abs(residual) <= pi + 1e-12
        q = np.ones(grid_degree + 1, dtype=complex)
        for j in range(1, grid_degree + 1):
            q[j] = q[j - 1] * (1j * residual) / j
        accum[:, nearest % sample_count] += np.convolve(p, q)
        v += count
        blocks += 1
    modes = np.fft.ifft(accum, axis=1) * sample_count
    normalized = np.arange(sample_count) / sample_count
    values = np.zeros(sample_count, dtype=complex)
    for row in modes[::-1]:
        values = values * normalized + row
    return width * normalized, values, blocks


def euler_maclaurin_correction(s, length, terms=12):
    """For a main sum INCLUDING n=length."""
    inverse = cmath.exp(-s * log(length))
    correction = inverse * (length / (s - 1) - 0.5)
    rising = s
    for k in range(1, terms + 1):
        coefficient = float(mp.bernoulli(2 * k)) / factorial(2 * k)
        correction += coefficient * rising * inverse / length ** (2 * k - 1)
        rising *= (s + 2 * k - 1) * (s + 2 * k)
    full_rising = 1.0
    for k in range(2 * terms):
        full_rising *= abs(s + k)
    remainder_bound = (2 * float(mp.zeta(2 * terms)) * full_rising
                       / (2 * pi) ** (2 * terms)
                       * length ** (1 - s.real - 2 * terms)
                       / (s.real + 2 * terms - 1))
    return correction, remainder_bound


def main():
    mp.mp.dps = 50
    reports = []
    cases = [(1024, 2, Fraction(1, 3)), (4096, 2, Fraction(1, 3)),
             (16384, 2, Fraction(1, 3)), (4096, 3, Fraction(4, 13)),
             (16384, 3, Fraction(4, 13)), (16384, 3, Fraction(5, 16))]
    for height, degree, exponent in cases:
        length = height
        width = integer_root(height ** exponent.numerator, exponent.denominator)
        offsets, values, blocks = zeta_main_sum_batch(
            height, length, width, phase_degree=degree, block_exponent=exponent)
        sample_indices = sorted({0, 1, len(values) // 11, len(values) // 5,
                                 len(values) // 3, len(values) // 2,
                                 3 * len(values) // 4, len(values) - 1})
        ns = np.arange(1, length + 1, dtype=float)
        logs = np.log(ns)
        weights = ns ** (-1.5)
        main_errors, zeta_errors, em_bounds = [], [], []
        for j in sample_indices:
            t = height + offsets[j]
            direct = np.sum(weights * np.exp(-1j * t * logs))
            main_errors.append(float(abs(values[j] - direct)))
            correction, error_bound = euler_maclaurin_correction(1.5 + 1j * t,
                                                               length)
            reference = complex(mp.zeta(mp.mpc('1.5', float(t))))
            zeta_errors.append(float(abs(values[j] + correction - reference)))
            em_bounds.append(error_bound)
        assert max(main_errors) < 1e-8
        assert max(zeta_errors) < 1e-8
        reports.append({
            "height": height, "main_sum_length": length, "batch_width": width,
            "phase_degree": degree, "block_exponent": str(exponent),
            "grid_values_computed": len(values), "blocks": blocks,
            "reference_points_checked": len(sample_indices),
            "max_main_sum_absolute_error": max(main_errors),
            "max_zeta_absolute_error": max(zeta_errors),
            "max_EM_analytic_remainder_bound": max(em_bounds),
        })
    tradeoffs = []
    for space in [Fraction(0), Fraction(1, 13), Fraction(2, 13)]:
        height = (12 + 13 * space) / 28
        time = (16 - 13 * space) / 28
        r = Fraction(1, 3) - space / (12 * height)
        assert height * (4 - 12 * r) == space
        assert 1 - height == height * (1 + r) - space == time
        assert Fraction(4, 13) <= r <= Fraction(1, 3)
        assert space <= height * r and height <= time and time >= Fraction(1, 2)
        tradeoffs.append({"space_exponent": str(space),
                          "height_exponent": str(height),
                          "block_exponent": str(r), "time_exponent": str(time)})
    result = {
        "status": "passed",
        "scope": "floating-point functional prototype; theta moments are naive",
        "interval_certified": False,
        "fast_theta_oracle_implemented": False,
        "fast_cubic_oracle_implemented": False,
        "sub_square_root_pi_algorithm": False,
        "cases": reports,
        "symbolically_checked_combination_tradeoffs": tradeoffs,
    }
    Path(__file__).with_name('zeta_batch_results.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
```

### A.4. verify_log_zeta_series.py

```python
"""Exact checks for log(zeta) coefficient cancellation and failed truncation.

This is a small Dirichlet-series experiment, not a fast prime-counting method.
"""

from fractions import Fraction
from math import factorial
from pathlib import Path
import json

from verify_identities import tables


def main():
    limit = 10000
    _, pi, *_ = tables(limit)
    expected = [Fraction(0) for _ in range(limit + 1)]
    for p in range(2, limit + 1):
        if pi[p] > pi[p - 1]:
            value, exponent = p, 1
            while value <= limit:
                expected[value] = Fraction(1, exponent)
                value *= p
                exponent += 1
    coefficients = [Fraction(0) for _ in range(limit + 1)]
    current = [0, 0] + [1] * (limit - 1)
    test_products = {1: 6, 2: 30, 3: 210, 4: 2310}
    counterexamples = []
    for k in range(1, limit.bit_length()):
        for n in range(2, limit + 1):
            coefficients[n] += Fraction((-1) ** (k + 1) * current[n], k)
        if k in test_products:
            n = test_products[k]
            prediction = (-1) ** (k + 1) * factorial(k)
            assert coefficients[n] == prediction
            assert expected[n] == 0
            counterexamples.append({"degree": k, "n": n,
                                    "truncated_coefficient": prediction,
                                    "correct_log_zeta_coefficient": 0})
        following = [0] * (limit + 1)
        for factor in range(2, limit + 1):
            for product in range(2 * factor, limit + 1, factor):
                following[product] += current[product // factor]
        current = following
    assert coefficients == expected

    result = {
        "status": "passed",
        "scope": "finite exact Dirichlet coefficient identities",
        "inputs_checked": limit,
        "fixed_degree_counterexamples": counterexamples,
        "sub_square_root_pi_algorithm": False,
    }
    Path(__file__).with_name('log_zeta_series_results.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
```

### A.5. verify_presieved_log.py

```python
"""Exact checks for pre-sieving and finite Dirichlet logarithms.

The sieve and dense coefficient arrays are reference implementations, not a
claimed fast evaluation of the factored Euler product.
"""

from fractions import Fraction
from math import comb, isqrt
from pathlib import Path
import json

from verify_identities import integer_root, tables


def prime_list(pi):
    return [p for p in range(2, len(pi)) if pi[p] > pi[p - 1]]


def euler_coefficients(limit, primes, y):
    coefficients = [0] * (limit + 1)
    coefficients[1] = 1
    for p in primes:
        if p > y:
            break
        for n in range(limit // p, 0, -1):
            coefficients[n * p] -= coefficients[n]
    return coefficients


def rough_flags(limit, primes, y):
    flags = [0] + [1] * limit
    for p in primes:
        if p > y:
            break
        for n in range(p, limit + 1, p):
            flags[n] = 0
    return flags


def finite_rough_log(limit, primes, y):
    flags = rough_flags(limit, primes, y)
    smallest = next(p for p in primes if p > y)
    degree, power = 0, 1
    while power * smallest <= limit:
        degree += 1
        power *= smallest
    current = flags.copy()
    current[1] = 0
    result = [Fraction(0) for _ in range(limit + 1)]
    for k in range(1, degree + 1):
        for n in range(2, limit + 1):
            result[n] += Fraction((-1) ** (k + 1) * current[n], k)
        following = [0] * (limit + 1)
        for a in range(2, limit + 1):
            if flags[a]:
                for product in range(2 * a, limit + 1, a):
                    following[product] += current[product // a]
        current = following
    expected = [Fraction(0) for _ in range(limit + 1)]
    for p in primes:
        if p <= y or p > limit:
            continue
        power, exponent = p, 1
        while power <= limit:
            expected[power] = Fraction(1, exponent)
            power *= p
            exponent += 1
    assert result == expected
    assert not any(current)
    return degree, flags, result


def main():
    limit = 100000
    mu, pi, mertens, divisor_sum, *_ = tables(limit)
    primes = prime_list(pi)
    cases = []
    for n in [1000, 10000]:
        for y in [2, 5, 11, 31, integer_root(n ** 2, 5)]:
            degree, flags, logarithm = finite_rough_log(n, primes, y)
            coefficients = euler_coefficients(n, primes, y)
            phi_value = sum(flags)
            inclusion = sum(coefficients[d] * (n // d) for d in range(1, n + 1))
            assert inclusion == phi_value
            smallest = next(p for p in primes if p > y)
            case = {"n": n, "y": y, "smallest_rough_prime": smallest,
                    "log_degree": degree, "phi": phi_value}
            if smallest ** 3 > n:
                semiprimes = 0
                for index, p in enumerate(primes):
                    if p <= y:
                        continue
                    if p * p > n:
                        break
                    semiprimes += pi[n // p] - index
                reconstructed = pi[y] + phi_value - 1 - semiprimes
                assert reconstructed == pi[n]
                prime_squares = max(0, pi[isqrt(n)] - pi[y])
                assert sum(logarithm) == pi[n] - pi[y] + Fraction(prime_squares, 2)
                case["semiprimes"] = semiprimes
                case["meissel_reconstructed_pi"] = reconstructed
            cases.append(case)

    support = []
    for n in [1000, 10000, 100000]:
        y = integer_root(n ** 2, 5)
        coefficients = euler_coefficients(n, primes, y)
        middle_primes = [p for p in primes if y < 2 * p and p <= y]
        lower_count = comb(len(middle_primes), 2)
        pair_products = {p * q for i, p in enumerate(middle_primes)
                         for q in middle_primes[i + 1:]}
        assert len(pair_products) == lower_count
        assert all(product <= n and coefficients[product] == 1
                   for product in pair_products)
        support.append({"n": n, "y": y,
                        "factored_euler_factors": pi[y],
                        "expanded_nonzero_coefficients_through_n":
                        sum(c != 0 for c in coefficients),
                        "middle_prime_pair_lower_bound": lower_count})

    # A related auxiliary identity: zeta(s)^3 = zeta(3s) in characteristic 3.
    # This does not recover pi(n), or even the full integer M(n).
    for n in range(1, limit + 1):
        value = sum(mu[d] * divisor_sum[n // d ** 3]
                    for d in range(1, integer_root(n, 3) + 1))
        assert value % 3 == mertens[n] % 3

    result = {
        "status": "passed",
        "scope": "exact finite identities and expansion-cost checks",
        "presieved_log_cases": cases,
        "euler_support_counts": support,
        "Mertens_mod3_identity_inputs": limit,
        "sub_square_root_pi_algorithm": False,
    }
    Path(__file__).with_name('presieved_log_results.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
```

### A.6. verify_heath_brown.py

```python
"""Exact small-input audit of K=3 identities and intermediate supports.

All Dirichlet convolutions here are reference computations. No sub-square-root
runtime is asserted. Omega is used only as an exact additive test weight.
"""

from collections import Counter
from itertools import product
from pathlib import Path
import json

from verify_identities import integer_root, tables


def convolution(a, b, limit):
    result = [0] * (limit + 1)
    for i in range(1, limit + 1):
        if a[i]:
            for j in range(1, limit // i + 1):
                if b[j]:
                    result[i * j] += a[i] * b[j]
    return result


def omega_and_prime_powers(limit, primes):
    omega = [0] * (limit + 1)
    expected = [0] * (limit + 1)
    for p in primes:
        value = p
        while value <= limit:
            expected[value] = 1
            for multiple in range(value, limit + 1, value):
                omega[multiple] += 1
            value *= p
    return omega, expected


def main():
    records = []
    for limit in (1000, 4096, 10000):
        mu, pi, mertens, *_ = tables(limit)
        primes = [p for p in range(2, limit + 1) if pi[p] > pi[p - 1]]
        y = integer_root(limit, 3)
        assert (y + 1) ** 3 > limit
        short = [mu[n] if n <= y else 0 for n in range(limit + 1)]
        one = [0] + [1] * limit
        square = convolution(short, short, limit)
        cube = convolution(square, short, limit)
        term2 = convolution(one, square, limit)
        term3 = convolution(one, convolution(one, cube, limit), limit)
        reconstructed_mu = [3 * short[n] - 3 * term2[n] + term3[n]
                            for n in range(limit + 1)]
        assert reconstructed_mu == mu

        omega, expected_powers = omega_and_prime_powers(limit, primes)
        weighted1 = convolution(omega, short, limit)
        weighted2 = convolution(omega, term2, limit)
        weighted3 = convolution(omega, term3, limit)
        reconstructed_powers = [3 * weighted1[n] - 3 * weighted2[n]
                                + weighted3[n] for n in range(limit + 1)]
        assert reconstructed_powers == expected_powers
        # Dividing a logarithmic derivative by log(n) is not reproduced by
        # treating the Omega test weight as a free, efficiently summable input.
        for n in range(1, limit + 1):
            root = integer_root(n, 3)
            diagonal = mu[root] if root ** 3 == n and root <= y else 0
            assert (cube[n] - diagonal) % 3 == 0
        records.append({
            "N": limit, "short_cutoff": y, "M_N": mertens[limit],
            "three_terms_for_M_N": [3 * sum(short), -3 * sum(term2), sum(term3)],
            "three_terms_for_prime_power_count":
            [3 * sum(weighted1), -3 * sum(weighted2), sum(weighted3)],
            "prime_power_count": sum(expected_powers),
        })

    support = []
    for y in (10, 20, 40, 80, 120):
        mu, *_ = tables(y)
        nonzero = [d for d in range(1, y + 1) if mu[d]]
        entry = {"y": y, "nonzero_mu_inputs": len(nonzero)}
        for k in (2, 3):
            signed = Counter()
            absolute = Counter()
            for factors in product(nonzero, repeat=k):
                value, weight = 1, 1
                for d in factors:
                    value *= d
                    weight *= mu[d]
                signed[value] += weight
                absolute[value] += 1
            assert all(abs(signed[m]) == count for m, count in absolute.items())
            assert sum(absolute.values()) == len(nonzero) ** k
            assert sum(signed.values()) == sum(mu) ** k
            entry[f"power_{k}"] = {
                "nonzero_output_coefficients": len(signed),
                "nonzero_ordered_tuple_terms": len(nonzero) ** k,
                "max_multiplicity": max(absolute.values()),
                "within_coefficient_cancellation": False,
                "full_prefix_sum": sum(signed.values()),
            }
        support.append(entry)

    result = {
        "status": "passed",
        "scope": "exact finite checks; no fast convolution implementation",
        "heath_brown_cases": records,
        "mobius_power_support_cases": support,
        "Omega_weight_is_only_a_reference_test": True,
        "sub_square_root_pi_algorithm": False,
    }
    Path(__file__).with_name('heath_brown_results.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
```

### A.7. verify_padic_lifting.py

```python
"""Exact formal-series checks of inverse/logarithm precision lifting.

Dense Dirichlet convolutions are used as reference computations only. Passing
these checks does not establish a fast prefix-sum algorithm.
"""

from math import factorial
from pathlib import Path
import json

from verify_heath_brown import convolution
from verify_identities import integer_root, tables


def add(a, b, scale=1):
    return [x + scale * y for x, y in zip(a, b)]


def scale(a, multiplier):
    return [multiplier * x for x in a]


def ordinary_poly_mul(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


def main():
    limit = 4096
    mu, pi, mertens, d2prefix, *_ = tables(limit)
    one = [0] + [1] * limit
    identity = [0] * (limit + 1)
    identity[1] = 1
    d2 = [d2prefix[n] - d2prefix[n - 1] if n else 0
          for n in range(limit + 1)]
    mu_cube = [0] * (limit + 1)
    for d in range(1, integer_root(limit, 3) + 1):
        mu_cube[d ** 3] = mu[d]
    a0 = convolution(d2, mu_cube, limit)
    f = convolution(one, a0, limit)
    assert all((f[n] - identity[n]) % 3 == 0 for n in range(limit + 1))
    b = [(f[n] - identity[n]) // 3 for n in range(limit + 1)]
    error = add(identity, f, -1)

    newton = a0.copy()
    stages = []
    for iteration in range(4):
        digits = 2 ** iteration
        modulus = 3 ** digits
        assert all((newton[n] - mu[n]) % modulus == 0
                   for n in range(limit + 1))
        stages.append({"iteration": iteration, "ternary_digits": digits,
                       "modulus": modulus, "maximum_zeta_order": 3 * digits - 1,
                       "prefix_residue": sum(newton) % modulus,
                       "M_N_residue": mertens[limit] % modulus})
        newton = convolution(newton, add(scale(identity, 2),
                                        convolution(one, newton, limit), -1), limit)

    # Geometric truncation after three terms gives precision 3^3.
    a3 = convolution(a0, add(add(identity, error),
                             convolution(error, error, limit)), limit)
    assert all((a3[n] - mu[n]) % 27 == 0 for n in range(limit + 1))
    b_cube_argument = [0] * (limit + 1)
    for d in range(1, integer_root(limit, 3) + 1):
        b_cube_argument[d ** 3] = b[d]
    correction = convolution(a0, b_cube_argument, limit)
    corrected = add(a3, correction, -27)
    assert all((corrected[n] - mu[n]) % 81 == 0 for n in range(limit + 1))
    defects = [n for n in range(1, limit + 1) if (a3[n] - mu[n]) % 81]
    assert defects

    # The p-integral logarithm log(1+3B)/3. All denominators are reduced
    # before modular inversion; dividing by a multiple of 3 is not allowed.
    logarithm_checks = []
    logarithms = {}
    for digits in (1, 2, 3, 4):
        modulus = 3 ** digits
        total = [0] * (limit + 1)
        power = identity.copy()
        included = []
        for j in range(1, 2 * digits + 1):
            power = convolution(power, b, limit)
            unit, valuation = j, 0
            while unit % 3 == 0:
                unit //= 3
                valuation += 1
            exponent = j - 1 - valuation
            if exponent >= digits:
                continue
            coefficient = ((-1) ** (j + 1) * 3 ** exponent
                           * pow(unit, -1, modulus)) % modulus
            included.append({"power": j, "coefficient": coefficient})
            for n in range(1, limit + 1):
                total[n] = (total[n] + coefficient * power[n]) % modulus
        expected = [0] * (limit + 1)
        for p in range(2, limit + 1):
            if pi[p] == pi[p - 1]:
                continue
            value, exponent = p, 1
            while value <= limit:
                if exponent % 3:
                    expected[value] = pow(exponent, -1, modulus)
                value *= p
                exponent += 1
        assert total == expected
        logarithms[modulus] = total
        prefix = 0
        for n in range(1, limit + 1):
            prefix = (prefix + total[n]) % modulus
            correction_roots = sum(pow(a, -1, modulus) * pi[integer_root(n, a)]
                                   for a in range(2, n.bit_length()) if a % 3)
            assert (prefix - correction_roots) % modulus == pi[n] % modulus
        logarithm_checks.append({"digits": digits, "modulus": modulus,
                                 "retained_terms": included})

    b2 = convolution(b, b, limit)
    b3 = convolution(b2, b, limit)
    b_times_dilate = convolution(b, b_cube_argument, limit)
    reduced9 = [(b[n] + 3 * b2[n] + 3 * b_cube_argument[n]) % 9
                for n in range(limit + 1)]
    reduced81 = [(b[n] + 39 * b2[n] + 3 * b3[n]
                  + 54 * b_times_dilate[n]) % 81 for n in range(limit + 1)]
    assert reduced9 == logarithms[9]
    assert reduced81 == logarithms[81]

    d3 = convolution(one, d2, limit)
    d3prefix = [0] * (limit + 1)
    for n in range(1, limit + 1):
        d3prefix[n] = d3prefix[n - 1] + d3[n]
    prime_power_prefix_mod3 = [0] * (limit + 1)
    for n in range(1, limit + 1):
        prime_power_prefix_mod3[n] = (
            pi[n] + sum(pow(a, -1, 3) * pi[integer_root(n, a)]
                        for a in range(2, n.bit_length()) if a % 3)) % 3
        root = integer_root(n, 3)
        reconstructed_d3 = (root + 3 * sum(
            prime_power_prefix_mod3[n // d ** 3] for d in range(1, root + 1))) % 9
        assert reconstructed_d3 == d3prefix[n] % 9
        f_prefix = sum(mu[d] * d3prefix[n // d ** 3]
                       for d in range(1, root + 1)) % 9
        assert (f_prefix - 1) % 3 == 0
        correction = sum(pow(a, -1, 3) * pi[integer_root(n, a)]
                         for a in range(2, n.bit_length()) if a % 3)
        reconstructed_pi = ((f_prefix - 1) // 3 - correction) % 3
        assert reconstructed_pi == pi[n] % 3

    # A dual certificate excludes undilated zeta powers 0,...,4 for a
    # coefficientwise inverse modulo 9, regardless of dilations >=2.
    annihilator = [1]
    for a in range(5):
        annihilator = ordinary_poly_mul(annihilator, [-a, 1])
    assert all(sum(c * a ** r for r, c in enumerate(annihilator)) == 0
               for a in range(5))
    contradiction = sum(c * (-1) ** r for r, c in enumerate(annihilator)) % 9
    assert contradiction == 6
    assert all((2 * 2 ** r - 5 ** r - (-1) ** r) % 9 == 0 for r in range(51))

    prime_log_certificates = []
    for degree, digits in [(2, 1), (5, 2), (8, 3), (8, 4)]:
        polynomial = [1]
        for a in range(degree + 1):
            polynomial = ordinary_poly_mul(polynomial, [-a, 1])
        modulus = 3 ** digits
        assert all(sum(c * a ** r for r, c in enumerate(polynomial)) == 0
                   for a in range(degree + 1))
        # The target is delta_{r,1} on squarefree integers with r prime factors.
        target = polynomial[1] % modulus
        assert target != 0
        primorial = 1
        used = 0
        for p in range(2, limit + 1):
            if pi[p] > pi[p - 1]:
                primorial *= p
                used += 1
                if used == degree + 1:
                    break
        prime_log_certificates.append({
            "excluded_maximum_undilated_order": degree,
            "modulus": modulus, "target_residual": target,
            "applies_to_all_coefficients_up_to_N_when_N_at_least": primorial,
        })

    minimum_orders = []
    for digits in range(1, 11):
        d = 0
        while factorial(d + 1) % (3 ** digits):
            d += 1
        minimum_orders.append({"digits": digits,
                               "necessary_maximum_undilated_order": d})

    # Prefix sum is not a Dirichlet-ring homomorphism: scalar Newton is wrong.
    prefix = 0
    first_scalar_failure = None
    for n in range(1, limit + 1):
        prefix += a0[n]
        alleged = prefix * (2 - n * prefix) % 9
        if alleged != mertens[n] % 9:
            first_scalar_failure = n
            break
    assert first_scalar_failure == 2

    result = {
        "status": "passed",
        "scope": "coefficientwise finite algebra checks; no prefix speed theorem",
        "coefficient_limit": limit,
        "newton_stages": stages,
        "27_to_81_correction": {
            "uncorrected_first_defect": defects[0],
            "all_coefficients_correct_after_correction": True,
            "maximum_undilated_zeta_order": 8,
            "requires_A3_evaluated_mod81": True,
        },
        "integral_logarithm": logarithm_checks,
        "pi_prefix_recovery_checked_at_all_inputs": limit,
        "reduced_log_orders": {"mod3": 3, "mod9": 6, "mod27": 9, "mod81": 9},
        "reduced_log_formulas_checked": True,
        "pi_mod3_D3_mod9_bidirectional_checks": limit,
        "prime_log_order_exclusion_certificates": prime_log_certificates,
        "order4_mod9_exclusion_certificate": {
            "annihilator_coefficients": annihilator,
            "target_residual_mod9": contradiction,
        },
        "necessary_orders_for_unbounded_coefficient_identities": minimum_orders,
        "scalar_prefix_Newton_first_failure": first_scalar_failure,
        "sub_square_root_pi_algorithm": False,
    }
    Path(__file__).with_name('padic_lifting_results.json').write_text(
        json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
```

### A.8. verify_quadratic_periods.py

```python
"""Exact checks of periodic quadratic floor sums and D3 symmetry reduction.

The direct sums and reduced-form enumeration are reference computations.
This is not a sub-square-root prime-counting implementation or a benchmark
of the class-number/character-sum algorithms cited in the research note.
"""

from math import gcd, isqrt
from pathlib import Path
from random import Random
import json

from verify_heath_brown import convolution
from verify_identities import integer_root, tables


def legendre(a, q):
    value = pow(a % q, (q - 1) // 2, q)
    return -1 if value == q - 1 else value


def negative_prime_class_number(q):
    """Enumerate reduced primitive forms of discriminant -q, q = 3 mod 4."""
    assert q > 3 and q % 4 == 3
    count = 0
    for a in range(1, isqrt(q // 3) + 1):
        for b in range(-a, a + 1):
            numerator = b * b + q
            if numerator % (4 * a):
                continue
            c = numerator // (4 * a)
            if c < a or gcd(gcd(a, b), c) != 1:
                continue
            if (abs(b) == a or a == c) and b < 0:
                continue
            count += 1
    return count


def complete_quadratic_sum(a, b, c, q, h, character_prefix):
    assert a % q
    shift = (c - b * b * pow(4 * a, -1, q)) % q
    main = (a * (q - 1) * (2 * q - 1) // 6
            + b * ((q - 1) // 2) + c - (q - 1) // 2)
    return (main + legendre(a, q) * h
            + legendre(a, q) * legendre(-1, q) * character_prefix[shift])


def complete_binary_quadratic_sum(a, b, c, d, e, f, q):
    """Sum floor((a*x^2+b*x*y+c*y^2+d*x+e*y+f)/q), 0<=x,y<q."""
    determinant4 = (4 * a * c - b * b) % q
    assert determinant4
    shift = (f - (c * d * d - b * d * e + a * e * e)
             * pow(determinant4, -1, q)) % q
    epsilon = legendre(-determinant4, q)
    s1 = q * (q - 1) // 2
    s2 = q * (q - 1) * (2 * q - 1) // 6
    polynomial_total = ((a + c) * q * s2 + b * s1 * s1
                        + (d + e) * q * s1 + f * q * q)
    residue_total = ((q - epsilon) * q * (q - 1) // 2
                     + q * epsilon * shift)
    assert (polynomial_total - residue_total) % q == 0
    return (polynomial_total - residue_total) // q


def repeated_coordinate_count(n):
    """Return #{(a,b): a != b, a^2*b <= n}, in O(n^(1/3)) steps."""
    root = integer_root(n, 3)
    total = sum(n // (a * a) for a in range(1, root + 1))
    max_quotient = n // ((root + 1) ** 2)
    for value in range(1, max_quotient + 1):
        upper = isqrt(n // value)
        lower = max(root, isqrt(n // (value + 1)))
        total += value * max(0, upper - lower)
    assert root + max_quotient <= 2 * root
    return total - root


def main():
    limit = 10000
    _, pi, _, d2_prefix, *_ = tables(limit)
    primes = [q for q in range(5, 258) if pi[q] > pi[q - 1]]
    rng = Random(20260922)
    univariate_checks = 0
    bivariate_checks = 0
    character_recovery_checks = 0
    anisotropic_prime_checks = 0
    integral_tangent_block_checks = 0
    class_numbers = {}
    for q in primes:
        h = negative_prime_class_number(q) if q % 4 == 3 else 0
        if h:
            class_numbers[str(q)] = h
        if q % 3 == 2:
            assert all((r * r + r + 1) % q for r in range(q))
            anisotropic_prime_checks += 1
        for side in range(1, isqrt((q - 1) // 3) + 1):
            direct = sum(q ** 3 // ((q + x) * (q + y))
                         for x in range(side + 1) for y in range(side + 1))
            assert direct == (side + 1) ** 2 * (q - side)
            integral_tangent_block_checks += 1
        chi = [legendre(r, q) for r in range(q)]
        character_prefix = [0] * q
        for r in range(1, q):
            character_prefix[r] = character_prefix[r - 1] + chi[r]
        assert sum(r * chi[r] for r in range(q)) == -q * h

        if q <= 47:
            cases = ((a, b, c) for a in range(1, q)
                     for b in (0, 1, q - 1) for c in range(q))
        else:
            cases = [(rng.randrange(1, q) - q * rng.randrange(3),
                      rng.randrange(-3 * q, 3 * q),
                      rng.randrange(-3 * q, 3 * q)) for _ in range(32)]
        for a, b, c in cases:
            direct = sum((a * k * k + b * k + c) // q for k in range(q))
            result = complete_quadratic_sum(a, b, c, q, h, character_prefix)
            assert direct == result, (q, a, b, c, direct, result)
            univariate_checks += 1

        # A general complete-period floor-sum oracle recovers every prefix
        # character sum: F(1,0,d)-F(1,0,0)-d = chi(-1)*sum_{r<=d}chi(r).
        base = sum(k * k // q for k in range(q))
        for shift in range(q):
            shifted = sum((k * k + shift) // q for k in range(q))
            recovered = legendre(-1, q) * (shifted - base - shift)
            assert recovered == character_prefix[shift]
            character_recovery_checks += 1

        if q <= 47:
            for _ in range(32):
                while True:
                    a, b, c, d, e, f = [rng.randrange(-2 * q, 2 * q)
                                       for _ in range(6)]
                    if (4 * a * c - b * b) % q:
                        break
                direct = sum((a * x * x + b * x * y + c * y * y
                              + d * x + e * y + f) // q
                             for x in range(q) for y in range(q))
                result = complete_binary_quadratic_sum(a, b, c, d, e, f, q)
                assert direct == result, (q, a, b, c, d, e, f)
                bivariate_checks += 1

    # References count products directly and do not use the symmetry formula.
    repeated_coefficients = [0] * (limit + 1)
    for a in range(1, isqrt(limit) + 1):
        for b in range(1, limit // (a * a) + 1):
            if a != b:
                repeated_coefficients[a * a * b] += 1
    strict_coefficients = [0] * (limit + 1)
    for a in range(1, integer_root(limit, 3) + 1):
        for b in range(a + 1, isqrt(limit // a) + 1):
            for c in range(b + 1, limit // (a * b) + 1):
                strict_coefficients[a * b * c] += 1
    d2 = [0] + [d2_prefix[n] - d2_prefix[n - 1] for n in range(1, limit + 1)]
    d3 = convolution([0] + [1] * limit, d2, limit)
    strict = repeated = ordered = 0
    for n in range(1, limit + 1):
        strict += strict_coefficients[n]
        repeated += repeated_coefficients[n]
        ordered += d3[n]
        root = integer_root(n, 3)
        assert repeated_coordinate_count(n) == repeated
        assert ordered == 6 * strict + 3 * repeated + root
        residual = (ordered - 3 * repeated - root) % 9
        assert residual % 3 == 0
        assert (2 * (residual // 3)) % 3 == strict % 3

    # Exact obstruction for approximants with denominator <= the block side.
    # For coefficient 1/A and q <= h <= A/2, every a/q differs by >= 1/A.
    # Checking the nearest candidates 0 and 1 suffices for integer a.
    denominator_checks = 0
    for block_side in range(2, 65, 2):
        center = 128 * block_side
        for denominator in range(1, block_side + 1):
            assert center - denominator >= denominator
            denominator_checks += 1
        # h^2/(8*A) > 6*h^3/A^2, with no floating-point operations.
        assert center > 48 * block_side

    results = {
        "status": "passed",
        "scope": "exact finite identity checks; direct reference computations",
        "sub_square_root_pi_algorithm": False,
        "GRH_class_number_algorithm_implemented": False,
        "univariate_complete_period_checks": univariate_checks,
        "character_prefix_recovery_checks": character_recovery_checks,
        "bivariate_complete_period_checks": bivariate_checks,
        "anisotropic_prime_checks": anisotropic_prime_checks,
        "integral_tangent_block_checks": integral_tangent_block_checks,
        "prime_modulus_range": [5, 257],
        "independently_enumerated_class_numbers": class_numbers,
        "shift_counterexample": {
            "modulus": 7, "coefficients": [1, 0, 1],
            "actual_floor_sum": 11,
            "result_if_character_prefix_is_omitted": 12,
            "missing_character_correction": -1
        },
        "D3_symmetry_and_cuberoot_repeated_count_checks": limit,
        "small_denominator_obstruction_checks": denominator_checks,
        "remaining_problem": "incomplete two-dimensional quadratic patches and uniform growing moduli"
    }
    output = Path(__file__).with_name("quadratic_periods_results.json")
    output.write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items()
                      if k != "independently_enumerated_class_numbers"}, indent=2))


if __name__ == "__main__":
    main()
```

### A.9. verify_convex_caps.py

```python
"""Exact floor-to-convex-cap reductions, plus exploratory hull statistics.

Point enumeration is a reference computation. The optional-looking hull stage
also enumerates every point first; it is not the proposed fast counting oracle.
SciPy hull construction is floating point and supplies descriptive data only.
"""

from fractions import Fraction
from pathlib import Path
from random import Random
from math import sqrt
import json

import numpy as np
from scipy.spatial import ConvexHull

from verify_identities import integer_root


def patch(n, a, b, hx, hy):
    denominator = a ** 3 * b ** 3
    q = (n * a * a * b * b, -n * a * b * b, -n * a * a * b,
         n * b * b, n * a * b, n * a * a)
    curvature_max = q[3] * hx * hx + q[4] * hx * hy + q[5] * hy * hy
    upper = (q[0] + curvature_max, q[1], q[2])
    quadratic_volume = Fraction(n, a * b) * (
        Fraction(2 * hx ** 3 * hy, 3 * a * a)
        + Fraction(3 * hx * hx * hy * hy, 4 * a * b)
        + Fraction(2 * hx * hy ** 3, 3 * b * b))
    product_volume_upper = Fraction(curvature_max * hx * hy, denominator)
    return denominator, q, upper, quadratic_volume, product_volume_upper


def polynomial(q, x, y):
    return q[0] + q[1] * x + q[2] * y + q[3] * x * x + q[4] * x * y + q[5] * y * y


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def affine_rank_and_normal(points):
    if not points:
        return -1, None
    base = points[0]
    first = normal = None
    for point in points[1:]:
        vector = tuple(x - y for x, y in zip(point, base))
        if not any(vector):
            continue
        if first is None:
            first = vector
        elif normal is None:
            candidate = cross(first, vector)
            if any(candidate):
                normal = candidate
        elif sum(x * y for x, y in zip(normal, vector)):
            return 3, None
    if normal is not None:
        return 2, normal
    return (1, None) if first is not None else (0, None)


def exploratory_hull(n, a, b, side):
    denominator, q, upper, lower_volume, upper_volume = patch(n, a, b, side, side)
    # The exact integer body has lower graph (n+1)/((a+x)*(b+y)).
    # Its volume can be smaller than that of the unshifted n-body.
    lower_volume = max(Fraction(0), lower_volume - Fraction(side * side, a * b))
    points = []
    z_offset = n // (a * b)
    for x in range(side + 1):
        for y in range(side + 1):
            z_min = n // ((a + x) * (b + y)) + 1
            z_max = (upper[0] + upper[1] * x + upper[2] * y) // denominator
            points.extend((x, y, z - z_offset) for z in range(z_min, z_max + 1))
    rank, normal = affine_rank_and_normal(points)
    if rank <= 0:
        vertices = len(points)
    elif rank == 1:
        vertices = 2
    else:
        coordinates = np.array(points, dtype=np.float64)
        if rank == 2:
            # An injective coordinate projection of the plane, chosen exactly.
            omit = max(range(3), key=lambda index: abs(normal[index]))
            coordinates = coordinates[:, [i for i in range(3) if i != omit]]
        vertices = len(ConvexHull(coordinates).vertices)
    return {
        "n": n, "a0": a, "b0": b, "side": side,
        "enumerated_points": len(points), "exact_affine_dimension": rank,
        "floating_point_hull_vertices": vertices,
        "continuous_volume_lower": float(lower_volume),
        "continuous_volume_upper": float(upper_volume),
        "vertices_over_sqrt_volume_upper": vertices / sqrt(float(upper_volume))
    }


def main():
    rng = Random(20260923)
    cases = []
    for _ in range(160):
        a, b = rng.randrange(8, 81), rng.randrange(8, 81)
        n = rng.randrange(8, 81) * a * b + rng.randrange(a * b)
        hx, hy = rng.randrange(1, min(10, a // 4) + 1), rng.randrange(1, min(10, b // 4) + 1)
        cases.append((n, a, b, hx, hy))
    for a in (8, 12, 18, 24, 32):
        for side in range(1, 1 + a // 4):
            cases.append((a ** 3, a, a, side, side))

    grid_points = 0
    product_boundary_points = 0
    quadratic_boundary_points = 0
    for n, a, b, hx, hy in cases:
        denominator, q, upper, volume, volume_upper = patch(n, a, b, hx, hy)
        assert 0 < volume < volume_upper
        z_first = max(0, n // ((a + hx) * (b + hy)) - 1)
        z_last = upper[0] // denominator + 2
        actual_sum = quadratic_sum = affine_sum = 0
        product_cap = quadratic_cap = 0
        for x in range(hx + 1):
            for y in range(hy + 1):
                product_denominator = (a + x) * (b + y)
                q_num = polynomial(q, x, y)
                u_num = upper[0] + upper[1] * x + upper[2] * y
                assert n * denominator <= q_num * product_denominator
                assert q_num <= u_num
                actual_sum += n // product_denominator
                quadratic_sum += q_num // denominator
                affine_sum += u_num // denominator
                product_boundary_points += (n % product_denominator == 0)
                quadratic_boundary_points += (q_num % denominator == 0)
                for z in range(z_first, z_last + 1):
                    # These are the closed, integer-coefficient inequalities
                    # of the convex bodies, including the strict-boundary +1.
                    product_cap += (product_denominator * z >= n + 1
                                    and denominator * z <= u_num)
                    quadratic_cap += (denominator * z >= q_num + 1
                                      and denominator * z <= u_num)
                grid_points += 1
        assert actual_sum == affine_sum - product_cap
        assert quadratic_sum == affine_sum - quadratic_cap
        assert product_cap >= quadratic_cap

    volume_checks = 0
    for scale in range(4, 24):
        for hx, hy in ((1, 1), (2, 3), (3, 2), (4, 5)):
            a, b = scale * hx, scale * hy
            n = a * b * (a + b) + 1
            _, _, _, volume, upper = patch(n, a, b, hx, hy)
            assert volume == Fraction(25 * n, 12 * scale ** 4)
            assert upper == Fraction(3 * n, scale ** 4)
            volume_checks += 1

    exponent_checks = []
    for dimension in range(2, 9):
        exponent = Fraction(dimension - 1, dimension + 1)
        for j in range(5):
            beta = Fraction(j, 5 * (dimension + 1))
            combined = beta * (dimension - 1) + (1 - beta * (dimension + 1)) * exponent
            assert combined == exponent
        exponent_checks.append({"fixed_dimension": dimension,
                                "full_dimension_hull_bound_exponent": str(exponent)})

    hull_cases = []
    for scale in (2 ** 8, 2 ** 12, 2 ** 16, 2 ** 20):
        side = integer_root(scale ** 9, 20)
        for _ in range(3):
            a, b = scale + rng.randrange(scale), scale + rng.randrange(scale)
            n = scale ** 3 + rng.randrange(scale ** 2)
            hull_cases.append(exploratory_hull(n, a, b, side))

    results = {
        "status": "passed",
        "scope": "exact cap-reduction checks and exploratory hull statistics",
        "sub_square_root_pi_algorithm": False,
        "fast_cap_counter_implemented": False,
        "hull_statistics_certified": False,
        "exact_patch_checks": len(cases),
        "exact_grid_point_checks": grid_points,
        "strict_product_boundary_cases": product_boundary_points,
        "strict_quadratic_boundary_cases": quadratic_boundary_points,
        "exact_volume_checks": volume_checks,
        "conditional_hull_bound_balance": exponent_checks,
        "exploratory_hull_cases": hull_cases,
        "interpretation": "A hull-size upper bound is not a counting algorithm or a time lower bound."
    }
    Path(__file__).with_name("convex_caps_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items() if k != "exploratory_hull_cases"}, indent=2))
    print("Exploratory hulls (side, points, dimension, vertices):")
    print([(r["side"], r["enumerated_points"], r["exact_affine_dimension"],
            r["floating_point_hull_vertices"]) for r in hull_cases])


if __name__ == "__main__":
    main()
```

### A.10. verify_fourier_traces.py

```python
"""Exact mod-9 Fourier/orbit checks and carry-compression counterexamples.

Arithmetic uses the full cyclotomic algebra for reference checks. It is dense
and does not implement a fast trace algorithm or a new prime-counting method.
"""

from math import comb
from pathlib import Path
from random import Random
import json


class CyclotomicReference:
    def __init__(self, prime, modulus=9):
        self.q = prime
        self.modulus = modulus

    def reduce(self, coefficients):
        cyclic = [0] * self.q
        for exponent, coefficient in enumerate(coefficients):
            cyclic[exponent % self.q] += coefficient
        # t^(q-1) = -(1+t+...+t^(q-2)); t^q=1.
        return tuple((c - cyclic[-1]) % self.modulus for c in cyclic[:-1])

    def constant(self, n):
        return (n % self.modulus,) + (0,) * (self.q - 2)

    def monomial(self, exponent):
        coefficients = [0] * self.q
        coefficients[exponent % self.q] = 1
        return self.reduce(coefficients)

    def add(self, a, b):
        return tuple((x + y) % self.modulus for x, y in zip(a, b))

    def scale(self, a, multiplier):
        return tuple(x * multiplier % self.modulus for x in a)

    def multiply(self, a, b):
        coefficients = [0] * (len(a) + len(b) - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    coefficients[i + j] += x * y
        return self.reduce(coefficients)

    def cube(self, a):
        return self.multiply(self.multiply(a, a), a)

    def frobenius(self, a):
        coefficients = [0] * self.q
        for i, coefficient in enumerate(a):
            coefficients[(3 * i) % self.q] += coefficient
        return self.reduce(coefficients)

    def kernel(self, j):
        result = self.constant(0)
        for r in range(self.q):
            result = self.add(result, self.scale(self.monomial(-j * r), r))
        return self.scale(result, -pow(self.q, -1, self.modulus))


def frobenius_orbits(q):
    unseen = set(range(1, q))
    result = []
    while unseen:
        start = min(unseen)
        orbit = []
        j = start
        while j not in orbit:
            orbit.append(j)
            unseen.remove(j)
            j = 3 * j % q
        assert j == start
        result.append(orbit)
    return result


def rank_mod_three(matrix):
    a = [[entry % 3 for entry in row] for row in matrix]
    rank = 0
    for column in range(len(a[0])):
        pivot = next((i for i in range(rank, len(a)) if a[i][column]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        inverse = pow(a[rank][column], -1, 3)
        a[rank] = [x * inverse % 3 for x in a[rank]]
        for i in range(rank + 1, len(a)):
            factor = a[i][column]
            if factor:
                a[i] = [(x - factor * y) % 3 for x, y in zip(a[i], a[rank])]
        rank += 1
    return rank


def f27_multiply(a, b):
    coefficients = [0] * 5
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            coefficients[i + j] += x * y
    # u^3 = u+1 over F3.
    for i in (4, 3):
        coefficients[i - 2] += coefficients[i]
        coefficients[i - 3] += coefficients[i]
    return tuple(x % 3 for x in coefficients[:3])


def main():
    primes = (2, 5, 7, 11, 13, 17, 19, 23, 29, 31)
    rng = Random(20260924)
    checks = 0
    frobenius_checks = 0
    incorrect_cube_groups = 0
    orbit_profiles = []
    for q in primes:
        algebra = CyclotomicReference(q)
        zero, one = algebra.constant(0), algebra.constant(1)
        kernels = {j: algebra.kernel(j) for j in range(1, q)}
        for j, kernel in kernels.items():
            denominator = algebra.add(one, algebra.scale(algebra.monomial(-j), -1))
            assert algebra.multiply(denominator, kernel) == one
        orbits = frobenius_orbits(q)
        degree = len(orbits[0])
        assert all(len(orbit) == degree for orbit in orbits)
        assert degree * len(orbits) == q - 1
        orbit_profiles.append({"prime": q, "extension_degree": degree,
                               "orbit_count": len(orbits),
                               "dense_base_coordinates": degree * len(orbits)})
        cases = [[r] for r in range(-q, 2 * q)]
        for _ in range(16):
            a, b, c, d, e, f = [rng.randrange(-2 * q, 2 * q) for _ in range(6)]
            side = rng.randrange(1, 6)
            cases.append([a * x * x + b * x * y + c * y * y + d * x + e * y + f
                          for x in range(side) for y in range(side)])
        for values in cases:
            frequencies = {}
            for j in range(1, q):
                exponential_sum = zero
                for value in values:
                    exponential_sum = algebra.add(exponential_sum, algebra.monomial(j * value))
                frequencies[j] = algebra.multiply(exponential_sum, kernels[j])
            total = zero
            for j, value in frequencies.items():
                assert algebra.frobenius(value) == frequencies[3 * j % q]
                assert all((x - y) % 3 == 0 for x, y in
                           zip(algebra.cube(value), algebra.frobenius(value)))
                total = algebra.add(total, value)
                frobenius_checks += 1
            grouped = wrong_grouped = zero
            for orbit in orbits:
                value = wrong_value = frequencies[orbit[0]]
                for _ in orbit:
                    grouped = algebra.add(grouped, value)
                    wrong_grouped = algebra.add(wrong_grouped, wrong_value)
                    value = algebra.frobenius(value)
                    wrong_value = algebra.cube(wrong_value)
            assert grouped == total
            incorrect_cube_groups += wrong_grouped != total
            invq, inv2 = pow(q, -1, 9), pow(2, -1, 9)
            main_term = (sum(values) - len(values) * (q - 1) * inv2) * invq
            recovered = algebra.add(algebra.constant(main_term), algebra.scale(total, invq))
            expected = algebra.constant(sum(value // q for value in values))
            assert recovered == expected
            checks += 1

    algebra = CyclotomicReference(5)
    s = algebra.add(algebra.constant(1), algebra.monomial(1))
    cube_defect = algebra.add(algebra.cube(s), algebra.scale(algebra.frobenius(s), -1))
    assert cube_defect == (0, 3, 3, 0)
    assert incorrect_cube_groups > 0

    powers = [(1, 0, 0)]
    for _ in range(26):
        powers.append(f27_multiply(powers[-1], (0, 1, 0)))
    assert powers[13] == (1, 0, 0)
    trace = tuple(sum(powers[k][i] for k in (2, 6, 18)) % 3 for i in range(3))
    assert trace == (2, 0, 0)

    rank_checks = []
    for q in range(2, 42):
        carry = [[(u + v) // q for v in range(q)] for u in range(q)]
        rank = rank_mod_three(carry)
        assert rank == q - 1
        assert all(carry[u][q - j] == int(u >= j)
                   for u in range(1, q) for j in range(1, q))
        rank_checks.append({"q": q, "rank_mod3": rank})

    moment_counterexamples = []
    q = 17
    for order in range(1, 10):
        signed = [(-1) ** u * comb(order, u) for u in range(order + 1)]
        positive = [max(0, c) for c in signed]
        negative = [max(0, -c) for c in signed]
        assert sum(positive) == sum(negative) == 2 ** (order - 1)
        for power in range(order):
            assert sum((positive[u] - negative[u]) * u ** power for u in range(order + 1)) == 0
        other_residue = q - order
        carry_difference = sum((positive[u] - negative[u]) * ((u + other_residue) // q)
                               for u in range(order + 1))
        assert carry_difference == (-1) ** order
        moment_counterexamples.append({"matched_moment_count": order,
                                       "histogram_mass": sum(positive),
                                       "other_residue": other_residue,
                                       "carry_difference": carry_difference})

    results = {
        "status": "passed",
        "scope": "exact dense reference algebra; no fast aggregation implementation",
        "sub_square_root_pi_algorithm": False,
        "mod9_floor_fourier_checks": checks,
        "frobenius_frequency_checks": frobenius_checks,
        "incorrect_cubing_group_failures": incorrect_cube_groups,
        "cube_defect_mod9_at_q5": list(cube_defect),
        "nonzero_trace_in_degree3_extension_mod3": list(trace),
        "orbit_profiles": orbit_profiles,
        "carry_rank_checks": rank_checks,
        "moment_counterexamples": moment_counterexamples,
        "limitation": "Rank statements concern arbitrary histograms and specified representations, not all structured counting algorithms."
    }
    Path(__file__).with_name("fourier_traces_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print(json.dumps({k: v for k, v in results.items()
                      if k not in ("carry_rank_checks", "orbit_profiles", "moment_counterexamples")}, indent=2))
    print("Orbit profiles:", orbit_profiles)


if __name__ == "__main__":
    main()
```

### A.11. direct_log_integral.py

```python
"""Functional prototype of a direct local log-zeta integral.

This constructs the Dirichlet coefficients by enumeration, uses mpmath rather
than intervals, and does not implement the fast theta/cubic moment oracle.
It checks the aggregation formulas, not a new asymptotic prime-counting bound.
"""

from pathlib import Path
import json

import mpmath as mp
import numpy as np


def exponential_coefficients(rate, degree):
    values = [mp.mpc(1)]
    for j in range(1, degree + 1):
        values.append(values[-1] * rate / j)
    return np.array(values, dtype=object)


def multiply_polynomials(a, b, degree):
    result = np.zeros((len(a) + len(b) - 1, degree + 1), dtype=object)
    for i, first in enumerate(a):
        for j, second in enumerate(b):
            result[i + j] += np.convolve(first, second)[:degree + 1]
    return result


def oscillatory_moments(omega, degree):
    if abs(omega) >= 2 * (degree + 1):
        rate = mp.j * omega
        endpoint = mp.exp(rate)
        result = [mp.expm1(rate) / rate]
        for j in range(1, degree + 1):
            result.append((endpoint - j * result[-1]) / rate)
        return result
    return [mp.hyp1f1(j + 1, j + 2, mp.j * omega) / (j + 1)
            for j in range(degree + 1)]


def aggregate_case(t0, width, frequency, cutoff, degree=28, log_terms=10, em_terms=8):
    sigma = 24
    s0 = mp.mpc(sigma, t0)

    def bin_and_residual(m):
        index = int(mp.nint(width * mp.log(m) / (2 * mp.pi)))
        residual = 2 * mp.pi * index - width * mp.log(m)
        return index, residual

    max_bin, em_residual = bin_and_residual(cutoff)
    g = np.zeros((max_bin + 1, degree + 1), dtype=object)
    analytic_norm = mp.mpf(0)
    for m in range(2, cutoff):
        index, residual = bin_and_residual(m)
        amplitude = mp.exp(-s0 * mp.log(m))
        g[index] += amplitude * exponential_coefficients(mp.j * residual, degree)
        analytic_norm += mp.mpf(m) ** (-sigma) * mp.exp(3 * abs(residual))

    # Euler--Maclaurin uses sum_{m=1}^{M-1}, so the M endpoint has +1/2.
    em_core = np.zeros(degree + 1, dtype=object)
    ratio = -mp.j * width / (s0 - 1)
    em_core[:] = [cutoff / (s0 - 1) * ratio ** j for j in range(degree + 1)]
    em_core[0] += mp.mpf('0.5')
    em_core_norm = cutoff / (abs(s0 - 1) - 3 * width) + mp.mpf('0.5')
    assert abs(s0 - 1) > 3 * width
    for k in range(1, em_terms + 1):
        rising = np.array([mp.mpc(1)], dtype=object)
        rising_norm = mp.mpf(1)
        for j in range(2 * k - 1):
            rising = np.convolve(rising, np.array([s0 + j, mp.j * width], dtype=object))
            rising_norm *= abs(s0 + j) + 3 * width
        scale = mp.bernoulli(2 * k) / mp.factorial(2 * k) * mp.mpf(cutoff) ** (1 - 2 * k)
        em_core[:len(rising)] += scale * rising
        em_core_norm += abs(scale) * rising_norm
    em_amplitude = mp.exp(-s0 * mp.log(cutoff))
    g[max_bin] += em_amplitude * np.convolve(
        em_core, exponential_coefficients(mp.j * em_residual, degree))[:degree + 1]
    analytic_norm += mp.mpf(cutoff) ** (-sigma) * mp.exp(3 * abs(em_residual)) * em_core_norm
    assert analytic_norm < mp.mpf(1) / 16

    result = np.zeros((log_terms * max_bin + 1, degree + 1), dtype=object)
    power = np.zeros((1, degree + 1), dtype=object)
    power[0, 0] = mp.mpc(1)
    for k in range(1, log_terms + 1):
        power = multiply_polynomials(power, g, degree)
        result[:len(power)] += (mp.mpf((-1) ** (k + 1)) / k) * power

    # Include the slowly varying factor 1/(sigma+i(t0+width*z)).
    weight = np.array([(-mp.j * width / s0) ** j / s0
                       for j in range(degree + 1)], dtype=object)
    for index in range(len(result)):
        result[index] = np.convolve(result[index], weight)[:degree + 1]
    integral = mp.mpc(0)
    for index, coefficients in enumerate(result):
        moments = oscillatory_moments(frequency * width - 2 * mp.pi * index, degree)
        integral += mp.fsum(coefficient * moment for coefficient, moment in zip(coefficients, moments))

    reference = mp.quad(lambda z: mp.exp(mp.j * frequency * width * z)
                        * mp.log(mp.zeta(s0 + mp.j * width * z))
                        / (s0 + mp.j * width * z), [0, mp.mpf('0.5'), 1])
    error = abs(integral - reference)

    rising_bound = mp.mpf(1)
    for j in range(2 * em_terms):
        rising_bound *= mp.sqrt((sigma + j) ** 2 + (t0 + width) ** 2)
    em_remainder = (2 * mp.zeta(2 * em_terms) / (2 * mp.pi) ** (2 * em_terms)
                    * rising_bound * mp.mpf(cutoff) ** (1 - sigma - 2 * em_terms)
                    / (sigma + 2 * em_terms - 1))
    rho = 3 * analytic_norm
    weight_bound = 1 / (abs(s0) - 2 * width)
    bound = weight_bound * (
        analytic_norm * mp.mpf(3) ** (-degree)
        + rho ** (log_terms + 1) / ((log_terms + 1) * (1 - rho))
        - mp.log(1 - rho) * mp.mpf(2) ** (-degree)
        + 2 * em_remainder)
    assert error < bound
    assert error < mp.mpf('1e-20')
    return {
        "t0": t0, "width": width, "sigma": sigma, "cutoff": cutoff,
        "carrier_frequency": mp.nstr(frequency, 25),
        "polynomial_degree": degree, "log_terms": log_terms,
        "em_terms": em_terms, "maximum_input_frequency_bin": max_bin,
        "dense_aggregate_coefficient_count": result.size,
        "analytic_norm_on_radius3": mp.nstr(analytic_norm, 10),
        "absolute_error_against_high_precision_quadrature": mp.nstr(error, 12),
        "analytic_error_bound_evaluated_numerically": mp.nstr(bound, 12),
        "em_remainder_bound_evaluated_numerically": mp.nstr(em_remainder, 12)
    }


def main():
    mp.mp.dps = 70
    cases = []
    parameters = [(64, 1, mp.log(1000), 256),
                  (128, 2, mp.pi, 512),
                  (512, 3, mp.log(10 ** 6), 2048)]
    for parameters_one in parameters:
        result = aggregate_case(*parameters_one)
        cases.append(result)
        print(json.dumps(result), flush=True)
    results = {
        "status": "passed",
        "scope": "local direct log-zeta integral formulas; high-precision non-interval prototype",
        "interval_certified": False,
        "fast_theta_or_cubic_oracle_implemented": False,
        "full_prime_counting_algorithm_implemented": False,
        "sub_square_root_pi_algorithm": False,
        "cases": cases
    }
    Path(__file__).with_name('direct_log_integral_results.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
```

### A.12. verify_resonant_coefficients.py

```python
"""B-spline frequency localization and selective log-coefficient checks.

Formal coefficient checks are exact modulo a prime, including two nilpotent
variables. Window moment comparisons use high precision without intervals.
No fast global prime counter is implemented.
"""

from fractions import Fraction
from math import comb, factorial
from pathlib import Path
from random import Random
import json

import mpmath as mp


def spline_exact(order, t):
    return sum(Fraction((-1) ** k * comb(order, k), factorial(order - 1))
               * max(Fraction(0), t - k) ** (order - 1)
               for k in range(order + 1))


def spline_piece_coefficients(order, piece):
    coefficients = [Fraction(0)] * order
    for k in range(piece + 1):
        multiplier = Fraction((-1) ** k * comb(order, k), factorial(order - 1))
        for degree in range(order):
            coefficients[degree] += (multiplier * comb(order - 1, degree)
                                     * order ** degree * (-k) ** (order - 1 - degree))
    return coefficients


class JetRing:
    """F_p[z,u]/(z^(D+1),u^(J+1)); dictionary keys are (z degree,u degree)."""

    def __init__(self, z_degree, u_degree, modulus=1000003):
        self.z_degree = z_degree
        self.u_degree = u_degree
        self.modulus = modulus

    def constant(self, value):
        value %= self.modulus
        return {(0, 0): value} if value else {}

    def add(self, a, b):
        result = a.copy()
        for key, value in b.items():
            updated = (result.get(key, 0) + value) % self.modulus
            if updated:
                result[key] = updated
            else:
                result.pop(key, None)
        return result

    def scale(self, a, multiplier):
        return {key: value * multiplier % self.modulus for key, value in a.items()
                if value * multiplier % self.modulus}

    def multiply(self, a, b):
        result = {}
        for (az, au), av in a.items():
            for (bz, bu), bv in b.items():
                key = (az + bz, au + bu)
                if key[0] <= self.z_degree and key[1] <= self.u_degree:
                    result[key] = (result.get(key, 0) + av * bv) % self.modulus
        return {key: value for key, value in result.items() if value}

    def inverse_unit(self, a):
        # Our denominators are 1 modulo u, so the geometric inverse is finite.
        assert {key: value for key, value in a.items() if key[1] == 0} == self.constant(1)
        negative_tail = self.add(self.constant(1), self.scale(a, -1))
        result = power = self.constant(1)
        for _ in range(self.u_degree):
            power = self.multiply(power, negative_tail)
            result = self.add(result, power)
        assert self.multiply(result, a) == self.constant(1)
        return result

    def polynomial_multiply(self, a, b):
        result = [{} for _ in range(len(a) + len(b) - 1)]
        for i, av in enumerate(a):
            for j, bv in enumerate(b):
                result[i + j] = self.add(result[i + j], self.multiply(av, bv))
        return result


def one_coefficient(ring, numerator, denominator, index):
    while index:
        negative_denominator = [ring.scale(value, (-1) ** k)
                                for k, value in enumerate(denominator)]
        product = ring.polynomial_multiply(numerator, negative_denominator)
        square = ring.polynomial_multiply(denominator, negative_denominator)
        assert all(not value for value in square[1::2])
        numerator = product[index % 2::2]
        denominator = square[::2]
        index //= 2
        if not numerator:
            return {}
    return ring.multiply(numerator[0], ring.inverse_unit(denominator[0]))


def main():
    partition_checks = 0
    for order in range(2, 13):
        for numerator in range(-12, 73):
            t = Fraction(numerator, 6)
            value = sum(spline_exact(order, t - shift)
                        for shift in range(t.numerator // t.denominator - order,
                                           t.numerator // t.denominator + 1))
            assert value == 1
            partition_checks += 1

    mp.mp.dps = 65
    moment_results = []
    for order in (4, 6, 10):
        pieces = []
        for piece in range(order):
            coefficients = spline_piece_coefficients(order, piece)
            pieces.append([mp.mpf(c.numerator) / c.denominator for c in coefficients])
        for power in (0, 1, 3):
            for omega in (mp.mpf(0), mp.mpf(order), mp.mpf(4 * (power + 2 * order))):
                def transform(t):
                    return mp.exp(mp.j * t / 2) * mp.sinc(t / (2 * order)) ** order / order
                closed = mp.diff(transform, omega, power) / (mp.j ** power)
                reference = mp.mpc(0)
                for piece, coefficients in enumerate(pieces):
                    reference += mp.quad(
                        lambda z: z ** power * mp.polyval(list(reversed(coefficients)), z)
                        * mp.exp(mp.j * omega * z),
                        [mp.mpf(piece) / order, mp.mpf(piece + 1) / order])
                error = abs(closed - reference)
                assert error < mp.mpf('1e-45')
                derivative_order = order - 1
                bound = mp.mpf(1) / order
                if omega:
                    bound *= min(1, (mp.mpf(power + 2 * order) / abs(omega)) ** derivative_order)
                assert abs(closed) <= bound + mp.mpf('1e-50')
                moment_results.append({"spline_order": order, "power": power,
                                       "frequency": str(omega),
                                       "absolute_error": mp.nstr(error, 8),
                                       "moment_magnitude": mp.nstr(abs(closed), 8),
                                       "analytic_upper_bound": mp.nstr(bound, 8)})

    rng = Random(20260925)
    ring = JetRing(2, 5)
    coefficient_checks = 0
    for _ in range(18):
        degree = rng.randrange(2, 7)
        marked_g = [{(z, 1): rng.randrange(1, 10) for z in range(3)}
                    for _ in range(degree + 1)]
        denominator = [value.copy() for value in marked_g]
        denominator[0] = ring.add(denominator[0], ring.constant(1))
        numerator = [ring.scale(marked_g[k], k) for k in range(1, degree + 1)]
        logarithm = [{} for _ in range(ring.u_degree * degree + 1)]
        power = [ring.constant(1)]
        for k in range(1, ring.u_degree + 1):
            power = ring.polynomial_multiply(power, marked_g)
            multiplier = (-1) ** (k + 1) * pow(k, -1, ring.modulus)
            for index, value in enumerate(power):
                logarithm[index] = ring.add(logarithm[index], ring.scale(value, multiplier))
        for target in (1, degree, degree + 1, 2 * degree,
                       rng.randrange(1, len(logarithm)), 10 ** 6):
            computed = one_coefficient(ring, numerator, denominator, target - 1)
            computed = ring.scale(computed, pow(target, -1, ring.modulus))
            expected = logarithm[target] if target < len(logarithm) else {}
            assert computed == expected
            coefficient_checks += 1

    # Exact finite checks of the dense-input sensitivity argument at K=B+1.
    sensitivity_checks = 0
    rho = Fraction(1, 32)
    for degree in range(2, 15):
        base = [Fraction(1)] + [-rho / degree] * degree
        target = degree + 1

        def log_coefficient(f):
            inverse = [Fraction(1)] + [Fraction(0)] * target
            for k in range(1, target + 1):
                inverse[k] = -sum(f[j] * inverse[k - j]
                                  for j in range(1, min(k, degree) + 1))
            return sum(j * f[j] * inverse[target - j]
                       for j in range(1, degree + 1)) / target

        original = log_coefficient(base)
        for index in range(1, degree + 1):
            changed = base.copy()
            changed[index] += rho / (2 * degree)
            difference = log_coefficient(changed) - original
            assert difference >= rho * rho / (4 * degree * degree)
            sensitivity_checks += 1

    results = {
        "status": "passed",
        "scope": "exact spline partition/formal coefficients; non-interval high-precision moments",
        "sub_square_root_pi_algorithm": False,
        "fast_fft_multiplication_implemented": False,
        "interval_certified": False,
        "exact_partition_of_unity_checks": partition_checks,
        "window_moment_checks": moment_results,
        "exact_marked_log_coefficient_checks": coefficient_checks,
        "coefficient_test_modulus": ring.modulus,
        "nilpotent_degrees": {"z": ring.z_degree, "u": ring.u_degree},
        "largest_target_index": 10 ** 6,
        "exact_dense_input_sensitivity_checks": sensitivity_checks,
        "limitation": "The coefficient-access bound concerns arbitrary dense inputs, not structured zeta representations."
    }
    Path(__file__).with_name('resonant_coefficients_results.json').write_text(json.dumps(results, indent=2) + '\n')
    print(json.dumps({key: value for key, value in results.items() if key != 'window_moment_checks'}, indent=2))
    print('Moment checks:', len(moment_results), 'maximum error:',
          mp.nstr(max(mp.mpf(case['absolute_error']) for case in moment_results), 8))


if __name__ == '__main__':
    main()
```
