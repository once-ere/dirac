#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
cliffordPath = FileNameJoin[{repositoryRoot, "wolfram", "Cl44.wl"}];
geometryPath = FileNameJoin[{repositoryRoot, "wolfram", "CurvedSpinGeometry.wl"}];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
outputPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{
      repositoryRoot,
      "artifacts",
      "curved-spin-geometry",
      "wolfram-report.json"
    }]
  ]
];

Scan[
  If[!FileExistsQ[#], Print["ERROR: missing package: ", #]; Exit[2]] &,
  {cliffordPath, geometryPath}
];
Quiet[Check[Get[cliffordPath], Print["ERROR: Clifford package load failed"]; Exit[2]]];
Quiet[Check[Get[geometryPath], Print["ERROR: geometry package load failed"]; Exit[2]]];

report = Dirac`CurvedSpinGeometry`CurvedSpinGeometryReport[];
checks = Lookup[report, "checks", <||>];
measurements = Lookup[report, "measurements", <||>];
expectedCheckCount = 11;
failedChecks = Keys[Select[checks, !TrueQ[#] &]];
If[Length[checks] =!= expectedCheckCount,
  AppendTo[failedChecks, "expectedCheckCount"]
];

Scan[
  Print["check_", #, "=", ToLowerCase[ToString[TrueQ[checks[#]]]]] &,
  Keys[checks]
];
Scan[Print["measurement_", #, "=", measurements[#]] &, Keys[measurements]];

output = <|
  "schemaVersion" -> 1,
  "sourceSha256" -> <|
    "Cl44.wl" -> ToLowerCase[IntegerString[FileHash[cliffordPath, "SHA256"], 16, 64]],
    "CurvedSpinGeometry.wl" -> ToLowerCase[IntegerString[FileHash[geometryPath, "SHA256"], 16, 64]]
  |>,
  "checks" -> checks,
  "measurements" -> measurements
|>;
If[!DirectoryQ[DirectoryName[outputPath]],
  CreateDirectory[DirectoryName[outputPath], CreateIntermediateDirectories -> True]
];
Export[outputPath, output, "RawJSON"];
Print["check_count=", Length[checks]];
Print["failed_check_count=", Length[DeleteDuplicates[failedChecks]]];
Print["output=", outputPath];
If[failedChecks =!= {},
  Print["failed_checks=", StringRiffle[DeleteDuplicates[failedChecks], ","]];
  Exit[1]
];
Exit[0];
