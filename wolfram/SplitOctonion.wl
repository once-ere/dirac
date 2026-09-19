BeginPackage["Dirac`SplitOctonion`"];

SplitOctonionMetric::usage = "SplitOctonionMetric is diag(1,1,1,1,-1,-1,-1,-1).";
SplitOctonionBasis::usage = "SplitOctonionBasis is the ordered orthonormal coordinate basis with the unit first.";
SplitOctonionConjugation::usage = "SplitOctonionConjugation[x] returns the standard split-octonion conjugate.";
SplitOctonionInnerProduct::usage = "SplitOctonionInnerProduct[x,y] returns the split bilinear form.";
SplitOctonionNorm::usage = "SplitOctonionNorm[x] returns the split quadratic norm.";
SplitOctonionProduct::usage = "SplitOctonionProduct[x,y] multiplies two coordinate vectors exactly.";
SplitOctonionParaProduct::usage = "SplitOctonionParaProduct[x,y] returns conjugate(x) conjugate(y).";
SplitOctonionMultiplicationTensor::usage = "SplitOctonionMultiplicationTensor contains the ordinary product structure constants.";
SplitOctonionParaTensor::usage = "SplitOctonionParaTensor contains the para-product structure constants.";
SplitOctonionLeftMatrices::usage = "SplitOctonionLeftMatrices contains left multiplication by each basis vector.";
SplitOctonionRightMatrices::usage = "SplitOctonionRightMatrices contains right multiplication by each basis vector.";
SplitOctonionVerificationReport::usage = "SplitOctonionVerificationReport[] returns exact algebra checks and measurements.";

Begin["`Private`"];

SplitOctonionMetric = DiagonalMatrix[Join[ConstantArray[1, 4], ConstantArray[-1, 4]]];
SplitOctonionBasis = IdentityMatrix[8];

toZorn[coordinates_List] := {
  coordinates[[1]] + coordinates[[5]],
  coordinates[[2 ;; 4]] + coordinates[[6 ;; 8]],
  -coordinates[[2 ;; 4]] + coordinates[[6 ;; 8]],
  coordinates[[1]] - coordinates[[5]]
};

fromZorn[{upperLeft_, upperRight_List, lowerLeft_List, lowerRight_}] := Join[
  {(upperLeft + lowerRight)/2},
  (upperRight - lowerLeft)/2,
  {(upperLeft - lowerRight)/2},
  (upperRight + lowerLeft)/2
];

zornProduct[
  {upperLeft_, upperRight_List, lowerLeft_List, lowerRight_},
  {otherUpperLeft_, otherUpperRight_List, otherLowerLeft_List, otherLowerRight_}
] := {
  upperLeft otherUpperLeft + upperRight . otherLowerLeft,
  upperLeft otherUpperRight + otherLowerRight upperRight -
    Cross[lowerLeft, otherLowerLeft],
  otherUpperLeft lowerLeft + lowerRight otherLowerLeft +
    Cross[upperRight, otherUpperRight],
  lowerLeft . otherUpperRight + lowerRight otherLowerRight
};

SplitOctonionConjugation[coordinates_List] := Join[
  {First[coordinates]},
  -Rest[coordinates]
];

SplitOctonionInnerProduct[left_List, right_List] :=
  left . SplitOctonionMetric . right;

SplitOctonionNorm[coordinates_List] :=
  SplitOctonionInnerProduct[coordinates, coordinates];

SplitOctonionProduct[left_List, right_List] :=
  fromZorn[zornProduct[toZorn[left], toZorn[right]]];

SplitOctonionParaProduct[left_List, right_List] := SplitOctonionProduct[
  SplitOctonionConjugation[left],
  SplitOctonionConjugation[right]
];

SplitOctonionMultiplicationTensor = Table[
  SplitOctonionProduct[SplitOctonionBasis[[left]], SplitOctonionBasis[[right]]],
  {left, 1, 8}, {right, 1, 8}
];
SplitOctonionParaTensor = Table[
  SplitOctonionParaProduct[SplitOctonionBasis[[left]], SplitOctonionBasis[[right]]],
  {left, 1, 8}, {right, 1, 8}
];

SplitOctonionLeftMatrices = Table[
  Transpose[Table[SplitOctonionMultiplicationTensor[[left, right]], {right, 1, 8}]],
  {left, 1, 8}
];
SplitOctonionRightMatrices = Table[
  Transpose[Table[SplitOctonionMultiplicationTensor[[left, right]], {left, 1, 8}]],
  {right, 1, 8}
];

associator[left_List, middle_List, right_List] :=
  SplitOctonionProduct[SplitOctonionProduct[left, middle], right] -
    SplitOctonionProduct[left, SplitOctonionProduct[middle, right]];

zeroVectorQ[vector_List] := And @@ (# === 0 & /@ (Expand /@ vector));

tensorModeRanks[tensor_List] := {
  MatrixRank[Table[Flatten[tensor[[index, All, All]]], {index, 1, 8}]],
  MatrixRank[Table[Flatten[tensor[[All, index, All]]], {index, 1, 8}]],
  MatrixRank[Table[Flatten[tensor[[All, All, index]]], {index, 1, 8}]]
};

SplitOctonionVerificationReport[] := Module[
  {
    genericLeft, genericRight, unit, ordinaryModeRanks, paraModeRanks,
    leftPolarization, rightPolarization, paraTrilinearCyclic, checks
  },
  genericLeft = Array[leftCoordinate, 8];
  genericRight = Array[rightCoordinate, 8];
  unit = SplitOctonionBasis[[1]];
  ordinaryModeRanks = tensorModeRanks[SplitOctonionMultiplicationTensor];
  paraModeRanks = tensorModeRanks[SplitOctonionParaTensor];

  leftPolarization = And @@ Flatten[Table[
    Transpose[SplitOctonionLeftMatrices[[left]]] . SplitOctonionMetric .
        SplitOctonionLeftMatrices[[right]] +
      Transpose[SplitOctonionLeftMatrices[[right]]] . SplitOctonionMetric .
        SplitOctonionLeftMatrices[[left]] ===
      2 SplitOctonionMetric[[left, right]] SplitOctonionMetric,
    {left, 1, 8}, {right, 1, 8}
  ]];
  rightPolarization = And @@ Flatten[Table[
    Transpose[SplitOctonionRightMatrices[[left]]] . SplitOctonionMetric .
        SplitOctonionRightMatrices[[right]] +
      Transpose[SplitOctonionRightMatrices[[right]]] . SplitOctonionMetric .
        SplitOctonionRightMatrices[[left]] ===
      2 SplitOctonionMetric[[left, right]] SplitOctonionMetric,
    {left, 1, 8}, {right, 1, 8}
  ]];
  paraTrilinearCyclic = And @@ Flatten[Table[
    SplitOctonionInnerProduct[
      SplitOctonionParaProduct[SplitOctonionBasis[[left]], SplitOctonionBasis[[right]]],
      SplitOctonionBasis[[third]]
    ] === SplitOctonionInnerProduct[
      SplitOctonionParaProduct[SplitOctonionBasis[[right]], SplitOctonionBasis[[third]]],
      SplitOctonionBasis[[left]]
    ],
    {left, 1, 8}, {right, 1, 8}, {third, 1, 8}
  ]];

  checks = <|
    "basisDimension" -> Dimensions[SplitOctonionBasis] === {8, 8},
    "metricSignature" -> Count[Diagonal[SplitOctonionMetric], 1] === 4 &&
      Count[Diagonal[SplitOctonionMetric], -1] === 4,
    "unit" -> And @@ Flatten[Table[
      SplitOctonionProduct[unit, SplitOctonionBasis[[index]]] === SplitOctonionBasis[[index]] &&
        SplitOctonionProduct[SplitOctonionBasis[[index]], unit] === SplitOctonionBasis[[index]],
      {index, 1, 8}
    ]],
    "conjugationInvolution" -> SplitOctonionConjugation[
      SplitOctonionConjugation[genericLeft]
    ] === genericLeft,
    "conjugationReversal" -> zeroVectorQ[
      SplitOctonionConjugation[SplitOctonionProduct[genericLeft, genericRight]] -
        SplitOctonionProduct[
          SplitOctonionConjugation[genericRight],
          SplitOctonionConjugation[genericLeft]
        ]
    ],
    "quadraticIdentity" -> zeroVectorQ[
      SplitOctonionProduct[genericLeft, SplitOctonionConjugation[genericLeft]] -
        SplitOctonionNorm[genericLeft] unit
    ],
    "normComposition" -> Expand[
      SplitOctonionNorm[SplitOctonionProduct[genericLeft, genericRight]] -
        SplitOctonionNorm[genericLeft] SplitOctonionNorm[genericRight]
    ] === 0,
    "leftAlternative" -> zeroVectorQ[
      associator[genericLeft, genericLeft, genericRight]
    ],
    "rightAlternative" -> zeroVectorQ[
      associator[genericRight, genericLeft, genericLeft]
    ],
    "flexible" -> zeroVectorQ[
      associator[genericLeft, genericRight, genericLeft]
    ],
    "integralStructureConstants" -> AllTrue[
      Flatten[SplitOctonionMultiplicationTensor],
      IntegerQ
    ],
    "leftCompositionPolarization" -> leftPolarization,
    "rightCompositionPolarization" -> rightPolarization,
    "ordinaryTensorNondegenerate" -> ordinaryModeRanks === {8, 8, 8},
    "paraNormComposition" -> Expand[
      SplitOctonionNorm[SplitOctonionParaProduct[genericLeft, genericRight]] -
        SplitOctonionNorm[genericLeft] SplitOctonionNorm[genericRight]
    ] === 0,
    "paraTrilinearCyclic" -> paraTrilinearCyclic,
    "paraTensorNondegenerate" -> paraModeRanks === {8, 8, 8}
  |>;

  <|
    "checks" -> checks,
    "measurements" -> <|
      "basisDimension" -> 8,
      "positiveNormBasisCount" -> Count[Diagonal[SplitOctonionMetric], 1],
      "negativeNormBasisCount" -> Count[Diagonal[SplitOctonionMetric], -1],
      "nonzeroOrdinaryStructureConstants" -> Count[
        Flatten[SplitOctonionMultiplicationTensor],
        Except[0]
      ],
      "nonzeroParaStructureConstants" -> Count[
        Flatten[SplitOctonionParaTensor],
        Except[0]
      ],
      "ordinaryTensorModeRanks" -> ordinaryModeRanks,
      "paraTensorModeRanks" -> paraModeRanks
    |>
  |>
];

End[];
EndPackage[];