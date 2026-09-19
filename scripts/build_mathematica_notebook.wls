#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
outputPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{repositoryRoot, "notebooks", "DiracTriality.nb"}]
  ]
];

inputCell[code_String] := Module[{held, boxes},
  held = ToExpression[code, InputForm, HoldComplete];
  boxes = held /. HoldComplete[expression_] :> ToBoxes[Unevaluated[expression], StandardForm];
  Cell[BoxData[boxes], "Input"]
];

cells = {
  Cell["Real Cl(4,4), Split Octonions, and Triality", "Title"],
  Cell[
    "A generated, executable notebook for the exact-real algebra and the two verified CVODE studies. Historical notebook output is not used.",
    "Text"
  ],
  Cell["Repository setup", "Section"],
  inputCell[
    "repositoryRoot = If[ValueQ[$DiracRepositoryRoot], $DiracRepositoryRoot, ParentDirectory[NotebookDirectory[]]];"
  ],
  inputCell[
    "Scan[Get, FileNameJoin[{repositoryRoot, \"wolfram\", #}] & /@ {\"Cl44.wl\", \"SplitOctonion.wl\", \"Triality44.wl\"}];"
  ],
  Cell["Exact Clifford algebra and half-spin modules", "Section"],
  inputCell["cliffordReport = Dirac`Cl44`Cl44VerificationReport[];"],
  inputCell["cliffordReport[\"measurements\"]"],
  Cell["Split-octonion multiplication", "Section"],
  inputCell["splitReport = Dirac`SplitOctonion`SplitOctonionVerificationReport[];"],
  inputCell["splitReport[\"measurements\"]"],
  inputCell["Dirac`SplitOctonion`SplitOctonionMultiplicationTensor"],
  Cell["Split-real triality", "Section"],
  inputCell["trialityReport = Dirac`Triality44`TrialityVerificationReport[];"],
  inputCell["trialityReport[\"measurements\"]"],
  Cell["Numerical studies", "Section"],
  inputCell[
    "transportSummary = Import[FileNameJoin[{repositoryRoot, \"artifacts\", \"triality-transport\", \"summary.json\"}], \"RawJSON\"];"
  ],
  inputCell[
    "cosmologySummary = Import[FileNameJoin[{repositoryRoot, \"artifacts\", \"spinor-cosmology\", \"summary.json\"}], \"RawJSON\"];"
  ],
  inputCell["{transportSummary, cosmologySummary}"],
  Cell["Fail-fast verification", "Section"],
  inputCell[
    "notebookChecks = <|\"cl44\" -> And @@ Values[cliffordReport[\"checks\"]], \"splitOctonion\" -> And @@ Values[splitReport[\"checks\"]], \"triality\" -> And @@ Values[trialityReport[\"checks\"]], \"transport\" -> transportSummary[\"verdict\"] === \"SUCCESS\", \"cosmology\" -> cosmologySummary[\"verdict\"] === \"SUCCESS\"|>;"
  ],
  inputCell[
    "If[!And @@ Values[notebookChecks], Failure[\"NotebookVerification\", <|\"FailedChecks\" -> Keys[Select[notebookChecks, !TrueQ[#] &]]|>], notebookChecks]"
  ]
};

notebook = Notebook[
  cells,
  WindowTitle -> "Real Cl(4,4), Split Octonions, and Triality",
  StyleDefinitions -> "Default.nb",
  TaggingRules -> <|
    "GeneratedBy" -> "scripts/build_mathematica_notebook.wls",
    "SchemaVersion" -> 1
  |>
];

If[!DirectoryQ[DirectoryName[outputPath]],
  CreateDirectory[DirectoryName[outputPath], CreateIntermediateDirectories -> True]
];
Put[notebook, outputPath];
Print["cell_count=", Length[cells]];
Print["input_cell_count=", Count[cells, Cell[_, "Input", ___]]];
Print["output=", outputPath];
Exit[0];