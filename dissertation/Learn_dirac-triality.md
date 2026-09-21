# Learning Real Clifford Algebra, Split Octonions, and Triality in Signature (4,4)

## A self-contained guide from matrices to verified computation

### Abstract

This book develops a complete path from familiar matrix algebra to the exact
real relationship among the Clifford algebra `Cl(4,4)`, the group
`Spin(4,4)`, two half-spin representations, split-octonion multiplication, and
triality. It assumes only calculus and basic matrix multiplication. Every
additional idea used later - bilinear forms, signature, tensor products,
algebras, Lie algebras, representations, spinors, nonassociativity, numerical
invariants, curved metrics, vielbeins, spin connections, torsion, and the
required cosmology - is introduced here before it is used.
References are supplied for historical and scholarly context, but no reference
is required to understand the argument.

The exact construction uses eight integral 16 by 16 matrices. Their 256
ordered Clifford monomials have rank 256, so the representation is faithful.
The full 16-dimensional Clifford module is irreducible, but its restriction to
the even algebra and to `Spin(4,4)` splits into two inequivalent real
8-dimensional half-spin modules. An independent Zorn construction produces an
8-dimensional split composition algebra. Its para-product has a cyclic
trilinear form whose related triples form a 28-dimensional Lie algebra. Three
inequivalent 8-dimensional modules are permuted by representatives of the
six-element outer automorphism group. An exact intertwiner joins the Clifford
and split-octonion pictures.

Four numerical studies show how the exact tensors can drive differential
equations. A 24-state transport problem preserves three split norms and one
triality trilinear form. An 18-state homogeneous real-spinor model reconstructs
a specified cosmological background. A curved `(4,4)` spinor bundle then
supports a coupled Einstein-spinor model without a scalar field or
cosmological constant. A flat, torsionful Weitzenböck connection gives an
independently implemented teleparallel formulation with the same homogeneous
state history. All studies use a pinned pure-Rust SUNDIALS CVODE engine and are
checked against independent identities. The cosmologies are background
consistency calculations, not observational fits, perturbation analyses, or
claims that nature must use these models.

## 1. How to use this guide

### 1.1 The reader contract

The starting requirements are modest. The reader should know how to add and
multiply real matrices, solve a small linear system, differentiate elementary
functions, and recognize a first-order ordinary differential equation. All
specialized language is defined in this guide. In particular, the word
"spinor" will not be used as a substitute for an explanation.

There are three kinds of statements throughout the book:

- A **definition** fixes the meaning of a word or symbol.
- A **deduction** follows from definitions by an argument displayed here.
- A **verified computation** is a finite calculation whose inputs, algorithm,
  and independent checks are specified here and implemented in the repository.

A finite computation can be a proof when it uses exact arithmetic and covers
all cases in a finite definition. A floating-point computation is different:
it supports a numerical claim only within stated tolerances and checks. This
distinction is central to the project.

### 1.2 The route through the subject

The main objects form the following chain.

- The 8-dimensional vector module `V` carries a quadratic form of signature
   `(4,4)`.
- The 256-dimensional Clifford algebra `Cl(4,4)` encodes that form in an
   associative product.
- A faithful 16-dimensional module realizes the full Clifford algebra by
   matrices.
- Two 8-dimensional half-spin modules `S+` and `S-` are the chiral pieces of
   the even action.
- The 8-dimensional split-octonion algebra `O_s` carries a nonassociative
   product with the same signature.
- The 28-dimensional related-triple algebra realizes `so(4,4)` on three
   modules.
- A six-element triality group represents the outer automorphism group and
   permutes `V`, `S+`, and `S-`.
- The 24-state transport model evolves one vector and two spinors together.
- The 18-state cosmology evolves time, density, and a 16-component real field.
- A vielbein places the rank-16 spinor on a curved `(4,4)` base.
- A coupled Einstein-spinor model separates dust-like and negative-pressure
   homogeneous terms.
- A Weitzenböck connection moves gravity from curvature to torsion while a
   boundary identity preserves the TEGR field equations.

The first half of the guide explains why these dimensions occur. The second
half explains how exact algebra controls the invariants of the numerical
models.

### 1.3 What is proved and what is not

The exact claims concern a particular, fully specified real model:

1. eight matrices give a faithful representation of `Cl(4,4)`;
2. the even action has two irreducible, inequivalent, 8-dimensional real
   half-spin modules;
3. a Zorn multiplication gives a split composition algebra with signature
   `(4,4)`;
4. its para-product realizes split-real triality and an `S3` action
   representing the outer automorphism group;
5. the Clifford and split-octonion realizations are exactly equivalent after a
   change of basis;
6. the explicit curved frame satisfies the metric relation and complete
   vielbein postulate;
7. the canonical and Weitzenböck spinor formulations are related by exact
   contortion, boundary, and homogeneous Dirac-operator identities.

The numerical claims concern four specified initial-value problems and their
reported error bounds. They do not classify observations, derive dark energy
from microscopic physics, establish perturbative stability, justify a
dimensional reduction to `(3,1)`, or identify a particle-generation mechanism.
A mathematically consistent model is not by itself an empirical theory.

### 1.4 Conventions

All vector spaces and matrices are real unless another field is named. Basis
indices run from 0 in machine-readable fixtures and from 1 in the gamma-matrix
labels. Thus the eight vector basis elements are `e0,...,e7`, while the eight
Clifford generators are `gamma_1,...,gamma_8`. Matrix products act on column
vectors from the left. The metric is

$$
\eta=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

The associated bilinear form is written

$$
\langle x,y\rangle=x^{\mathsf T}\eta y,
$$

and its quadratic form is `n(x)=<x,x>`. The symbols `I_d` and `0_d` denote the
identity and zero matrices of size `d`. A commutator is

$$
[A,B]=AB-BA.
$$

### Misconception check M1: Advanced words are not explanations

Knowing that `Spin(4,4)` is a Lie group or that a spinor is a module does not
yet explain either object. The next chapters build those words from matrices,
linear maps, and symmetry equations.

## 2. Toolkit I: vectors, matrices, and forms

### 2.1 Vector spaces and coordinates

A real vector space is a set whose elements can be added and multiplied by
real numbers while satisfying the usual distributive rules. A basis
`(e0,...,e7)` is a list in which every vector has one and only one expansion

$$
x=x_0e_0+x_1e_1+\cdots+x_7e_7.
$$

The coordinate column of `x` is `(x0,...,x7)^T`. Dimension counts basis
vectors, not the number of vectors in the space. An 8-dimensional real space
contains infinitely many vectors.

A linear map `A:V -> W` obeys

$$
A(ax+by)=aA(x)+bA(y).
$$

After bases are chosen, a linear map is a matrix. Changing a basis changes the
matrix but not the underlying map. This distinction will matter when an exact
intertwiner converts one Clifford realization into another.

### 2.2 Matrix multiplication as composition

If `B` acts first and `A` acts second, the composite is represented by `AB`.
In general `AB` and `BA` differ. Their difference is the commutator `[A,B]`.
Noncommuting matrices encode order-sensitive transformations, which is why the
transport path later is more interesting than a single fixed direction.

### Worked example W1: A commutator

Let

$$
A=\begin{pmatrix}0&1\\0&0\end{pmatrix},
\qquad
B=\begin{pmatrix}0&0\\1&0\end{pmatrix}.
$$

Then

$$
AB=\begin{pmatrix}1&0\\0&0\end{pmatrix},
\qquad
BA=\begin{pmatrix}0&0\\0&1\end{pmatrix},
$$

so

$$
[A,B]=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

The result is another matrix acting on the same vector space. Lie algebras use
this commutator as their multiplication.

### 2.3 Rank, nullity, and linear constraints

The rank of a matrix is the dimension of its image, equivalently the number of
independent pivot columns after row reduction. The nullspace consists of
vectors `x` satisfying `Ax=0`. If `A` has `n` columns, the rank-nullity theorem
states

$$
\operatorname{rank}(A)+\operatorname{nullity}(A)=n.
$$

This elementary theorem later converts 84 unknown coefficients and constraint
rank 56 into a 28-dimensional triality algebra.

### Worked example W2: Rank-nullity on a small system

For

$$
C=\begin{pmatrix}1&2&3\\2&4&6\end{pmatrix},
$$

the second row is twice the first, so the rank is 1. There are 3 columns, so
the nullity is 2. For example, `(-2,1,0)^T` and `(-3,0,1)^T` form a nullspace
basis. The large related-triple calculation uses exactly this logic, only with
an exact sparse matrix containing hundreds of equations.

### 2.4 Bilinear and quadratic forms

A bilinear form takes two vectors and is linear in each input. In coordinates
it has the form

$$
B(x,y)=x^{\mathsf T}My.
$$

It is symmetric when `M^T=M`. The associated quadratic form is `Q(x)=B(x,x)`.
The ordinary Euclidean dot product has `M=I`, so every nonzero vector has
positive square. An indefinite form allows positive, negative, and zero
squares for nonzero vectors.

Two vectors are orthogonal when `B(x,y)=0`. Orthogonality therefore depends on
the chosen form. In an indefinite space, a nonzero vector can be orthogonal to
itself; such a vector is called null or isotropic.

### 2.5 Signature

Every nondegenerate real symmetric form can be diagonalized to entries `+1`
and `-1`. The numbers of each sign are unchanged by real changes of basis.
They are the signature `(p,q)`. Our convention places `p` plus signs first and
`q` minus signs second.

For signature `(4,4)`,

$$
n(x)=x_0^2+x_1^2+x_2^2+x_3^2
-x_4^2-x_5^2-x_6^2-x_7^2.
$$

### Worked example W3: A null vector that is not zero

Take `u=e0+e4`. Then

$$
n(u)=1^2-1^2=0,
$$

although `u` is not the zero vector. This possibility distinguishes the split
algebra from a division algebra: a multiplicative norm can vanish on a
nonzero element, allowing zero divisors.

### 2.6 Metric-skew matrices

A matrix `A` is skew with respect to `eta` when

$$
A^{\mathsf T}\eta+\eta A=0.
$$

For the Euclidean metric this reduces to ordinary skew symmetry `A^T=-A`.
Metric-skew matrices form the Lie algebra `so(p,q)`. To see why the equation is
natural, let `x(t)` solve `x'=Ax`. Differentiating its quadratic form gives

$$
\frac{d}{dt}(x^{\mathsf T}\eta x)
=x^{\mathsf T}(A^{\mathsf T}\eta+\eta A)x=0.
$$

Thus metric-skew generators preserve the form, at least infinitesimally and,
after exponentiation, along the full linear flow.

### Misconception check M2: Zero norm does not mean zero vector

That implication is valid for a positive-definite norm but false in split
signature. Null vectors are not numerical accidents; they are an essential
part of the geometry.

## 3. Toolkit II: algebras, tensors, and exact computation

### 3.1 What an algebra is

An algebra is a vector space equipped with a bilinear multiplication. If `x`,
`y`, and `z` are elements, several extra properties may or may not hold:

- A unit `1` satisfies `1x=x1=x`.
- Associativity means `(xy)z=x(yz)`.
- Commutativity means `xy=yx`.
- Alternativity means `(xx)y=x(xy)` and `y(xx)=(yx)x`.
- Flexibility means `(xy)x=x(yx)`.

Matrix algebras are associative but usually noncommutative. Octonion algebras
are nonassociative but alternative. Parentheses therefore cannot be dropped
carelessly in octonion calculations.

The associator measures failure of associativity:

$$
[x,y,z]=(xy)z-x(yz).
$$

Alternativity says the associator vanishes whenever two adjacent inputs are
equal. In fact, for an alternative algebra the associator is an alternating
trilinear function.

### 3.2 Structure constants

Choose a basis `(e0,...,e7)` for an 8-dimensional algebra. Every basis product
has a unique expansion

$$
e_i e_j=\sum_{k=0}^{7}c_{ij}^{\phantom{ij}k}e_k.
$$

The numbers `c_ij^k` are structure constants. Bilinearity then determines all
products:

$$
xy=\sum_{i,j,k}x_i y_j c_{ij}^{\phantom{ij}k}e_k.
$$

The three-index array `c` is a tensor once the input and output spaces are
properly identified. In this repository it is stored as an exact integer
array, so examples can be recomputed without trusting printed tables.

### 3.3 Tensor products

If `U` has basis `(u_i)` and `W` has basis `(w_j)`, the tensor product `U x W`
in this paragraph means the vector space traditionally written with a tensor
symbol; it has basis elements `u_i` tensor `w_j`. Its dimension is

$$
\dim(U\mathbin{\otimes}W)=\dim(U)\dim(W).
$$

Matrices act by Kronecker products. If `A` acts on `U` and `B` on `W`, then
`A tensor B` acts on simple tensors by

$$
(A\mathbin{\otimes}B)(u\mathbin{\otimes}w)
=Au\mathbin{\otimes}Bw.
$$

Four copies of a 2-dimensional space have dimension `2^4=16`. This is the
source of the 16 by 16 gamma matrices used later.

### Worked example W4: A two-factor Kronecker product

For

$$
D=\begin{pmatrix}1&0\\0&-1\end{pmatrix},
\qquad
I=\begin{pmatrix}1&0\\0&1\end{pmatrix},
$$

the Kronecker product is

$$
D\mathbin{\otimes}I=
\operatorname{diag}(1,1,-1,-1).
$$

Each eigenvalue of `D` is repeated across the two basis choices of the second
factor. Repeating this idea four times makes chirality a parity rule on four
binary indices.

### 3.4 Graded algebras

A `Z2`-graded algebra is split into even and odd vector subspaces,

$$
A=A^0\mathbin{\oplus}A^1,
$$

such that parity adds modulo two under multiplication. A product of an even
number of Clifford generators is even; a product of an odd number is odd.
This grading explains why even elements preserve chirality while odd elements
exchange the two chiral spaces.

### 3.5 Exact arithmetic as proof

Integers and rational numbers can be represented without roundoff. Every
Clifford and split-octonion identity in the exact part of this project is a
finite polynomial identity over integers or rationals. Checking every basis
case is enough because multiplication is multilinear.

Rank is also checked exactly. One efficient method reduces an integer matrix
modulo a prime. If a square minor has nonzero determinant modulo that prime,
its integer determinant cannot be zero. Therefore the same minor is nonzero
over the rationals and the reals. A modular rank of 256 for a matrix with 256
rows proves real rank 256; this is a proof, not a floating-point estimate.

### Misconception check M3: Computer-assisted does not mean approximate

A symbolic or integer calculation can be exact. The relevant questions are
whether the input is fully specified, whether arithmetic is exact, whether all
required cases are covered, and whether an independent implementation checks
the result.

## 4. Toolkit III: groups, Lie algebras, and representations

### 4.1 Groups and matrix groups

A group is a set with an associative multiplication, an identity, and an
inverse for every element. A matrix group is a group whose elements are
invertible matrices. The orthogonal group for a metric `eta` is

$$
O(p,q)=\{g:g^{\mathsf T}\eta g=\eta\}.
$$

The subgroup connected to the identity and with determinant one is denoted
`SO_0(p,q)` in contexts where the connected component matters. Global
components and central quotients are separate from the local Lie-algebra
computations below.

### 4.2 Lie groups and tangent generators

A Lie group is both a group and a smooth manifold, with smooth multiplication
and inversion. A path through the identity can be written locally as
`g(t)=I+tA+O(t^2)`. Substitution into `g(t)^T eta g(t)=eta` gives

$$
A^{\mathsf T}\eta+\eta A=0.
$$

The tangent matrices form the Lie algebra `so(p,q)`. Its product is the
commutator. For dimension `n=p+q`, a metric-skew matrix is determined by
`n(n-1)/2` entries. Hence

$$
\dim\mathfrak{so}(4,4)=\frac{8\cdot7}{2}=28.
$$

### 4.3 Representations and modules

A representation of a group assigns an invertible linear map to each group
element while preserving multiplication. A representation of a Lie algebra
assigns a matrix to each Lie-algebra element while preserving commutators. The
vector space carrying the action is called a module.

A subspace `W` is invariant if every representation matrix sends `W` into
`W`. A nonzero module is irreducible when its only invariant subspaces are
`0` and the whole module. Reducible does not mean defective; it means the
module contains smaller invariant pieces.

### 4.4 Commutants and intertwiners

The commutant of matrices `rho(X)` consists of matrices `C` satisfying

$$
C\rho(X)=\rho(X)C
$$

for every generator `X`. An intertwiner from representation `rho_1` to
`rho_2` is a matrix `L` satisfying

$$
L\rho_1(X)=\rho_2(X)L.
$$

An invertible intertwiner is a change of basis identifying the two
representations. If two irreducible modules have no nonzero intertwiner, they
are inequivalent.

For finite-dimensional representations of a real semisimple Lie algebra,
complete reducibility supplies invariant complements. If a representation
were reducible, projection onto a proper summand would be a nonscalar member
of its commutant. Therefore a one-dimensional commutant consisting only of
real scalar matrices proves irreducibility in the setting used here.

### Worked example W5: A commutant detects a split

Let a single matrix act on `R^2` by

$$
R=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

Every diagonal matrix commutes with `R`, so the commutant has dimension 2.
The coordinate axes are invariant, and the representation splits. By
contrast, the computed commutant of each 8-dimensional triality module has
dimension 1 after all 28 generators are imposed.

### 4.5 Inner and outer automorphisms

An automorphism preserves all algebraic operations. Conjugation by a group
element gives an inner automorphism. An automorphism not obtainable this way
is outer. Inner automorphisms cannot change the equivalence class of a module
merely by relabeling the same action. Triality cyclically permutes three
inequivalent 8-dimensional modules, so that permutation is outer.

### 4.6 The spin group in one paragraph

Let `alpha` be the grade involution: it fixes even Clifford elements and
negates odd ones. Products of vectors with norm `+1` or `-1` form the pin
group and act on `V` by the twisted adjoint map

$$
\widetilde{\operatorname{Ad}}_g(v)=\alpha(g)vg^{-1}.
$$

This gives a two-to-one map from `Pin(p,q)` onto `O(p,q)`. The even subgroup
is `Spin(p,q)` and maps onto `SO(p,q)` under the convention used in this
paragraph. Its identity component gives the two-to-one covering

$$
\operatorname{Spin}_0(p,q)\longrightarrow SO_0(p,q).
$$

Terminology for the disconnected global groups varies between sources, but
the differential is unambiguous: it identifies the spin Lie algebra with
`so(p,q)`. The exact calculations in this guide are Lie-algebra calculations.
Statements about global components, fundamental groups, or central characters
require additional bookkeeping and are not inferred from those calculations.

### Misconception check M4: Same dimension does not mean same representation

Two 8-dimensional vector spaces are abstractly isomorphic as vector spaces.
They can nevertheless carry inequivalent actions of the same Lie algebra.
Triality relates the vector and half-spin actions through an outer
relabeling, not through an intertwiner that leaves the Lie algebra fixed.

## 5. Clifford algebras from geometry

### 5.1 Why introduce a new product?

A quadratic form stores lengths but ordinary vector-space addition does not
turn reflection geometry into multiplication. A Clifford algebra adds an
associative product constrained by

$$
v^2=n(v)1.
$$

Polarizing this equation with `v=x+y` yields

$$
xy+yx=2\langle x,y\rangle1.
$$

Thus orthogonal vectors anticommute. A basis vector with positive square acts
like an involution, while one with negative square acts like a real matrix
whose square is `-I`.

### 5.2 Definition and universal property

For a real quadratic space `(V,n)`, the Clifford algebra `Cl(V,n)` is the
unital associative algebra generated by `V` subject only to

$$
xy+yx=2\langle x,y\rangle1.
$$

"Subject only to" has a precise meaning: any linear map from `V` into an
associative unital algebra whose images obey these relations extends uniquely
to an algebra homomorphism from `Cl(V,n)`. This is the universal property. It
lets a set of matrices satisfying the relations define a Clifford
representation automatically.

### 5.3 Ordered monomials and dimension

With an orthogonal basis `(e1,...,en)`, repeated generators can be removed
using their squares, and out-of-order distinct generators can be swapped at
the cost of a minus sign. Every word therefore reduces to an ordered monomial

$$
e_{i_1}e_{i_2}\cdots e_{i_k},
\qquad i_1<i_2<\cdots<i_k.
$$

There is one monomial for each subset of `n` generators, including the empty
subset that gives `1`. Hence the spanning count is

$$
\sum_{k=0}^{n}\binom{n}{k}=2^n.
$$

For `n=8`, this is 256. Linear independence follows from the standard
construction of the Clifford algebra, and in our matrix realization it is
also checked directly by rank.

### 5.4 Two one-generator examples

If a real generator `e` has `e^2=+1`, then every element is `a+be`, and

$$
(a+be)(c+de)=(ac+bd)+(ad+bc)e.
$$

The idempotents `(1+e)/2` and `(1-e)/2` split this algebra into two real
copies. If instead `e^2=-1`, the same multiplication is the complex-number
rule with `e` playing the role of the imaginary unit. These examples show how
the sign of the quadratic form changes the real algebra.

### Misconception check M5: The factor two is not optional

From `xy+yx=2<x,y>1`, setting `x=y` gives `2x^2=2n(x)1`, hence
`x^2=n(x)1`. Omitting the factor two would contradict the intended generator
squares.

## 6. The exact `Cl(4,4)` construction

### 6.1 Three elementary matrices

Define

$$
P=\begin{pmatrix}0&1\\1&0\end{pmatrix},
\qquad
N=\begin{pmatrix}0&1\\-1&0\end{pmatrix},
\qquad
G=\begin{pmatrix}1&0\\0&-1\end{pmatrix}.
$$

Direct multiplication gives

$$
P^2=I_2,\qquad N^2=-I_2,\qquad G^2=I_2.
$$

Each pair anticommutes:

$$
PN=-NP,\qquad PG=-GP,\qquad NG=-GN.
$$

### Worked example W6: Checking the seed matrices

For example,

$$
PN=\begin{pmatrix}-1&0\\0&1\end{pmatrix}=-G,
\qquad
NP=\begin{pmatrix}1&0\\0&-1\end{pmatrix}=G.
$$

Therefore `PN+NP=0`. Similarly,

$$
PG=\begin{pmatrix}0&-1\\1&0\end{pmatrix}=-N,
\qquad
GP=N.
$$

These 2 by 2 checks are the local engine of the 16 by 16 construction.

### 6.2 Four tensor factors

On the fourth tensor power of `R^2`, define for `k=1,2,3,4`

$$
\gamma_k^+=G^{\mathbin{\otimes}(k-1)}
\mathbin{\otimes}P\mathbin{\otimes}
I_2^{\mathbin{\otimes}(4-k)},
$$

$$
\gamma_k^-=G^{\mathbin{\otimes}(k-1)}
\mathbin{\otimes}N\mathbin{\otimes}
I_2^{\mathbin{\otimes}(4-k)}.
$$

There are four positive generators and four negative generators. Each is an
integral 16 by 16 matrix because every tensor factor has integral entries.
The factors before `P` or `N` are `G`; they supply exactly the signs needed
when different generators pass one another.

The ordered generator list is

$$
(\gamma_1^+,\gamma_2^+,\gamma_3^+,\gamma_4^+,
\gamma_1^-,\gamma_2^-,\gamma_3^-,\gamma_4^-).
$$

It satisfies

$$
\gamma_a\gamma_b+\gamma_b\gamma_a
=2\eta_{ab}I_{16}.
$$

### 6.3 Why the relations hold

Squaring a tensor product squares each factor. The positive generator contains
one `P`, so its square is `+I_16`; the negative generator contains one `N`, so
its square is `-I_16`. For distinct generators, find the first tensor position
where they differ. One has a `P` or `N` there and the other has a `G`.
Those factors anticommute, while all remaining swaps contribute no further
sign. The full matrices therefore anticommute.

### 6.4 Faithfulness by rank

The 256 ordered monomials are flattened into 256 coordinate rows in the
256-dimensional space of 16 by 16 matrices. Exact row reduction gives rank
256. Consequently they span all of `Mat_16(R)` and are linearly independent.
The induced homomorphism

$$
\mathrm{Cl}(4,4)\longrightarrow\operatorname{Mat}_{16}(\mathbb R)
$$

is therefore an isomorphism. This proves both faithfulness and

$$
\mathrm{Cl}(4,4)\simeq\operatorname{Mat}_{16}(\mathbb R).
$$

The even monomials have rank 128. Their algebra is

$$
\mathrm{Cl}^0(4,4)\simeq
\operatorname{Mat}_{8}(\mathbb R)\mathbin{\oplus}
\operatorname{Mat}_{8}(\mathbb R).
$$

### Verification record V1: Clifford construction

```text
matrix_dimension=16
generator_count=8
ordered_monomial_count=256
full_algebra_rank=256
even_algebra_rank=128
```

### Misconception check M6: A dimension count alone is not faithfulness

Knowing that both abstract and target algebras have dimension 256 is not
enough unless the map is known to be injective or surjective. The rank-256
matrix calculation supplies that missing step directly.

## 7. Chirality and the two half-spin modules

### 7.1 The volume element

Multiply the eight generators in the fixed order:

$$
\omega=\gamma_1\gamma_2\cdots\gamma_8.
$$

For this construction,

$$
\omega=G\mathbin{\otimes}G\mathbin{\otimes}G\mathbin{\otimes}G,
\qquad \omega^2=I_{16}.
$$

Moving any generator through the other seven contributes seven minus signs,
so

$$
\omega\gamma_a=-\gamma_a\omega.
$$

The eigenvalues of `omega` are `+1` and `-1`, each eight times. In the
published tensor-product coordinate order its diagonal is

```text
(+1,-1,-1,+1,-1,+1,+1,-1,
 -1,+1,+1,-1,+1,-1,-1,+1).
```

### 7.2 Projectors and chirality

Define

$$
P_+=\frac{I_{16}+\omega}{2},
\qquad
P_-=\frac{I_{16}-\omega}{2}.
$$

Using `omega^2=I` gives

$$
P_+^2=P_+,
\quad P_-^2=P_-,
\quad P_+P_-=0,
\quad P_++P_-=I.
$$

Their images `S+` and `S-` both have dimension 8. Since `omega` anticommutes
with odd elements, an odd Clifford element exchanges `S+` and `S-`. Since it
commutes with even elements, every even element preserves both spaces.

### Worked example W7: Projecting a spinor

In zero-based coordinates, the positive eigenspace uses indices
`0,3,5,6,9,10,12,15`, while the negative eigenspace uses
`1,2,4,7,8,11,13,14`. Thus `P+` retains the components in the first list and
sets the others to zero; `P-` does the reverse. For example, if `s` has every
component equal to 1, then

$$
P_+s=(1,0,0,1,0,1,1,0,0,1,1,0,1,0,0,1)^{\mathsf T},
$$

and `P-s` has ones in the complementary positions. The interleaving is
basis-dependent, but the eigenspace definition is not. Reordering coordinates
could display two contiguous blocks without changing chirality.

### 7.3 Spin generators

For `a<b`, define

$$
\Sigma_{ab}=\frac14[\gamma_a,\gamma_b]
=\frac12\gamma_a\gamma_b.
$$

The second equality uses anticommutation. These 28 matrices obey

$$
[\Sigma_{ab},\gamma_c]
=\eta_{bc}\gamma_a-\eta_{ac}\gamma_b
$$

and the commutation relations of `so(4,4)`. Because each `Sigma_ab` is even,
it preserves `S+` and `S-`.

### 7.4 Irreducible but inequivalent

Three exact tests settle the representation type:

- the even algebra acts with rank 64 on each 8-space, filling all of
  `End(R^8)`;
- the commutant of each restricted spin action has dimension 1;
- the intertwiner space from one restricted action to the other has dimension
  0.

The first test alone already shows that no proper subspace is invariant under
the full even algebra. The commutant test independently proves irreducibility
using complete reducibility. The zero intertwiner space proves inequivalence
for the fixed labeling of `so(4,4)`.

### Verification record V2: Half-spin modules

```text
plus_indices_zero_based=[0,3,5,6,9,10,12,15]
minus_indices_zero_based=[1,2,4,7,8,11,13,14]
projector_ranks=(8,8)
even_action_ranks=(64,64)
spin_commutant_dimensions=(1,1)
cross_intertwiner_dimension=0
```

### Misconception check M7: Full Clifford irreducibility versus spin reducibility

The real 16-dimensional module is irreducible for the full algebra
`Cl(4,4)=Mat_16(R)`. Its restriction to the even algebra or to `Spin(4,4)` is
reducible and equals `S+` direct sum `S-`. These statements concern different
acting algebras and do not conflict.

## 8. Type `D4` and the scope of representation classification

### 8.1 Roots and highest weights in usable form

A semisimple Lie algebra can be organized by choosing a maximal commuting
subalgebra and recording how the remaining generators transform under it.
The resulting root diagram compresses commutator information. The complexified
Lie algebra of `so(4,4)` has Dynkin type `D4`. Its diagram has one central node
joined to three outer nodes.

A highest weight is a nonnegative integer combination of fundamental weights:

$$
\lambda=n_1\lambda_1+n_2\lambda_2+n_3\lambda_3+n_4\lambda_4,
\qquad n_i\in\mathbb Z_{\ge0}.
$$

With the labeling used here:

- `lambda_1` gives the 8-dimensional vector module `V`;
- `lambda_2` gives the 28-dimensional adjoint module;
- `lambda_3` gives one 8-dimensional half-spin module;
- `lambda_4` gives the other 8-dimensional half-spin module.

### 8.2 Exactly what is classified

Dominant integral highest weights classify finite-dimensional irreducible
algebraic representations of the simply connected split algebraic group after
the appropriate real-form information is included. Here "simply connected"
is the algebraic-group condition; it is not an assertion that the manifold of
real points is topologically simply connected. Highest weights do not
classify all possible infinite-dimensional, unitary, topological, or merely
smooth representations. They also do not erase global questions about the
center or which quotient of the spin group acts faithfully.

Within the finite-dimensional algebraic scope relevant to the exact tensors,
every irreducible family is indexed by the four nonnegative integers above.
The diagram automorphism group fixes the central coefficient `n2` and permutes
`n1`, `n3`, and `n4`.

### 8.3 The `D4` symmetry

Most Dynkin diagrams have at most a twofold visible symmetry. The `D4` diagram
has three indistinguishable outer arms, so its automorphism group is the
permutation group `S3`. It permutes the vector and two half-spin fundamental
weights. This exceptional three-way symmetry is the representation-theoretic
shadow of triality.

### Worked example W8: Permuting a highest weight

Suppose a module has highest-weight coefficients `(2,1,0,3)`. A cyclic diagram
automorphism sends the three outer coefficients `(2,0,3)` to `(0,3,2)` while
leaving the central coefficient 1 fixed. One resulting ordering is therefore
`(0,1,3,2)`. Triality acts on whole representation families, not only on the
three fundamental 8-dimensional modules.

### Misconception check M8: Triality does not identify three actions pointwise

For a fixed labeling of `so(4,4)`, `V`, `S+`, and `S-` are pairwise
inequivalent. An outer automorphism changes the labeling of the Lie algebra and
then carries one action to another. Saying "triality permutes them" is more
precise than saying "they are the same."

## 9. From familiar number systems to split octonions

### 9.1 A ladder of algebras

The real numbers are commutative, associative, and one-dimensional. The
complex numbers are still commutative and associative but two-dimensional over
the reals. The quaternions are four-dimensional, associative, and
noncommutative. The octonions are eight-dimensional, noncommutative and
nonassociative, but alternative.

Each of these division algebras has a conjugation and a positive norm obeying

$$
n(xy)=n(x)n(y).
$$

A split composition algebra keeps the multiplicative norm but makes it
indefinite. Nonzero null elements then exist, so division can fail.

### 9.2 Composition algebras

A real composition algebra consists of a finite-dimensional unital algebra
and a nondegenerate quadratic form `n` such that

$$
n(xy)=n(x)n(y).
$$

Conjugation is the linear map satisfying

$$
x+\bar x=\operatorname{tr}(x)1,
\qquad
x\bar x=\bar x x=n(x)1.
$$

For split octonions the norm has signature `(4,4)`. The word "split" refers to
this maximally indefinite real form, not to a direct-product decomposition of
the nonassociative algebra.

### 9.3 Why alternatives are enough

Associativity is stronger than many geometric constructions require.
Alternativity guarantees that every subalgebra generated by two elements is
associative. Thus expressions involving only two chosen elements can be
reassociated safely, while general three-element expressions retain genuine
octonionic information.

### Misconception check M9: Nonassociative does not mean arbitrary

Octonion multiplication obeys a unit law, bilinearity, conjugation reversal,
a quadratic identity, norm composition, alternativity, and flexibility. It is
highly constrained even though general reassociation is invalid.

## 10. Split octonions from Zorn data

### 10.1 Scalars and three-vectors

Represent an element by a quadruple

$$
X=(a,u,v,b),
$$

where `a,b` are real numbers and `u,v` are ordinary 3-component real vectors.
For another element `Y=(c,r,w,d)`, define

$$
XY=\left(
ac+u\mathbin{\cdot}w,
ar+du-v\mathbin{\times}w,
cv+bw+u\mathbin{\times}r,
v\mathbin{\cdot}r+bd
\right).
$$

The symbol `times` denotes the ordinary three-dimensional cross product. In
coordinates,

$$
(r_1,r_2,r_3)\mathbin{\times}(s_1,s_2,s_3)
=(r_2s_3-r_3s_2,
 r_3s_1-r_1s_3,
 r_1s_2-r_2s_1).
$$

The unit is `(1,0,0,1)`. Conjugation and norm are

$$
\overline{(a,u,v,b)}=(b,-u,-v,a),
\qquad
n(a,u,v,b)=ab-u\mathbin{\cdot}v.
$$

This is the Zorn vector-matrix model written as data rather than as a formal
2 by 2 block matrix.

### 10.2 Orthogonal coordinates

The implementation uses coordinates `(x0,...,x7)` related by

$$
a=x_0+x_4,\qquad b=x_0-x_4,
$$

$$
u=(x_1+x_5,x_2+x_6,x_3+x_7),
$$

$$
v=(-x_1+x_5,-x_2+x_6,-x_3+x_7).
$$

Substitution gives

$$
n(x)=x_0^2+x_1^2+x_2^2+x_3^2
-x_4^2-x_5^2-x_6^2-x_7^2.
$$

Conjugation fixes `e0` and negates `e1,...,e7`.

### Worked example W9: Basis multiplication and signs

The exact tensor gives

$$
e_1^2=-e_0,\qquad e_4^2=e_0,
$$

$$
e_1e_2=-e_3,\qquad e_2e_1=e_3,
$$

$$
e_1e_4=-e_5,\qquad e_4e_1=e_5.
$$

The signs reflect both noncommutativity and the split signature. They were
computed independently from the Zorn dot-and-cross formula and from the stored
integer structure tensor.

### Worked example W10: Norm composition with ordinary integers

Choose

$$
x=e_0+e_1,\qquad y=e_0+e_2.
$$

Both have norm 2. Bilinearity and the products above give

$$
xy=e_0+e_1+e_2-e_3.
$$

All four displayed basis directions are positive, so

$$
n(xy)=1+1+1+1=4=n(x)n(y).
$$

This example is illustrative; the project verifies the complete polynomial
identity `n(xy)=n(x)n(y)`, not merely selected inputs.

### Worked example W11: Nonassociativity appears explicitly

The first lexicographic basis triple with a nonzero associator is
`(e1,e2,e4)`. Exact multiplication gives

$$
(e_1e_2)e_4=e_7,
\qquad
e_1(e_2e_4)=-e_7.
$$

Therefore

$$
[e_1,e_2,e_4]=2e_7.
$$

No contradiction with alternativity occurs because the three inputs are
distinct. Replacing the first two inputs by the same element makes the
associator vanish.

### 10.3 Complete exact checks

The implementation verifies on basis elements, then extends by multilinearity:

- the unit laws;
- conjugation is an involution and reverses products;
- `x bar(x)=n(x)1`;
- norm composition;
- left and right alternativity;
- flexibility;
- integral structure constants;
- nondegeneracy in every tensor mode.

There are 64 nonzero structure constants in the chosen basis. Each of the
three tensor flattenings has rank 8, so no input or output direction silently
drops out.

### Verification record V3: Split multiplication

```text
basis_dimension=8
metric_signature=(4,4)
ordinary_nonzero_structure_constants=64
ordinary_tensor_mode_ranks=(8,8,8)
null_example=e0+e4
norm_example_product=e0+e1+e2-e3
associator[e1,e2,e4]=2e7
```

## 11. The para-product and its invariant trilinear form

### 11.1 Changing the product

Define the para-product by

$$
x\star y=\bar x\,\bar y.
$$

Conjugation preserves the norm, so

$$
n(x\star y)=n(x)n(y).
$$

The para-product need not have the same unit behavior as the ordinary product.
Its purpose is to place the three 8-dimensional slots on a more symmetric
footing.

### 11.2 Polarization of the norm

The bilinear form associated with `n` is

$$
\langle x,y\rangle
=\frac12\left(n(x+y)-n(x)-n(y)\right).
$$

The composition law implies identities relating multiplication and this form.
For the para-product, define

$$
T(x,y,z)=\langle x\star y,z\rangle.
$$

Exact expansion in the Zorn model gives cyclic symmetry:

$$
T(x,y,z)=T(y,z,x)=T(z,x,y).
$$

Cyclic does not automatically mean invariant under every transposition. The
three-cycle is the fundamental symmetry here; a reflection requires
conjugation in the appropriate slots.

### Worked example W12: A nontrivial cyclic value

For three positive imaginary basis elements, the exact tensor gives

$$
T(e_1,e_2,e_3)=-1,
$$

and direct recomputation gives

$$
T(e_2,e_3,e_1)=-1,
\qquad
T(e_3,e_1,e_2)=-1.
$$

The equality is exact. It is not the result of rounding three nearly equal
floating-point numbers.

### 11.3 Why a trilinear form is the right carrier

A quadratic form compares one module with itself. Triality concerns three
different modules. A nondegenerate trilinear form accepts one vector from each
slot and can remain fixed while the slots are permuted. This packages the
three-way relation without selecting a preferred nonzero spinor or identifying
the modules pointwise.

### Verification record V4: Para-product

```text
para_nonzero_structure_constants=64
para_tensor_mode_ranks=(8,8,8)
T(e1,e2,e3)=T(e2,e3,e1)=T(e3,e1,e2)=-1
```

### Misconception check M10: A single isometry is not triality

An isometry of one 8-space preserves one quadratic form. Triality also relates
three inequivalent actions and preserves a trilinear coupling among their
slots. One matrix on one space does not establish the full structure.

## 12. Related triples and split-real triality

### 12.1 The defining equation

A related triple is a triple of metric-skew endomorphisms `(A,B,C)` satisfying

$$
A(x\star y)=Bx\star y+x\star Cy
$$

for all split octonions `x,y`. The collection is denoted

$$
\mathfrak{tri}(\mathbb O_s).
$$

The equation is a Leibniz rule distributed over three positions. It says that
an infinitesimal change in the output equals compatible infinitesimal changes
in the two inputs.

### 12.2 Turning the definition into linear algebra

Each member of `so(4,4)` has 28 parameters. Three members begin with

$$
3\cdot28=84
$$

unknown coefficients. It is enough to impose the defining equation on the 64
ordered pairs of basis elements `(e_i,e_j)`. Each output is an 8-vector, so
there are 512 scalar equations. Many equations are dependent. Exact row
reduction finds rank 56, hence

$$
\dim\mathfrak{tri}(\mathbb O_s)=84-56=28.
$$

### Worked example W13: Reading the rank calculation

Rank 56 does not mean only 56 equations were checked. All 512 scalar equations
were assembled. Rank says that 56 independent combinations constrain the 84
parameters. The other equations are consequences. Rank-nullity then leaves a
28-dimensional exact solution space.

### 12.3 Three projections, three modules

Project a related triple to its first, second, or third component. Each
projection has rank 28, so each identifies the related-triple Lie algebra with
`so(4,4)`. The three resulting 8-dimensional actions have

$$
\text{commutant dimensions }(1,1,1)
$$

and pairwise intertwiner dimensions

$$
(0,0,0).
$$

They are therefore irreducible and pairwise inequivalent for the fixed
labeling. Exact comparison identifies the second and third with the canonical
half-spin modules from the Clifford construction, in the chosen order.

### 12.4 The six triality symmetries

Cyclic permutation defines

$$
r(A,B,C)=(B,C,A),
\qquad r^3=1.
$$

Let

$$
\kappa=\operatorname{diag}(1,-1,-1,-1,-1,-1,-1,-1),
$$

the matrix of split-octonion conjugation. The reflection fixes the vector
position up to conjugation and exchanges the spin positions:

$$
s(A,B,C)=(\kappa A\kappa,\kappa C\kappa,\kappa B\kappa).
$$

It satisfies

$$
s^2=1,\qquad srs=r^{-1}.
$$

Every word reduces to one of

$$
1,\ r,\ r^2,\ s,\ sr,\ sr^2.
$$

The exact automorphism matrices show that all six are distinct. They form an
`S3` subgroup of `Aut(so(4,4))` representing the outer automorphism group.
The identity is inner, as every identity automorphism is; the other five
elements represent nontrivial outer classes and are outer.

### Worked example W14: Why the action is outer

Assume for contradiction that the cyclic map were inner. Precomposing a
representation by an inner automorphism produces an equivalent
representation: the implementing group element itself supplies an
intertwiner. But `r` carries the vector action to a half-spin action, and the
computed intertwiner space between those fixed actions has dimension zero.
Therefore `r` cannot be inner.

### Verification record V5: Triality

```text
constraint_rank=56
triality_dimension=28
projection_ranks=(28,28,28)
representation_commutant_dimensions=(1,1,1)
representation_intertwiner_dimensions=(0,0,0)
s3_element_count=6
```

### Misconception check M11: `S3` here is an automorphism group

The six elements do not add six dimensions to the Lie algebra. The
28-dimensional Lie algebra is continuous infinitesimal data; `S3` is a finite
automorphism group acting on that data. Its identity is not called outer; its
five nonidentity elements are outer.

## 13. Compatibility of the Clifford and split-octonion pictures

### 13.1 Multiplication as a chiral map

Fix `x` in the split octonions. Left or right multiplication by `x` is a
linear map on an 8-dimensional space, even though the algebra itself is
nonassociative. In a suitable arrangement, multiplication maps between two
chiral 8-spaces. Combining a chiral block with its conjugate block gives a
16 by 16 matrix

$$
\Gamma(x)=\begin{pmatrix}0&L_{\bar x}\\L_x&0\end{pmatrix},
$$

where `L_x(y)=xy` is ordinary left multiplication.

For basis vectors, the eight resulting matrices satisfy the same Clifford
relations as the tensor-product gamma matrices.

### 13.2 The intertwiner equation

Let `gamma_a` be the canonical matrices and `Gamma_a` the
multiplication-induced matrices. A matrix `K` relates them when

$$
\gamma_aK=K\Gamma_a
$$

for all eight generators. These are linear equations in the 256 entries of
`K`. Their exact solution space has dimension 1. A primitive integer solution
has rank 16 and is therefore invertible.

The equation rearranges to

$$
\Gamma_a=K^{-1}\gamma_aK,
$$

so the two representations are the same abstract Clifford module in different
bases.

### 13.3 Why independent constructions matter

If the octonion matrices had merely been copied from the Clifford matrices,
the agreement would be built in. Instead, one construction starts from three
2 by 2 matrices and tensor products; the other starts from dot products,
cross products, and Zorn multiplication. The exact rank-16 intertwiner is a
nontrivial bridge between independently defined objects.

### Verification record V6: Compatibility

```text
octonion_clifford_intertwiner_dimension=1
octonion_clifford_intertwiner_rank=16
canonical_half_spin_matching_dimensions=((1,0),(0,1))
```

### Misconception check M12: An intertwiner changes coordinates, not facts

The matrix `K` does not turn a nonassociative octonion algebra into an
associative matrix algebra. It identifies the induced Clifford actions. The
underlying octonion multiplication remains nonassociative.

## 14. Numerical toolkit: ODEs, invariants, and error

### 14.1 First-order systems

An ordinary differential equation in first-order form is

$$
y'(t)=f(t,y(t)),\qquad y(t_0)=y_0.
$$

A higher-order equation can be converted to first order by adding variables
for derivatives. A system with 24 scalar components is one vector equation in
`R^24`.

For a linear time-dependent system `y'=A(t)y`, matrices at different times may
fail to commute. Then the solution is not generally
`exp(integral A) y0` without time ordering. A numerical integrator advances
through many local steps instead.

### 14.2 Invariants as strong tests

An invariant is a quantity `I(y(t))` that should remain constant along an
exact solution. Differentiating `I` and substituting the differential equation
can prove invariance. Numerically, drift in `I` tests the combined effects of
discretization, nonlinear solves, implementation errors, and roundoff.

For `y'=Ay` and a symmetric metric `eta`,

$$
\frac{d}{dt}(y^{\mathsf T}\eta y)
=y^{\mathsf T}(A^{\mathsf T}\eta+\eta A)y.
$$

Metric-skew `A` makes this derivative zero.

### Worked example W15: Scalar decay before a 24-state system

The equation `z'=-3z/2` has solution

$$
z(t)=z(0)e^{-3t/2}.
$$

Squaring gives `z(t)^2=z(0)^2e^{-3t}`. The spinor cosmology later contains
this dilution in every component plus a skew internal rotation. The rotation
changes direction but not the sum of squares.

### 14.3 What BDF, Newton, and a dense solver mean

A backward differentiation formula, abbreviated BDF, approximates a
derivative using current and previous solution values while evaluating the
right-hand side at the new time. This implicit form is useful for stiff
systems, where explicit methods may require extremely small steps.

An implicit step produces nonlinear equations for the new state. Newton
iteration solves them by repeated linearization. A dense linear solver stores
and factors the full Jacobian matrix rather than exploiting sparsity. These
are algorithmic choices, not additional physical assumptions.

CVODE controls estimated local error using relative and absolute tolerances.
A relative tolerance scales with solution magnitude; an absolute tolerance
protects components near zero. Tolerances are requests to the adaptive method,
not proofs of global accuracy. Independent analytic identities and invariant
drifts provide the stronger end-to-end checks used here.

### 14.4 Deterministic replay and semantic verification

Byte-identical repeated output shows that a fixed implementation and
environment produced the same serialized result. It does not alone prove the
result is correct. Conversely, two semantically correct floating-point files
need not always be byte-identical across platforms. This project requires both
semantic checks and byte identity in its verified environment, and states that
scope explicitly.

### Misconception check M13: Small tolerance is not a proof

A solver can accurately integrate the wrong equations. The checker therefore
recomputes invariants and analytic formulas from the emitted state columns,
rather than trusting the solver's success flag or stored error columns.

## 15. Numerical study I: 24-state triality transport

### 15.1 State and path

The state contains one vector and two half-spin blocks:

$$
y(t)=(v(t),s_+(t),s_-(t))\in V\mathbin{\oplus}S_+
\mathbin{\oplus}S_-.
$$

Each block has eight real components, so the total dimension is 24. Choose the
Lie-algebra path

$$
X(t)=\frac15E_{01}
+\left(\frac3{20}+\frac{t}{40}\right)E_{14}
+\left(-\frac1{10}+\frac{t}{50}\right)E_{45}
+\frac{t(4-t)}{80}E_{26}.
$$

Indices in this formula are zero-based. The vector generator convention is

$$
(E_{ab})_{ij}=\delta_{ia}\eta_{bj}-\delta_{ib}\eta_{aj},
\qquad 0\le a<b\le7.
$$

The selected generators include compact and split directions and do not all
commute. The three representation matrices act through

$$
\dot v=\rho_v(X)v,
\qquad
\dot s_+=\rho_+(X)s_+,
\qquad
\dot s_-=\rho_-(X)s_-.
$$

All three initial blocks equal `e0`.

### 15.2 Deriving the four invariants

Each representation generator is metric-skew, so the calculation in Section
14 preserves

$$
\langle v,v\rangle,
\qquad
\langle s_+,s_+\rangle,
\qquad
\langle s_-,s_-\rangle.
$$

For the trilinear form, differentiate one slot at a time:

$$
\frac{d}{dt}T(s_+,s_-,v)
=T(\rho_+(X)s_+,s_-,v)
+T(s_+,\rho_-(X)s_-,v)
+T(s_+,s_-,\rho_v(X)v).
$$

The related-triple defining equation is precisely the infinitesimal identity
that makes this sum zero, with signs fixed by the representation convention.
Thus all four quantities should remain at their initial value 1.

### 15.3 Solver configuration

The application uses the pure-Rust SUNDIALS 7.8.0 CVODE implementation with:

```text
method=BDF
nonlinear_iteration=Newton
linear_solver=dense
relative_tolerance=1e-11
absolute_tolerance=1e-13
maximum_step=0.02
integration_interval=[0,4]
output_spacing=0.1
```

Forty intervals plus the initial endpoint give 41 output samples.

### 15.4 Verified result

The canonical run used 237 accepted internal steps and 251 right-hand-side
evaluations. Maximum absolute drifts were:

| Invariant | Maximum drift |
|---|---:|
| vector norm | `1.2915224445464446e-12` |
| plus-spin norm | `3.070876886113183e-12` |
| minus-spin norm | `2.8042013155982204e-12` |
| triality trilinear | `2.9650726318664056e-12` |

All are below the required `1e-8` bound. The checker reloads every CSV row,
recomputes all four quantities from the 24 state columns and the exact tensor,
and reconciles the JSON summary. A repeated release run is byte-identical.

### Verification record V7: Transport

```text
state_dimension=24
sample_count=41
solver_steps=237
rhs_evaluations=251
verdict=SUCCESS
```

### 15.5 What this demonstrates

The study demonstrates that one exact triality triple can drive a common
noncommuting transport while preserving the defining quadratic and trilinear
invariants to much better than the required tolerance. It does not show that
this path is unique, physically realized, or exhaustive.

## 16. Cosmology toolkit: expansion, density, and equation of state

### 16.1 Physical spacetime versus the internal split space

The `(4,4)` quadratic space in the algebraic construction is an internal
8-dimensional real representation space. The homogeneous cosmology uses an
ordinary expanding background with scale factor `a(t)`. The guide does not
identify four negative internal directions with four observed time
directions. Conflating those roles would add a physical claim not present in
the equations.

### 16.2 Scale factor and Hubble rate

In a homogeneous, isotropic background, the scale factor `a(t)` measures
relative spatial expansion. Its logarithmic rate is

$$
H=\frac{1}{a}\frac{da}{dt}.
$$

Set the present scale to `a=1` and define e-fold time

$$
N=\ln a.
$$

Then `dN/dt=H`. Negative `N` describes smaller scale factors in the modeled
past; positive `N` describes larger scale factors in the modeled future.

### 16.3 Density, pressure, and conservation

For a homogeneous component with density `rho` and pressure `p`, define the
equation-of-state parameter `w=p/rho`. Background energy conservation gives

$$
\frac{d\rho}{dN}=-3(1+w)\rho.
$$

Constant `w=0` gives matter-like dilution `rho proportional to a^{-3}`;
constant `w=1/3` gives radiation-like dilution `a^{-4}`; and `w=-1` gives a
constant density.

### 16.4 The CPL parameterization

The Chevallier-Polarski-Linder, or CPL, form is

$$
w(a)=w_0+w_a(1-a).
$$

It is a two-parameter description of a background history, not a microscopic
explanation. Here

$$
w_0=-0.861,\qquad w_a=-0.60.
$$

Solving `w(a)=-1` gives

$$
a=1+\frac{1+w_0}{w_a}=0.7683333333333333.
$$

The model therefore crosses the value `-1` within the integration interval.
That fact makes perturbative stability an important unanswered question.

### 16.5 Dimensionless Friedmann closure

Let `E=H/H0`, where `H0` is the present Hubble rate. With present radiation
and matter fractions `Omega_r0` and `Omega_m0`, the modeled closure equation is

$$
E^2=\Omega_{r0}e^{-4N}+\Omega_{m0}e^{-3N}+\rho.
$$

The spinor-sector density is normalized so that its present value is
`Omega_psi0`. The parameters satisfy

$$
\Omega_{r0}+\Omega_{m0}+\Omega_{\psi0}
=0.00009+0.305+0.69491=1.
$$

This is a flat-background normalization inside the specified model.

### Misconception check M14: A parameterized background is not an observation

Choosing CPL parameters and reconstructing a field that realizes them proves
an internal consistency statement. It does not fit supernovae, microwave
background data, structure growth, or covariance matrices.

## 17. Numerical study II: an 18-state real-spinor background

### 17.1 State and equations

The state is

$$
y=(u,\rho,\psi_0,\ldots,\psi_{15}),
$$

where `u=H0(t-t0)` is dimensionless time and `psi` is a real 16-component
column. Define the positive Euclidean condensate

$$
S=\psi^{\mathsf T}\psi.
$$

Choose

$$
J=\gamma_1^-,
$$

the fifth generator in the ordered Clifford list of Section 6. It satisfies

$$
J^{\mathsf T}=-J,\qquad J^2=-I_{16}.
$$

This generator is odd, so it exchanges `S+` and `S-`. Its exponential is an
ordinary Euclidean rotation on the full 16-dimensional internal module. The
term used here is not a `Spin(4,4)` action, whose infinitesimal generators are
even bivectors, and it is not a transformation of physical spacetime.

The equations are

$$
\frac{du}{dN}=\frac1E,
$$

$$
\frac{d\rho}{dN}=-3[1+w(e^N)]\rho,
$$

$$
\frac{d\psi}{dN}=-\frac32\psi+\frac{U_{,S}}EJ\psi.
$$

The initial state at `N=0` has `rho=Omega_psi0`, `psi_0=1`, all other spinor
components zero, and `u=0`.

### 17.2 Deriving condensate dilution

Differentiate `S`:

$$
\frac{dS}{dN}=2\psi^{\mathsf T}\frac{d\psi}{dN}.
$$

Substitution gives

$$
\frac{dS}{dN}=-3\psi^{\mathsf T}\psi
+2\frac{U_{,S}}E\psi^{\mathsf T}J\psi.
$$

For a real skew matrix, the scalar `psi^T J psi` equals its own negative:

$$
\psi^{\mathsf T}J\psi
=(\psi^{\mathsf T}J\psi)^{\mathsf T}
=\psi^{\mathsf T}J^{\mathsf T}\psi
=-\psi^{\mathsf T}J\psi,
$$

so it is zero. Therefore

$$
\frac{dS}{dN}=-3S,
\qquad
S(N)=e^{-3N}
$$

for `S(0)=1`. The internal rotation changes the spinor's direction but not
this dilution law.

### 17.3 Integrating the CPL density

Insert `a=e^N` into the continuity equation:

$$
\frac{d\ln\rho}{dN}
=-3[1+w_0+w_a(1-e^N)].
$$

Integrate from 0 to `N`:

$$
\ln\frac{\rho(N)}{\Omega_{\psi0}}
=-3(1+w_0+w_a)N-3w_a(1-e^N).
$$

Hence

$$
\rho(N)=\Omega_{\psi0}
\exp\left[-3(1+w_0+w_a)N-3w_a(1-e^N)\right].
$$

This analytic expression is independent of the numerical integrator and is
used as a check.

### 17.4 Reconstructing the potential

Since `S=e^{-3N}`, we have

$$
N=-\frac13\ln S,
\qquad e^N=S^{-1/3}.
$$

Substitution into the analytic density yields

$$
U(S)=\Omega_{\psi0}
S^{1+w_0+w_a}
\exp\left[-3w_a\left(1-S^{-1/3}\right)\right].
$$

The model chooses `rho=U(S)` along the homogeneous solution. Differentiating
this displayed formula supplies the `U_,S` used in the spinor rotation rate.
Nothing is inferred by fitting the numerical trajectory back to an unknown
potential; the potential is reconstructed analytically first and then checked.

### Worked example W16: Present-epoch closure

At `N=0`, `a=1`, `S=1`, and all exponential factors equal 1. Thus

$$
U(1)=\Omega_{\psi0}=0.69491.
$$

The Friedmann expression gives

$$
E(0)^2=0.00009+0.305+0.69491=1,
$$

so `E(0)=1`, as required by normalization to `H0`.

### 17.5 Integration and verified result

CVODE integrates one branch from `N=0` down to `N=-4` and another from `N=0`
up to `N=1`. The branches are reversed and joined so the present sample
appears once. With output spacing `1/240`, the interval length 5 produces
1,201 ordered samples.

The canonical run used 711 accepted steps and 783 right-hand-side evaluations.
The checker recomputes `S` from all 16 field components, then recomputes the
analytic density, potential, equation of state, and Friedmann expression.
Maximum relative errors are:

| Identity | Maximum relative error |
|---|---:|
| condensate dilution | `6.565508926246135e-9` |
| analytic density | `8.67334933419025e-10` |
| potential reconstruction | `7.707676290195425e-9` |
| derived Friedmann-expression consistency | `3.0848480998659325e-11` |

All are below the required `1e-8` bound. Repeated release runs produce
byte-identical CSV and JSON. The Friedmann diagnostic is derived rather than
independent: its numerical-versus-analytic difference is the density
difference after the identical radiation and matter terms cancel.

The output checker requires the dimensionless time `u` to be finite but does
not independently compare it with a numerical quadrature of `1/E`. Therefore
this release makes no separate accuracy claim for `u` beyond successful ODE
integration and finite output.

### Verification record V8: Cosmology

```text
state_dimension=18
integration_interval_in_N=[-4,1]
sample_count=1201
solver_steps=711
rhs_evaluations=783
w_minus_one_crossing_scale=0.7683333333333333
verdict=SUCCESS
```

### 17.6 Scientific boundary

The calculation establishes a homogeneous background realization for the
specified equations. It does not establish stability of perturbations,
causality of an effective description, uniqueness of the potential,
compatibility with all observations, or a microscopic origin. The region with
`w<-1` particularly requires a separate fluctuation and initial-data analysis.

### Misconception check M15: Numerical agreement cannot enlarge the hypotheses

Accurately reproducing the chosen CPL background shows that the equations and
implementation agree. It cannot show that the CPL parameters are preferred by
data or that omitted perturbations are stable.

## 18. Geometry toolkit: curved metrics, frames, and spinors

### 18.1 Coordinate and tangent indices

On a curved manifold, a coordinate basis changes from point to point. Greek
indices such as `mu,nu` label coordinate components. Latin indices such as
`a,b` label a local orthonormal tangent frame. In this project both range from
0 through 7, but they play different roles.

The constant tangent metric is

$$
\eta_{ab}=\operatorname{diag}(1,1,1,1,-1,-1,-1,-1).
$$

The coordinate metric `g_mu nu(x)` may vary with position. A vielbein, also
called an achtbein in eight dimensions, relates them:

$$
g_{\mu\nu}=e_\mu{}^a\eta_{ab}e_\nu{}^b.
$$

This equation does not say that `g` and `eta` are competing metrics. They are
the same bilinear form written in coordinate and orthonormal bases.

### 18.2 The explicit curved split-signature frame

Use coordinates

```text
(x0,x1,x2,x3,t,y1,y2,y3)
```

and a positive function `a(t)`. Choose

$$
e_\mu{}^a=\operatorname{diag}(a,a,a,a,1,a,a,a).
$$

Then

$$
ds^2=a^2\left[(dx^0)^2+(dx^1)^2+(dx^2)^2+(dx^3)^2
-(dy^1)^2-(dy^2)^2-(dy^3)^2\right]-dt^2.
$$

The metric has four positive and four negative directions. A constant-time
slice has signature `(4,3)`, not the positive-definite spatial signature of
ordinary FLRW cosmology.

### Worked example W17: Reconstructing the metric from the frame

The first diagonal entry is

$$
g_{00}=e_0{}^0\eta_{00}e_0{}^0=a\cdot1\cdot a=a^2.
$$

The evolution entry is

$$
g_{44}=e_4{}^4\eta_{44}e_4{}^4=1\cdot(-1)\cdot1=-1.
$$

The final entry is

$$
g_{77}=a\cdot(-1)\cdot a=-a^2.
$$

The off-diagonal entries vanish because both `e` and `eta` are diagonal.

### 18.3 Levi-Civita and spin connections

The torsion-free metric connection has Christoffel symbols

$$
\Gamma^\rho{}_{\mu\nu}
=\frac12g^{\rho\sigma}
(\partial_\mu g_{\nu\sigma}+\partial_\nu g_{\mu\sigma}
-\partial_\sigma g_{\mu\nu}).
$$

Writing `H=adot/a`, the nonzero coefficients for transverse indices `I` are

$$
\Gamma^4{}_{II}=\eta_{II}a\dot a,
\qquad
\Gamma^I{}_{4I}=\Gamma^I{}_{I4}=H.
$$

The vielbein postulate determines the spin connection:

$$
\partial_\mu e_\nu{}^a
-\Gamma^\rho{}_{\mu\nu}e_\rho{}^a
+\omega_\mu{}^a{}_b e_\nu{}^b=0.
$$

The spinor covariant derivative is

$$
D^{LC}_\mu\psi
=\partial_\mu\psi
+\frac18\omega_{\mu ab}[\gamma^a,\gamma^b]\psi.
$$

Both ordered tangent indices are summed. If only `a<b` were summed, the
coefficient would be `1/4`.

### 18.4 The spinor bundle

Assume the manifold admits a spin structure. The real spinor bundle is

$$
\mathcal S=P_{\operatorname{Spin}(4,4)}(M)
\mathbin{\times}_\rho\Delta_{\mathbb R}.
$$

The fiber is the 16-dimensional module constructed in Section 6, and

$$
\Delta_{\mathbb R}=\Delta_+\oplus\Delta_-.
$$

Thus the type-one and type-two eight-component fields are the two chiral
summands of one rank-16 bundle. Exact contraction gives

$$
\gamma^\mu D^{LC}_\mu\psi
=\gamma^4\left(\partial_t+\frac72H\right)\psi
$$

for a homogeneous field.

### Verification record V9: Curved spin geometry

The exact fixture records 21 nonzero Christoffel components and 14 nonzero
lowered spin-connection components. Python checks 16 independent identities,
and Wolfram checks 11, including every component of the vielbein postulate and
the `7H/2` contraction.

### Misconception check M16: A vielbein is not unique

A local `SO(4,4)` transformation changes the frame without changing the
metric. The displayed diagonal frame is a declared gauge choice, not a frame
uniquely forced by `g`.

## 19. Numerical study III: coupled Einstein-spinor gravity

### 19.1 Action and invariant condensate

Define

$$
C=\gamma_1^+\gamma_2^+\gamma_3^+\gamma_4^+,
\qquad
\bar\psi=\psi^{\mathsf T}C,
\qquad
S=\bar\psi\psi.
$$

The classical components commute. The action is

$$
I=\int d^8x\sqrt{|g|}\left[
\frac{R}{2\kappa_8}
+\frac12(\bar\psi\gamma^\mu D^{LC}_\mu\psi
-(D^{LC}_\mu\bar\psi)\gamma^\mu\psi)-V(S)\right].
$$

There is no quintessence scalar and no cosmological constant.

### 19.2 Potential, density, and pressure

Choose

$$
V(S)=\frac1{20}S+\frac{19}{20}S^{1/5}.
$$

For a homogeneous solution,

$$
\rho=V(S),
\qquad
p=SV'(S)-V(S)=-\frac45\frac{19}{20}S^{1/5}.
$$

The linear term has zero pressure. The fractional-power term has equation of
state `-4/5` when considered separately.

### Worked example W18: Present-epoch dark-sector fractions

At `S=1`,

$$
\rho=\frac1{20}+\frac{19}{20}=1,
$$

$$
p=-\frac45\frac{19}{20}=-\frac{19}{25}=-0.76.
$$

The linear fraction is `1/20=0.05`, and the negative-pressure fraction is
`19/20=0.95`.

### 19.3 Reduced field equations

With `kappa_8=21`, the two gravitational equations are

$$
21H^2=\kappa_8\rho,
$$

$$
6\dot H+21H^2=-\kappa_8p.
$$

The spinor equation is

$$
\dot\psi=-\frac72H\psi-V'(S)\gamma^4\psi.
$$

Since `gamma^4` is skew-adjoint for `C`,

$$
\dot S=-7HS,
\qquad S=a^{-7}.
$$

### 19.4 Verified numerical result

The 18-state CVODE solution contains 171 samples on `-0.2 <= t <= 1.5`.
The canonical run uses 1,372 steps and 1,486 right-hand-side evaluations.
Maximum relative condensate, density, and Friedmann errors are below
`7.5e-9`. The acceleration transition is

$$
t=-0.1380052933032450,
\qquad a=0.8631436165767085.
$$

### Verification record V10: Einstein-spinor dynamics

Four exact checks derive the stress and Einstein tensors. Four Rust tests and
24 release checks recompute all thermodynamic fields, both gravitational
equations, all 18 state equations by five-point differences, deterministic
replay, and tighter-tolerance convergence.

### Misconception check M17: Dust-like is not observed dark matter

The linear term has the homogeneous scaling and pressure of dust in seven
transverse dimensions. The calculation does not provide clustering, halos,
particle phenomenology, or a reduction to observed spacetime.

## 20. Weitzenböck connection and teleparallel gravity

### 20.1 Flat connection with torsion

In a selected proper frame, set the inertial tangent connection to zero and
define

$$
\Gamma^\rho{}_{W\,\mu\nu}
=e_a{}^\rho\partial_\mu e_\nu{}^a.
$$

The only nonzero coefficients are

$$
\Gamma^I{}_{W\,4I}=H.
$$

This connection is metric-compatible and has zero curvature, but its torsion

$$
T^\rho{}_{\mu\nu}
=\Gamma^\rho{}_{W\,\mu\nu}-\Gamma^\rho{}_{W\,\nu\mu}
$$

is nonzero:

$$
T^I{}_{4I}=H,
\qquad T^I{}_{I4}=-H.
$$

### 20.2 Contortion and gauge covariance

Define

$$
K^\rho{}_{\mu\nu}
=\Gamma^\rho{}_{W\,\mu\nu}-\Gamma^\rho{}_{LC\,\mu\nu}.
$$

Then `GammaW=GammaLC+K`. The spin lifts satisfy

$$
\Omega_W=\Omega_{LC}+K_{\rm spin}=0
$$

in the selected gauge. A local Lorentz transformation generally produces a
nonzero pure-gauge inertial connection. Therefore zero coefficients do not
mean that the geometric connection or gravity has disappeared.

### Worked example W19: Torsion trace and scalar

Summing the seven transverse torsion components gives

$$
	au_4=T^\nu{}_{4\nu}=7H.
$$

The quadratic torsion scalar evaluates to

$$
\mathbb T=42H^2.
$$

At `H=1`, these are `tau_4=7` and `T=42`.

### 20.3 The teleparallel boundary identity

Exact contraction gives

$$
R_{LC}=14\dot H+56H^2,
$$

$$
B=14\dot H+98H^2,
$$

and therefore

$$
\boxed{R_{LC}=-\mathbb T+B.}
$$

The TEGR action `-T/(2 kappa_8)` differs from the Einstein-Hilbert action by
the boundary divergence `B`.

### 20.4 Hermitian spinor equation

The symmetric spinor action in torsionful geometry yields

$$
\gamma^\mu\left(D^W_\mu+\frac12\tau_\mu\right)\psi
-V'(S)\psi=0.
$$

In the selected gauge `OmegaW=0`, but `tau_4/2=7H/2`. Hence the homogeneous
operator equals the Levi-Civita operator. Simply deleting the canonical spin
connection without retaining the torsion-trace term would not follow from the
action.

### Verification record V11: Weitzenböck geometry

The generator passes 15 exact checks. Independent Python and Wolfram paths
check 21 and 15 identities, including zero curvature, nonzero torsion, raw
spin-connection antisymmetry, contortion, `R=-T+B`, and the Dirac-operator
identity.

### Misconception check M18: TEGR torsion is not an extra dark fluid

In this model torsion rewrites the gravitational sector. Counting it again as
independent matter would double-count the same dynamics.

## 21. Numerical study IV: independent teleparallel spinor dynamics

### 21.1 Independent implementation

The Phase 6 application generates `C` and `gamma^4` directly from exact
fixtures and owns its state, right-hand side, and CVODE setup. It does not call
the Levi-Civita application. Equality of results is therefore tested rather
than built in by delegation.

### 21.2 Emitted teleparallel diagnostics

Every one of the 171 rows records

$$
\dot H,\quad\tau_4,\quad\mathbb T,\quad R_{LC},\quad B,
\quad R_{LC}+\mathbb T-B,
$$

and the difference between the Weitzenböck and Levi-Civita homogeneous Dirac
coefficients.

### Worked example W20: Checking the present boundary identity

At the normalized epoch, `H=1` and `Hdot=-21/25`. Therefore

$$
\mathbb T=42,
$$

$$
R_{LC}=14\left(-\frac{21}{25}\right)+56=\frac{1106}{25},
$$

$$
B=14\left(-\frac{21}{25}\right)+98=\frac{2156}{25}.
$$

Indeed `R_LC+T-B=0` exactly.

### 21.3 Verified equivalence and convergence

All serialized times and 18 state components agree exactly with the canonical
Einstein-spinor output. The maximum floating boundary residual is
`2.842170943040401e-14`, and the Dirac-coefficient residual is zero. The
refined run changes normalized state components by at most
`6.310776406656671e-10`.

### Verification record V12: Teleparallel dynamics

Thirteen exact action and field-equation checks cover three rational
condensates. Seven Rust tests exercise the independently owned solver. Thirty-
four output checks include all state equations, every teleparallel column,
byte replay, baseline comparison, and refined convergence.

### 21.4 Scientific boundary

The linear potential term is dust-like and the fractional term is
negative-pressure-like in the homogeneous model. Neither is identified with
the observed dark sectors. Nonminimal models such as `f(T)`, `f(T,B)`, or
`F(S)T` have different field equations and are not results of this study.

### Misconception check M19: Equivalent backgrounds are not identical geometries

The two connections have different curvature and torsion. Their homogeneous
field equations agree because the actions differ by a boundary term and the
Hermitian spinor equations are related by contortion.

## 22. Reproducibility and independent evidence

### 22.1 Ownership boundaries

The repository separates definitions, generated data, applications, and
presentations:

- `wolfram/` contains exact symbolic definitions and verifiers;
- `artifacts/exact/` contains hash-linked integer and rational tensors;
- `vendor/sundials_rs` is a pinned, read-only solver submodule;
- `studies/` contains application-owned ODE equations;
- `artifacts/` contains canonical numerical CSV and JSON outputs;
- `notebooks/` contains generated Mathematica and Jupyter presentations;
- `dissertation/` contains authoritative Markdown and generated publications;
- `provenance/` contains complete reconstruction commands.

This organization prevents a presentation file from silently becoming the
source of mathematical truth and prevents application behavior from being
hidden inside the solver engine.

### 22.2 Independent exact checks

The Wolfram implementation constructs the exact objects. Separate Python
programs use standard-library integer and rational arithmetic to reconstruct
the defining identities. The Clifford checker rebuilds all ordered monomials,
projectors, commutants, and intertwiner equations. The split-octonion checker
rebuilds Zorn multiplication from dot and cross products. The triality checker
rebuilds the related-triple and automorphism identities from exported tensors.

Agreement between implementations does not create logical independence in an
absolute philosophical sense, but it sharply reduces the chance that one
software-specific simplification or serialization error controls the result.

### 22.3 Numerical checks

Each numerical study is run twice in release mode. A semantic checker reloads
the emitted CSV rather than trusting the summary. It recomputes invariants or
analytic comparison values and checks the summary against them. The two runs
must also serialize to identical bytes in the verified environment.

### 22.4 Publication checks

The Markdown source generates a complete standalone LaTeX document; the TeX
does not include the Markdown at compile time. Three pdfTeX passes stabilize
the table of contents. Volatile timestamps and trailer identifiers are
suppressed. Two isolated builds must be byte-identical, letter-sized, free of
LaTeX warnings, and equal to the pinned canonical hash.

### 22.5 What a hash proves

A SHA-256 digest is a compact fingerprint of bytes. Matching a trusted digest
provides strong evidence that bytes did not change. It does not prove that the
content is mathematically correct. Correctness comes from definitions,
deductions, exhaustive exact checks, numerical comparisons, and review. Hashes
then preserve the reviewed object.

### Misconception check M20: Reproducible is not synonymous with correct

A mistake can be reproduced perfectly. This project combines reproducibility
with independent semantic checks and explicit scientific limitations.

## 23. Claim-to-evidence map and limitations

### 23.1 Exact algebraic claims

- **Faithful Clifford action.** Eight exact generators obey the Clifford
   relations, and 256 ordered monomials have rank 256. This concerns the real
   full Clifford algebra acting on `R^16`.
- **Half-spin decomposition.** The volume projectors have ranks 8 and 8, and
   even elements preserve both images. This concerns the even algebra and spin
   Lie algebra.
- **Representation type.** Even-action ranks are 64, both commutants are
   scalar, and the cross intertwiner space is zero. Inequivalence is for the
   fixed `so(4,4)` labeling.
- **Split multiplication.** Exact unit, conjugation, quadratic identity,
   alternativity, and norm composition checks establish the Zorn algebra in
   the chosen orthogonal basis.
- **Triality.** A cyclic nondegenerate trilinear tensor and 28-dimensional
   related-triple algebra establish the split-real triality structure.
- **Outer action.** Exact order-three and order-two maps generate an `S3`
   representing the outer automorphism group. Its identity is inner; its five
   nonidentity elements are outer and permute inequivalent modules.
- **Compatibility.** A one-dimensional intertwiner space contains a rank-16
   matrix, proving equivalence of the Clifford actions after a basis change.
- **Curved spin geometry.** The complete vielbein postulate, canonical spin
   connection, and rank-16 spinor bundle are checked independently.
- **Teleparallel geometry.** Zero curvature, nonzero torsion, contortion,
   `R_LC=-T+B`, and equality of the homogeneous Hermitian Dirac operators are
   exact tensor identities.

### 23.2 Numerical claims

- **Transport invariants.** Recalculation from all 41 CSV samples gives
   maximum drift below `3.1e-12`, against a required `1e-8` bound.
- **Condensate dilution.** Recalculation from all 16 state components gives
   relative error below `6.6e-9` against `e^(-3N)`.
- **Analytic density.** Comparison with the closed CPL formula gives relative
   error below `8.7e-10`.
- **Potential reconstruction.** Independent substitution of `S` gives
   relative error below `7.8e-9`.
- **Friedmann-expression consistency.** Recomputed radiation, matter, and
   field terms give relative error below `3.1e-11`. This is derived from the
   density comparison, not an independent diagnostic.
- **Deterministic replay.** Two release-mode runs are byte-identical in the
   verified Windows and WSL environment.
- **Einstein-spinor dynamics.** All 18 equations, the two gravitational
   equations, analytic dilution, acceleration transition, and refined
   convergence are checked independently.
- **Teleparallel dynamics.** An independent application reproduces every
   serialized canonical state value while independently emitting and checking
   torsion, boundary, and Dirac-equivalence diagnostics.

### 23.3 Claims deliberately not made

This work does not claim:

1. that internal signature `(4,4)` is observed spacetime signature;
2. that all representations of `Spin(4,4)` of every analytic kind have been
   classified;
3. that the cosmological parameters are a new observational fit;
4. that the homogeneous spinor model is perturbatively stable;
5. that the potential has a unique microscopic origin;
6. that triality explains particle generations;
7. that one numerical trajectory exhausts possible dynamics;
8. that historical notebook outputs constitute proof.
9. that split-signature `(4,4)` is the observed spacetime geometry;
10. that dust-like and negative-pressure terms are observational detections;
11. that TEGR torsion is an additional dark fluid.

### 23.4 Future work

Natural next problems include global integration with explicit centers and
components, orbit and stabilizer classification for null triality triples,
perturbations of the homogeneous background, likelihood analysis with full
observational covariance, geometric field equations connecting the internal
algebra to physical spacetime, and deterministic comparison on additional
platforms, dimensional reduction, and perturbation analysis for both
connection formulations.

## 24. Exercises

The exercises use only material defined in this guide. Complete solutions
follow in Section 25.

### Exercise E1: Bilinear form and null vectors

For `eta=diag(1,1,-1,-1)`, compute the norms of `x=(1,2,1,0)` and
`y=(1,0,1,0)`. Determine whether either vector is null and compute `<x,y>`.

### Exercise E2: Metric-skew conservation

Let `A` satisfy `A^T eta+eta A=0` and let `z'=Az`. Differentiate
`z^T eta z` and prove it is constant.

### Exercise E3: Tensor dimensions

A matrix `A` acts on `R^2` and `B` acts on `R^3`. What size is `A tensor B`?
What is the dimension after four copies of `R^2` are tensored together?

### Exercise E4: Clifford polarization

Starting from `(x+y)^2=n(x+y)1`, use `x^2=n(x)1` and `y^2=n(y)1` to derive
`xy+yx=2<x,y>1`.

### Exercise E5: Ordered monomial count

List all ordered monomials for three generators and verify that there are
`2^3=8`. Then explain why eight generators give 256.

### Exercise E6: Seed matrices

Multiply `P`, `N`, and `G` from Section 6 to verify `P^2=I`, `N^2=-I`, and
`PN=-NP`.

### Exercise E7: Projectors

Assume `omega^2=I`. Prove that `(I+omega)/2` and `(I-omega)/2` are
complementary projectors.

### Exercise E8: Even and odd parity

If `omega gamma_a=-gamma_a omega`, show that a product of two gamma matrices
commutes with `omega`. Explain why all even monomials preserve chirality.

### Exercise E9: Commutant and reducibility

For `R=diag(1,-1)`, solve `CR=RC` for a general 2 by 2 real matrix `C`. Use
the answer to identify invariant subspaces.

### Exercise E10: A split-octonion norm

Using the signature `(4,4)`, compute the norms of `e0+e1`, `e0+e2`, and
`e0+e1+e2-e3`. Verify the norm-composition numbers in Worked example W10.

### Exercise E11: Nonassociativity and alternativity

Use Worked example W11 to show that split-octonion multiplication is not
associative. Explain why this example does not violate either alternative law.

### Exercise E12: Related-triple dimension

Explain why three metric-skew 8 by 8 matrices start with 84 parameters. If the
constraint matrix has rank 56, compute the solution dimension.

### Exercise E13: Six permutation words

Using `r^3=s^2=1` and `srs=r^{-1}`, reduce `rsr`, `r^4`, and `srsr` to the
list `1,r,r^2,s,sr,sr^2`.

### Exercise E14: Trilinear invariance

Differentiate `T(a(t),b(t),c(t))` by the product rule. State the identity the
three representation generators must satisfy for the derivative to vanish.

### Exercise E15: CPL density

Integrate `d ln(rho)/dN=-3[1+w0+wa(1-e^N)]` from 0 to `N` and recover the
formula in Section 17.

### Exercise E16: Condensate dilution

For `psi'=-3psi/2+qJpsi`, where `J^T=-J`, prove that
`S=psi^T psi` satisfies `S'=-3S` for any scalar function `q(N)`.

### Exercise E17: Present closure

Using the three density parameters in Section 16, verify `E(0)=1` and compute
the present value of the reconstructed potential.

### Exercise E18: Error interpretation

The largest transport invariant drift is about `3.1e-12`, while the acceptance
bound is `1e-8`. By roughly how many decimal orders is the observed drift
smaller? Explain why this comparison is useful but is not a proof of the ODE
model's physical validity.

### Exercise E19: Metric from a vielbein

For `eta=diag(1,-1)` and `e=diag(a,1)`, compute `g=e eta e^T`. State its
signature for positive `a`.

### Exercise E20: Torsion trace

Suppose there are seven transverse indices and

$$
T^I{}_{4I}=H,
\qquad
T^I{}_{I4}=-H.
$$

Compute

$$
	au_4=T^\nu{}_{4\nu}.
$$

### Exercise E21: Teleparallel boundary identity

Using `T=42H^2`, `R=14Hdot+56H^2`, and
`B=14Hdot+98H^2`, verify `R=-T+B`.

### Exercise E22: Dust-like and negative-pressure terms

For `V(S)=mS+lambda S^q`, compute `p=SV'(S)-V(S)`. Show that the linear
term has zero pressure and the power term has `w=q-1`.

## 25. Complete solutions

### Solution E1: Bilinear form and null vectors

The norm is `q0^2+q1^2-q2^2-q3^2`. Therefore

$$
n(x)=1+4-1-0=4,
$$

while

$$
n(y)=1+0-1-0=0.
$$

Thus `y` is a nonzero null vector and `x` is not null. The bilinear product is

$$
\langle x,y\rangle=1\cdot1+2\cdot0-1\cdot1-0\cdot0=0.
$$

So `x` and `y` are orthogonal even though `y` is nonzero.

### Solution E2: Metric-skew conservation

Apply the ordinary product rule:

$$
\frac{d}{dt}(z^{\mathsf T}\eta z)
=(z')^{\mathsf T}\eta z+z^{\mathsf T}\eta z'.
$$

Substitute `z'=Az`:

$$
(z')^{\mathsf T}\eta z+z^{\mathsf T}\eta z'
=z^{\mathsf T}A^{\mathsf T}\eta z+z^{\mathsf T}\eta Az
=z^{\mathsf T}(A^{\mathsf T}\eta+\eta A)z=0.
$$

A differentiable function with zero derivative is constant.

### Solution E3: Tensor dimensions

The tensor product space has dimension `2*3=6`, so `A tensor B` is a 6 by 6
matrix. Four copies of a 2-dimensional space have dimension
`2*2*2*2=16`; operators on that space are 16 by 16 matrices.

### Solution E4: Clifford polarization

Expand using distributivity but not commutativity:

$$
(x+y)^2=x^2+xy+yx+y^2.
$$

The quadratic-form polarization identity is

$$
n(x+y)=n(x)+2\langle x,y\rangle+n(y).
$$

Replacing each square by its norm and cancelling `n(x)1` and `n(y)1` leaves

$$
xy+yx=2\langle x,y\rangle1.
$$

### Solution E5: Ordered monomial count

For generators `e1,e2,e3`, the ordered monomials are

```text
1
e1, e2, e3
e1 e2, e1 e3, e2 e3
e1 e2 e3
```

The counts are `1+3+3+1=8`. Each monomial corresponds to a subset of the
generators. Eight generators have `2^8=256` subsets.

### Solution E6: Seed matrices

Direct multiplication gives

$$
P^2=\begin{pmatrix}1&0\\0&1\end{pmatrix},
\qquad
N^2=\begin{pmatrix}-1&0\\0&-1\end{pmatrix}.
$$

Also `PN=-G` and `NP=G`, so `PN=-NP`. These are exact integer products.

### Solution E7: Projectors

Let `P+=(I+omega)/2`. Then

$$
P_+^2=\frac{I+2\omega+\omega^2}{4}
=\frac{2I+2\omega}{4}=P_+.
$$

The same calculation proves `P-^2=P-`. Their product is

$$
P_+P_-=\frac{I-\omega^2}{4}=0,
$$

and their sum is `I`. Hence their images are complementary.

### Solution E8: Even and odd parity

Using anticommutation twice,

$$
\omega\gamma_a\gamma_b
=-\gamma_a\omega\gamma_b
=\gamma_a\gamma_b\omega.
$$

Every additional generator changes the sign once. An even number gives total
sign `+1`, so every even monomial commutes with `omega` and preserves its two
eigenspaces.

### Solution E9: Commutant and reducibility

Write

$$
C=\begin{pmatrix}a&b\\c&d\end{pmatrix}.
$$

Then

$$
CR=\begin{pmatrix}a&-b\\c&-d\end{pmatrix},
\qquad
RC=\begin{pmatrix}a&b\\-c&-d\end{pmatrix}.
$$

Equality forces `b=c=0`, while `a,d` are free. The commutant is the
2-dimensional space of diagonal matrices. The two coordinate axes are proper
invariant subspaces.

### Solution E10: A split-octonion norm

All four basis directions `e0,e1,e2,e3` have positive square. Thus

$$
n(e_0+e_1)=2,
\qquad n(e_0+e_2)=2,
$$

and

$$
n(e_0+e_1+e_2-e_3)=1+1+1+1=4.
$$

Therefore the displayed product has norm `4=2*2`, as required.

### Solution E11: Nonassociativity and alternativity

Worked example W11 gives

$$
(e_1e_2)e_4=e_7\ne-e_7=e_1(e_2e_4),
$$

so associativity fails. The left alternative law repeats the first input,
`(xx)y=x(xy)`, and the right alternative law repeats the second input,
`y(xx)=(yx)x`. The three inputs `e1,e2,e4` are distinct, so neither law claims
the two parenthesizations in W11 are equal.

### Solution E12: Related-triple dimension

A metric-skew 8 by 8 matrix has `8*7/2=28` free parameters. Three such
matrices have `3*28=84`. Rank-nullity gives

$$
84-56=28
$$

free solution parameters.

### Solution E13: Six permutation words

From `srs=r^{-1}=r^2`, multiply on the right by `s` to obtain `sr=r^2s`, or
equivalently `rs=sr^2`. Then

$$
rsr=sr^2r=s,
$$

$$
r^4=r,
$$

and

$$
srsr=r^{-1}r=1.
$$

Each result lies in the six-word normal form.

### Solution E14: Trilinear invariance

Multilinearity gives

$$
\frac{d}{dt}T(a,b,c)=T(a',b,c)+T(a,b',c)+T(a,b,c').
$$

If `a'=rho_1(X)a`, `b'=rho_2(X)b`, and `c'=rho_3(X)c`, invariance requires

$$
T(\rho_1(X)a,b,c)+T(a,\rho_2(X)b,c)
+T(a,b,\rho_3(X)c)=0.
$$

This is the trilinear form of the related-triple infinitesimal identity.

### Solution E15: CPL density

Expand the derivative:

$$
\frac{d\ln\rho}{dN}
=-3(1+w_0+w_a)+3w_a e^N.
$$

Integrating from 0 to `N` gives

$$
\ln\rho(N)-\ln\rho(0)
=-3(1+w_0+w_a)N+3w_a(e^N-1).
$$

Since `rho(0)=Omega_psi0`, exponentiation yields

$$
\rho(N)=\Omega_{\psi0}
\exp[-3(1+w_0+w_a)N-3w_a(1-e^N)].
$$

### Solution E16: Condensate dilution

Differentiate:

$$
S'=2\psi^{\mathsf T}\psi'
=-3\psi^{\mathsf T}\psi+2q\psi^{\mathsf T}J\psi.
$$

Because `J` is skew, the scalar `psi^T J psi` equals its negative and is zero.
Thus `S'=-3S`, independently of the function `q`.

### Solution E17: Present closure

At `N=0`, every exponential is 1 and `rho=Omega_psi0`. Therefore

$$
E(0)^2=0.00009+0.305+0.69491=1.
$$

The expanding branch has `E(0)=1`. Since `S(0)=1`, the reconstructed potential
is

$$
U(1)=\Omega_{\psi0}=0.69491.
$$

### Solution E18: Error interpretation

The ratio is approximately

$$
\frac{10^{-8}}{3.1\mathbin{\cdot}10^{-12}}
\mathrel{\approx}3.2\mathbin{\cdot}10^3.
$$

Thus the measured drift is about three and a half decimal orders smaller than
the acceptance bound. This is strong evidence that the numerical trajectory
respects the encoded invariant. It says nothing by itself about whether the
encoded ODE is a complete or empirically correct physical model.

### Solution E19: Metric from a vielbein

Direct multiplication gives

$$
g=\begin{pmatrix}a&0\\0&1\end{pmatrix}
\begin{pmatrix}1&0\\0&-1\end{pmatrix}
\begin{pmatrix}a&0\\0&1\end{pmatrix}
=\operatorname{diag}(a^2,-1).
$$

For positive `a`, one eigenvalue is positive and one is negative, so the
signature is `(1,1)`.

### Solution E20: Torsion trace

The trace sums one `H` from each transverse direction:

$$
	au_4=\sum_I T^I{}_{4I}=7H.
$$

The components `T^I_(I4)` do not enter this ordering of the trace.

### Solution E21: Teleparallel boundary identity

Substitution gives

$$
-\mathbb T+B=-42H^2+14\dot H+98H^2
=14\dot H+56H^2=R.
$$

Thus the two gravitational Lagrangians differ by the displayed divergence.

### Solution E22: Dust-like and negative-pressure terms

Differentiate:

$$
V'(S)=m+\lambda qS^{q-1}.
$$

Then

$$
p=S(m+\lambda qS^{q-1})-(mS+\lambda S^q)
=(q-1)\lambda S^q.
$$

The `mS` terms cancel, so the linear component has zero pressure. For the
power component, `p_q=(q-1)rho_q`, hence `w_q=q-1`.

## 26. Glossary

### Algebra

A vector space with a bilinear multiplication. Associativity, commutativity,
and the existence of a unit are additional properties, not part of the bare
definition.

### Alternative algebra

An algebra satisfying `(xx)y=x(xy)` and `y(xx)=(yx)x`. Every two-generated
subalgebra is associative.

### Associator

The trilinear expression `[x,y,z]=(xy)z-x(yz)` measuring failure of
associativity.

### Automorphism

An invertible map from a mathematical object to itself that preserves all
specified operations.

### BDF

Backward differentiation formula, an implicit family of numerical methods for
ordinary differential equations, especially useful for stiff systems.

### Bilinear form

A scalar-valued function linear in each of two vector inputs.

### Chirality

The `+1` or `-1` eigenspace label of the Clifford volume element in even
dimension.

### Clifford algebra

The universal associative algebra generated by a quadratic space with
`xy+yx=2<x,y>1`.

### Commutant

All linear maps commuting with every matrix in a given action.

### Commutator

The order-sensitive difference `[A,B]=AB-BA`.

### Contortion

The tensor difference between a metric-compatible torsionful connection and
the Levi-Civita connection: `K=Gamma_W-Gamma_LC` in this guide.

### Complete reducibility

The property that every invariant subspace has an invariant complement, so a
finite-dimensional representation decomposes into irreducible summands.

### Composition algebra

A unital algebra with a nondegenerate quadratic norm satisfying
`n(xy)=n(x)n(y)`.

### Conjugation

A distinguished linear involution reversing products and relating an element
to its trace and norm.

### Deterministic replay

Repeated execution that produces exactly the same serialized bytes in the
specified environment.

### Dynkin diagram

A graph encoding the simple-root geometry of a semisimple Lie algebra.

### E-fold time

The logarithmic scale variable `N=ln(a)` used in cosmology.

### Faithful representation

A representation with zero kernel; distinct algebra elements act by distinct
linear maps.

### Half-spin module

One of the two chiral irreducible modules for the even Clifford algebra in the
present even-dimensional split case.

### Highest weight

A label classifying a finite-dimensional irreducible representation relative
to a chosen positive-root system.

### Indefinite form

A real quadratic form taking both positive and negative values on nonzero
vectors.

### Inner automorphism

An automorphism produced by conjugation inside the relevant group.

### Intertwiner

A linear map `L` satisfying `L rho_1(X)=rho_2(X)L` for all acting elements.

### Invariant

A quantity unchanged along a transformation or differential-equation flow.

### Invariant subspace

A subspace mapped into itself by every operator in a representation.

### Irreducible module

A nonzero module with no invariant subspaces other than zero and itself.

### Lie algebra

A vector space with an antisymmetric bracket satisfying the Jacobi identity;
for matrix Lie algebras the bracket is the commutator.

### Lie group

A group that is also a smooth manifold with smooth multiplication and
inversion.

### Module

A vector space on which an algebra, group, or Lie algebra acts linearly.

### Nondegenerate form

A bilinear form for which `<x,y>=0` for every `y` implies `x=0`.

### Null vector

A nonzero vector whose value under an indefinite quadratic form is zero.

### Octonion

An element of an 8-dimensional alternative composition algebra. The ordinary
real octonions have positive norm; split octonions have signature `(4,4)`.

### Outer automorphism

An automorphism that is not inner.

### Para-product

The product `x star y=bar(x)bar(y)` used to display the cyclic symmetry of a
composition algebra.

### Projector

A linear map `P` satisfying `P^2=P`; it maps onto its image and kills a
complementary subspace.

### Quadratic form

A homogeneous degree-two scalar function, represented here as `x^T M x`.

### Rank

The dimension of the image of a linear map or matrix.

### Related triple

A triple `(A,B,C)` obeying
`A(x star y)=Bx star y+x star Cy` for all inputs.

### Representation

A structure-preserving assignment of linear maps to elements of a group,
algebra, or Lie algebra.

### Signature

The pair `(p,q)` counting positive and negative squares in a diagonalized
nondegenerate real symmetric form.

### Spin group

The even Clifford group that double-covers the identity component of the
special orthogonal group.

### Spin connection

A connection on a spinor bundle obtained by lifting a tangent-frame
connection through the spin representation.

### Spinor

A vector in a module for a spin group or spin Lie algebra. It is not generally
a vector in the defining vector representation.

### Split octonions

The real 8-dimensional composition algebra whose norm has signature `(4,4)`.

### Structure constants

The coefficients `c_ij^k` expressing basis products in a chosen basis.

### Tensor product

A vector space representing bilinear combinations of two vector spaces; its
dimension is the product of their dimensions.

### Triality

The exceptional `D4` symmetry that permutes the vector and two half-spin
8-dimensional representations while preserving a trilinear relation.

### Torsion

The antisymmetric lower-index part of an affine connection,
`T^rho_(mu nu)=Gamma^rho_(mu nu)-Gamma^rho_(nu mu)`.

### Teleparallel equivalent of general relativity

TEGR: a curvature-free, torsion-based formulation whose gravitational action
differs from the Einstein-Hilbert action by a boundary divergence.

### Vielbein

A local orthonormal frame or coframe relating a coordinate metric to a
constant tangent metric by `g=e eta e^T`.

### Volume element

The ordered product of all Clifford generators; in this case its two
eigenspaces define chirality.

### Zorn model

A split-octonion construction using two scalars, two 3-vectors, dot products,
and cross products.

### Weitzenböck connection

A metric-compatible flat connection defined from a frame and a flat inertial
tangent connection; in a proper-frame gauge its inertial coefficients vanish
while its torsion generally does not.

## 27. Notation index

- `R`: the real numbers.
- `V`: the 8-dimensional vector module.
- `S+`, `S-`: the positive and negative half-spin modules.
- `Cl(4,4)`: the real Clifford algebra of signature `(4,4)`.
- `Cl^0(4,4)`: the even Clifford subalgebra.
- `eta`: the diagonal metric with four plus and four minus entries.
- `<x,y>`: the bilinear form `x^T eta y`.
- `n(x)`: the quadratic norm `<x,x>`.
- `P,N,G`: the elementary 2 by 2 seed matrices.
- `gamma_a`: one of the eight 16 by 16 Clifford generators.
- `omega`: the Clifford volume element.
- `P+`, `P-`: the chiral projectors.
- `Sigma_ab`: the spin generator `[gamma_a,gamma_b]/4`.
- `so(4,4)`: the metric-skew 8 by 8 Lie algebra.
- `Spin(4,4)`: the spin group covering the identity orthogonal component.
- `O_s`: the split-octonion algebra.
- `bar(x)`: the split-octonion conjugate.
- `x star y`: the para-product `bar(x)bar(y)`.
- `T(x,y,z)`: the cyclic trilinear form `<x star y,z>`.
- `tri(O_s)`: the related-triple Lie algebra.
- `r,s`: the order-three and order-two triality automorphisms.
- `rho_v,rho_+,rho_-`: the vector and half-spin representations.
- `N`: the cosmological e-fold variable `ln(a)`.
- `a`: the cosmological scale factor.
- `H,E`: the Hubble rate and dimensionless ratio `H/H0`.
- `rho`: the homogeneous modeled density.
- `psi`: the real 16-component homogeneous field.
- `S`: the Euclidean condensate `psi^T psi`.
- `J`: the exact real skew internal rotation satisfying `J^2=-I`.
- `U(S)`: the reconstructed nonlinear potential.
- `w0,wa`: the CPL equation-of-state parameters.
- `g_mu nu`: the curved coordinate metric.
- `e_mu^a`: the vielbein or eight-dimensional coframe.
- `Gamma_LC`: the Levi-Civita affine connection.
- `omega_LC`, `Omega_LC`: the tangent and lifted canonical spin connections.
- `Gamma_W`, `Omega_W`: the Weitzenböck affine and inertial spin connections.
- `K`: the contortion tensor or its spin lift, according to context.
- `tau_mu`: the torsion trace `T^nu_(mu nu)`.
- `mathbb T`: the quadratic torsion scalar.
- `B`: the teleparallel boundary divergence.
- `C`: the invariant split spinor bilinear.
- `bar(psi)`: the real adjoint `psi^T C`.

## 28. Reference capsules and bibliography

The capsules below contain the outside background actually used in the guide.
They make the logical narrative self-contained. The bibliography records where
these ideas entered the literature and where fuller historical treatments can
be found; it is optional further reading, not an assigned prerequisite.

### 28.1 Real Clifford classification capsule

Real Clifford algebras repeat with period eight in signature. A particularly
useful recurrence is

$$
\mathrm{Cl}(p+1,q+1)
\simeq\operatorname{Mat}_2(\mathrm{Cl}(p,q)).
$$

Starting from `Cl(0,0)=R` and applying the recurrence four times gives

$$
\mathrm{Cl}(4,4)
\simeq\operatorname{Mat}_{16}(\mathbb R).
$$

The even algebra can be identified with a neighboring Clifford algebra and, in
this split case, becomes two simple 8 by 8 real matrix blocks:

$$
\mathrm{Cl}^0(4,4)
\simeq\operatorname{Mat}_{8}(\mathbb R)
\mathbin{\oplus}\operatorname{Mat}_{8}(\mathbb R).
$$

A full matrix algebra has one irreducible defining real module up to
equivalence. A direct sum of two full matrix algebras has two irreducible
modules, one supported on each block. This classification predicts the
16-dimensional full module and two 8-dimensional half-spin modules; the exact
rank calculations independently realize and verify them.

### 28.2 Complete reducibility and the commutant capsule

Finite-dimensional representations of a semisimple Lie algebra over a field
of characteristic zero are completely reducible. Therefore any invariant
subspace has an invariant complement. Projection onto a proper summand
commutes with the action and is not scalar. It follows that a scalar-only
commutant implies irreducibility in this setting. Schur's lemma gives the
forward direction: endomorphisms of an irreducible module form a real division
algebra. The computed commutant here is specifically `R`, dimension one.

### 28.3 Highest weights and `D4` capsule

After complexification and a choice of positive roots, every
finite-dimensional irreducible module of a complex semisimple Lie algebra has
a unique dominant integral highest weight. For the split real algebra, the
relevant algebraic real representations are obtained with compatible real
structures. Type `D4` has four fundamental weights: one vector, one adjoint,
and two half-spin weights in the labeling used here. Its diagram automorphism
group permutes the three outer nodes and is isomorphic to `S3`. This is the
classification scope used in Section 8; no assertion about all
infinite-dimensional representations is implied.

### 28.4 Composition algebras and triality capsule

A Hurwitz composition algebra has dimension 1, 2, 4, or 8. Over the reals each
nontrivial dimension has division and split possibilities according to its
quadratic norm. The 8-dimensional split algebra is alternative and has norm
signature `(4,4)`. Its para-product exposes a cyclic trilinear form. Related
triples preserving that product realize `so(4,4)`, and permutations of the
three positions produce the exceptional triality automorphisms. The exact
Zorn and nullspace computations in this project instantiate these structural
theorems without importing a multiplication table on trust.

### 28.5 Numerical ODE capsule

SUNDIALS is a suite of numerical solvers for differential and
algebraic equations. CVODE solves initial-value ODE systems with variable-step,
variable-order Adams or BDF methods. In this project BDF is paired with Newton
iteration and a dense linear solver. Adaptive local error control is combined
with analytic identities, invariant recomputation, output reconciliation, and
deterministic replay. Those added checks are essential because solver success
alone tests neither the model nor the surrounding serialization code.

### 28.6 CPL cosmology capsule

The CPL form `w(a)=w0+wa(1-a)` is a compact two-parameter description of a
possibly varying homogeneous equation of state. Combining it with the
continuity equation gives the analytic density derived in Section 17. It is a
parameterization, not a fundamental field theory. The present work asks a
constructive question: can a specified real homogeneous spinor system realize
that background while satisfying its own analytic identities? It does not use
CPL as evidence that the realization is unique or observationally selected.

### 28.7 Teleparallel gravity capsule

The Levi-Civita connection is metric-compatible and torsion-free, with gravity
encoded in curvature. A Weitzenböck connection can instead be
metric-compatible and curvature-free, with gravity encoded in torsion. In
TEGR, a specific quadratic torsion scalar differs from the Levi-Civita scalar
curvature by a boundary divergence. Covariant teleparallel calculations keep
both the frame and its flat inertial connection; setting the inertial
connection to zero is a gauge choice tied to a proper frame.

### 28.8 Bibliography

1. Elie Cartan, *The Theory of Spinors*, Hermann, 1938; English translation,
   Dover Publications, 1981.
2. Claude Chevalley, *The Algebraic Theory of Spinors and Clifford Algebras*,
   collected works volume 2, Springer, 1997.
3. H. Blaine Lawson, Jr. and Marie-Louise Michelsohn, *Spin Geometry*,
   Princeton University Press, 1989.
4. Tonny A. Springer and Ferdinand D. Veldkamp, *Octonions, Jordan Algebras
   and Exceptional Groups*, Springer Monographs in Mathematics, 2000.
5. John C. Baez, "The Octonions," *Bulletin of the American Mathematical
   Society* 39 (2002), 145-205.
6. Robert L. Bryant, "Submanifolds and Special Structures on the Octonians,"
   *Journal of Differential Geometry* 17 (1982), 185-232. The historical title
   uses the spelling "Octonians."
7. Alan C. Hindmarsh, Peter N. Brown, Keith E. Grant, Steven L. Lee, Radu
   Serban, Dan E. Shumaker, and Carol S. Woodward, "SUNDIALS: Suite of
   Nonlinear and Differential/Algebraic Equation Solvers," *ACM Transactions
   on Mathematical Software* 31 (2005), 363-396.
8. Michel Chevallier and David Polarski, "Accelerating Universes with Scaling
   Dark Matter," *International Journal of Modern Physics D* 10 (2001),
   213-224.
9. Eric V. Linder, "Exploring the Expansion History of the Universe,"
   *Physical Review Letters* 90 (2003), 091301.
10. Ruben Aldrovandi and Jose G. Pereira, *Teleparallel Gravity: An
   Introduction*, Springer, 2013.
11. Martin Krssak et al., "Teleparallel Theories of Gravity: Illuminating a
   Fully Invariant Approach," *Classical and Quantum Gravity* 36 (2019),
   183001.

## 29. Conclusion

Starting with matrices and calculus, we built the full chain of ideas needed
to understand the project. A quadratic form of signature `(4,4)` determines a
Clifford algebra. Eight explicit tensor-product matrices realize it as
`Mat_16(R)`. The volume element splits the spin action into two inequivalent
8-dimensional half-spin modules. Independently, Zorn data defines a split
composition algebra whose para-product supplies a cyclic trilinear form.
Related triples recover `so(4,4)`, and an exact `S3` representing the outer
automorphism group permutes the vector and half-spin modules; its five
nonidentity elements are outer. A rank-16 intertwiner proves that the Clifford
and split-octonion actions are compatible descriptions of the same
representation-theoretic structure.

The numerical studies then use, rather than merely display, the exact tensors.
The 24-state flow preserves the defining triality invariants. The first
18-state spinor system reproduces a derived homogeneous CPL background. The
curved construction distinguishes `eta`, `g`, the vielbein, and the canonical
spin connection. A coupled Einstein-spinor system and an independently coded
Weitzenböck system agree exactly at every serialized state because exact
contortion, boundary, and Hermitian Dirac identities relate their actions.
The linear and fractional potential terms are dust-like and
negative-pressure-like only within this homogeneous split-signature model. In
each case the conclusion is no larger than the hypotheses and checks.

The enduring technique is the combination of independent constructions,
exact finite verification, invariant-based numerical testing, explicit scope,
and reproducible publication. That technique is accessible with elementary
linear algebra once every bridge is made visible, and it remains useful far
beyond this particular example.
