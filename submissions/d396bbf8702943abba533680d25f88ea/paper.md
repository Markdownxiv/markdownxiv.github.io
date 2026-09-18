# Integer Factorization Across Algebra and Geometry: A Survey of Exact Oracle Reductions

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

Integer factorization is connected to many exact computational tasks whose formulations hide prime-power structure behind arithmetic, algebraic, or geometric language. We organize a selected reduction map around four mechanisms: explicit Chinese-remainder components, short multiples of group exponents, finite-field norm factors, and recovery of an integer main term by queries at high powers. Each relation records its input representation, output requirement, and use of randomness or promises. We give proofs of the norm-factor splitting mechanism and of a bounded-denominator main-term recovery lemma, and derive consequences for cyclic sublattices, projective and Grassmannian point counts, modular-curve invariants, and coefficients of fixed noncuspidal modular forms. We also distinguish radical computation, exponent-only information, numerical counts, witnesses, and explicit lists. The purpose is an interface-sensitive synthesis of established results and elementary combinations, not a claim that all reductions are new or that any unresolved reverse reduction has been proved. In particular, changing the query input, dropping a nonvanishing promise, or ignoring output bit length can invalidate an apparent equivalence.

## 1. What a reduction map must specify

Let F(n) denote the complete prime factorization of a positive integer n, including exponents. Integers are encoded in binary and L denotes their bit length. We write A≤_D B for deterministic polynomial-time Turing reducibility and A≤_R B for randomized polynomial-time oracle reducibility; the constructive factoring procedures below use expected polynomial time and verify their returned divisors. The symbol ≡_R allows one direction to be deterministic.

An oracle may be queried on polynomially many inputs of polynomial bit length, including inputs different from n. This convention must be distinguished from an algorithm receiving one extra value attached to n. A complete factorization oracle can also factor auxiliary integers, whereas a supplied factorization of n provides no automatic factorization of φ(n).

Fixed parameters are genuine constants: the dimension of a lattice, the dimension of a finite geometric space, and the weight and level of a modular form do not grow with n. An object specified succinctly by n can have exponentially many vertices, cells, roots, or coefficients. A formula for an output does not remove the cost of writing its binary expansion.

This survey selects a coherent part of a larger working reduction map. Standard reductions are attributed to their sources; the proofs below spell out useful combinations and their precise interfaces. No exhaustive classification or bibliographic priority is claimed. A missing arrow means that this paper does not establish it, not that a separation has been proved.

Use the following distinct arithmetic functions:

$$\operatorname{rad}(n)=\prod_{p\mid n}p,\qquad
\tau(n)=\prod_{p^e\parallel n}(e+1),\qquad
\omega(n)=\#\{p:p\mid n\},$$

$$\sigma_s(n)=\sum_{d\mid n}d^s,\qquad
J_s(n)=n^s\prod_{p\mid n}(1-p^{-s}).$$

The squarefree kernel retaining only odd prime exponents is different from rad(n). Likewise Carmichael's group exponent λ(n) is different from Liouville's function, despite a common use of the letter lambda in the literature.

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

## 10. Validation and use of the map

The source working survey records a literature cutoff of September 16, 2026 and separates published theorems, proved combinations, conditional statements, and unproved candidate links. The present manuscript retains that distinction while selecting the four mechanisms above. The norm-factor and rounding arguments are mathematical proofs; finite examples check formulas and arithmetic but cannot certify their asymptotic claims.

Examples suitable for independent checks include J_2(15)=192 and the modular-curve values in Section 6; P_2(15)=24 and P_3(15)=403; Gr(2,4)(15)=104780 from its two finite-field factors; and the high-power recovery identity (4). A publication-time arithmetic check verifies these examples and 3,996 instances of the rounding identity, for 2≤n≤1000 and 1≤s≤4. The Leech and pure-cusp arguments rely on their stated modular-form identities and bounds, not on extrapolation from those small checks.

For reuse, a proposed new arrow should identify the allowed oracle input, the precise output representation, whether the original n can be changed, which randomness or hypotheses are used, and how intermediate and output lengths are bounded. The useful commonality across the examples is the information encoded by their outputs; a shared mathematical vocabulary alone is not a reduction.

The larger working notes and their full visual map are not deposited in this manuscript version. All claims needed for the selected mechanisms are stated here with proofs or source attribution. No priority is claimed for elementary consequences that may already be known in specialized literature.

## AI assistance and license

OpenAI GPT-6 through the Codex client assisted with the English synthesis, checking interfaces and assumptions, local arithmetic validation, and submission. The exact model build is unknown, and complete model provenance for earlier working sessions is unavailable. The manuscript has not undergone independent human peer review or formal verification.

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
