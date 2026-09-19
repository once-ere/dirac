#!/usr/bin/env python3
"""Convert the authoritative dissertation Markdown to standalone LaTeX."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TITLE = "Real Clifford Algebra, Split Octonions, and Triality in Signature (4,4)"
SUBTITLE = "A reproducible exact and numerical study"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("dissertation/dirac-triality.md"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dissertation/dirac-triality.tex"),
    )
    return parser.parse_args()


def escape_text(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "“": "``",
        "”": "''",
        "–": "--",
        "—": "---",
    }
    return "".join(replacements.get(character, character) for character in value)


def inline_markup(value: str) -> str:
    result: list[str] = []
    index = 0
    while index < len(value):
        if value.startswith("**", index):
            end = value.find("**", index + 2)
            if end >= 0:
                result.append(r"\textbf{" + inline_markup(value[index + 2 : end]) + "}")
                index = end + 2
                continue
        if value[index] == "*":
            end = value.find("*", index + 1)
            if end >= 0:
                result.append(r"\emph{" + inline_markup(value[index + 1 : end]) + "}")
                index = end + 1
                continue
        if value[index] == "`":
            end = value.find("`", index + 1)
            if end >= 0:
                result.append(r"\texttt{\detokenize{" + value[index + 1 : end] + "}}")
                index = end + 1
                continue
        if value[index] == "$":
            end = value.find("$", index + 1)
            if end >= 0:
                result.append(value[index : end + 1])
                index = end + 1
                continue
        next_special = min(
            [
                position
                for position in (
                    value.find("**", index),
                    value.find("*", index),
                    value.find("`", index),
                    value.find("$", index),
                )
                if position >= 0
            ]
            or [len(value)]
        )
        if next_special == index:
            result.append(escape_text(value[index]))
            index += 1
        else:
            result.append(escape_text(value[index:next_special]))
            index = next_special
    return "".join(result)


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def render_table(lines: list[str]) -> list[str]:
    rows = [
        [inline_markup(cell.strip()) for cell in line.strip().strip("|").split("|")]
        for line in lines
        if not is_table_separator(line)
    ]
    columns = len(rows[0])
    width = 0.92 / columns
    specification = "@{}" + "".join(f"p{{{width:.3f}\\linewidth}}" for _ in range(columns)) + "@{}"
    output = [f"\\begin{{longtable}}{{{specification}}}", "\\toprule"]
    output.append(" & ".join(r"\textbf{" + cell + "}" for cell in rows[0]) + r" \\")
    output.append("\\midrule")
    output.append("\\endfirsthead")
    output.append("\\toprule")
    output.append(" & ".join(r"\textbf{" + cell + "}" for cell in rows[0]) + r" \\")
    output.append("\\midrule")
    output.append("\\endhead")
    for row in rows[1:]:
        output.append(" & ".join(row) + r" \\")
    output.extend(["\\bottomrule", "\\end{longtable}"])
    return output


def convert(markdown: str) -> str:
    lines = markdown.splitlines()
    body: list[str] = []
    paragraph: list[str] = []
    in_math = False
    in_code = False
    in_abstract = False
    list_kind: str | None = None
    index = 0

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            body.append(inline_markup(" ".join(line.strip() for line in paragraph)))
            body.append("")
            paragraph = []

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            body.append(f"\\end{{{list_kind}}}")
            body.append("")
            list_kind = None

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            if in_code:
                body.extend(["\\end{Verbatim}", ""])
            else:
                body.append("\\begin{Verbatim}[fontsize=\\small]")
            in_code = not in_code
            index += 1
            continue
        if in_code:
            body.append(line)
            index += 1
            continue
        if stripped == "$$":
            flush_paragraph()
            close_list()
            body.append("\\[" if not in_math else "\\]")
            if in_math:
                body.append("")
            in_math = not in_math
            index += 1
            continue
        if in_math:
            body.append(line)
            index += 1
            continue
        if stripped.startswith("|") and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            flush_paragraph()
            close_list()
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and lines[index].strip().startswith("|"):
                table_lines.append(lines[index])
                index += 1
            body.extend(render_table(table_lines))
            body.append("")
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            text = heading.group(2)
            if in_abstract:
                body.extend(["\\end{abstract}", ""])
                in_abstract = False
            if level == 1 or text == SUBTITLE:
                index += 1
                continue
            if text == "Abstract":
                body.append("\\begin{abstract}")
                in_abstract = True
            elif level == 2:
                body.extend([f"\\section{{{inline_markup(text)}}}", ""])
            elif level == 3:
                body.extend([f"\\subsection{{{inline_markup(text)}}}", ""])
            else:
                body.extend([f"\\subsubsection{{{inline_markup(text)}}}", ""])
            index += 1
            continue
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        unordered = re.match(r"^-\s+(.+)$", stripped)
        if ordered or unordered:
            flush_paragraph()
            wanted = "enumerate" if ordered else "itemize"
            if list_kind != wanted:
                close_list()
                body.append(f"\\begin{{{wanted}}}")
                list_kind = wanted
            body.append("\\item " + inline_markup((ordered or unordered).group(1)))
            index += 1
            continue
        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue
        paragraph.append(line)
        index += 1

    flush_paragraph()
    close_list()
    if in_abstract:
        body.append("\\end{abstract}")

    preamble = rf"""\documentclass[11pt]{{article}}
\usepackage[T1]{{fontenc}}
\usepackage[utf8]{{inputenc}}
\usepackage{{lmodern}}
\usepackage[margin=1in]{{geometry}}
\usepackage{{amsmath,amssymb,mathtools}}
\usepackage{{booktabs,longtable,array}}
\usepackage{{fancyvrb}}
\usepackage[hidelinks]{{hyperref}}
\usepackage{{microtype}}
\pdfobjcompresslevel=0
\pdfinfoomitdate=1
\pdftrailerid{{}}
\pdfsuppressptexinfo=15
\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.65em}}
\setlength{{\emergencystretch}}{{3em}}
\title{{{TITLE}\\[0.5em]\large {SUBTITLE}}}
\author{{Reproducible exact-real implementation}}
\date{{September 2026}}
\begin{{document}}
\maketitle
\tableofcontents
\newpage
"""
    return preamble + "\n".join(body) + "\n\\end{document}\n"


def main() -> int:
    arguments = parse_arguments()
    input_path = arguments.input.resolve()
    output_path = arguments.output.resolve()
    latex = convert(input_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(latex, encoding="utf-8", newline="\n")
    print(f"input={input_path}")
    print(f"output={output_path}")
    print(f"output_bytes={output_path.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())