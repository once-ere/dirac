#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
wolframDirectory = FileNameJoin[{repositoryRoot, "wolfram"}];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
outputPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{repositoryRoot, "artifacts", "exact", "triality44.json"}]
  ]
];

packagePaths = FileNameJoin[{wolframDirectory, #}] & /@ {
  "Cl44.wl", "SplitOctonion.wl", "Triality44.wl"
};
If[!And @@ (FileExistsQ /@ packagePaths),
  Print["ERROR: missing exact package"]; Exit[2]
];
Scan[
  Quiet[Check[Get[#], Print["ERROR: package load failed: ", #]; Exit[2]]] &,
  packagePaths
];

report = Dirac`Triality44`TrialityVerificationReport[];
checks = Lookup[report, "checks", <||>];
measurements = Lookup[report, "measurements", <||>];
expectedCheckCount = 25;
failedChecks = Keys[Select[checks, !TrueQ[#] &]];

Scan[
  Print["check_", #, "=", ToLowerCase[ToString[TrueQ[checks[#]]]]] &,
  Keys[checks]
];
Scan[Print["measurement_", #, "=", measurements[#]] &, Keys[measurements]];
If[Length[checks] =!= expectedCheckCount,
  AppendTo[failedChecks, "expectedCheckCount"]
];

encodeExact[array_List] := Map[{Numerator[#], Denominator[#]} &, array, {-1}];
packageHashes = AssociationThread[
  {"cl44", "splitOctonion", "triality44"},
  ToLowerCase[IntegerString[FileHash[#, "SHA256"], 16, 64]] & /@ packagePaths
];
fixture = <|
  "schemaVersion" -> 1,
  "packageSha256" -> packageHashes,
  "signature" -> {4, 4},
  "lieDimension" -> 28,
  "liePairsZeroBased" -> (
    (# - 1) & /@ Dirac`Triality44`TrialityLiePairs
  ),
  "coefficientBasisRationals" -> encodeExact[
    Dirac`Triality44`TrialityCoefficientBasis
  ],
  "representationsRationals" -> encodeExact[
    Dirac`Triality44`TrialityRepresentations
  ],
  "cyclicAutomorphismRationals" -> encodeExact[
    Dirac`Triality44`TrialityCyclicAutomorphism
  ],
  "reflectionAutomorphismRationals" -> encodeExact[
    Dirac`Triality44`TrialityReflectionAutomorphism
  ],
  "octonionCliffordGenerators" ->
    Dirac`Triality44`TrialityOctonionCliffordGenerators,
  "canonicalCliffordIntertwiner" ->
    Dirac`Triality44`TrialityCliffordIntertwiner,
  "checks" -> checks,
  "measurements" -> measurements
|>;

If[!DirectoryQ[DirectoryName[outputPath]],
  CreateDirectory[DirectoryName[outputPath], CreateIntermediateDirectories -> True]
];
Export[outputPath, fixture, "RawJSON"];

Print["check_count=", Length[checks]];
Print["failed_check_count=", Length[DeleteDuplicates[failedChecks]]];
Print["output=", outputPath];
If[failedChecks =!= {},
  Print["failed_checks=", StringRiffle[DeleteDuplicates[failedChecks], ","]];
  Exit[1]
];
Exit[0];