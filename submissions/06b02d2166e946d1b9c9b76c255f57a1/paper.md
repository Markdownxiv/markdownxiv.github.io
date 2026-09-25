# Integer Factorization Across Algebra and Geometry: A Survey of Exact Oracle Reductions

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 25, 2026 · Revised version 3

## Abstract

Integer factorization is connected to exact arithmetic, algebraic, and geometric tasks whose outputs encode hidden prime-power structure. We organize a selected reduction map around explicit Chinese-remainder components, short group-exponent multiples, finite-field norm factors, and recovery of integer main terms by high-power queries. Each reduction records its representation, output, randomness, and promises. Consequences include sublattice and finite-geometric counts, modular-curve invariants, and coefficients of fixed modular forms. We then integrate quadratic forms, ideal classes, real quadratic infrastructure, conductor maps, and sieve relations. Explicit two-torsion classes can expose discriminant factors, while class-group two-torsion and unit square classes obstruct recovering an element square from an ideal square in the number field sieve. Two diagrams separate oracle reductions from arithmetic mechanisms, and the algorithm comparison distinguishes unconditional, conditional, and heuristic bounds. This is an interface-sensitive synthesis of established results and elementary combinations; no general reverse reduction from radical computation, divisor counts, quadratic-residuosity decision, or arbitrary RSA inversion is asserted.

## 1. What a reduction map must specify

Let F(n) denote the complete prime factorization of a positive integer n, including exponents. Integers are encoded in binary and L denotes their bit length. We write A≤_D B for deterministic polynomial-time Turing reducibility and A≤_R B for randomized polynomial-time oracle reducibility; the constructive factoring procedures below use expected polynomial time and verify their returned divisors. The symbol ≡_R allows one direction to be deterministic.

An oracle may be queried on polynomially many inputs of polynomial bit length, including inputs different from n. This convention must be distinguished from an algorithm receiving one extra value attached to n. A complete factorization oracle can also factor auxiliary integers, whereas a supplied factorization of n provides no automatic factorization of φ(n).

Fixed parameters are genuine constants: the dimension of a lattice, the dimension of a finite geometric space, and the weight and level of a modular form do not grow with n. An object specified succinctly by n can have exponentially many vertices, cells, roots, or coefficients. A formula for an output does not remove the cost of writing its binary expansion.

This survey selects a coherent part of a larger working reduction map. Standard reductions are attributed to their sources; the proofs below spell out useful combinations and their precise interfaces. No exhaustive classification or bibliographic priority is claimed. A missing arrow means that this paper does not establish it, not that a separation has been proved. Sections 10–12 extend the map through quadratic norms, two-torsion, infrastructure, and sieves; their mechanism diagrams are explicitly distinguished from complexity reductions.

Use the following distinct arithmetic functions:

$$\operatorname{rad}(n)=\prod_{p\mid n}p,\qquad
\tau(n)=\prod_{p^e\parallel n}(e+1),\qquad
\omega(n)=\#\{p:p\mid n\},$$

$$\sigma_s(n)=\sum_{d\mid n}d^s,\qquad
J_s(n)=n^s\prod_{p\mid n}(1-p^{-s}).$$

The squarefree kernel retaining only odd prime exponents is different from rad(n). Likewise Carmichael's group exponent λ(n) is different from Liouville's function, despite a common use of the letter lambda in the literature.


![Exact oracle reduction map. An arrow points from a task to the oracle used to compute it; hypotheses are stated in the corresponding sections.](figures/exact-reductions.png)

*Figure 1. Exact oracle interfaces in this survey. D denotes deterministic polynomial time; R permits randomized expected polynomial time. “R-equivalent” permits a deterministic direction. The pure-cusp arrow retains every promise in Section 8, including the level and small-prime restrictions and the fixed bound on omega(n). The order-class-number equivalence applies only to the displayed semiprime family. The one-way arrow from radical, divisor-count, component-count, and residuosity tasks records only their reduction to factorization.*

## 2. The arithmetic core

The classical core can be summarized as follows. Promises and the oracle convention are part of each row.

| Exact task | Relation | Essential qualification |
|---|---|---|
| Return one proper divisor of a composite | Equivalent to F deterministically | Recurse on both factors and recognize primes |
| Return the least or greatest prime factor | Equivalent to F deterministically | A numerical factor, not just a count |
| Decide whether a proper divisor is at most a variable B | Equivalent to F deterministically | Binary search in B recovers the least factor |
| Compute Euler's φ(n) or Carmichael's λ(n) | Equivalent to F with randomness | The general reverse direction uses exponent-based splitting |
| Supply a positive multiple M of λ(n) | Sufficient for randomized factoring | M must have polynomial binary length |
| Compute σ_s(n), fixed s≥1 | Equivalent to F with randomness | The s=0 divisor-count function is a different case |
| Return a square root of a promised unit square modulo n | Equivalent to F with randomness | A root witness, not quadratic-residuosity decision |
| Return a nontrivial idempotent modulo n | Factoring-equivalent on its promise | At least two distinct prime factors are required |
| Compute the multiplicative order of a supplied unit | Equivalent to F with randomness | The upper reduction may factor auxiliary integers |

Miller's exponent method [1] and the oracle treatment of Morain, Renault, and Smith [3] explain the distinction between randomized and deterministic versions. Divisor sums are treated in Bach, Miller, and Shallit [2]. Modular square roots and their reduction interfaces are discussed in [4,5].

To see why a short exponent multiple helps, remove perfect powers and the factor two, write M=2^s u with u odd, and sample bases. A nonunit base already exposes a divisor. Otherwise repeated squaring from a^u may reveal a square root of one different from ±1; gcd extraction splits n. Independence of the prime components gives a constant success probability in the usual Miller-style analysis. The resulting splits can be recursively verified. There is no need to factor M first.

A useful extension needs only a multiple of λ(rad(n)). If each p−1 divides M, then nM is a multiple of λ(n), because the extra local p-power factor divides n. This yields the same randomized factoring capability. For example, the exact values

$$\prod_{p^e\parallel n}(p^e-1),\qquad
\prod_{p^e\parallel n}(p^{se}-1)\quad(s\ge1\text{ fixed})$$

are short enough and contain p−1 for every p dividing n. They are unitary variants of totient and Jordan functions, not the ordinary functions evaluated at n.

For a semiprime n=pq with distinct primes, a single value φ(n) gives p+q=n+1−φ(n). The roots of X²−(p+q)X+n then give p and q deterministically. This special calculation must not be substituted for the general-input randomized reduction.

## 3. Structural witnesses and weaker-looking outputs

The ring Z/nZ illustrates why output type matters. A proper nonzero zero divisor exposes a factor by an integer gcd. A full Chinese-remainder decomposition into indecomposable components gives their additive orders p^e, from which p and e can be recovered. A complete set of primitive orthogonal idempotents gives the same information. Conversely, factorization constructs these objects by CRT.

By comparison,

$$J(\mathbb Z/n\mathbb Z)=\operatorname{rad}(n)(\mathbb Z/n\mathbb Z),$$

where J denotes the Jacobson radical. Additive generators of this ideal recover rad(n) by taking their common gcd with n. Given rad(n), that ideal is immediate. Its size is n/rad(n). The count of connected components of Spec(Z/nZ) is ω(n), whereas the number of idempotents is 2^{ω(n)} and the number of units is φ(n).

Thus the same small ring family gives several distinct interfaces:

| Output | Arithmetic information recovered |
|---|---|
| Explicit local components or all primitive idempotents | Full factorization |
| Generators for the radical | rad(n) |
| Number of components | ω(n) |
| Number of units | φ(n), sufficient for randomized factoring |

This table does not prove that the middle two tasks are strictly easier. It prevents replacing their known information content by a stronger one without an argument.

The same distinction appears for finitely generated abelian groups. Smith invariant factors of an integer matrix can be computed without factoring those integers. Splitting them into labelled prime-power elementary divisors adds the factorization problem. Likewise the two-term chain complex with boundary map multiplication by n has torsion group Z/nZ. Asking for all its p-primary components is different from asking for an invariant-factor presentation. General algorithmic treatment of modules also separates isomorphism and decomposition; see [6].

One should additionally state whether a finite algebra is given by an additive basis and structure constants, by a multiplication table, or by an arbitrary polynomial presentation. Computing a basis from the last kind of input can dominate the cost. A reduction proved for one encoding cannot be transferred merely because all three descriptions define rings.

## 4. A finite-field norm-factor mechanism

For a fixed integer d≥2 define

$$K_d(p)=1+p+\cdots+p^{d-1}=\frac{p^d-1}{p-1}.$$

**Lemma 1.** Suppose a positive integer M of polynomial bit length is supplied with n, and K_d(p) divides M for every prime p dividing n. Then n can be completely factored in randomized expected polynomial time. The same M may be reused on every divisor of n.

This is a formulation of the finite-field norm mechanism underlying the divisor-sum reductions in [2]. We include the proof to make the required integer interface explicit.

**Proof.** Handle prime powers and the factor two first. For a remaining composite, alternate the following two trials:

1. Run exponent-based splitting using nM.
2. Choose uniformly a monic degree-d polynomial f modulo n and a residue polynomial r of degree less than d. Compute h=r^M in (Z/nZ)[X]/(f), and take the gcd with n of every nonconstant coefficient of h.

Monicity permits reduction without inverting unknown nonunits. If every p−1 divides M, nM is a multiple of λ(n), and the first trial has the standard splitting guarantee.

Otherwise choose a prime q dividing n for which q−1 does not divide M, and choose a different prime p dividing n. These primes are analysis variables, not algorithm inputs. A random monic f is irreducible modulo p with probability at least 1/(2d). It is squarefree and reducible modulo q with probability at least 1/6. These standard finite-field counting bounds follow from the irreducible polynomial formula and the count of monic squarefree polynomials. For the latter bound, 1−1/q−1/d is sufficient except for q=d=2, where the direct probability is 1/4. The two events are independent by CRT.

Modulo p, the quotient is F_{p^d}. Because K_d(p) divides M, every r^M lies in the constant field F_p, including the zero input. Modulo q, the quotient is a product of at least two finite fields F_{q^{d_i}}. Since q−1 does not divide M, none of q^{d_i}−1 divides M. In each component the power map has at least two nonzero outputs. Under uniform input, every output atom has probability at most 1/2, including zero.

The first two component outputs are independent. The probability that they are the same element of the constant field F_q is at most 1/2. Therefore, with probability at least 1/2, h is not constant modulo q while it is constant modulo p. Some nonconstant coefficient is divisible by p but not q, yielding a proper gcd. The second type of trial consequently has success probability at least 1/(24d).

This reasoning uses reductions modulo p and q and permits repeated factors in n. Each trial has polynomial bit cost since d is fixed and log M is polynomially bounded. Recursion reuses M because its divisibility promises hold for every remaining prime. Primality tests terminate the recursion, and all returned splits are directly verified. □

The lemma does not require all p−1 to divide M. Its second branch exists precisely to handle that missing implication. A visible product formula containing norm factors can thus support factoring even when it is not a unit-group order.

## 5. Sublattices, coverings, and finite geometry

### 5.1 Two-dimensional sublattices and torus coverings

Hermite normal form counts the sublattices of index n in Z² as

$$\sum_{ab=n}a=\sigma(n).$$

For a fixed two-dimensional torus, connected n-sheeted coverings up to isomorphism commuting with the map to the base correspond to these sublattices. Its abelian fundamental group introduces no further subgroup-conjugacy quotient. Therefore this exact numerical count has the randomized factorization equivalence of σ. The equivalence relation is part of the statement: further quotienting by automorphisms of the base gives a different count.

### 5.2 Cyclic quotients and projective points

Surjections Z^d→Z/nZ correspond to primitive d-tuples modulo n, of which there are J_d(n). Two surjections have the same kernel exactly when they differ by a unit of Z/nZ. The unit action is free, so the number of index-n sublattices with cyclic quotient is

$$P_d(n)=\frac{J_d(n)}{\varphi(n)}
=\prod_{p^e\parallel n}p^{(d-1)(e-1)}K_d(p). \tag{1}$$

The same value counts primitive vectors modulo unit scaling, namely the points of projective (d−1)-space over Z/nZ, and cyclic subgroups of order exactly n in (Z/nZ)^d. Related finite abelian group counting formulas appear in Tóth [7].

For fixed d≥2, P_d(n) has O_d(log n) bits and is divisible by K_d(p) for every p dividing n. Lemma 1 proves that this single value is enough for randomized factoring of the same n. Factorization computes (1) deterministically. Hence P_d≡_R F. For d=2, P_2 is Dedekind's psi function n∏(1+1/p).

For a fixed closed orientable surface of genus g≥1, surjections of its fundamental group onto Z/nZ factor through its rank-2g abelianization. Counting surjections gives J_{2g}(n); forgetting the identification of the cyclic deck group, while preserving the base map, gives P_{2g}(n). Both counts support factoring, by the exponent mechanism and Lemma 1 respectively. This does not include quotienting by the mapping class group of the base surface.

### 5.3 Grassmannian point counts

Let G_{d,k}(n) count the free rank-k direct summands of (Z/nZ)^d, for fixed 0<k<d. Its local factor is

$$G_{d,k}(p^e)=p^{(e-1)k(d-k)}{d\brack k}_p. \tag{2}$$

The finite-field Gaussian binomial counts the initial subspace. At each further p-adic level a lift is specified by a k-by-(d−k) matrix, proving the power factor. CRT gives multiplication over primes and therefore the deterministic upper reduction to F.

To prove the reverse reduction, use

$${d\brack k}_X=\prod_{m=1}^d\Phi_m(X)^{c_m},\qquad
c_m=\left\lfloor\frac dm\right\rfloor-\left\lfloor\frac km\right\rfloor-\left\lfloor\frac{d-k}{m}\right\rfloor.$$ 

By symmetry assume k≤d/2. The Sylvester–Schur theorem, as treated by Erdős [8], ensures that one of d−k+1,…,d has a prime divisor ℓ>k. Exactly one integer in this interval is divisible by ℓ, and no denominator integer 1,…,k is. Thus c_ℓ=1. For every prime p dividing n, K_ℓ(p)=Φ_ℓ(p) divides G_{d,k}(n). The prime ℓ depends only on the fixed dimensions and can be precomputed. Lemma 1 now gives G_{d,k}≡_R F.

For example, the finite-field factor for Gr(2,4) is (p²+1)(p²+p+1), containing K_3(p). The degenerate cases k=0,d have count one and are excluded.

Constructing one point is easy: take the span of the first k coordinate vectors. Thus exact counting in this family can encode factorization even though finding a single point requires none. This comparison does not equate exact counting with listing all points.

## 6. Compact geometric invariants

Consider the connected compact complex modular curve X(n) associated with the principal congruence subgroup, using n≥7 to avoid exceptional small levels. For the projective modular group, its index I, number of cusps c, and genus g satisfy

$$I=\frac{nJ_2(n)}2,\qquad c=\frac{J_2(n)}2,\qquad
g=1+\frac{(n-6)J_2(n)}{24}. \tag{3}$$

These are the standard full-level formulas; see [9]. One can also derive the genus from g=1+I/12−c/2, since the relevant group is torsion-free. Any of the three displayed integers recovers J_2(n) by exact arithmetic. Since φ(n) divides J_2(n), each supplies a unit-group exponent multiple and therefore randomized factoring. The reverse direction is the product formula.

Holomorphic differential dimension h^{1,0}, first Betti number, Euler characteristic, and hyperbolic area normalized by π carry the same numerical information: they are g, 2g, 2−2g, and nJ_2(n)/6. For n=15 the values are J_2=192, I=1440, c=96, g=73, and normalized area 480.

The input here is the binary level n. If an exponentially large triangulation were supplied instead, computing an Euler characteristic from that triangulation would be a different complexity statement. Nor does (3) imply that genus computation for arbitrary algebraic curves is factorization-equivalent.

A similar warning applies to complex multiplication. An order class number, the degree of a class field, a list of class representatives, a class-group structure, and effective coordinates in that group are distinct outputs. Class number product formulas can be used in specialized reduction families, but the existence of those formulas does not identify all class-group computational tasks with factoring. Regulator problems additionally require an explicit precision and representation convention.

## 7. High-power queries and recovery of a main term

### 7.1 Exact divisor-sum values

For fixed s≥1, the identity

$$\frac{n^{s(j+1)}}{\sigma_s(n^j)}
=\frac{J_s(n)}{\prod_{p^e\parallel n}(1-p^{-s(ej+1)})} \tag{4}$$

provides an instructive oracle reduction. Set j=2L+b for a sufficiently large fixed b. With ε=Σ_{p|n}p^{−s(ej+1)}, the product is at least 1−ε, and

$$0<\frac{n^{s(j+1)}}{\sigma_s(n^j)}-J_s(n)
\le2n^sL2^{-s(j+1)}<\frac12.$$

Rounding therefore recovers J_s(n). The queried integer n^j and its divisor-sum answer have O_s(L²) bits. Exponent-based splitting completes a randomized reduction to σ_s. This illustrates an explicit cross-input oracle argument. The stronger single-value divisor-sum results of [2] should not be silently inferred merely from this argument.

### 7.2 Bounded-denominator main-term recovery

**Lemma 2.** Fix s≥2, a nonzero rational A, and positive constants C,δ with an effective error bound. Suppose a rational sequence a(m), with a fixed common denominator, satisfies

$$a(m)=A\sigma_s(m)+g(m),\qquad |g(m)|\le C m^{s-\delta}. \tag{5}$$

Then J_s(n) is deterministically polynomial-time Turing reducible to exact coefficient queries for a, and F≤_R a.

The bounded-denominator hypothesis makes the size of an exact rational answer follow from its magnitude. A bound on absolute value alone would not control the number of bits in an arbitrary rational denominator.

**Proof.** Set j=2L+b and m=n^j, choosing the constant b large enough in terms of s,A,C,δ. Let

$$Q=\frac{A n^{s(j+1)}}{a(n^j)},\qquad
Q_0=\frac{n^{s(j+1)}}{\sigma_s(n^j)}.$$

Equation (4) bounds Q_0−J_s(n) by 2n^sL2^{−s(j+1)}. Also σ_s(m)≥m^s. Enlarging b ensures |a(m)|≥|A|m^s/2, and hence

$$|Q-Q_0|\le\frac{2C}{|A|}n^s m^{-\delta}.$$

Both errors can be made less than 1/8 uniformly for n≥2, by increasing the fixed b. The nearest integer to Q is exactly J_s(n). Input, answer, and intermediate numerator and denominator lengths are polynomial in L, by the fixed denominator and growth assumptions. Handle n=1 separately. Finally, φ(n) divides J_s(n), so its exact value permits randomized factorization. □

The error may have either sign; nearest-integer rounding is the appropriate uniform operation. The query is at n^j, not at n alone. Neither detail is optional.

### 7.3 Fixed modular forms and theta coefficients

Let f be a fixed rational modular form of even weight k≥4 and level one, with nonzero constant term a_0. Write f=a_0E_k+h, with h cuspidal. Its positive coefficients have the form

$$a_f(m)=-\frac{2ka_0}{B_k}\sigma_{k-1}(m)+a_h(m).$$

For fixed h, the elementary cusp bound a_h(m)=O(m^{k/2}) follows by bounding y^{k/2}|h(x+iy)| and taking the Fourier integral at y=1/m. Rational forms at fixed weight have a fixed common denominator after choosing an integral basis. Thus Lemma 2 applies with s=k−1 and δ=k/2−1>0, proving F≤_R a_f.

In particular, the theta series of a fixed positive-definite even unimodular lattice has constant term one and weight half its rank, so its exact shell-count sequence meets these hypotheses. The coefficient-computation results in [10] give the complementary algorithmic context and require careful distinction between fixed and variable weight or rank. The elementary argument here establishes the lower reduction directly; it does not supply a new coefficient-computation algorithm.

For the Leech lattice,

$$r_{\Lambda_{24}}(2m)=\frac{65520}{691}\bigl(\sigma_{11}(m)-\tau_\Delta(m)\bigr).$$

If M=r_{Λ_24}(2n^j) with j=2L+2, then

$$J_{11}(n)=\operatorname{round}\!\left(\frac{65520\,n^{11(j+1)}}{691M}\right). \tag{6}$$

The bound |τ_Δ(m)|≤2m^6 makes the cusp contribution to the ratio smaller than 1/4; the truncated Euler-factor error is also smaller than 1/4. This does not require the nonvanishing of τ_Δ. A pure cusp form, whose constant term is zero, has no divisor-sum main term and is outside Lemma 2.

## 8. Pure cusp coefficients: a restricted exact reconstruction

This section isolates a different, explicitly limited combination from the working map. Bach and Charles [11] prove a factoring connection for coefficients of suitable eigenforms on a density-one set of RSA moduli. A general worst-case factoring equivalence for an arbitrary pure cusp sequence does not follow from that result or from Section 7.

Fix a normalized integral Hecke eigenform of even weight w≥2, fixed level, and trivial character. Put s=w−1. Suppose n is squarefree, coprime to the level, has no prime factors below five, and satisfies a(n)≠0. Multiplicativity gives a(p)≠0 for every p dividing n. Let α_p,β_p be the roots of

$$X^2-a(p)X+p^s.$$

The coefficient bound gives v_p(a(p))≤(s−1)/2, so α_p and β_p have distinct p-adic valuations. At every different prime dividing n they are units. The Hecke recurrence consequently expresses

$$u_j=a(n^j)=\sum_{\varepsilon}c_\varepsilon z_\varepsilon^j$$

as t=2^{ω(n)} terms with nonzero coefficients and distinct bases z_ε, each a product choosing one root for every p. Distinctness follows by examining the valuation at a prime where the choices differ.

For T≥t, the Hankel matrix (u_{i+j})_{0≤i,j<T} has rank t; its leading t-by-t block factors as a Vandermonde matrix times a nonsingular diagonal matrix times its transpose. Exact recurrence recovery therefore gives

$$P(X)=\prod_\varepsilon(X-z_\varepsilon)\in\mathbb Z[X].$$

The integer coefficients follow from Galois invariance and algebraic integrality. Form R(Y)=Res_X(P(X),P(YX)) and factor it over Q by exact polynomial factorization [12]. Ratios of two bases that differ only at p include α_p/β_p. If a(p)=p^v u with p not dividing u and d=s−2v>0, the primitive irreducible quadratic for that ratio is

$$p^dY^2-(u^2-2p^d)Y+p^d.$$

Its discriminant is negative, since u²<4p^d, and its coefficients are coprime. The gcd of its leading coefficient with squarefree n is exactly p. Considering all irreducible factors of the resultant therefore recovers every prime divisor.

The degrees are t and at most t², and the coefficient lengths are polynomial in t and L: |z_ε|=n^{s/2}, and all ratio roots have complex absolute value one. Exact Hankel linear algebra, resultants, and rational polynomial factorization have polynomial cost in those parameters. Unknown t can be handled by doubling T, accepting only a prime factorization whose product is n. One must not stop merely because some smaller leading Hankel minor is singular.

Thus this argument gives a deterministic reduction with cost polynomial in 2^{ω(n)} and L. Under the fixed promise ω(n)≤C log log n it is polynomial in L. It retains the nonvanishing and squarefree promises. If a(p)=0, the relevant root ratio is −1 and the denominator extraction disappears; the argument cannot be extended by ignoring that case. Generalizing to repeated primes requires a promise on a(rad(n)), since a(n)≠0 alone no longer excludes zero prime coefficients. No average-case distribution assertion is made here.

## 9. Changes of question that break apparent equivalences

Several recurrent distinctions explain missing arrows in a reduction map.

**A witness versus a decision.** A modular square-root witness permits random CRT splitting. Merely deciding quadratic residuosity does not provide that witness by the same argument. Adding a bound on the requested root gives yet another problem; bounded quadratic congruences have NP-completeness results [13].

**RSA private-key recovery versus arbitrary inversion.** A private exponent supplies the short exponent multiple ed−1. A procedure that inverts one ciphertext does not explicitly supply that integer. Restricted-model equivalence results must retain their model; see Boneh and Venkatesan [14].

**A count versus a quotient count.** Index-n sublattices of Z² are counted by σ(n). Their orbits under GL_2(Z) are counted by

$$O_2(n)=\prod_{p^e\parallel n}\bigl(\lfloor e/2\rfloor+1\bigr),$$

as Smith normal form shows. In particular O_2(n²)=τ(n). Cyclic-quotient sublattices form just one GL_d(Z) orbit. Changing the equivalence relation changes the computational information.

**An invariant versus effective coordinates.** An abstract group order, an abstract invariant-factor list, generators represented as ideals, and a coordinate map acting on those representatives are not interchangeable. A factor-extraction step that uses a representative cannot be justified from its abstract order alone.

**Fixed objects versus variable families.** Lemma 2 applies with fixed coefficient-growth constants and fixed modular-form weight. A uniform result whose weight, level, rank, or genus is an input needs its own complexity analysis and hypotheses. A finite list of constant-parameter algorithms is not automatically a uniform polynomial-time algorithm.

**Values versus explicit lists.** A list with n entries already has exponential size relative to log n. Even one numerical count can have too many bits: a value at least (n−1)! has Ω(n log n) bits. Exact expanded Pell solutions, full spectra, all coverings, or full class polynomials therefore need explicit output-size accounting. A compressed expression, a logarithmic approximation, and a residue modulo a supplied modulus are different outputs.

These distinctions prevent a shortcut from the displayed reductions to general reverse reductions from radical computation, divisor counts, quadratic-residuosity decision, or arbitrary RSA inversion to full factoring. This paper establishes neither those shortcuts nor a strict complexity separation.

## 10. Quadratic forms, ideal classes, and representation

Binary quadratic forms connect norm representations to ideal classes and modular square roots. These connections explain factor-extraction mechanisms, but do not by themselves supply polynomial-time algorithms for finding the required representations or classes.

### 10.1 The normalized norm dictionary

Let Q(x,y)=ax²+bxy+cy² be a primitive positive-definite integral form: gcd(a,b,c)=1, a>0, and D=b²−4ac<0. Write

$$K=\mathbb Q(\sqrt D),\qquad D=f^2d_K,\qquad
\mathcal O_D=\mathbb Z+f\mathcal O_K,\qquad
I_Q=a\mathbb Z+\frac{-b+\sqrt D}{2}\mathbb Z.$$

Here d_K is the fundamental discriminant and f is the order conductor. The ideal norm is N(I_Q)=[O_D:I_Q]=a. Primitivity gives

$$I_Q\overline{I_Q}=a\mathcal O_D:$$

after dividing the product by a, its generators contain a,c and two elements summing to −b. Thus I_Q is invertible. An ideal is proper when its multiplier ring is exactly O_D. For quadratic orders, proper ideals are precisely the invertible ideals; arbitrary ideals of nonmaximal orders need not satisfy this property. [15]

For the displayed sign convention, put α=ax+(b−√D)y/2∈I_Q. Direct calculation gives

$$N_{K/\mathbb Q}(\alpha)=aQ(x,y),\qquad
(2ax+by)^2-Dy^2=4aQ(x,y).$$

The form is therefore the field norm on an ideal lattice divided by its ideal norm, not the unscaled field norm. Proper equivalence under SL₂(Z) corresponds to ideal-class equivalence, and Gauss composition corresponds to ideal multiplication. Passing to GL₂(Z) additionally identifies inverse classes. [16]

If Q(x,y)=m>0, the integral invertible ideal J=(α)I_Q⁻¹ has norm m and class [I_Q]⁻¹. Conversely, such a J yields a representing α. Thus representation by a specified form requires the correct ideal class, not merely the existence of an ideal of the desired norm. Conjugating the ideal convention changes the inverse-class convention accordingly.

### 10.2 Splitting and representation are different conditions

For an odd prime p not dividing D, the condition (D/p)=1 says that p splits in K, equivalently that an invertible O_D-ideal of norm p exists. Some form of discriminant D represents p; a specified form Q requires one of the two conjugate prime-ideal classes to be [I_Q]⁻¹. The principal form requires principal prime ideals. [17]

For D=−23 the reduced forms are (1,1,6), (2,1,3), and (2,−1,3). The prime 3 splits and is represented by the last two, but not by the principal form, since

$$x^2+xy+6y^2=(x+y/2)^2+23y^2/4.$$

For y≠0 this exceeds 3, while y=0 gives a square.

For squarefree m coprime to D, suppose all its prime factors split and choose one prime ideal 𝔭_p above each p. A principal norm representation exists exactly when some choices of conjugates satisfy

$$\prod_{p\mid m}[\mathfrak p_p]^{\varepsilon_p}=1,
\qquad\varepsilon_p\in\{1,-1\}.$$

Classes can therefore cancel. Neither 3 nor 7 is x²+5y², but 21=1²+5·2² is the norm of 1+2√−5. A composite represented by the principal form need not have its individual prime factors represented by that form. For nonmaximal orders this ideal-factorization argument is restricted to ideals prime to the conductor.

### 10.3 Two representations as a splitting witness

Suppose odd m satisfies

$$m=x_1^2+dy_1^2=x_2^2+dy_2^2,
\qquad\gcd(dy_1y_2,m)=1.$$

Then r_i=x_i y_i⁻¹ modulo m are unit square roots of −d. If r_1≠±r_2, their local signs differ, and

$$\gcd(x_1y_2-x_2y_1,m),\qquad
\gcd(x_1y_2+x_2y_1,m)$$

give proper factors. Nonunit data must first be handled by gcd; a gcd equal to m is a degeneracy, not a successful split. Two visibly different representations can still yield only globally opposite roots.

For example, 65=8²+1²=7²+4² gives gcd(32−7,65)=5 and gcd(32+7,65)=13. In Z[i], the gcd of 8+i and 7+4i is associated to 2−i, of norm 5. The extraction is elementary once suitable representations are supplied; their efficient production is a separate problem. Cornacchia's use of a supplied prime-modulus square root does not remove the composite-modulus root problem.

### 10.4 Ambiguous forms and the genus quotient

A canonical reduced positive-definite form, with |b|≤a≤c and b≥0 on the boundary, represents a class of order dividing two precisely when b=0, b=a, or a=c. These boundaries expose factorizations: [16]

$$-D=4ac\quad(b=0),\qquad
-D=a(4c-a)\quad(b=a),\qquad
-D=(2a-b)(2a+b)\quad(a=c).$$

For primitive forms, common factors in the last two products are supported at 2. Nevertheless, the displayed factorization may separate only 1, a known power of two, or an auxiliary multiplier. A nonidentity two-torsion class need not yield a useful divisor of the original target.

For D=−299, Q=(3,1,25) is equivalent to (3,13,39), whose Dirichlet square is (9,13,13). Reduction gives

$$[Q]^2=[(9,5,9)],\qquad299=(18-5)(18+5)=13\cdot23.$$

The reduced square lies on the a=c boundary; Q itself has order four. Finding such a useful square remains part of the algorithm.

For a negative fundamental discriminant with t distinct prime divisors, genus theory gives

$$|C/C^2|=|C[2]|=2^{t-1},\qquad
\text{principal genus}=C^2,\quad C=\operatorname{Cl}(\mathcal O_K).$$

Ramified prime-ideal classes generate C[2], while genus characters detect the quotient C/C². Equal sizes do not identify their information. In C≅Z/4Z the nontrivial two-torsion class is itself a square and is invisible to every genus character. Concretely, for D=−39,

$$[(2,1,5)]^2=[(3,3,4)].$$

For D=−23, C≅Z/3Z and C²=C: every class lies in the principal genus, although only one is principal. For positive discriminants, proper indefinite forms require the narrow class group and positivity conventions; ordinary classes cannot be substituted without accounting for units of negative norm. Nonfundamental discriminants require conductor and dyadic genus corrections. [16]

### 10.5 Conductors carry square-part information

For a fixed imaginary quadratic field with class number h_K, set O_f=Z+fO_K. Its order class-number formula is

$$h(\mathcal O_f)=\frac{h_Kf}{[\mathcal O_K^\times:\mathcal O_f^\times]}
\prod_{p\mid f}\left(1-\frac{(d_K/p)}p\right).$$

The character uses d_K, not f²d_K. Its factors p−(d_K/p) connect the formula to local norm-one groups. [18]

If m=pq with distinct p,q≡1 modulo 4, the conductor-m order in Q(i) has 2h(−4m²)=φ(m), so p+q=m+1−2h(−4m²). For m=65, h(−16900)=24 gives p+q=18 and the factors 5,13. This is a deterministic extraction under the stated semiprime promise. The order Z[√−65], of discriminant −260, is different.

More generally, write N=A²B with B positive and squarefree. The field is Q(√−B), while Z[√−N] has discriminant −4N and conductor

$$f=\begin{cases}2A,&B\equiv3\pmod4,\\A,&B\not\equiv3\pmod4.\end{cases}$$

Recovering the conductor reveals the square part A, not necessarily the prime factors of B. Computing D=f²d_K is itself squarefree decomposition data; introducing this notation does not make that computation free.

### 10.6 Ring class fields, CM, and point counts

Let n≥1, O=Z[√−n], D=−4n, and let L be its ring class field. For a prime p not dividing 2n,

$$p=x^2+ny^2\quad\Longleftrightarrow\quad
p\text{ splits completely in }L/\mathbb Q.$$

A norm-p element gives a principal prime ideal, whose Artin symbol is trivial; the converse recovers that principal ideal. A nonmaximal O requires its ring class field, not automatically the Hilbert class field of K. [17], Theorem 21.5 and Corollary 21.10.

For the j-class polynomial H_D, the condition is also equivalent to

$$\left(\frac Dp\right)=1
\quad\text{and}\quad H_D\bmod p\text{ has a root in }\mathbb F_p.$$

In this unramified ordinary CM situation, one root forces complete linear splitting. Without the symbol condition, a root is insufficient: H_{−4}=X−1728 has a root modulo 3, although 3 is inert in Q(i) and is not a sum of two squares. An arbitrary class-field defining polynomial additionally requires attention to index or discriminant exceptions when applying Dedekind's criterion. [17], Remark 21.12.

If E/F_p is ordinary with endomorphism order O⊂K, its Frobenius satisfies

$$N(\pi)=p,\qquad
\#E(\mathbb F_p)=p+1-\operatorname{Tr}(\pi)=N(1-\pi).$$

Supersingular reduction cannot be assigned the same prescribed quadratic endomorphism field without further justification. Computing a full H_D may also require superpolynomial output length in log|D|.

ECM exploits differing local point orders and nonunits to obtain factors; it does not require constructing a CM class polynomial first. ECPP instead produces primality certificates, often using CM to construct suitable curves. Their common elliptic-curve language does not identify their outputs or the complexity of certificate construction with verification. [19] [20]

### 10.7 Special CM norms are not arbitrary factoring algorithms

Gross–Zagier give explicit prime-power factorization formulas for normalized conjugate products of differences of singular moduli, initially for relatively prime negative fundamental discriminants d_1,d_2. The formula involves positive integers

$$\frac{d_1d_2-x^2}{4},\qquad x^2\equiv d_1d_2\pmod4,$$

and divisor products controlled by quadratic characters. Their Theorem 1.3 and Corollary 1.6 constrain the prime factors and their splitting behavior. [21]

These are special algebraic norms with additional structure. The theorem does not express every input integer as such a norm in polynomial time, eliminate the cost of enumerating CM classes or auxiliary x, or handle arbitrary discriminants without further hypotheses. Norm identities, witness extraction, and complete factoring algorithms remain distinct levels of assertion.

## 11. Class-group relations, infrastructure, and square-form algorithms

Two witnesses recur in quadratic factoring methods: a useful class of order dividing two, represented by a form, and a nontrivial congruence of squares modulo N. Efficient extraction from a supplied witness does not establish efficient production of that witness. Throughout, a factor of an auxiliary discriminant must be intersected with N and checked to be proper.

### 11.1 Exponents and partial relations

Let C_D be the proper class group of primitive positive-definite forms of negative discriminant D, with N dividing D. One can construct prime forms without factoring D. For a known odd prime ℓ not dividing D with (D/ℓ)=1, choose b of the required parity with b²≡D modulo 4ℓ. Then

$$q_\ell=\left(\ell,b,\frac{b^2-D}{4\ell}\right)$$

is primitive. This uses square-root extraction modulo the known prime ℓ. Constructing several such forms neither proves that they generate C_D nor provides uniform sampling from it.

Suppose ord(g)=2^s m, with m odd. An odd exponent M satisfying m|M makes g^M have order exactly 2^s. If s>0, repeated squaring until the first identity produces a nonidentity predecessor z with z²=1. A suitable ambiguous representative can expose a factor. The divisibility condition includes prime powers: M=3 does not annihilate an odd part m=9. Exponentiation costs depend on log M, so a large smoothness bound is not free. This is the basic exponent mechanism in the Schnorr–Lenstra random-class-group method, which also varies discriminant multipliers and uses additional stages [22].

Relations provide another route. For explicitly represented classes g_1,…,g_t, define

$$\pi:\mathbb Z^t\longrightarrow\langle g_1,\ldots,g_t\rangle,
\qquad v\longmapsto\prod_jg_j^{v_j},\qquad\Lambda=\ker\pi.$$

A complete relation lattice describes this generated subgroup; identifying it with C_D additionally requires generation of the whole group. A partial relation list need not suffice for either assertion.

Nevertheless, verified relations r_i∈Λ and a dependence Σ_i c_i r_i=2v immediately give

$$z=\prod_jg_j^{v_j},\qquad z^2=\pi(2v)=1.$$

Only the selected relations are needed. No complete class number, relation lattice, or invariant-factor decomposition is required. The result may be the identity or yield only an already known multiplier factor; its usefulness and success probability remain separate questions. Lenstra–Pomerance explicitly use this relation-halving construction in Algorithm 10.1, Steps 5–6 [23].

### 11.2 Continued fractions and Pell witnesses

For convergents A_j/B_j to √N, the signed norms

$$q_j=A_j^2-NB_j^2\equiv A_j^2\pmod N,
\qquad |q_j|<2\sqrt N$$

provide small auxiliary integers. Their signs must be distinguished from the positive complete-quotient denominators in other continued-fraction conventions. CFRAC retains smooth q_j and includes −1 as a sign coordinate in its parity matrix. A dependency then gives a positive square Πq_j=Y² and X=ΠA_j modulo N, hence X²≡Y² modulo N. The residues A_j modulo N can be maintained without storing enormous convergents [19].

In the unit case, X≢±Y modulo N ensures that gcd(X−Y,N) gives a proper factor. Small norms alone do not prove either a sufficient supply of smooth values or a sufficient proportion of nontrivial dependencies.

A Pell solution is not automatically useful. The equation 4²−15·1²=1 yields gcd(4−1,15)=3 and gcd(4+1,15)=5. In contrast, the least positive solution 129²−65·16²=1 has 129≡−1 modulo 65, giving gcds 1 and 65. Its powers still have first coordinate ±1 modulo 65. Thus solving the original Pell equation and applying this gcd test once is not a universally successful factoring reduction.

### 11.3 Infrastructure and square forms

For positive discriminants, reduced representatives within a proper equivalence class form a cycle. These positions are additional information inside a class, not different class-group elements. For equivalent invertible fractional ideals 𝔞=γ𝔟, a distance convention is

$$\delta(\mathfrak a,\mathfrak b)
=\frac12\log\left|\frac{\gamma}{\bar\gamma}\right|.$$

Changing γ by a unit changes the distance by a period. Ordinary ideal classes allow arbitrary principal generators; narrow classes require totally positive generators. If ε>1 generates the free unit group and R=log ε, the positive-norm period is R⁺=R when N(ε)=1 and R⁺=2R when N(ε)=−1. Nonmaximal orders require their own unit groups. Reduction introduces principal factors and distance corrections, so reduced representatives cannot simply be treated as a group with an exactly additive real coordinate [24] [25].

Fix proper equivalence and the corresponding narrow convention. If F=(a²,b,c) is primitive and principal, with a>0 and gcd(a,b)=1, then

$$G=(a,b,ac),\qquad \operatorname{disc}(G)=\operatorname{disc}(F),
\qquad [G]^2=[F]=1.$$

This special composition formula requires its coprimality condition. A square coefficient alone is insufficient. Although F is principal, G need not be: a square root of the identity can be a nontrivial two-torsion class.

SQUFOF finds square forms, takes a suitable root or inverse root, reduces it, and follows its cycle to a symmetry point giving an ambiguous form. Signed implementations require their own formulas; for example, the convention F=(−Q,2P,S²) uses inverse root (−S,2P,SQ) under its parity and coprimality conditions. For discriminant 4N, the principal form (1,2q,q²−N), q=⌊√N⌋, also fixes the otherwise easily reversed sign [24].

The queue stores selected earlier small coefficients and congruence information to reject square forms leading to trivial ambiguous factors. It is neither the full cycle nor a table of numerical logarithmic distances. Its deletion rules have a specific proof. Infrastructure explains the halving of appropriate distances, but this does not imply exactly half as many reduction steps: step lengths vary. Short average queues are likewise not uniform constant-space guarantees; see [24], §§2.4, 3.2–3.5.

### 11.4 Constructing a square form by sieving

Bradford–Wagstaff's SQUFOF2 replaces waiting for a square coefficient by sieving values of a principal form F_0(x,y). A parity dependency, including signs, makes their product square. Composition identities express that product as another value of F_0. Removing a common factor of x,y removes only a square from this value. Once gcd(x,y)=1 and F_0(x,y)=w², a Bézout identity completes (x,y) to an SL_2(Z) matrix, producing an equivalent form with square leading coefficient. The coprimality and parity checks for the chosen square-root formula are still required; failures need a gcd check or the general composition rules. The algorithm then uses inverse square roots, reduction, and a symmetry point; see [25], §§2, 6. Section 12 treats the distinct bookkeeping required by QS and MPQS.

### 11.5 What the runtime statements establish

Write

$$L_N[\alpha,c]=\exp\bigl((c+o(1))(\log N)^\alpha
(\log\log N)^{1-\alpha}\bigr).$$

| Method | Bound or scale | Status |
|---|---|---|
| Classical CFRAC with trial-division smoothness testing | L_N[1/2,√2] | Heuristic auxiliary-value and nontrivial-dependency model [19] |
| Basic SQUFOF | About N^{1/4} reduction steps on average, with polynomial logarithmic bit cost per step | Squarefree input and distribution assumptions in [24], §4; queue estimates are also model-dependent |
| SQUFOF2, elimination exponent 2<r≤3 | Time L_N[1/2,r/(2√(r−1))]; space L_N[1/2,1/√(r−1)] | Squarefree input and Hypotheses 1–4 of [25], Theorem 4 |
| Original Schnorr–Lenstra smooth-class-number analysis | The proposed uniform L_N[1/2,1] justification cannot be retained | Its smoothness premise fails on input families identified in [23], §11 |
| Lenstra–Pomerance class-group relations algorithm | Unconditional expected L_N[1/2,1]; splitting-stage space at most L_N[1/2,1/2] | Every input; [23], Theorems 10.3, 10.5 and p.509 |

SQUFOF2's four hypotheses concern split-prime supply, smooth values, return distances, and distribution among ambiguous forms. Its often quoted constant 1.02 corresponds to a selected elimination exponent, not an unconditional theorem.

Lenstra–Pomerance remove GRH from the analysis of a **class-group relations** algorithm. Their splitting subroutine has success probability at least 1/64 for sufficiently large odd composites that are not prime powers; repetition and recursion give complete factorization. Section 12 of their paper defines expectation over random bits for each fixed input, not over randomly chosen integers. This rigorous result neither proves polynomial time nor repairs the distinct Schnorr–Lenstra smooth-class-number heuristic.

### 11.6 Nonmaximal orders and large square factors

Write N=A²B with B squarefree. The order of discriminant −4N has conductor A or 2A, according as B is not, or is, 3 modulo 4. Mulder exploits the map

$$C(-4A^2B)\longrightarrow C(-4B).$$

A candidate need only map to the identity rather than become the identity upstairs. Suitable **nontrivial** kernel elements, after lifting and reduction, reveal square factors; composite A may require recovering a partial factor and completing it by further steps. The displayed map describes the mathematical relation: the algorithm detects its consequences indirectly and does not first compute the unknown A to evaluate an oracle for it [26] [27].

The local class-number factors also restrict smoothness heuristics. At a conductor prime p unramified in the underlying quadratic field, coprime multipliers change the relevant factor between p−1 and p+1. If p already ramifies, or the multiplier introduces p, a p-factor can occur instead. Multiplier trials therefore cannot universally be treated as independent random class numbers.

Under the stated heuristic smoothness and multiplier assumptions, Mulder obtains the B-dependent expected bound

$$\widetilde O\!\left(L_B[1/2,1]\log N+
L_B[1/2,1/2](\log N)^2\right).$$

The ANTS manuscript treats N=p²B in Theorem 4.3 and composite square parts in Proposition 4.6. Squarefree decomposition of p²q exposes p and q, but on squarefree N the output A=1,B=N supplies no prime factors. It therefore establishes no general reverse reduction from radical computation to full factoring.

## 12. Sieves, norm-one groups, and the square-root obstruction

Quadratic norms connect several factoring methods without making their computational interfaces identical. Sieves combine relations into squares; the p−1 and p+1 methods annihilate elements in local groups; the number field sieve must additionally turn ideal information into an element square that can be mapped modulo the integer being factored. These mechanisms explain extraction from suitable data. They do not, by themselves, give polynomial-time algorithms for finding those data.

### 12.1 Quadratic-sieve relations and the leading coefficient

For a nonsquare odd composite N, the quadratic-sieve polynomial is

$$Q(t)=t^2-N
=N_{\mathbb Q(\sqrt N)/\mathbb Q}(t+\sqrt N).$$

Values near √N are relatively small, which motivates searching for smooth values. Given their complete signed factorizations, linear algebra on prime-exponent vectors modulo two finds subsets with square product. A sign coordinate is necessary when negative values are allowed. If

$$\prod_{i\in S}Q(t_i)=Y^2,\qquad
X=\prod_{i\in S}t_i\pmod N,$$

then X²≡Y² modulo N. For unit X,Y with X≢±Y, gcd(X−Y,N) gives a proper divisor. Nonunits can be checked first; a trivial collision requires another dependency. Collecting enough relations and obtaining useful collisions remain separate parts of the algorithm [19].

For N=1649,

$$Q(41)=32=2^5,\qquad Q(43)=200=2^3\cdot5^2,\qquad
Q(41)Q(43)=80^2.$$

Since 41·43≡114 modulo 1649, the two gcds are

$$\gcd(114-80,1649)=17,\qquad
\gcd(114+80,1649)=97.$$

For an odd prime ℓ not dividing N, divisibility ℓ|Q(t) requires N to be a quadratic residue modulo ℓ. These known small primes form the usual factor base, with two handled separately.

Multiple-polynomial variants use a positive multiplier k and coefficients satisfying

$$B^2-AC=kN,\qquad Q(x,y)=Ax^2+2Bxy+Cy^2.$$

The discriminant is 4kN, and the exact identity is

$$(Ax+By)^2-kNy^2=AQ(x,y).$$

Thus the factorization of A must enter the parity bookkeeping unless its square contribution has already been absorbed. Across different polynomials, a square product of the Q-values alone is insufficient: the relevant product is ∏A_iQ_i. For example, A=5, B=2, C=−329 and (x,y)=(9,1) give Q=112 but (45+2)²−1649=560=5Q.

Constructing B requires a square root of kN modulo the deliberately chosen, already factored A. It does not require a square root modulo the unknown composite N. Shared factors with A or k are checked by gcd first. The identity and this distinction explain the quadratic-form connection; they do not make the supply of smooth relations automatic [19].

### 12.2 The two local forms of a norm-one group

For an odd prime p not dividing d, consider

$$\mathcal A_p=\mathbb F_p[T]/(T^2-d),\qquad
G_{p,d}=\{u\in\mathcal A_p^\times:u\bar u=1\}.$$

If d is a square modulo p, the algebra splits as F_p×F_p and the kernel consists of (z,z⁻¹). Otherwise it is F_{p²}, whose norm kernel is cyclic of order p+1. Consequently

$$|G_{p,d}|=p-\left(\frac d p\right).$$

In coordinates this is the conic x²−dy²=1 with multiplication

$$(x,y)(u,v)=(xu+dyv,\;xv+yu).$$

Pollard's p−1 method works directly in F_p^×. Williams's p+1 method exploits the nonsplit case of this quadratic construction [28]. Computation modulo N operates on all unknown prime components simultaneously.

Assume N is odd, choose P with gcd(P²−4,N)=1, and let γ satisfy γ²−Pγ+1=0. Its conjugate is γ⁻¹. The traces

$$V_m=\gamma^m+\gamma^{-m},\qquad
V_0=2,\quad V_1=P,\quad V_{m+1}=PV_m-V_{m-1}$$

can be evaluated by doubling identities in O(log M) modular operations. If p−((P²−4)/p) divides M, then γ^M=1 modulo p, so p divides gcd(V_M−2,N). The gcd is useful when annihilation differs across prime components; it may equal N if all components vanish.

The exponent must contain sufficient prime powers. Knowing only that every prime divisor of p+1 is at most B does not imply p+1 divides lcm(1,…,B). Choosing M, paying for its bit length, and obtaining local separation are therefore substantive algorithmic requirements. This differs from Section 2, where a suitable short exponent multiple is supplied.

### 12.3 The NFS homomorphism and its domain

In the simplest setup, choose monic irreducible f∈Z[X], a root α defining K=Q(α), and an integer m with f(m)≡0 modulo N. There is then a ring homomorphism

$$\varphi:\mathbb Z[\alpha]\longrightarrow\mathbb Z/N\mathbb Z,
\qquad \alpha\longmapsto m.$$

For a relation set S put

$$\Theta=\prod_{(a,b)\in S}(a-b\alpha),\qquad
U=\prod_{(a,b)\in S}(a-bm).$$

If U=Y² and Θ=β², a congruence φ(β)²≡Y² follows only when β lies in the domain of φ, or in a localization whose denominators map to units. The two square roots can then be compared by gcd [29].

Monicity ensures that α is integral and Z[α] is an order. For a nonmonic polynomial of degree d and leading coefficient c, one can use θ=cα with monic polynomial c^{d−1}f(X/c), and work in Z[θ,1/c] when gcd(c,N)=1, mapping θ to cm. Coefficient and norm corrections involving c must be retained. A proper gcd exposes a factor; gcd(c,N)=N instead requires different parameters or separate treatment [30].

### 12.4 The successive square obstructions

For monic f,

$$N_{K/\mathbb Q}(a-b\alpha)=b^d f(a/b).$$

Smoothness of this integer helps find relations, but the norm merges distinct prime ideals above the same rational prime. The following failures must be distinguished.

1. **Square norm need not mean square ideal.** In Z[i], the element 5 has norm 25, but (5) is the product of the two distinct prime ideals generated by 2+i and 2−i, each with odd exponent.
2. **Square ideal need not mean square element.** In Q(√−5), the ideal 𝔭=(2,1+√−5) satisfies 𝔭²=(2), but is nonprincipal: a generator would have norm x²+5y²=2, which is impossible.
3. **A principal half-ideal leaves a unit obstruction.** In the same field, (−1) is the square of the unit ideal, but −1 is not a square element.
4. **A field square root need not lie in the chosen order.** For α=4i, the element 3+α=(2+i)² lies in Z[α], whereas its square roots do not.

These are separate obstacles, including when complete ideal exponents are known [29], Sections 6–8.

### 12.5 The class-group and unit obstruction

Work in the maximal order O_K, where nonzero fractional ideals have unique prime-ideal factorization. Define

$$V(K)=
\{a\in K^\times:v_{\mathfrak p}(a)\in2\mathbb Z
\text{ for every finite prime }\mathfrak p\}/K^{\times2}.$$

There is a natural exact sequence

$$1\longrightarrow O_K^\times/(O_K^\times)^2
\longrightarrow V(K)
\overset{\rho}{\longrightarrow}\operatorname{Cl}(K)[2]
\longrightarrow1.$$

Here is the full argument. For a representative a, unique ideal factorization gives a unique fractional ideal 𝔞 with (a)=𝔞²; set ρ([a])=[𝔞]. Replacing a by ac² multiplies 𝔞 by the principal ideal (c), so the map is well defined, with image in the two-torsion. If a unit u=c² in K, all valuations of c vanish, making c a unit; hence the left map is injective. The kernel of ρ consists exactly of a with 𝔞=(c), equivalently a/c² a unit. Finally, every two-torsion ideal class has a fractional representative 𝔞 whose square is principal, say 𝔞²=(a), and this a maps onto it. This proves surjectivity as well as exactness.

The sequence describes an obstruction space, not an algorithm supplying its basis or preimages. NFS relations surviving all maximal-order valuation parity tests give a subspace of V(K), not necessarily the whole space. For nonmaximal orders, primes dividing the conductor or index require additional treatment; merged exponents there need not detect every maximal-order valuation. Localization likewise changes the relevant units and ideal class group [29].

### 12.6 Characters, verification, and the final collision

At suitable odd prime ideals 𝔮 avoiding the relations' numerators and denominators, quadratic residue characters kill actual squares. For a good degree-one prime 𝔮=(ℓ,α−r), one computes

$$\chi_{\mathfrak q}(a-b\alpha)
=\left(\frac{a-br}{\ell}\right).$$

Appending such characters as parity columns can reject nonsquares missed by ideal exponents. Passing an arbitrary finite collection is only necessary, not a certificate: sufficiency requires proving that these characters separate the relevant square-class quotient. Sampling and separation need their own analysis [29], Section 9.

One must compute and verify a square root. Couveignes' CRT method has an odd-degree condition; Montgomery's method uses ideal factorizations and lattice reduction; Thomé discusses lifting and further CRT approaches [31], [32], [30]. Their input includes the relation collection, whose size cannot be discarded in a complexity claim.

To address the order issue, monicity gives f′(α)O_K⊆Z[α]. Thus, when Θ=β² in O_K, compute and verify an integer polynomial T satisfying

$$T(\alpha)^2=f'(\alpha)^2\Theta.$$

The final modular comparison uses X=T(m) and Y′=f′(m)Y: the correction multiplies both sides. Check gcd(f′(m),N) first. A proper value gives a factor, value one preserves unit collisions, and value N is a degenerate case, not a successful split.

These procedures need not compute the full class group or a complete unit system. Conversely, their structural explanation does not establish a new equivalence between factoring and an unspecified class-group or norm oracle. Relation collection, character separation, actual square-root computation, and a nontrivial final collision remain distinct obligations.

## 13. Integrated map and validation

The two maps answer different questions. Figure 1 records oracle reductions whose running time and representation assumptions are specified in Sections 1–8 and 10.5. Figure 2 records the mathematical data transformed by quadratic and sieve algorithms. In the latter, obtaining enough relations, producing useful two-torsion, controlling square classes, and finding a nontrivial collision retain their separate costs.

![Quadratic and sieve mechanisms: relations can produce either explicit two-torsion for ambiguous-form extraction or square congruences after the required ideal, unit, and evaluation checks.](figures/quadratic-mechanisms.png)

*Figure 2. Mechanism arrows describe transformations of suitable data, not polynomial-time oracle reductions. In the class-group branch, a useful two-torsion representative exposes a discriminant factor. In the NFS branch, class-group two-torsion and units are obstructions to an actual element square. All final gcds must be checked to lie strictly between one and the target integer.*

| Information supplied | What it permits | What it does not automatically supply |
|---|---|---|
| Explicit CRT component or suitable exponent multiple | Polynomial-time factor extraction with the stated randomness | Such data from an arbitrary weak invariant |
| Exact finite-geometric count containing norm factors | The randomized reduction of Lemma 1 | A claim about every geometric counting problem |
| High-power coefficient queries with an effective main term | Recovery by Lemma 2 | The same conclusion for a pure cusp coefficient |
| Useful explicit two-torsion class or square-root collision | Checked gcd extraction | A polynomial-time method for finding the witness |
| A complete set of even prime-ideal valuations | A class in the obstruction space V(K) | An element square or a root in the evaluation order |
| Conductor or squarefree decomposition | The square part of the integer | A prime factorization of its squarefree part |

The source working survey's original literature cutoff was September 16, 2026. This revision incorporates a source audit through September 25, 2026 for the added quadratic and sieve material. Published theorems, proved combinations, conditional statements, and heuristic analyses remain distinct. The norm-factor and rounding arguments are mathematical proofs; finite examples check formulas and arithmetic but cannot certify their asymptotic claims.

Arithmetic checks include J_2(15)=192 and the modular-curve values in Section 6; P_2(15)=24 and P_3(15)=403; Gr(2,4)(15)=104780; and 3,996 instances of the rounding identity (4), for 2≤n≤1000 and 1≤s≤4. The revision also checks the two representations of 65, the form calculations for discriminants −299 and −39, h(−16900)=24, the Pell examples, and the QS/MPQS examples at 1649. The Leech and pure-cusp arguments rely on their stated identities and bounds, not on extrapolation from these checks.

For reuse, a proposed arrow should identify the allowed oracle input, precise output representation, whether the original integer can be changed, randomness and hypotheses, and intermediate and output lengths. No priority is claimed for elementary consequences that may already be known in specialized literature. This manuscript and its two figures provide a self-contained selected map; they do not assert an exhaustive classification of factorization-related tasks.

## AI assistance and license

OpenAI GPT-6 through the Codex client assisted with the English synthesis, source checking, independent agent checks of interfaces and assumptions, local arithmetic and rendering validation, diagrams, and submission. The exact model build is unknown, and complete model provenance for earlier working sessions is unavailable. Agent checks are not independent human peer review or formal verification; the manuscript has undergone neither.

Copyright 2026 Kaiyi Zhang. Licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References


1. Gary L. Miller. *Riemann's Hypothesis and Tests for Primality*. Journal of Computer and System Sciences 13(3), 300–317, 1976. [Author-hosted paper](https://www.cs.cmu.edu/~glmiller/Publications/Papers/Mi76.pdf).
2. Eric Bach, Gary L. Miller, and Jeffrey Shallit. *Sums of Divisors, Perfect Numbers and Factoring*. SIAM Journal on Computing 15(4), 1143–1154, 1986. [Author-hosted paper](https://www.cs.cmu.edu/~glmiller/Publications/Papers/BMS86.pdf).
3. François Morain, Guénaël Renault, and Benjamin Smith. *Deterministic factoring with oracles*. [Author preprint, version 2](https://arxiv.org/abs/1802.08444v2).
4. Alfred J. Menezes, Paul C. van Oorschot, and Scott A. Vanstone. *Handbook of Applied Cryptography*, Chapter 3. 1996. [Author-hosted chapter](https://cacr.uwaterloo.ca/hac/about/chap3.pdf).
5. Emil Jeřábek. *Integer factoring and modular square roots*. [Author preprint](https://arxiv.org/abs/1207.5220).
6. Iuliana Ciocănea-Teodorescu. *The Module Isomorphism Problem for Finite Rings and Related Results*. 2015. [Author preprint](https://arxiv.org/abs/1512.08365). Cited for the distinction between module isomorphism, generator construction, and decomposition tasks; no stronger encoding-independent assertion is used.
7. László Tóth. *On the Number of Cyclic Subgroups of a Finite Abelian Group*. Bulletin Mathématique de la Société des Sciences Mathématiques de Roumanie 55(103), 423–428, 2012. [Author preprint](https://arxiv.org/abs/1203.6201).
8. Paul Erdős. *A Theorem of Sylvester and Schur*. Journal of the London Mathematical Society 9, 282–288, 1934. [Author archive](https://www.renyi.hu/~p_erdos/1934-01.pdf).
9. Francesc Bars, Aristides Kontogeorgis, and Xavier Xarles. *Bielliptic and Hyperelliptic modular curves X(N) and the group Aut(X(N))*. [Author preprint, version 2](https://arxiv.org/abs/1207.2273v2). Section 2 and its genus formula supply the standard quantities in (3).
10. Bas Edixhoven and Jean-Marc Couveignes, editors, with Robin de Jong, Franz Merkl, and Johan Bosman. *Computational Aspects of Modular Forms and Galois Representations*. Annals of Mathematics Studies 176, 2011. [Book preprint](https://arxiv.org/abs/math/0605244).
11. Eric Bach and Denis Charles. *The hardness of computing an eigenform*. Contemporary Mathematics 463, 9–16, 2008. [Author preprint](https://arxiv.org/abs/0708.1192).
12. Arjen K. Lenstra, Hendrik W. Lenstra, Jr., and László Lovász. *Factoring Polynomials with Rational Coefficients*. Mathematische Annalen 261, 515–534, 1982. [Paper](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Lovasz/LovaszLenstraLenstrafactor.pdf).
13. Kenneth L. Manders and Leonard Adleman. *NP-complete decision problems for binary quadratics*. Journal of Computer and System Sciences 16(2), 168–184, 1978. [DOI](https://doi.org/10.1016/0022-0000(78)90044-2).
14. Dan Boneh and Ramarathnam Venkatesan. *Breaking RSA may not be equivalent to factoring*. EUROCRYPT 1998. [Author's publication page](https://crypto.stanford.edu/~dabo/pubs/abstracts/no_rsa_red.html).
15. Andrew V. Sutherland. The CM Torsor. MIT 18.783, Lecture 17, 2022. [Source](https://math.mit.edu/classes/18.783/2022/LectureNotes17.pdf).
16. Wieb Bosma and Peter Stevenhagen. On the Computation of Quadratic 2-Class Groups. Journal de théorie des nombres de Bordeaux 8(2), 283–313, 1996. [Source](https://www.numdam.org/item/JTNB_1996__8_2_283_0.pdf).
17. Andrew V. Sutherland. Ring Class Fields and the CM Method. MIT 18.783, Lecture 21, 2022. [Source](https://math.mit.edu/classes/18.783/2022/LectureNotes21.pdf).
18. Harris B. Daniels and Álvaro Lozano-Robledo. On the Number of Isomorphism Classes of CM Elliptic Curves Defined over a Number Field. Journal of Number Theory 157, 2015. [Source](https://hdaniels.people.amherst.edu/CMj.pdf).
19. Carl Pomerance. A Tale of Two Sieves. Notices of the AMS 43(12), 1473–1485, 1996. [Source](https://math.dartmouth.edu/~carlp/PDF/paper109.pdf).
20. Andrew V. Sutherland. Primality Proving. MIT 18.783, Lecture 11, 2023. [Source](https://math.mit.edu/classes/18.783/2023/LectureNotes11.pdf).
21. Benedict H. Gross and Don B. Zagier. On Singular Moduli. Journal für die reine und angewandte Mathematik 355, 191–220, 1985. [Source](https://people.mpim-bonn.mpg.de/zagier/files/doi/10.1515/crll.1985.355.191/fulltext.pdf).
22. Claus P. Schnorr and Hendrik W. Lenstra, Jr. A Monte Carlo Factoring Algorithm With Linear Storage. Mathematics of Computation 43(167), 289–311, 1984. [Source](https://pub.math.leidenuniv.nl/~lenstrahw/PUBLICATIONS/1984c/artc.pdf).
23. Hendrik W. Lenstra, Jr., and Carl Pomerance. A Rigorous Time Bound for Factoring Integers. Journal of the American Mathematical Society 5(3), 483–516, 1992. [Source](https://math.dartmouth.edu/~carlp/PDF/paper85.pdf).
24. Jason E. Gower and Samuel S. Wagstaff, Jr. Square Form Factorization. Mathematics of Computation 77, 551–588, 2008. [Source](https://homes.cerias.purdue.edu/~ssw/squfof.pdf).
25. Clinton Bradford and Samuel S. Wagstaff, Jr. Square form factorization, II. Bulletin of the Polish Academy of Sciences. Mathematics 70(1), 13–34, 2022. DOI:10.4064/ba211003-1-11. [Source](https://homes.cerias.purdue.edu/~ssw/squfof2.pdf).
26. Erik Mulder. Fast square-free decomposition of integers using class groups. Research in Number Theory 11, Article 9, 2025; published online December 8, 2024. [Source](https://doi.org/10.1007/s40993-024-00585-8).
27. Erik Mulder. Fast Square-Free Decomposition of Integers Using Class Groups. ANTS XVI author manuscript, 2024. [Source](https://antsmath.org/ANTSXVI/papers/Mulder.pdf).
28. Williams, H. C. (1982). A p+1 method of factoring. Mathematics of Computation 39(159), 225–234. [Source](https://doi.org/10.1090/S0025-5718-1982-0658227-7).
29. Stevenhagen, P. (2008). The number field sieve. In Algorithmic Number Theory, MSRI Publications 44, 83–100. [Source](https://pub.math.leidenuniv.nl/~stevenhagenp/ANTproc/04psh.pdf).
30. Thomé, E. (2012). Square Root Algorithms for the Number Field Sieve. WAIFI 2012, Lecture Notes in Computer Science 7369, 208–224. [Source](https://members.loria.fr/EThome/files/nfs-sqrt.pdf).
31. Couveignes, J.-M. (1993). Computing a square root for the number field sieve. In The Development of the Number Field Sieve, Lecture Notes in Mathematics 1554, 95–102. [Source](https://www.math.u-bordeaux.fr/~jcouveig/publi/Cou94-2.pdf).
32. Montgomery, P. L. (1997). Square roots of products of algebraic numbers. Draft of May 16, 1997. [Source](https://cseweb.ucsd.edu/~ethome/files/Montgomery97.pdf).
