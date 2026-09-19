#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
packagePath = FileNameJoin[{repositoryRoot, "wolfram", "SplitOctonion.wl"}];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
outputPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{repositoryRoot, "artifacts", "exact", "split-octonion.json"}]
  ]
];

If[!FileExistsQ[packagePath],
  Print["ERROR: missing package: ", packagePath];
  Exit[2];
];

Quiet[Check[Get[packagePath], Print["ERROR: package load failed"]; Exit[2]]];

report = Dirac`SplitOctonion`SplitOctonionVerificationReport[];
checks = Lookup[report, "checks", <||>];
measurements = Lookup[report, "measurements", <||>];
expectedCheckCount = 17;
failedChecks = Keys[Select[checks, !TrueQ[#] &]];

Scan[
  Print["check_", #, "=", ToLowerCase[ToString[TrueQ[checks[#]]]]] &,
  Keys[checks]
];
Scan[Print["measurement_", #, "=", measurements[#]] &, Keys[measurements]];

If[Length[checks] =!= expectedCheckCount,
  AppendTo[failedChecks, "expectedCheckCount"]
];

packageHash = ToLowerCase[
  IntegerString[FileHash[packagePath, "SHA256"], 16, 64]
];
fixture = <|
  "schemaVersion" -> 1,
  "packageSha256" -> packageHash,
  "signature" -> {4, 4},
  "basisOrder" -> {
    "unit", "positive-1", "positive-2", "positive-3",
    "negative-0", "negative-1", "negative-2", "negative-3"
  },
  "metric" -> Dirac`SplitOctonion`SplitOctonionMetric,
  "conjugationMatrix" -> DiagonalMatrix[{1, -1, -1, -1, -1, -1, -1, -1}],
  "multiplicationTensor" -> Dirac`SplitOctonion`SplitOctonionMultiplicationTensor,
  "paraMultiplicationTensor" -> Dirac`SplitOctonion`SplitOctonionParaTensor,
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