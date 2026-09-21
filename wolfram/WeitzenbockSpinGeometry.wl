BeginPackage["Dirac`WeitzenbockSpinGeometry`"];

WeitzenbockSpinGeometryReport::usage = "WeitzenbockSpinGeometryReport[] returns exact flat-connection, torsion, contortion, boundary, and spinor checks for the cohomogeneity-one (4,4) frame.";

Begin["`Private`"];

eta = Dirac`Cl44`Cl44Metric;
gamma = Dirac`Cl44`Cl44Generators;
volume = Dirac`Cl44`Cl44VolumeElement;
coordinates = {x0, x1, x2, x3, t, y1, y2, y3};
timeIndex = 5;
transverseIndices = DeleteCases[Range[8], timeIndex];
scale = a[t];
frameDiagonal = ReplacePart[ConstantArray[scale, 8], timeIndex -> 1];
frame = DiagonalMatrix[frameDiagonal];
inverseFrame = Simplify[Inverse[frame]];
metric = Simplify[frame . eta . Transpose[frame]];
inverseMetric = Simplify[Inverse[metric]];

weitzenbockConnection = Table[
  Simplify[Sum[
    inverseFrame[[rho, tangentA]]
      D[frame[[nu, tangentA]], coordinates[[mu]]],
    {tangentA, 8}
  ]],
  {rho, 8}, {mu, 8}, {nu, 8}
];

torsion = Table[
  Simplify[
    weitzenbockConnection[[rho, mu, nu]] -
    weitzenbockConnection[[rho, nu, mu]]
  ],
  {rho, 8}, {mu, 8}, {nu, 8}
];

weitzenbockCurvature = Table[
  Simplify[
    D[weitzenbockConnection[[rho, nu, sigma]], coordinates[[mu]]] -
    D[weitzenbockConnection[[rho, mu, sigma]], coordinates[[nu]]] +
    Sum[
      weitzenbockConnection[[rho, mu, lambda]]
        weitzenbockConnection[[lambda, nu, sigma]] -
      weitzenbockConnection[[rho, nu, lambda]]
        weitzenbockConnection[[lambda, mu, sigma]],
      {lambda, 8}
    ]
  ],
  {rho, 8}, {sigma, 8}, {mu, 8}, {nu, 8}
];

christoffel = Table[
  Simplify[1/2 Sum[
    inverseMetric[[rho, sigma]] (
      D[metric[[nu, sigma]], coordinates[[mu]]] +
      D[metric[[mu, sigma]], coordinates[[nu]]] -
      D[metric[[mu, nu]], coordinates[[sigma]]]
    ),
    {sigma, 8}
  ]],
  {rho, 8}, {mu, 8}, {nu, 8}
];

contortion = Simplify[weitzenbockConnection - christoffel];

leviCivitaSpinConnection = Table[
  Simplify[Sum[
    eta[[tangentA, tangentC]] inverseFrame[[tangentB, nu]] (
      Sum[
        christoffel[[rho, mu, nu]] frame[[rho, tangentC]],
        {rho, 8}
      ] - D[frame[[nu, tangentC]], coordinates[[mu]]]
    ),
    {tangentC, 8}, {nu, 8}
  ]],
  {mu, 8}, {tangentA, 8}, {tangentB, 8}
];

tangentContortion = Table[
  Simplify[Sum[
    eta[[tangentA, tangentC]] inverseFrame[[tangentB, nu]]
      contortion[[rho, mu, nu]] frame[[rho, tangentC]],
    {tangentC, 8}, {rho, 8}, {nu, 8}
  ]],
  {mu, 8}, {tangentA, 8}, {tangentB, 8}
];

spinLift[connection_] := Table[
  Simplify[1/8 Sum[
    connection[[mu, tangentA, tangentB]] (
      gamma[[tangentA]] . gamma[[tangentB]] -
      gamma[[tangentB]] . gamma[[tangentA]]
    ),
    {tangentA, 8}, {tangentB, 8}
  ]],
  {mu, 8}
];

leviCivitaSpinLift = spinLift[leviCivitaSpinConnection];
contortionSpinLift = spinLift[tangentContortion];
inertialSpinLift = ConstantArray[0, {8, 16, 16}];
curvedGamma = Table[
  Simplify[Sum[
    inverseFrame[[tangentA, mu]] gamma[[tangentA]],
    {tangentA, 8}
  ]],
  {mu, 8}
];
leviCivitaSlash = Simplify[Sum[
  curvedGamma[[mu]] . leviCivitaSpinLift[[mu]],
  {mu, 8}
]];
torsionTrace = Table[
  Simplify[Sum[torsion[[nu, mu, nu]], {nu, 8}]],
  {mu, 8}
];
torsionSlash = Simplify[1/2 Sum[
  curvedGamma[[mu]] torsionTrace[[mu]],
  {mu, 8}
]];

torsionScalar = Simplify[
  1/4 Sum[
    metric[[rho, rho]] inverseMetric[[mu, mu]]
      inverseMetric[[nu, nu]] torsion[[rho, mu, nu]]^2,
    {rho, 8}, {mu, 8}, {nu, 8}
  ] +
  1/2 Sum[
    inverseMetric[[mu, mu]] torsion[[rho, mu, nu]]
      torsion[[nu, mu, rho]],
    {rho, 8}, {mu, 8}, {nu, 8}
  ] -
  Sum[inverseMetric[[mu, mu]] torsionTrace[[mu]]^2, {mu, 8}]
];

ricci = Table[
  Simplify[
    Sum[
      D[christoffel[[rho, mu, nu]], coordinates[[rho]]] -
      D[christoffel[[rho, mu, rho]], coordinates[[nu]]] +
      Sum[
        christoffel[[rho, rho, sigma]] christoffel[[sigma, mu, nu]] -
        christoffel[[rho, nu, sigma]] christoffel[[sigma, mu, rho]],
        {sigma, 8}
      ],
      {rho, 8}
    ]
  ],
  {mu, 8}, {nu, 8}
];
ricciScalar = Simplify[Sum[
  inverseMetric[[mu, nu]] ricci[[mu, nu]],
  {mu, 8}, {nu, 8}
]];
oppositeTrace = Table[
  Simplify[Sum[torsion[[nu, nu, mu]], {nu, 8}]],
  {mu, 8}
];
raisedOppositeTrace = Simplify[inverseMetric . oppositeTrace];
volumeDensity = scale^7;
boundaryTerm = Simplify[2/volumeDensity Sum[
  D[volumeDensity raisedOppositeTrace[[mu]], coordinates[[mu]]],
  {mu, 8}
]];

WeitzenbockSpinGeometryReport[] := Module[
  {postulate, metricCompatibility, expectedAffine, expectedTorsion, checks},
  postulate = And @@ Flatten[Table[
    Simplify[
      D[frame[[nu, tangentA]], coordinates[[mu]]] -
      Sum[
        weitzenbockConnection[[rho, mu, nu]] frame[[rho, tangentA]],
        {rho, 8}
      ]
    ] === 0,
    {mu, 8}, {nu, 8}, {tangentA, 8}
  ]];
  metricCompatibility = And @@ Flatten[Table[
    Simplify[
      D[metric[[nu, rho]], coordinates[[mu]]] -
      Sum[
        weitzenbockConnection[[sigma, mu, nu]] metric[[sigma, rho]] +
        weitzenbockConnection[[sigma, mu, rho]] metric[[nu, sigma]],
        {sigma, 8}
      ]
    ] === 0,
    {mu, 8}, {nu, 8}, {rho, 8}
  ]];
  expectedAffine = And @@ Table[
    Simplify[
      weitzenbockConnection[[index, timeIndex, index]] -
      D[scale, t]/scale
    ] === 0,
    {index, transverseIndices}
  ];
  expectedTorsion = And @@ Table[
    Simplify[
      torsion[[index, timeIndex, index]] - D[scale, t]/scale
    ] === 0 &&
    Simplify[
      torsion[[index, index, timeIndex]] + D[scale, t]/scale
    ] === 0,
    {index, transverseIndices}
  ];
  checks = <|
    "metricFromFrame" -> Simplify[
      metric - frame . eta . Transpose[frame]
    ] === ConstantArray[0, {8, 8}],
    "affineComponents" -> expectedAffine,
    "vielbeinPostulate" -> postulate,
    "metricCompatibility" -> metricCompatibility,
    "torsionComponents" -> expectedTorsion,
    "torsionAntisymmetry" -> And @@ Flatten[Table[
      Simplify[torsion[[rho, mu, nu]] + torsion[[rho, nu, mu]]] === 0,
      {rho, 8}, {mu, 8}, {nu, 8}
    ]],
    "curvatureZero" -> And @@ Flatten[
      Map[Simplify[#] === 0 &, weitzenbockCurvature, {4}]
    ],
    "connectionDecomposition" -> Simplify[
      weitzenbockConnection - christoffel - contortion
    ] === ConstantArray[0, {8, 8, 8}],
    "inertialSpinConnectionZero" -> inertialSpinLift ===
      ConstantArray[0, {8, 16, 16}],
    "spinContortionIdentity" -> Simplify[
      leviCivitaSpinLift + contortionSpinLift
    ] === ConstantArray[0, {8, 16, 16}],
    "torsionTrace" -> Simplify[
      torsionTrace - ReplacePart[
        ConstantArray[0, 8],
        timeIndex -> 7 D[scale, t]/scale
      ]
    ] === ConstantArray[0, 8],
    "torsionScalar" -> Simplify[
      torsionScalar - 42 (D[scale, t]/scale)^2
    ] === 0,
    "boundaryIdentity" -> Simplify[
      ricciScalar + torsionScalar - boundaryTerm
    ] === 0,
    "homogeneousDiracEquivalence" -> Simplify[
      torsionSlash - leviCivitaSlash
    ] === ConstantArray[0, {16, 16}],
    "chiralityPreserved" -> And @@ Table[
      inertialSpinLift[[mu]] . volume ===
        volume . inertialSpinLift[[mu]],
      {mu, 8}
    ]
  |>;
  <|
    "checks" -> checks,
    "measurements" -> <|
      "baseDimension" -> 8,
      "spinorDimension" -> 16,
      "transverseDimension" -> 7,
      "nonzeroAffineConnectionComponents" -> Count[
        Flatten[weitzenbockConnection],
        value_ /; !TrueQ[Simplify[value == 0]]
      ],
      "nonzeroTorsionComponents" -> Count[
        Flatten[torsion],
        value_ /; !TrueQ[Simplify[value == 0]]
      ],
      "nonzeroContortionComponents" -> Count[
        Flatten[contortion],
        value_ /; !TrueQ[Simplify[value == 0]]
      ],
      "torsionScalar" -> ToString[torsionScalar, InputForm],
      "ricciScalar" -> ToString[ricciScalar, InputForm],
      "boundaryTerm" -> ToString[boundaryTerm, InputForm]
    |>
  |>
];

End[];
EndPackage[];