#!/usr/bin/env wolframscript

ClearAll["Global`*"];

scriptDirectory = DirectoryName[ExpandFileName[$InputFileName]];
repositoryRoot = ParentDirectory[scriptDirectory];
arguments = Select[Rest[$ScriptCommandLine], # =!= "--" &];
notebookPath = ExpandFileName[
  If[
    Length[arguments] >= 1,
    First[arguments],
    FileNameJoin[{repositoryRoot, "notebooks", "DiracTriality.nb"}]
  ]
];

If[!FileExistsQ[notebookPath],
  Print["ERROR: missing notebook: ", notebookPath];
  Exit[2]
];
notebook = Quiet[Check[Import[notebookPath, "Notebook"], $Failed]];
If[notebook === $Failed || !MatchQ[notebook, _Notebook],
  Print["ERROR: notebook import failed"];
  Exit[2]
];
inputBoxes = Cases[notebook, Cell[BoxData[boxes_], "Input", ___] :> boxes, Infinity];
expectedInputCount = 20;
If[Length[inputBoxes] =!= expectedInputCount,
  Print["ERROR: expected ", expectedInputCount, " input cells, found ", Length[inputBoxes]];
  Exit[1]
];

messages = {};
results = Block[{$DiracRepositoryRoot = repositoryRoot, $MessageList = {}},
  values = Table[
    value = Quiet[Check[
      ReleaseHold[ToExpression[boxes, StandardForm, HoldComplete]],
      $Failed
    ]];
    messages = Join[messages, ToString[#, InputForm] & /@ $MessageList];
    $MessageList = {};
    value,
    {boxes, inputBoxes}
  ];
  values
];
messages = DeleteDuplicates[messages];
failedEvaluationCount = Count[results, $Failed];
checks = If[ValueQ[notebookChecks], notebookChecks, <||>];
failedChecks = Keys[Select[checks, !TrueQ[#] &]];

Print["input_cell_count=", Length[inputBoxes]];
Print["failed_evaluation_count=", failedEvaluationCount];
Print["message_count=", Length[messages]];
Print["notebook_check_count=", Length[checks]];
Print["failed_notebook_check_count=", Length[failedChecks]];
If[messages =!= {}, Print["messages=", StringRiffle[messages, ","]]];
If[failedChecks =!= {}, Print["failed_checks=", StringRiffle[failedChecks, ","]]];

If[
  failedEvaluationCount > 0 || messages =!= {} || Length[checks] =!= 9 || failedChecks =!= {},
  Exit[1]
];
Exit[0];