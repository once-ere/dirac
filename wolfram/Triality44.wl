BeginPackage[
  "Dirac`Triality44`",
  {"Dirac`Cl44`", "Dirac`SplitOctonion`"}
];

TrialityMetric::usage = "TrialityMetric is the common split metric on the three eight-dimensional modules.";
TrialityLiePairs::usage = "TrialityLiePairs is the lexicographic list of 28 bivector labels.";
TrialityCoefficientBasis::usage = "TrialityCoefficientBasis gives the 28 related triples in the fixed vector-generator basis.";
TrialityBasisTriples::usage = "TrialityBasisTriples gives the three exact 8 by 8 matrices for each related triple.";
TrialityRepresentations::usage = "TrialityRepresentations contains the vector and two half-spin actions.";
TrialityCyclicAutomorphism::usage = "TrialityCyclicAutomorphism is the order-three outer action on the 28-dimensional Lie algebra.";
TrialityReflectionAutomorphism::usage = "TrialityReflectionAutomorphism is the order-two outer action on the 28-dimensional Lie algebra.";
TrialityOctonionCliffordGenerators::usage = "TrialityOctonionCliffordGenerators is the 16-dimensional Clifford representation induced by left multiplication.";
TrialityCliffordIntertwiner::usage = "TrialityCliffordIntertwiner maps the octonion-induced Clifford representation to the canonical seed.";
TrialityVerificationReport::usage = "TrialityVerificationReport[] returns exact triality checks and measurements.";

Begin["`Private`"];

TrialityMetric = Dirac`SplitOctonion`SplitOctonionMetric;
basis = Dirac`SplitOctonion`SplitOctonionBasis;
paraProduct = Dirac`SplitOctonion`SplitOctonionParaProduct;
innerProduct = Dirac`SplitOctonion`SplitOctonionInnerProduct;
leftMatrices = Dirac`SplitOctonion`SplitOctonionLeftMatrices;
canonicalGenerators = Dirac`Cl44`Cl44Generators;
canonicalMetric = Dirac`Cl44`Cl44Metric;
canonicalHalfSpinIndices = Dirac`Cl44`Cl44HalfSpinIndices;
canonicalSpinMatrices = Lookup[Dirac`Cl44`Cl44SpinGenerators, "matrix"];

TrialityLiePairs = Subsets[Range[8], {2}];

vectorGenerator[left_Integer, right_Integer] := Module[
  {leftBasis, rightBasis},
  leftBasis = basis[[left]];
  rightBasis = basis[[right]];
  Outer[Times, leftBasis, TrialityMetric[[right]]] -
    Outer[Times, rightBasis, TrialityMetric[[left]]]
];

soBasis = vectorGenerator[#[[1]], #[[2]]] & /@ TrialityLiePairs;

residualColumn[position_Integer, generator_List] := Flatten[Table[
  Switch[
    position,
    1,
      generator . paraProduct[basis[[left]], basis[[right]]],
    2,
      -paraProduct[generator . basis[[left]], basis[[right]]],
    3,
      -paraProduct[basis[[left]], generator . basis[[right]]]
  ],
  {left, 1, 8}, {right, 1, 8}
]];

constraintColumns = Flatten[
  Table[residualColumn[position, generator], {position, 1, 3}, {generator, soBasis}],
  1
];
constraintMatrix = SparseArray[Transpose[constraintColumns]];
rawCoefficientBasis = NullSpace[constraintMatrix];
rawVectorProjection = rawCoefficientBasis[[All, 1 ;; 28]];
TrialityCoefficientBasis = Inverse[rawVectorProjection] . rawCoefficientBasis;

coefficientMatrix[coefficients_List] := Total[
  MapThread[#1 #2 &, {coefficients, soBasis}]
];

tripleFromCoefficients[coefficients_List] := {
  coefficientMatrix[coefficients[[1 ;; 28]]],
  coefficientMatrix[coefficients[[29 ;; 56]]],
  coefficientMatrix[coefficients[[57 ;; 84]]]
};

TrialityBasisTriples = tripleFromCoefficients /@ TrialityCoefficientBasis;
TrialityRepresentations = Transpose[TrialityBasisTriples];

conjugationSigns = {1, -1, -1, -1, -1, -1, -1, -1};
pairConjugationSigns = Times @@ conjugationSigns[[#]] & /@ TrialityLiePairs;

cyclicCoefficientAction[coefficients_List] := Join[
  coefficients[[29 ;; 56]],
  coefficients[[57 ;; 84]],
  coefficients[[1 ;; 28]]
];

reflectionCoefficientAction[coefficients_List] := Join[
  pairConjugationSigns coefficients[[1 ;; 28]],
  pairConjugationSigns coefficients[[57 ;; 84]],
  pairConjugationSigns coefficients[[29 ;; 56]]
];

coordinatesFromVectorProjection[coefficients_List] := coefficients[[1 ;; 28]];

automorphismMatrix[action_] := Transpose[
  coordinatesFromVectorProjection[action[#]] & /@ TrialityCoefficientBasis
];

TrialityCyclicAutomorphism = automorphismMatrix[cyclicCoefficientAction];
TrialityReflectionAutomorphism = automorphismMatrix[reflectionCoefficientAction];

representationGenerator[representation_List, left_Integer, right_Integer] := Which[
  left === right,
    ConstantArray[0, {8, 8}],
  left < right,
    representation[[First[FirstPosition[TrialityLiePairs, {left, right}]]]],
  True,
    -representationGenerator[representation, right, left]
];

representationLieRelations[representation_List] := And @@ Flatten[Table[
  representationGenerator[representation, left, right] .
      representationGenerator[representation, first, second] -
    representationGenerator[representation, first, second] .
      representationGenerator[representation, left, right] ===
    TrialityMetric[[right, first]] representationGenerator[representation, left, second] -
    TrialityMetric[[left, first]] representationGenerator[representation, right, second] -
    TrialityMetric[[right, second]] representationGenerator[representation, left, first] +
    TrialityMetric[[left, second]] representationGenerator[representation, right, first],
  {left, 1, 8}, {right, left + 1, 8},
  {first, 1, 8}, {second, first + 1, 8}
]];

intertwinerCoefficientMatrix[left_List, right_List] := Module[
  {dimension, variables, equations},
  dimension = Length[First[left]];
  variables = Array[entry, {dimension, dimension}];
  equations = Flatten[MapThread[#1 . variables - variables . #2 &, {left, right}]];
  SparseArray[CoefficientArrays[equations, Flatten[variables]][[2]]]
];

intertwinerDimension[left_List, right_List] := Module[{dimension},
  dimension = Length[First[left]];
  dimension^2 - MatrixRank[intertwinerCoefficientMatrix[left, right]]
];

normalizeIntegerVector[vector_List] := Module[
  {integerVector, divisor, firstNonzero},
  integerVector = Apply[LCM, Denominator /@ vector] vector;
  divisor = Apply[GCD, Abs[Select[integerVector, # =!= 0 &]]];
  integerVector = integerVector/divisor;
  firstNonzero = First[Select[integerVector, # =!= 0 &]];
  If[firstNonzero < 0, -integerVector, integerVector]
];

octonionConjugationSigns = conjugationSigns;
conjugateLeftMatrices = MapThread[#1 #2 &, {octonionConjugationSigns, leftMatrices}];
TrialityOctonionCliffordGenerators = MapThread[
  ArrayFlatten[{{0, #1}, {#2, 0}}] &,
  {conjugateLeftMatrices, leftMatrices}
];

cliffordIntertwinerMatrix = intertwinerCoefficientMatrix[
  canonicalGenerators,
  TrialityOctonionCliffordGenerators
];
cliffordIntertwinerNullSpace = NullSpace[cliffordIntertwinerMatrix];
TrialityCliffordIntertwiner = If[
  Length[cliffordIntertwinerNullSpace] === 1,
  Partition[normalizeIntegerVector[First[cliffordIntertwinerNullSpace]], 16],
  ConstantArray[0, {16, 16}]
];

precomposeRepresentation[representation_List, automorphism_List] := Table[
  Total[MapThread[#1 #2 &, {automorphism[[All, column]], representation}]],
  {column, 1, 28}
];

conjugateRepresentation[representation_List] :=
  DiagonalMatrix[conjugationSigns] . # . DiagonalMatrix[conjugationSigns] & /@
    representation;

canonicalPlusSpin = #[[
    canonicalHalfSpinIndices["Plus"],
    canonicalHalfSpinIndices["Plus"]
  ]] & /@ canonicalSpinMatrices;
canonicalMinusSpin = #[[
    canonicalHalfSpinIndices["Minus"],
    canonicalHalfSpinIndices["Minus"]
  ]] & /@ canonicalSpinMatrices;

exactArrayQ[array_] := AllTrue[Flatten[array], MatchQ[#, _Integer | _Rational] &];

TrialityVerificationReport[] := Module[
  {
    representationCommutants, representationIntertwiners, cyclicClosure,
    reflectionClosure, definingRelation, invariantTrilinear, cyclicMatrix,
    reflectionMatrix, identity28, s3Elements, octonionCliffordRelations,
    halfSpinMatching, checks
  },
  identity28 = IdentityMatrix[28];
  cyclicMatrix = TrialityCyclicAutomorphism;
  reflectionMatrix = TrialityReflectionAutomorphism;

  definingRelation = And @@ Flatten[Table[
    With[
      {
        firstMatrix = TrialityBasisTriples[[triple, 1]],
        secondMatrix = TrialityBasisTriples[[triple, 2]],
        thirdMatrix = TrialityBasisTriples[[triple, 3]]
      },
      firstMatrix . paraProduct[basis[[left]], basis[[right]]] ===
        paraProduct[secondMatrix . basis[[left]], basis[[right]]] +
        paraProduct[basis[[left]], thirdMatrix . basis[[right]]]
    ],
    {triple, 1, 28}, {left, 1, 8}, {right, 1, 8}
  ]];

  invariantTrilinear = And @@ Flatten[Table[
    With[
      {
        firstMatrix = TrialityBasisTriples[[triple, 1]],
        secondMatrix = TrialityBasisTriples[[triple, 2]],
        thirdMatrix = TrialityBasisTriples[[triple, 3]]
      },
      innerProduct[
        paraProduct[secondMatrix . basis[[left]], basis[[right]]],
        basis[[third]]
      ] + innerProduct[
        paraProduct[basis[[left]], thirdMatrix . basis[[right]]],
        basis[[third]]
      ] + innerProduct[
        paraProduct[basis[[left]], basis[[right]]],
        firstMatrix . basis[[third]]
      ] === 0
    ],
    {triple, 1, 28}, {left, 1, 8}, {right, 1, 8}, {third, 1, 8}
  ]];

  cyclicClosure = And @@ (
    constraintMatrix . cyclicCoefficientAction[#] === ConstantArray[0, 512] & /@
      TrialityCoefficientBasis
  );
  reflectionClosure = And @@ (
    constraintMatrix . reflectionCoefficientAction[#] === ConstantArray[0, 512] & /@
      TrialityCoefficientBasis
  );
  representationCommutants = intertwinerDimension[#, #] & /@ TrialityRepresentations;
  representationIntertwiners = {
    intertwinerDimension[TrialityRepresentations[[1]], TrialityRepresentations[[2]]],
    intertwinerDimension[TrialityRepresentations[[1]], TrialityRepresentations[[3]]],
    intertwinerDimension[TrialityRepresentations[[2]], TrialityRepresentations[[3]]]
  };
  octonionCliffordRelations = And @@ Flatten[Table[
    TrialityOctonionCliffordGenerators[[left]] .
        TrialityOctonionCliffordGenerators[[right]] +
      TrialityOctonionCliffordGenerators[[right]] .
        TrialityOctonionCliffordGenerators[[left]] ===
      2 TrialityMetric[[left, right]] IdentityMatrix[16],
    {left, 1, 8}, {right, 1, 8}
  ]];
  halfSpinMatching = {
    {
      intertwinerDimension[TrialityRepresentations[[2]], canonicalPlusSpin],
      intertwinerDimension[TrialityRepresentations[[2]], canonicalMinusSpin]
    },
    {
      intertwinerDimension[TrialityRepresentations[[3]], canonicalPlusSpin],
      intertwinerDimension[TrialityRepresentations[[3]], canonicalMinusSpin]
    }
  };
  s3Elements = DeleteDuplicates[{
    identity28,
    cyclicMatrix,
    MatrixPower[cyclicMatrix, 2],
    reflectionMatrix,
    reflectionMatrix . cyclicMatrix,
    reflectionMatrix . MatrixPower[cyclicMatrix, 2]
  }];

  checks = <|
    "metricAgreement" -> TrialityMetric === canonicalMetric,
    "soBasisCount" -> Length[soBasis] === 28,
    "soMetricSkew" -> And @@ (
      (Transpose[#] . TrialityMetric + TrialityMetric . # ===
        ConstantArray[0, {8, 8}]) & /@ soBasis
    ),
    "trialityDimension" -> Length[TrialityCoefficientBasis] === 28 &&
      MatrixRank[constraintMatrix] === 56,
    "canonicalVectorProjection" ->
      TrialityCoefficientBasis[[All, 1 ;; 28]] === IdentityMatrix[28] &&
      TrialityRepresentations[[1]] === soBasis,
    "exactCoefficientBasis" -> exactArrayQ[TrialityCoefficientBasis],
    "definingRelation" -> definingRelation,
    "projectionIsomorphisms" ->
      (MatrixRank /@ {
        TrialityCoefficientBasis[[All, 1 ;; 28]],
        TrialityCoefficientBasis[[All, 29 ;; 56]],
        TrialityCoefficientBasis[[All, 57 ;; 84]]
      }) === {28, 28, 28},
    "coordinateMetricSkew" -> And @@ (
      (Transpose[#] . TrialityMetric + TrialityMetric . # ===
        ConstantArray[0, {8, 8}]) & /@ Flatten[TrialityRepresentations, 1]
    ),
    "coordinateLieRelations" -> And @@ (
      representationLieRelations /@ TrialityRepresentations
    ),
    "representationCommutants" -> representationCommutants === {1, 1, 1},
    "representationInequivalence" -> representationIntertwiners === {0, 0, 0},
    "invariantTrilinear" -> invariantTrilinear,
    "cyclicClosure" -> cyclicClosure,
    "reflectionClosure" -> reflectionClosure,
    "cyclicOrderThree" -> MatrixPower[cyclicMatrix, 3] === identity28,
    "reflectionOrderTwo" -> MatrixPower[reflectionMatrix, 2] === identity28,
    "s3BraidRelation" -> reflectionMatrix . cyclicMatrix . reflectionMatrix ===
      MatrixPower[cyclicMatrix, 2],
    "s3ElementCount" -> Length[s3Elements] === 6,
    "cyclicPermutesRepresentations" -> And[
      precomposeRepresentation[TrialityRepresentations[[1]], cyclicMatrix] ===
        TrialityRepresentations[[2]],
      precomposeRepresentation[TrialityRepresentations[[2]], cyclicMatrix] ===
        TrialityRepresentations[[3]],
      precomposeRepresentation[TrialityRepresentations[[3]], cyclicMatrix] ===
        TrialityRepresentations[[1]]
    ],
    "reflectionConjugateSwap" -> And[
      precomposeRepresentation[TrialityRepresentations[[1]], reflectionMatrix] ===
        conjugateRepresentation[TrialityRepresentations[[1]]],
      precomposeRepresentation[TrialityRepresentations[[2]], reflectionMatrix] ===
        conjugateRepresentation[TrialityRepresentations[[3]]],
      precomposeRepresentation[TrialityRepresentations[[3]], reflectionMatrix] ===
        conjugateRepresentation[TrialityRepresentations[[2]]]
    ],
    "octonionCliffordRelations" -> octonionCliffordRelations,
    "octonionCliffordIntertwinerUnique" ->
      Length[cliffordIntertwinerNullSpace] === 1,
    "octonionCliffordIntertwinerInvertible" ->
      MatrixRank[TrialityCliffordIntertwiner] === 16 &&
      And @@ MapThread[
        #1 . TrialityCliffordIntertwiner === TrialityCliffordIntertwiner . #2 &,
        {canonicalGenerators, TrialityOctonionCliffordGenerators}
      ],
    "canonicalHalfSpinMatching" ->
      Sort /@ halfSpinMatching === {{0, 1}, {0, 1}} &&
      Total[halfSpinMatching] === {1, 1}
  |>;

  <|
    "checks" -> checks,
    "measurements" -> <|
      "constraintRank" -> MatrixRank[constraintMatrix],
      "trialityDimension" -> Length[TrialityCoefficientBasis],
      "projectionRanks" -> MatrixRank /@ {
        TrialityCoefficientBasis[[All, 1 ;; 28]],
        TrialityCoefficientBasis[[All, 29 ;; 56]],
        TrialityCoefficientBasis[[All, 57 ;; 84]]
      },
      "representationCommutantDimensions" -> representationCommutants,
      "representationIntertwinerDimensions" -> representationIntertwiners,
      "s3ElementCount" -> Length[s3Elements],
      "octonionCliffordIntertwinerDimension" ->
        Length[cliffordIntertwinerNullSpace],
      "octonionCliffordIntertwinerRank" ->
        MatrixRank[TrialityCliffordIntertwiner],
      "canonicalHalfSpinMatchingDimensions" -> halfSpinMatching
    |>
  |>
];

End[];
EndPackage[];