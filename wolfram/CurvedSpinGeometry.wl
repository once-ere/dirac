BeginPackage["Dirac`CurvedSpinGeometry`"];

CurvedSpinGeometryReport::usage = "CurvedSpinGeometryReport[] returns exact frame, connection, and spin-bundle checks for the cohomogeneity-one (4,4) metric.";

Begin["`Private`"];

eta = Dirac`Cl44`Cl44Metric;
gamma = Dirac`Cl44`Cl44Generators;
coordinates = {x0, x1, x2, x3, t, y1, y2, y3};
timeIndex = 5;
transverseIndices = DeleteCases[Range[8], timeIndex];
scale = a[t];
frameDiagonal = ReplacePart[ConstantArray[scale, 8], timeIndex -> 1];
frame = DiagonalMatrix[frameDiagonal];
inverseFrame = Simplify[Inverse[frame]];
metric = Simplify[frame . eta . Transpose[frame]];
expectedMetric = DiagonalMatrix[
  MapThread[Times, {Diagonal[eta], frameDiagonal^2}]
];
inverseMetric = Simplify[Inverse[metric]];

christoffel = Table[
  Simplify[
    1/2 Sum[
      inverseMetric[[rho, sigma]] (
        D[metric[[nu, sigma]], coordinates[[mu]]] +
        D[metric[[mu, sigma]], coordinates[[nu]]] -
        D[metric[[mu, nu]], coordinates[[sigma]]]
      ),
      {sigma, 8}
    ]
  ],
  {rho, 8}, {mu, 8}, {nu, 8}
];

spinConnectionRaised = Table[
  Simplify[Sum[
    inverseFrame[[tangentB, nu]] (
      Sum[
        christoffel[[rho, mu, nu]] frame[[rho, tangentA]],
        {rho, 8}
      ] - D[frame[[nu, tangentA]], coordinates[[mu]]]
    ),
    {nu, 8}
  ]],
  {mu, 8}, {tangentA, 8}, {tangentB, 8}
];

spinConnection = Table[
  Simplify[Sum[
    eta[[tangentA, tangentC]]
      spinConnectionRaised[[mu, tangentC, tangentB]],
    {tangentC, 8}
  ]],
  {mu, 8}, {tangentA, 8}, {tangentB, 8}
];

spinMatrices = Table[
  Simplify[1/8 Sum[
    spinConnection[[mu, tangentA, tangentB]] (
      gamma[[tangentA]] . gamma[[tangentB]] -
      gamma[[tangentB]] . gamma[[tangentA]]
    ),
    {tangentA, 8}, {tangentB, 8}
  ]],
  {mu, 8}
];

curvedGamma = Table[
  Simplify[Sum[
    inverseFrame[[tangentA, mu]] gamma[[tangentA]],
    {tangentA, 8}
  ]],
  {mu, 8}
];

slashConnection = Simplify[Sum[
  curvedGamma[[mu]] . spinMatrices[[mu]],
  {mu, 8}
]];

charge = Apply[Dot, Take[gamma, 4]];
volume = Dirac`Cl44`Cl44VolumeElement;

CurvedSpinGeometryReport[] := Module[
  {postulate, expectedChristoffel, expectedSpinConnection, checks},
  postulate = And @@ Flatten[Table[
    Simplify[
      D[frame[[nu, tangentA]], coordinates[[mu]]] -
      Sum[
        christoffel[[rho, mu, nu]] frame[[rho, tangentA]],
        {rho, 8}
      ] + Sum[
        spinConnectionRaised[[mu, tangentA, tangentB]]
          frame[[nu, tangentB]],
        {tangentB, 8}
      ]
    ] === 0,
    {mu, 8}, {nu, 8}, {tangentA, 8}
  ]];
  expectedChristoffel = And @@ Table[
    Simplify[
      christoffel[[timeIndex, index, index]] -
      eta[[index, index]] scale D[scale, t]
    ] === 0 &&
    Simplify[
      christoffel[[index, timeIndex, index]] - D[scale, t]/scale
    ] === 0 &&
    Simplify[
      christoffel[[index, index, timeIndex]] - D[scale, t]/scale
    ] === 0,
    {index, transverseIndices}
  ];
  expectedSpinConnection = And @@ Table[
    Simplify[
      spinConnection[[index, index, timeIndex]] -
      eta[[index, index]] D[scale, t]
    ] === 0 &&
    Simplify[
      spinConnection[[index, timeIndex, index]] +
      eta[[index, index]] D[scale, t]
    ] === 0,
    {index, transverseIndices}
  ];
  checks = <|
    "metricFromFrame" -> Simplify[metric - expectedMetric] === ConstantArray[0, {8, 8}],
    "christoffelComponents" -> expectedChristoffel,
    "spinConnectionComponents" -> expectedSpinConnection,
    "spinConnectionAntisymmetric" -> And @@ Flatten[Table[
      Simplify[
        spinConnection[[mu, tangentA, tangentB]] +
        spinConnection[[mu, tangentB, tangentA]]
      ] === 0,
      {mu, 8}, {tangentA, 8}, {tangentB, 8}
    ]],
    "vielbeinPostulate" -> postulate,
    "chargeSymmetric" -> Transpose[charge] === charge,
    "chargeInvolution" -> charge . charge === IdentityMatrix[16],
    "chargeSignature" -> Sort[Eigenvalues[charge]] === Join[
      ConstantArray[-1, 8],
      ConstantArray[1, 8]
    ],
    "gammaChargeSkew" -> And @@ Table[
      Transpose[gamma[[index]]] . charge === -charge . gamma[[index]],
      {index, 8}
    ],
    "slashConnection" -> Simplify[
      slashConnection - 7 D[scale, t]/(2 scale) gamma[[timeIndex]]
    ] === ConstantArray[0, {16, 16}],
    "connectionPreservesChirality" -> And @@ Table[
      Simplify[spinMatrices[[mu]] . volume - volume . spinMatrices[[mu]]]
        === ConstantArray[0, {16, 16}],
      {mu, 8}
    ]
  |>;
  <|
    "checks" -> checks,
    "measurements" -> <|
      "baseDimension" -> 8,
      "spinorDimension" -> 16,
      "transverseDimension" -> 7,
      "nonzeroChristoffelComponents" -> Count[
        Flatten[christoffel],
        value_ /; !TrueQ[Simplify[value == 0]]
      ],
      "nonzeroSpinConnectionComponents" -> Count[
        Flatten[spinConnection],
        value_ /; !TrueQ[Simplify[value == 0]]
      ]
    |>
  |>
];

End[];
EndPackage[];
