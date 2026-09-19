#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
manifestPath = ExpandFileName[
  If[Length[arguments] >= 1, First[arguments],
    FileNameJoin[{repositoryRoot, "audit", "source-manifest.json"}]]
];
outputPath = ExpandFileName[
  If[Length[arguments] >= 2, arguments[[2]],
    FileNameJoin[{repositoryRoot, "audit", "wolfram-structure.json"}]]
];

If[!FileExistsQ[manifestPath],
  Print["ERROR: missing source manifest: ", manifestPath];
  Exit[2];
];

manifest = Quiet[Check[Import[manifestPath, "RawJSON"], $Failed]];
If[manifest === $Failed || !AssociationQ[manifest],
  Print["ERROR: source manifest is not valid JSON: ", manifestPath];
  Exit[2];
];

manifestHash = ToLowerCase[IntegerString[FileHash[manifestPath, "SHA256"], 16, 64]];
requiredClasses = {"wolfram-source", "wolfram-notebook"};
records = Select[
  Lookup[manifest, "files", {}],
  MemberQ[requiredClasses, Lookup[#, "auditClass", ""]] &
];

SetAttributes[captureImport, HoldFirst];
captureImport[expression_] := Module[{value, messages},
  Block[{$MessageList = {}},
    value = Quiet[Check[expression, $Failed]];
    messages = DeleteDuplicates[ToString[#, InputForm] & /@ $MessageList];
  ];
  <|"value" -> value, "messages" -> messages|>
];

cellMarkerStyle[line_String] := Module[{matches},
  matches = StringCases[
    StringTrim[line],
    RegularExpression["^\\(\\* ::([^:]+):: \\*\\)$"] -> "$1"
  ];
  If[Length[matches] === 1, First[matches], Missing["NotMarker"]]
];

cellManifestCells[path_String] := Module[
  {lines, currentStyle, buffer, cells, style},
  lines = Import[path, "Lines"];
  currentStyle = Missing["NotStarted"];
  buffer = {};
  cells = {};
  Do[
    style = cellMarkerStyle[line];
    If[MissingQ[style],
      If[!MissingQ[currentStyle], AppendTo[buffer, line]],
      If[!MissingQ[currentStyle],
        AppendTo[cells, {currentStyle, StringRiffle[buffer, "\n"]}]
      ];
      currentStyle = style;
      buffer = {};
    ],
    {line, lines}
  ];
  If[!MissingQ[currentStyle],
    AppendTo[cells, {currentStyle, StringRiffle[buffer, "\n"]}]
  ];
  Select[cells, First[#] =!= "CELLMANIFEST-PART" &]
];

cellManifestFileQ[path_String] := Module[{text},
  text = Quiet[Check[Import[path, "Text"], $Failed]];
  StringQ[text] && StringStartsQ[
    StringTrim[text],
    "(* ::CELLMANIFEST-PART::"
  ]
];

cellManifestImport[path_String] := Module[
  {cells, styles, inputBodies, captures, values, successes, messages},
  cells = cellManifestCells[path];
  styles = First /@ cells;
  inputBodies = Last /@ Select[cells, First[#] === "Input" &];
  captures = captureImport[
    ToExpression[#, InputForm, HoldComplete]
  ] & /@ inputBodies;
  values = Lookup[captures, "value"];
  successes = MatchQ[#, _HoldComplete] & /@ values;
  messages = DeleteDuplicates[Flatten[Lookup[captures, "messages"]]];
  <|
    "value" -> {},
    "messages" -> messages,
    "parsed" -> And @@ successes,
    "details" -> <|
      "parseStrategy" -> "cell-manifest-input-chunks",
      "cellCount" -> Length[cells],
      "styleCounts" -> Association[KeySort[Counts[styles]]],
      "inputCellCount" -> Length[inputBodies],
      "inputParseFailureCount" -> Count[successes, False],
      "topLevelExpressionCount" -> Count[values, _HoldComplete]
    |>
  |>
];

recordPath[record_Association] := FileNameJoin[
  Join[
    {Lookup[record, "rootPath"]},
    StringSplit[Lookup[record, "relativePath"], "/"]
  ]
];

fileDigest[path_String] := ToLowerCase[
  IntegerString[FileHash[path, "SHA256"], 16, 64]
];

initializationCellQ[cell_Cell] := !FreeQ[
  cell,
  HoldPattern[InitializationCell -> True]
];

authoredCellStyles = {
  "Abstract", "Chapter", "Code", "DisplayFormula", "ExternalLanguage",
  "InlineFormula", "Input", "Item", "ItemNumbered", "Program", "Section",
  "Subsection", "Subsubsection", "Subtitle", "Text", "Title"
};

cellStyle[Cell[_, style_String, ___]] := style;

cellBodyText[Cell[body_, ___]] := ToString[
  HoldComplete[body],
  InputForm
];

stringDigest[value_String] := ToLowerCase[
  IntegerString[Hash[value, "SHA256"], 16, 64]
];

singleLinePreview[value_String] := StringTake[
  StringReplace[StringTrim[value], RegularExpression["\\s+"] -> " "],
  UpTo[240]
];

authoredCellRecord[cell_Cell, ordinal_Integer] := Module[
  {bodyText},
  bodyText = cellBodyText[cell];
  <|
    "ordinal" -> ordinal,
    "style" -> cellStyle[cell],
    "bodyCharacterCount" -> StringLength[bodyText],
    "bodySha256" -> stringDigest[bodyText],
    "preview" -> singleLinePreview[bodyText]
  |>
];

notebookDetails[notebook_Notebook] := Module[
  {cells, styles, styleCounts, authoredCells, authoredCellRecords},
  cells = Cases[notebook, _Cell, Infinity];
  styles = Cases[cells, Cell[_, style_String, ___] :> style, {1}];
  styleCounts = Association[KeySort[Counts[styles]]];
  authoredCells = Select[
    cells,
    MemberQ[authoredCellStyles, cellStyle[#]] &
  ];
  authoredCellRecords = MapIndexed[
    authoredCellRecord[#1, First[#2]] &,
    authoredCells
  ];
  <|
    "cellCount" -> Length[cells],
    "cellGroupCount" -> Count[notebook, _CellGroupData, Infinity],
    "styleCounts" -> styleCounts,
    "inputCellCount" -> Total[Lookup[styleCounts, {"Code", "Input"}, 0]],
    "textCellCount" -> Total[
      Lookup[
        styleCounts,
        {"Abstract", "Chapter", "Item", "Section", "Subsection",
          "Subsubsection", "Text", "Title"},
        0
      ]
    ],
    "outputCellCount" -> Total[
      Lookup[styleCounts, {"Echo", "Message", "Output", "Print"}, 0]
    ],
    "messageCellCount" -> Lookup[styleCounts, "Message", 0],
    "initializationCellCount" -> Count[cells, _?initializationCellQ],
    "graphicsExpressionCount" -> Count[
      notebook,
      _Graphics | _Graphics3D | _GraphicsBox | _Graphics3DBox,
      Infinity
    ],
    "compressedDataCount" -> Count[notebook, _CompressedData, Infinity],
    "dynamicModuleCount" -> Count[
      notebook,
      _DynamicModule | _DynamicModuleBox,
      Infinity
    ],
    "authoredCellCount" -> Length[authoredCellRecords],
    "authoredCellStreamSha256" -> stringDigest[
      StringRiffle[Lookup[authoredCellRecords, "bodySha256"], "\n"]
    ],
    "authoredCells" -> authoredCellRecords
  |>
];

sourceDetails[expressions_List] := <|
  "topLevelExpressionCount" -> Length[expressions],
  "heldExpressionCount" -> Count[expressions, _HoldComplete, Infinity]
|>;

auditRecord[record_Association] := Module[
  {path, artifactClass, captured, value, digest, size, parsed, details,
    cellManifest},
  path = recordPath[record];
  artifactClass = Lookup[record, "auditClass"];
  If[!FileExistsQ[path],
    Return[<|
      "logicalPath" -> Lookup[record, "logicalPath"],
      "auditClass" -> artifactClass,
      "parseStatus" -> "missing",
      "messageNames" -> {},
      "hashMatchesManifest" -> False,
      "sizeMatchesManifest" -> False
    |>]
  ];
  cellManifest = artifactClass === "wolfram-source" && cellManifestFileQ[path];
  captured = Which[
    artifactClass === "wolfram-notebook",
      captureImport[Import[path, "Notebook"]],
    cellManifest,
      cellManifestImport[path],
    True,
      captureImport[Import[path, "HeldExpressions"]]
  ];
  value = Lookup[captured, "value"];
  parsed = Which[
    cellManifest, Lookup[captured, "parsed", False],
    artifactClass === "wolfram-notebook", MatchQ[value, _Notebook],
    True, ListQ[value] && AllTrue[value, MatchQ[#, _HoldComplete] &]
  ];
  details = Which[
    cellManifest, Lookup[captured, "details", <||>],
    parsed && artifactClass === "wolfram-notebook", notebookDetails[value],
    parsed && artifactClass === "wolfram-source", sourceDetails[value],
    True, <||>
  ];
  digest = fileDigest[path];
  size = FileByteCount[path];
  Join[
    <|
      "logicalPath" -> Lookup[record, "logicalPath"],
      "rootId" -> Lookup[record, "rootId"],
      "relativePath" -> Lookup[record, "relativePath"],
      "auditClass" -> artifactClass,
      "parseStatus" -> If[parsed, "parsed", "failed"],
      "messageNames" -> Lookup[captured, "messages"],
      "messageCount" -> Length[Lookup[captured, "messages"]],
      "sha256" -> digest,
      "hashMatchesManifest" -> (digest === Lookup[record, "sha256"]),
      "size" -> size,
      "sizeMatchesManifest" -> (size === Lookup[record, "size"])
    |>,
    details
  ]
];

results = MapIndexed[
  Function[{record, index},
    result = auditRecord[record];
    Print[
      "artifact=", First[index], "/", Length[records],
      " status=", Lookup[result, "parseStatus"],
      " path=", Lookup[result, "logicalPath"]
    ];
    result
  ],
  records
];

parseFailures = Count[Lookup[results, "parseStatus"], Except["parsed"]];
messageFiles = Count[Lookup[results, "messageCount", 0], value_ /; value > 0];
hashFailures = Count[Lookup[results, "hashMatchesManifest"], False];
sizeFailures = Count[Lookup[results, "sizeMatchesManifest"], False];
report = <|
  "schemaVersion" -> 1,
  "sourceManifestSha256" -> manifestHash,
  "summary" -> <|
    "artifactCount" -> Length[results],
    "sourceCount" -> Count[Lookup[results, "auditClass"], "wolfram-source"],
    "notebookCount" -> Count[
      Lookup[results, "auditClass"],
      "wolfram-notebook"
    ],
    "parseFailureCount" -> parseFailures,
    "filesWithMessages" -> messageFiles,
    "hashFailureCount" -> hashFailures,
    "sizeFailureCount" -> sizeFailures
  |>,
  "files" -> results
|>;

If[!DirectoryQ[DirectoryName[outputPath]],
  CreateDirectory[
    DirectoryName[outputPath],
    CreateIntermediateDirectories -> True
  ]
];
Export[outputPath, report, "RawJSON"];
Print["artifacts=", Length[results]];
Print["parse_failures=", parseFailures];
Print["files_with_messages=", messageFiles];
Print["hash_failures=", hashFailures];
Print["size_failures=", sizeFailures];
Print["output=", outputPath];

If[parseFailures + hashFailures + sizeFailures > 0, Exit[1]];
Exit[0];