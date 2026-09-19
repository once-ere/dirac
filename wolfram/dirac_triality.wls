#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
outputPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{repositoryRoot, "artifacts", "wolfram", "dirac-triality-report.json"}]
  ]
];

packagePaths = FileNameJoin[{scriptDirectory, #}] & /@ {
  "Cl44.wl", "SplitOctonion.wl", "Triality44.wl"
};
Scan[
  Function[path,
    If[!FileExistsQ[path], Print["ERROR: missing package: ", path]; Exit[2]];
    Quiet[Check[Get[path], Print["ERROR: package load failed: ", path]; Exit[2]]]
  ],
  packagePaths
];

cliffordReport = Dirac`Cl44`Cl44VerificationReport[];
splitReport = Dirac`SplitOctonion`SplitOctonionVerificationReport[];
trialityReport = Dirac`Triality44`TrialityVerificationReport[];
transportSummaryPath = FileNameJoin[{
  repositoryRoot, "artifacts", "triality-transport", "summary.json"
}];
cosmologySummaryPath = FileNameJoin[{
  repositoryRoot, "artifacts", "spinor-cosmology", "summary.json"
}];
If[!FileExistsQ[transportSummaryPath] || !FileExistsQ[cosmologySummaryPath],
  Print["ERROR: numerical summaries are missing"];
  Exit[2]
];
transportSummary = Import[transportSummaryPath, "RawJSON"];
cosmologySummary = Import[cosmologySummaryPath, "RawJSON"];

allChecks = Join[
  Association@KeyValueMap[("cl44." <> #1) -> #2 &, cliffordReport["checks"]],
  Association@KeyValueMap[("split." <> #1) -> #2 &, splitReport["checks"]],
  Association@KeyValueMap[("triality." <> #1) -> #2 &, trialityReport["checks"]],
  <|
    "transport.success" -> Lookup[transportSummary, "verdict", ""] === "SUCCESS",
    "transport.stateDimension" -> Lookup[transportSummary, "stateDimension", 0] === 24,
    "cosmology.success" -> Lookup[cosmologySummary, "verdict", ""] === "SUCCESS",
    "cosmology.stateDimension" -> Lookup[cosmologySummary, "stateDimension", 0] === 18
  |>
];
failedChecks = Keys[Select[allChecks, !TrueQ[#] &]];

report = <|
  "schemaVersion" -> 1,
  "checks" -> allChecks,
  "measurements" -> <|
    "cl44" -> cliffordReport["measurements"],
    "splitOctonion" -> splitReport["measurements"],
    "triality" -> trialityReport["measurements"],
    "transport" -> <|
      "sampleCount" -> transportSummary["sampleCount"],
      "solverSteps" -> transportSummary["solverSteps"],
      "rhsEvaluations" -> transportSummary["rhsEvaluations"],
      "maximumDrift" -> transportSummary["maximumDrift"]
    |>,
    "cosmology" -> <|
      "sampleCount" -> cosmologySummary["sampleCount"],
      "solverSteps" -> cosmologySummary["solverSteps"],
      "rhsEvaluations" -> cosmologySummary["rhsEvaluations"],
      "maximumRelativeError" -> cosmologySummary["maximumRelativeError"]
    |>
  |>,
  "sourceSha256" -> AssociationThread[
    FileNameTake /@ packagePaths,
    ToLowerCase[IntegerString[FileHash[#, "SHA256"], 16, 64]] & /@ packagePaths
  ]
|>;

If[!DirectoryQ[DirectoryName[outputPath]],
  CreateDirectory[DirectoryName[outputPath], CreateIntermediateDirectories -> True]
];
Export[outputPath, report, "RawJSON"];
Print["check_count=", Length[allChecks]];
Print["failed_check_count=", Length[failedChecks]];
Print["output=", outputPath];
If[failedChecks =!= {},
  Print["failed_checks=", StringRiffle[failedChecks, ","]];
  Exit[1]
];
Exit[0];