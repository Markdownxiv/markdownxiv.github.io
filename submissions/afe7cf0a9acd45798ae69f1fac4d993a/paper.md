# Coefficient Derivatives for CM Factorization with Arbitrary Target Multiplicity

**Kaiyi Zhang**  
Author homepage: https://github.com/kzoacn  
September 18, 2026

## Abstract

Complex multiplication methods for integer factorization can encounter a saturation event: a division-polynomial value vanishes in the entire Hilbert class polynomial quotient ring, so the value alone yields no nontrivial factor. We study a specific repair that computes the partial derivative with respect to an independent Weierstrass coefficient only after this event. Suppose a composite integer n has a prime divisor p satisfying 4p−1=Db², where −D is a fundamental negative discriminant and D>3. Given the correct Hilbert class polynomial, we prove a success probability of at least one third per trial, with cost polynomial in its degree and the bit length of n. The target prime may occur with arbitrary multiplicity e. The key local statement is that the coefficient derivative has p-adic valuation exactly e−1 on the anomalous side, whereas it vanishes modulo p^e on the complementary saturated side. A separate lifting argument shows that conditioning on the value-stage failure preserves the target component's uniform distribution. We give the complete probability argument, division-free evaluation recurrences, and exact repeated-prime diagnostics. This establishes the scope of the specified derivative algorithm within the anomalous-prime family already considered by Cheng; it does not claim a larger input family or priority for the underlying CM and deformation methods.

## 1. Introduction and scope

An elliptic curve over a finite field with p elements is anomalous when its group has order p. For a prime divisor p of an unknown composite n, such a group is automatically annihilated by n. Complex multiplication supplies these curves when

$$4p-1=Db^2.$$

Working modulo n avoids having to know p. A failure of invertibility during a curve or polynomial computation may then reveal an integer factor. Cheng's general manuscript [1] already states a special-purpose factorization result for this anomalous-prime condition and discusses the Hilbert class polynomial quotient ring. Subsequent CM methods [2,3,7] develop related constructions and extraction procedures.

The local vanishing of a division polynomial is not, by itself, a proof that a proper factor will be obtained. It is possible for the value to vanish on all relevant components. In particular, a zero in the whole quotient ring contains no immediately usable leading coefficient. We examine the following precise remedy: retain the original value test, and only when that value is zero in the whole quotient ring, evaluate the partial derivative with respect to the curve coefficient B while holding A and the horizontal coordinate fixed.

The mathematical ingredients have substantial precedents. Belding [6] studies coefficient deformations over dual numbers in attacks on anomalous-curve discrete logarithms. Maïga, Robert, and Sow [5] give the canonical-lift criterion used in our local nondegeneracy argument. Ordinary CM reduction and class polynomial computation are established tools [4]. Our object is their combination in an unknown composite characteristic, including the failure-conditioned probability calculation and the treatment of repeated target primes. We make no first-publication claim for this combination.

The result concerns finding one nontrivial factor. Recursively factoring the cofactor may lose the stated structural promise. It also does not provide a polynomial-time algorithm for arbitrary integer factorization, general CM traces, or arbitrary annihilating multipliers.

## 2. Statement of the algorithmic result

Write L for the bit length of n. The class polynomial is monic, and all coefficient arrays used for arithmetic are in ascending degree order.

**Theorem 1.** Let n be a composite integer. Suppose that a prime p dividing n and a fundamental negative discriminant −D satisfy

$$D>3,\qquad 4p-1=Db^2$$

for a positive integer b. Let H=H_{−D} be the correct Hilbert class polynomial, of degree h. After the preprocessing described below, the value-and-coefficient-derivative algorithm finds a nontrivial divisor of n with probability at least 1/3 per independent trial. With H already reduced modulo n, a trial uses polynomial time and space in h and L. No restriction is imposed on e=v_p(n), on the class number, or on the multiplicities of other prime factors.

Consequently, independent repetition has expected trial count at most three, and the probability that r trials all fail is at most (2/3)^r. Every returned divisor is verified by integer divisibility. The algorithm does not receive p, e, b, or a factorization of n.

If only n is given and D is promised to be at most L^C for a fixed constant C, class polynomial construction and a fair schedule over candidate discriminants give an expected polynomial-time algorithm under GRH, using the class polynomial construction bounds of [4]. GRH is used for that construction bound; it is not used in the separation proof once a correct H is supplied. Reading an unreduced, externally supplied H incurs its input-length cost separately.

The discriminant −3 requires a different model at j=0 and is outside Theorem 1. We restrict the paper to D>3 rather than importing a separate exceptional-model algorithm.

## 3. Quotient ring, initialization, and sampling

Preprocessing tests the small prime divisors 2, 3, 5, and 7 and handles perfect powers by exact integer roots. Thus the remaining n is odd, its designated p is greater than 7, and n has another prime divisor distinct from p. A prime input may be recognized separately by a primality test.

Set

$$R=(\mathbb Z/n\mathbb Z)[J]/(H(J)).$$

First calculate

$$g=\gcd\bigl(n,6H(0)H(1728)\bigr).$$

A proper g is already an answer. For the correct target discriminant, ordinary CM reduction gives distinct roots j_1,…,j_h in the field with p elements, with no root equal to 0 or 1728. Thus p does not divide the tested quantity and g=n cannot occur for this correct candidate. For an incorrect discriminant, such a failed initialization may simply be skipped.

If g=1, define

$$k=\frac{J}{1728-J},\qquad A=3k,\qquad B=2k.$$

These define a smooth short Weierstrass model

$$E:\ y^2=x^3+Ax+B$$

over R. Indeed,

$$4A^3+27B^2=108k^2(k+1),\qquad k+1=\frac{1728}{1728-J},$$

and all factors are units. The inverse of 1728−J can be obtained without a general ring inversion routine: if

$$H(X)-H(1728)=(X-1728)S(X),$$

then

$$ (1728-J)^{-1}=S(J)H(1728)^{-1}.$$

Each trial samples all coefficients of

$$x=x_0+x_1J+\cdots+x_{h-1}J^{h-1}$$

independently and uniformly modulo n. Sampling only the scalar coefficient would not provide the independence used below.

At the designated prime, the ordinary maximal-order CM reduction theorem [4, Section 2] gives

$$H(J)\bmod p=\prod_{i=1}^h(J-j_i),$$

and each resulting curve and its quadratic twist have group orders p and p+2, in some order. These orders are odd. In particular there is no rational nonzero 2-torsion, and each horizontal coordinate belongs to exactly one member of the twist pair.

For e=v_p(n), simple-root Hensel lifting yields

$$R_{p^e}:=(\mathbb Z/p^e\mathbb Z)[J]/(H)\simeq\prod_{i=1}^h\mathbb Z/p^e\mathbb Z.$$

The evaluation matrix is a Vandermonde matrix with unit determinant. Thus uniform coefficient sampling induces independent uniform coordinates at the target roots, both modulo p and modulo p^e. No hypothesis of splitting or separability is imposed at the other prime factors of n. The algorithm never needs to compute the hidden roots j_i.

## 4. Exact evaluation and factor extraction

Let ψ_m denote the standard division polynomial, and put f=x³+Ax+B. Define integer polynomials

$$F_m=\begin{cases}\psi_m,&m\text{ odd},\\ \psi_m/(2y),&m\text{ even}.\end{cases}$$

Their initial values are

$$F_0=0,\quad F_1=F_2=1,$$

$$F_3=3x^4+6Ax^2+12Bx-A^2,$$

$$F_4=2(x^6+5Ax^4+20Bx^3-5A^2x^2-4ABx-8B^2-A^3).$$

With W=16f², the recurrences, applied beyond the initial cases, are

$$F_{2a}=F_a(F_{a+2}F_{a-1}^2-F_{a-2}F_{a+1}^2),$$

$$F_{2a+1}=\begin{cases}WF_{a+2}F_a^3-F_{a-1}F_{a+1}^3,&a\text{ even},\\ F_{a+2}F_a^3-WF_{a-1}F_{a+1}^3,&a\text{ odd}.\end{cases}$$

All evaluations use addition and multiplication in R. In particular, no division by y or an unknown nonunit is performed. Since n is odd, F_n=ψ_n. The balanced recurrences have a bounded-width set of dependency indices at each halving level, hence O(L) distinct indices with memoization; they do not expand the degree-Θ(n²) polynomial.

The derivative

$$w=\partial_B\psi_n(A,B,x)$$

means the partial derivative of the universal integer polynomial before specialization. A, J, and x are held fixed. It can be evaluated with first-order pairs and the product rule, using input (B,1), (A,0), and (x,0). This adds constant-factor ring work. Differentiating in x, differentiating in J, or using a deformation that keeps j fixed is a different operation.

For extraction, run the ordinary polynomial Euclidean algorithm on H and the degree-less-than-h representative of a value. Before every division, compute the integer gcd of n with the nonzero leading coefficient of the divisor. A nonunit coefficient gives a proper divisor of n. Zero polynomials are detected explicitly.

**Lemma 2 (degree separation).** If

$$\deg\gcd(H\bmod p,z\bmod p)\ne\deg\gcd(H\bmod q,z\bmod q)$$

for distinct prime divisors p and q of n, this Euclidean computation exposes a nontrivial integer factor.

**Proof.** If every encountered nonzero leading coefficient were a unit modulo n, it would remain nonzero after reduction at either prime. Each division, remainder degree, and final gcd degree would therefore agree in the two fields. Different final degrees contradict this. A nonzero residue modulo n with a nonunit leading coefficient has gcd strictly between 1 and n. This reasoning allows repeated prime factors and arbitrary behavior of H modulo q. □

One trial consists of the following steps:

1. Sample x uniformly in the full ring R and compute z=ψ_n(A,B,x).
2. Apply leading-coefficient factor extraction to H and z, returning any proper divisor.
3. If z is nonzero in R, end the unsuccessful trial.
4. If z is zero in R, compute w=∂_Bψ_n(A,B,x), apply the same extraction procedure, and return any proper divisor.
5. If no divisor was returned, start an independent trial.

The derivative trigger is equality to zero in the whole ring, not vanishing at one CM root and not a zero resultant.

## 5. A local bridge for division polynomials

We work over an unramified p-adic integer ring O, normalized by v(p)=1, with p>7. The curve has good reduction and A, B, and its discriminant are units. Let P be an affine point whose reduction P_0 is a nonzero r-torsion point of odd order dividing r.

Using the usual multiplication polynomials,

$$\phi_r=x\psi_r^2-\psi_{r+1}\psi_{r-1},$$

$$\omega_r^2=\phi_r^3+A\phi_r\psi_r^4+B\psi_r^6.$$

At P_0, the values ψ_{r−1} and ψ_{r+1} are nonzero because [r±1]P_0=±P_0. Consequently φ_r and ω_r are units in this neighborhood. The projective multiplication formula is

$$[r]P=[\phi_r\psi_r:\omega_r:\psi_r^3].$$

For the local parameter U=−X/Y at the identity,

$$U([r]P)=V_r\psi_r(P),\qquad V_r=-\phi_r/\omega_r\in O^\times. \tag{1}$$

This identity also holds in a first-order coefficient deformation; V_r and its coefficient derivative are integral. It gives a unit comparison between the division-polynomial value and the local parameter of the multiplication point. In particular, it does not infer ψ_r=0 merely from ψ_r³=0 in a ring with nilpotents.

## 6. The initial nonzero derivative

Suppose P_0 is a nonzero p-torsion point of an ordinary curve. The local canonical-lift criterion in [5, Proposition 4.1 and Lemma 5.2] says that, for an unramified lift of this point,

$$\psi_{p}(\widetilde x)\equiv0\pmod{p^2}$$

holds exactly when the lifted j-invariant is the canonical one modulo p². The criterion is independent of the chosen horizontal lift. We use this local statement, not the additional hypotheses of the paper's point-counting algorithm.

Fix integral lifts A, B, x and vary B to B+pη. The derivative

$$\partial_Bj=-\frac{1728\cdot216A^3B}{(4A^3+27B^2)^2}$$

is a unit. Thus η modulo p parametrizes the possible first-order j-lifts bijectively. Exactly one η gives the canonical j-lift. On the other hand, the integer polynomial Taylor identity gives

$$\psi_p(A,B+p\eta,x)\equiv\psi_p(A,B,x)+p\eta\,\partial_B\psi_p(A,B,x)\pmod{p^2}.$$

An affine function of η over the residue field has exactly one zero only when its slope is nonzero. We obtain

$$\partial_B\psi_p(A,B,x)\not\equiv0\pmod p. \tag{2}$$

The vertical coordinate can be lifted throughout: its residue is nonzero, and 2y is a unit. Equation (2) concerns an independent B-direction; it does not follow from the existence of a canonical lift without the parameter and Taylor argument.

## 7. Propagation to arbitrary target multiplicity

Consider the integral family

$$E_s:\ y^2=x^3+Ax+B+s.$$

At fixed x, Hensel lifting defines y_s with y_s²=y²+s. Differentiation in s at zero is precisely the B partial derivative. Let [a]_s(U) be the formal group multiplication series and write its invariant differential as ρ_s(U)dU, where ρ_s(0)=1. The identities

$$[a]_s(U)=aU+O(U^2),\qquad \partial_s[a]_s(U)=O(U^2), \tag{3}$$

$$\partial_U[a]_s(U)=a\frac{\rho_s(U)}{\rho_s([a]_s(U))} \tag{4}$$

show the distinction between differentiating the argument and differentiating the coefficients. At u in pO, equation (4) gives valuation one for a=p, and valuation zero when p does not divide a.

Let u_0(s) be integral with v(u_0(0))≥1 and set u_{j+1}(s)=[p]_s(u_j(s)). Equation (3) implies

$$v(u_j(0))\ge j+1.$$

Writing a dot for d/ds at zero, the chain rule is

$$\dot u_{j+1}=\partial_U[p]_0(u_j(0))\dot u_j+(\partial_s[p]_s)(u_j(0))\big|_{s=0}. \tag{5}$$

The second term has valuation at least 2j+2. If $v(\dot u_0)=0$, induction gives $v(\dot u_j)=j$: the first term has valuation j+1, strictly below the second, so cancellation is impossible. If $\dot u_0$ is only known to be integral, the same argument gives the lower bound $v(\dot u_j)\ge j$. Applying a fixed multiplier coprime to p preserves these conclusions by (3) and (4).

**Lemma 3 (valuation dichotomy).** Let n=p^e c with p not dividing c.

- If P_0 has order p, then

$$v(\psi_n(P))\ge e,\qquad v(\partial_B\psi_n(P))=e-1. \tag{6}$$

- If P_0 has order d dividing n with p not dividing d, then

$$v(\psi_n(P))\ge e+1,\qquad v(\partial_B\psi_n(P))\ge e. \tag{7}$$

**Proof.** In the first case, take u_0(s)=U([p]P_s). Equation (2) and the unit relation (1) give v(dot u_0)=0. Apply e−1 further multiplications by p and then multiplication by c. The resulting parameter has valuation at least e and derivative valuation exactly e−1. Differentiate (1) for r=n. The term containing the derivative of V_n has valuation at least e, so it cannot cancel the leading derivative term. This proves (6).

In the second case, start at U([d]P_s), whose constant term lies in pO and whose derivative is integral. The remaining multiplier n/d contains exactly e factors of p. Applying (5) e times gives parameter valuation at least e+1 and derivative valuation at least e. The same unit comparison proves (7). □

These statements do not require the chosen p-adic curve lift to remain canonical at higher precision. Canonical lifting is used only to establish the initial residue-field slope (2).

For a quadratic twist choose a fixed nonsquare unit δ. The coordinate change is

$$ (A,B,x)\longmapsto(\delta^2A,\delta^3B,\delta x).$$

For odd n, division-polynomial homogeneity gives

$$\psi_n(\delta^2A,\delta^3B,\delta x)=\delta^{(n^2-1)/2}\psi_n(A,B,x).$$

Differentiating at fixed δ changes the coefficient derivative only by a unit factor. Hence the valuations (6) and (7) apply equally to horizontal coordinates on the anomalous twist. Choosing δ is a proof device, not an operation requiring the algorithm to know p.

## 8. Saturation lifts to the entire prime-power component

Call a target root saturated when both groups in its twist pair are annihilated by n. The anomalous group already has exponent p. The other group has odd order p+2 and an exponent λ coprime to p.

Suppose every target root is saturated. The kernel of reduction from a good-reduction elliptic curve over Z/p^eZ to its residue-field group is killed by p^{e−1}. This follows directly from the formal group filtration; related structural descriptions appear in [8]. Thus the full lifted anomalous group is killed by p^e, and the other lifted group is killed by λp^{e−1}. Both integers divide n in the saturated case.

Each horizontal coordinate lifts to a point on one member of the twist pair, with unit vertical coordinate. Equation (1) therefore implies

$$\psi_n(A_i,B_i,x_i)=0\pmod{p^e}$$

for every x_i at every target root. By the Hensel product decomposition,

$$z=0\text{ in }R_{p^e}\quad\text{for every target input}. \tag{8}$$

The passage from modulo p to modulo p^e uses the group exponent and the formal reduction kernel. It is not an inference that a polynomial vanishing modulo p must vanish modulo p^e.

## 9. Probability of obtaining a proper factor

We first record two counting facts. For odd n, if a twist pair over F_p has n-torsion sizes K and K', then the number of distinct horizontal roots of ψ_n is

$$\frac{K+K'-2}{2}. \tag{9}$$

Every nonidentity odd-order point is paired with its negative. In the present target twist pairs, there are no rational 2-torsion points, so the two sets of horizontal coordinates partition F_p. Root multiplicities of ψ_n do not enter (9).

Also, if independent Bernoulli variables X_1,…,X_h include one with success probability in [c,1−c], then

$$\sup_a\Pr(X_1+\cdots+X_h=a)\le1-c. \tag{10}$$

Condition on all variables except that one to prove the bound. At the target roots, the degree of gcd(H,z) is exactly a sum of independent zero indicators. Reduction at any other prime divisor q depends on independent CRT coordinates.

### 9.1 At least one target root is not saturated

At such a root the anomalous group contributes K=p. The n-torsion in the other, odd-order group is a proper subgroup, of size κ with

$$1\le\kappa\le(p+2)/3.$$

Its horizontal zero probability is

$$a=\frac{p+\kappa-2}{2p}\in[1/3,2/3].$$

By (10), the target gcd degree has maximum point mass at most 2/3. Fix the independent data at another prime q dividing n. Its gcd degree is then fixed, and with probability at least 1/3 the target degree differs. Lemma 2 exposes a factor. This argument uses only reduction modulo p and applies for every e.

### 9.2 All target roots are saturated

By (8), every coefficient of the representative z is divisible by p^e. If z is nonzero modulo n, its highest nonzero coefficient a satisfies p^e dividing a and n not dividing a. Its integer gcd with n is immediately proper. Therefore failure of the value stage is exactly the event

$$\mathcal F=\{z=0\text{ in }R\}. \tag{11}$$

Write n=p^e m with gcd(p,m)=1. Under

$$R\simeq R_{p^e}\times R_m,$$

equation (8) says that event F depends only on the R_m coordinate. Conditional on F, the target coordinate stays uniform, its h root coordinates stay independent, and it stays independent of the other component. This remains true if H has repeated or extension-field roots at the other primes.

At a target root, the anomalous side contains (p−1)/2 horizontal coordinates; the other side contains (p+1)/2. Lemma 3 now completes the proof in two cases.

**Repeated target, e≥2.** Every root value of w is divisible by p^{e−1}. The invertible evaluation matrix implies the same divisibility for every representative coefficient. If at least one root is on the anomalous side, (6) makes w nonzero modulo p^e and hence nonzero modulo n. Its highest nonzero coefficient is divisible by p but not by n, and the first leading-coefficient check yields a proper factor. Conditional on F, the probability of this event is

$$1-\left(\frac{p+1}{2p}\right)^h\ge\frac{p-1}{2p}>\frac13. \tag{12}$$

The algorithm need not divide by the unknown p^{e−1}; integer gcd detects the surviving nilpotent-layer signal directly.

**Single target, e=1.** By (6) and (7), the derivative is zero exactly on the complementary side, with probability

$$\theta=\frac{p+1}{2p}\in[1/2,2/3].$$

Conditional independence and (10) give maximum point mass at most 2/3 for the target derivative gcd degree. Its mismatch with the degree at another prime exposes a factor with conditional probability at least 1/3, by Lemma 2.

If Pr(F)=u, either case gives total success probability at least

$$ (1-u)+u/3\ge1/3.$$

Together with Section 9.1, this proves the probability part of Theorem 1. Independent repetition gives its stated expectation and tail bound. □

## 10. Complexity and implementation boundaries

An element of R is represented by h residues of at most L bits. Naive polynomial multiplication and reduction already have polynomial bit cost in h and L. The balanced division-polynomial evaluation uses O(L) dependency indices. First-order automatic differentiation multiplies the number of ring operations by a constant. The Euclidean extraction has at most h degree reductions and uses polynomial-time integer gcd and modular inverse operations. These observations establish the claimed polynomial time and space per trial; they do not assert an optimized exponent or practical advantage over other factoring methods.

For a fixed bound D≤L^C, one can enumerate the polynomially many candidate fundamental discriminants, compute their class polynomials using [4], and cycle through initialized candidates. Under the cited GRH complexity bound, constructing all candidate polynomials has polynomial expected cost. Each pass includes a fresh trial for the correct discriminant, so the expected number of passes is bounded. One must not wait indefinitely on one incorrect candidate. Perfect-power processing also does not imply complete factorization of its base.

The implementation underlying the working reports evaluates the core with exact Python integer arithmetic and an explicit dependency stack. A later integration adds class polynomial generation and bounded discriminant scanning, including existing FLINT and PARI backends. Those are implementation integrations, not new class polynomial algorithms. A finite budget may return without a divisor; this is neither a primality certificate nor proof that the input lies outside the promised family.

## 11. Exact diagnostics and finite checks

The following two diagnostics exercise the derivative branch after genuine whole-ring vanishing. Take D=139, p=42569, and

$$H(J)=J^3+12183160834031616J^2-53041786755137667072J+67408489017571610198016.$$

The target relation is 4p−1=139·35². Define

$$n_e=1279\cdot2092188149\cdot42569^e\cdot42571.$$

| e | n_e | Bit length | Derivative-stage factor | Cofactor |
|---|---|---:|---|---:|
| 2 | 206429628269945970426200201 | 88 | 4849294751343606155329 | 42569 |
| 3 | 8787502845823330015072916356369 | 103 | 206429628269945970426200201 | 42569 |

For a fully specified e=2 calculation, use the horizontal coordinate with ascending coefficients

$$x=(157176448639805019514367514,\ 32992677408189723639705400,\ 193146405452747808440711350).$$

The value ψ_n is the zero element of R. The derivative has ascending coefficients

$$w=(162480469938518867840453474,\ 112232077725096420858934376,\ 28319881347846659947121360).$$

Thus the very first leading-coefficient check gives

$$\gcd(n_2,28319881347846659947121360)=4849294751343606155329=n_2/42569.$$

The displayed n, H, x and the recurrences in Section 4 specify an exact arithmetic reproduction without hidden factors as search inputs. The factorizations shown here explain and verify the diagnostic. These horizontal coordinates were deliberately constructed to reach the derivative branch. They are not random performance samples and do not estimate the success probability.

The development records include 9,504 scalar valuation checks at ten small primes and target multiplicities two and three, plus 240 exact finite-difference comparisons. A separate check records 2,216 scalar cases, 45 finite differences, 48 quotient-ring samples, and 120 Hensel root projections. The extended core self-test also covers class numbers 2, 3, 4, 5, and 8, target multiplicities 2, 3, and 5, and noncanonical coefficient lifts; its added checks include 60 quotient-ring finite differences and 264 root valuations. These are recorded finite validations of arithmetic and local statements. The success bound and the unrestricted multiplicity statement rely on the proofs above.

No empirical speedup, general-purpose factoring benchmark, or cryptographic-size performance claim is made. This manuscript includes the mathematical specification and exact diagnostics; the development code and its full logs are not deposited as part of this manuscript version.

## 12. Relation to prior work and limitations

Cheng's general Theorem 1 [1] already states the anomalous-prime input condition for general D. Removing the multiplicity restriction from the proof of this particular derivative procedure therefore does not enlarge that earlier stated family. The contribution examined here is the specified value-plus-derivative procedure and its separation proof, especially the valuation e−1 and the preservation of independence after conditioning on whole-ring failure.

Shirase [2] explicitly discusses anomalous saturation failures. Aikawa, Nuida, and Shirase [3] use general class polynomials and resultant-based extraction in a semiprime setting. Full-ring sampling, CM constructions, and group-order multiples also appear in related work such as [7]. Our extraction argument requires checking intermediate leading coefficients; a final resultant alone is not interchangeable with that procedure.

Belding's dual-number treatment [6] is a close conceptual precursor. Its setting has known characteristic and targets discrete logarithms, whereas the present computation uses the unknown composite modulus n and extracts integer factors. The initial local nondegeneracy assertion here is justified through [5], not through an unproved converse suggested by numerical deformation experiments. Sala and Taufer [8] provide related prime-power group structure, but those results alone do not give the failure-conditioned factor-separation algorithm.

The argument uses the specific cooperation of an anomalous group of order p, the index n, and e=v_p(n). It makes no corresponding assertion for a general trace, an arbitrary known multiplier, an arbitrary nonmaximal CM order, or a derivative direction preserving j. Priority for the combined method has not been established by an exhaustive literature audit. The result is presented for further mathematical scrutiny.

## AI assistance and license

OpenAI GPT-6, accessed through the Codex client, assisted with preparation of this English manuscript, consistency checks, local validation, and submission. The exact model build is unknown. Earlier working materials contain internally cross-checked derivations and implementation records; complete model provenance for those earlier sessions is unavailable. Automated checks are not independent human peer review or formal verification of the mathematical theorem.

Copyright 2026 Kaiyi Zhang. This manuscript is licensed under [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/).

## References

1. Qi Cheng. *A New Special-Purpose Factorization Algorithm*. Author preprint, 2002. [Author manuscript](https://qcheng2023.github.io/paper/speint.pdf). This is the general-D manuscript, distinct from the earlier ePrint titled *A New Class of Unsafe Primes*.
2. Masaaki Shirase. *Condition on composite numbers easily factored with elliptic curve method*. Cryptology ePrint Archive, 2017/403, 2017. [Paper](https://eprint.iacr.org/2017/403).
3. Yusuke Aikawa, Koji Nuida, and Masaaki Shirase. *Elliptic Curve Method Using Complex Multiplication Method*. IEICE Transactions on Fundamentals, E102.A(1), 74–80, 2019. [Publisher](https://www.jstage.jst.go.jp/article/transfun/E102.A/1/E102.A_74/_article/-char/en), [DOI](https://doi.org/10.1587/transfun.E102.A.74).
4. Andrew V. Sutherland. *Computing Hilbert class polynomials with the Chinese Remainder Theorem*. Mathematics of Computation 80, 501–538, 2011. [Author preprint](https://arxiv.org/abs/0903.2785), [DOI](https://doi.org/10.1090/S0025-5718-2010-02373-7).
5. Abdoulaye Maïga, Damien Robert, and Djiby Sow. *Towards computing canonical lifts of ordinary elliptic curves in medium characteristic*. Designs, Codes and Cryptography 93, 5231–5255, 2025. [Three-author manuscript, version 2](https://hal.science/hal-03702658v2), [DOI](https://doi.org/10.1007/s10623-025-01719-4). The local criterion used here is Proposition 4.1 and Lemma 5.2 of that manuscript.
6. Juliana V. Belding. *A Weil pairing on the p-torsion of ordinary elliptic curves over the dual numbers of K*. arXiv:math/0703906, 2007. [Paper](https://arxiv.org/abs/math/0703906).
7. Giuseppe Vitto. *Factoring Primes to Factor Moduli: Backdooring and Distributed Generation of Semiprimes*. Cryptology ePrint Archive, 2021/1610, 2021. [Paper](https://eprint.iacr.org/2021/1610).
8. Massimiliano Sala and Daniele Taufer. *The group structure of elliptic curves over Z/NZ*. Journal of Mathematical Cryptology 18(1), 2024. [Author preprint](https://arxiv.org/abs/2010.15543), [DOI](https://doi.org/10.1515/jmc-2023-0025).
