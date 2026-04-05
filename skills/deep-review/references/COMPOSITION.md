# Composition

LuaLaTeX compilation pipeline. Never use pdflatex. Never use xelatex.

## Prerequisites

Copy `tufte-swiss.sty` and its companion `.lua` file into the working
directory (from `skills/deep-review/assets/` or the project root). The
style file defines all `\TS*` macros used in the paper skeleton.

## Document Class and Style

```latex
\documentclass[10pt]{article}
\usepackage[nofonts]{tufte-swiss}
```

Use `[nofonts]` mode. This disables the style's default font loading so
you can set fonts manually based on what is installed.

## Font Discovery

Run `fc-list` to find available fonts. Prefer:

| Role | First Choice | Fallback |
| ------ | ------------- | ---------- |
| Body (serif) | Minion Pro | Charter |
| Headings (sans) | Acumin Pro | Aktiv Grotesk |

These are closest to Nature's typographic style.

## Four-Face Rule

Every font family must have exactly four faces loaded:

```latex
\setmainfont{MinionPro-Regular.otf}[
  ItalicFont    = MinionPro-It.otf,
  BoldFont      = MinionPro-Bold.otf,
  BoldItalicFont = MinionPro-BoldIt.otf,
  Numbers       = OldStyle,
]

\setsansfont{AcuminPro-Regular.otf}[
  ItalicFont    = AcuminPro-Italic.otf,
  BoldFont      = AcuminPro-Bold.otf,
  BoldItalicFont = AcuminPro-BoldItalic.otf,
]
```

If a face is missing, LuaLaTeX silently substitutes, producing
inconsistent weight/style. Verify all four exist via `fc-list` before
setting.

## Bibliography

```latex
\usepackage[numbers,super,sort&compress]{natbib}
\bibliographystyle{naturemag}
```

Requires `naturemag.bst` in the working directory or `TEXINPUTS` path.
Download from Nature's author resources if not present.

## Compilation Pipeline

Three `lualatex` passes plus one `bibtex` pass:

```bash
lualatex paper.tex        # Pass 1: generate .aux
bibtex paper               # Process citations
lualatex paper.tex        # Pass 2: resolve refs
lualatex paper.tex        # Pass 3: stable cross-refs
```

Check for warnings after each pass:

- "Citation undefined" after pass 3 = missing `.bib` entry.
- "Label(s) may have changed" = run one more pass.

## Overfull Box Fix

```latex
\setlength{\emergencystretch}{3em}
```

Set in the preamble. Allows TeX to stretch interword spacing slightly
rather than producing overfull hbox warnings. If overfull boxes persist,
rewrite the sentence (shorter words, different line breaks).

## Microtype

```latex
\usepackage{microtype}
```

Enables character protrusion and font expansion for optically even
margins. Works with LuaLaTeX out of the box.

## SI Compilation

The SI (`si_unified.tex`) uses the same preamble and style. Compile
separately or `\input{}` it after `\clearpage` in the main document.
Use `longtable` for the tool call log (it spans multiple pages).

## Troubleshooting

| Problem | Fix |
| --------- | ----- |
| Font not found | Run `fc-list : family style` and update font names |
| Missing .bst | Download `naturemag.bst` from Nature author guidelines |
| Overfull hbox | Increase `\emergencystretch` or rewrite sentence |
| Unicode errors | LuaLaTeX handles UTF-8 natively; check file encoding |
| Slow compilation | LuaLaTeX is slower than pdflatex; this is expected |
| `\TS*` undefined | Ensure `tufte-swiss.sty` is in the working directory |
