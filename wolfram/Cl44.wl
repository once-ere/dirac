BeginPackage["Dirac`Cl44`"];

Cl44Metric::usage = "Cl44Metric is diag(1,1,1,1,-1,-1,-1,-1).";
Cl44Generators::usage = "Cl44Generators is the ordered list of eight exact-real 16 by 16 Clifford generators.";
Cl44VolumeElement::usage = "Cl44VolumeElement is the ordered product of the eight Clifford generators.";
Cl44Projectors::usage = "Cl44Projectors contains the two exact rank-eight volume-element projectors.";
Cl44HalfSpinIndices::usage = "Cl44HalfSpinIndices contains the coordinate indices of the two volume-element eigenspaces.";
Cl44SpinGenerators::usage = "Cl44SpinGenerators contains the 28 bivector generators in lexicographic index order.";
Cl44MonomialBasis::usage = "Cl44MonomialBasis contains all 256 ordered Clifford monomials.";
Cl44VerificationReport::usage = "Cl44VerificationReport[] returns exact checks and measurements for the representation.";

Begin["`Private`"];

identity2 = IdentityMatrix[2];
positiveBlock = {{0, 1}, {1, 0}};
negativeBlock = {{0, 1}, {-1, 0}};
gradingBlock = {{1, 0}, {0, -1}};
identity16 = IdentityMatrix[16];

tensorGenerator[slot_Integer, block_List] := Apply[
  KroneckerProduct,
  Join[
    ConstantArray[gradingBlock, slot - 1],
    {block},
    ConstantArray[identity2, 4 - slot]
  ]
];

positiveGenerators = Table[
  tensorGenerator[slot, positiveBlock],
  {slot, 1, 4}
];
negativeGenerators = Table[
  tensorGenerator[slot, negativeBlock],
  {slot, 1, 4}
];

Cl44Metric = DiagonalMatrix[Join[ConstantArray[1, 4], ConstantArray[-1, 4]]];
Cl44Generators = Join[positiveGenerators, negativeGenerators];
Cl44VolumeElement = Apply[Dot, Cl44Generators];
Cl44Projectors = <|
  "Plus" -> (identity16 + Cl44VolumeElement)/2,
  "Minus" -> (identity16 - Cl44VolumeElement)/2
|>;
Cl44HalfSpinIndices = <|
  "Plus" -> Flatten[Position[Diagonal[Cl44VolumeElement], 1]],
  "Minus" -> Flatten[Position[Diagonal[Cl44VolumeElement], -1]]
|>;

spinMatrix[a_Integer, b_Integer] :=
  (Cl44Generators[[a]] . Cl44Generators[[b]] -
    Cl44Generators[[b]] . Cl44Generators[[a]])/4;

spinPairs = Subsets[Range[8], {2}];
spinMatrices = spinMatrix[#[[1]], #[[2]]] & /@ spinPairs;
Cl44SpinGenerators = MapThread[
  <|"indices" -> #1, "matrix" -> #2|> &,
  {spinPairs, spinMatrices}
];

monomialSubsets = Subsets[Range[8]];
Cl44MonomialBasis = Fold[Dot, identity16, Cl44Generators[[#]]] & /@
  monomialSubsets;

zeroMatrixQ[matrix_List] := matrix === ConstantArray[0, Dimensions[matrix]];

commutantDimension[representation_List] := Module[
  {dimension, variables, equations, coefficientMatrix},
  dimension = Length[First[representation]];
  variables = Array[entry, {dimension, dimension}];
  equations = Flatten[
    (# . variables - variables . #) & /@ representation
  ];
  coefficientMatrix = CoefficientArrays[equations, Flatten[variables]][[2]];
  dimension^2 - MatrixRank[coefficientMatrix]
];

intertwinerDimension[left_List, right_List] := Module[
  {dimension, variables, equations, coefficientMatrix},
  dimension = Length[First[left]];
  variables = Array[entry, {dimension, dimension}];
  equations = Flatten[MapThread[#1 . variables - variables . #2 &, {left, right}]];
  coefficientMatrix = CoefficientArrays[equations, Flatten[variables]][[2]];
  dimension^2 - MatrixRank[coefficientMatrix]
];

Cl44VerificationReport[] := Module[
  {
    plusIndices, minusIndices, evenMonomials, plusEvenAction,
    minusEvenAction, plusSpinAction, minusSpinAction, fullRank, evenRank,
    plusEvenRank, minusEvenRank, plusCommutant, minusCommutant,
    intertwiner, checks
  },
  plusIndices = Cl44HalfSpinIndices["Plus"];
  minusIndices = Cl44HalfSpinIndices["Minus"];
  evenMonomials = Pick[Cl44MonomialBasis, EvenQ[Length[#]] & /@ monomialSubsets];
  plusEvenAction = #[[plusIndices, plusIndices]] & /@ evenMonomials;
  minusEvenAction = #[[minusIndices, minusIndices]] & /@ evenMonomials;
  plusSpinAction = #[[plusIndices, plusIndices]] & /@ spinMatrices;
  minusSpinAction = #[[minusIndices, minusIndices]] & /@ spinMatrices;

  fullRank = MatrixRank[Flatten /@ Cl44MonomialBasis];
  evenRank = MatrixRank[Flatten /@ evenMonomials];
  plusEvenRank = MatrixRank[Flatten /@ plusEvenAction];
  minusEvenRank = MatrixRank[Flatten /@ minusEvenAction];
  plusCommutant = commutantDimension[plusSpinAction];
  minusCommutant = commutantDimension[minusSpinAction];
  intertwiner = intertwinerDimension[plusSpinAction, minusSpinAction];

  checks = <|
    "generatorCount" -> Length[Cl44Generators] === 8,
    "generatorDimensions" -> And @@ (Dimensions[#] === {16, 16} & /@ Cl44Generators),
    "integerEntries" -> AllTrue[Flatten[Cl44Generators], IntegerQ],
    "metricSignature" -> Count[Diagonal[Cl44Metric], 1] === 4 &&
      Count[Diagonal[Cl44Metric], -1] === 4,
    "cliffordRelations" -> And @@ Flatten[Table[
      Cl44Generators[[a]] . Cl44Generators[[b]] +
        Cl44Generators[[b]] . Cl44Generators[[a]] ===
        2 Cl44Metric[[a, b]] identity16,
      {a, 1, 8}, {b, 1, 8}
    ]],
    "monomialCount" -> Length[Cl44MonomialBasis] === 256,
    "fullAlgebraRank" -> fullRank === 256,
    "evenAlgebraRank" -> evenRank === 128,
    "volumeElementForm" -> Cl44VolumeElement === Apply[
      KroneckerProduct,
      ConstantArray[gradingBlock, 4]
    ],
    "volumeElementSquare" -> Cl44VolumeElement . Cl44VolumeElement === identity16,
    "volumeOddAnticommutation" -> And @@ (
      zeroMatrixQ[Cl44VolumeElement . # + # . Cl44VolumeElement] & /@
        Cl44Generators
    ),
    "halfSpinDimensions" -> Length[plusIndices] === 8 && Length[minusIndices] === 8,
    "projectorIdentities" -> And[
      Cl44Projectors["Plus"] . Cl44Projectors["Plus"] === Cl44Projectors["Plus"],
      Cl44Projectors["Minus"] . Cl44Projectors["Minus"] === Cl44Projectors["Minus"],
      zeroMatrixQ[Cl44Projectors["Plus"] . Cl44Projectors["Minus"]],
      Cl44Projectors["Plus"] + Cl44Projectors["Minus"] === identity16
    ],
    "projectorRanks" -> MatrixRank[Cl44Projectors["Plus"]] === 8 &&
      MatrixRank[Cl44Projectors["Minus"]] === 8,
    "spinPreservesHalfSpin" -> And @@ (
      zeroMatrixQ[#[[plusIndices, minusIndices]]] &&
        zeroMatrixQ[#[[minusIndices, plusIndices]]] & /@ spinMatrices
    ),
    "oddExchangesHalfSpin" -> And @@ (
      zeroMatrixQ[#[[plusIndices, plusIndices]]] &&
        zeroMatrixQ[#[[minusIndices, minusIndices]]] & /@ Cl44Generators
    ),
    "spinVectorRelations" -> And @@ Flatten[Table[
      spinMatrix[a, b] . Cl44Generators[[c]] -
        Cl44Generators[[c]] . spinMatrix[a, b] ===
        Cl44Metric[[b, c]] Cl44Generators[[a]] -
        Cl44Metric[[a, c]] Cl44Generators[[b]],
      {a, 1, 8}, {b, a + 1, 8}, {c, 1, 8}
    ]],
    "spinLieRelations" -> And @@ Flatten[Table[
      With[
        {
          a = leftPair[[1]], b = leftPair[[2]],
          c = rightPair[[1]], d = rightPair[[2]]
        },
        spinMatrix[a, b] . spinMatrix[c, d] -
          spinMatrix[c, d] . spinMatrix[a, b] ===
          Cl44Metric[[b, c]] spinMatrix[a, d] -
          Cl44Metric[[a, c]] spinMatrix[b, d] -
          Cl44Metric[[b, d]] spinMatrix[a, c] +
          Cl44Metric[[a, d]] spinMatrix[b, c]
      ],
      {leftPair, spinPairs}, {rightPair, spinPairs}
    ]],
    "plusEvenActionRank" -> plusEvenRank === 64,
    "minusEvenActionRank" -> minusEvenRank === 64,
    "plusSpinCommutant" -> plusCommutant === 1,
    "minusSpinCommutant" -> minusCommutant === 1,
    "halfSpinInequivalence" -> intertwiner === 0
  |>;

  <|
    "checks" -> checks,
    "measurements" -> <|
      "generatorCount" -> Length[Cl44Generators],
      "matrixDimension" -> 16,
      "monomialCount" -> Length[Cl44MonomialBasis],
      "fullAlgebraRank" -> fullRank,
      "evenAlgebraRank" -> evenRank,
      "plusProjectorRank" -> MatrixRank[Cl44Projectors["Plus"]],
      "minusProjectorRank" -> MatrixRank[Cl44Projectors["Minus"]],
      "plusEvenActionRank" -> plusEvenRank,
      "minusEvenActionRank" -> minusEvenRank,
      "plusSpinCommutantDimension" -> plusCommutant,
      "minusSpinCommutantDimension" -> minusCommutant,
      "halfSpinIntertwinerDimension" -> intertwiner
    |>
  |>
];

End[];
EndPackage[];