# Journal Format

Nature Reviews checklist distilled. Follow every item.

## Title

- Max 82 characters including spaces.
- No abbreviations, no acronyms.
- No colon-subtitle format unless unavoidable.
- Convey the main finding or claim, not the method.

## Abstract

- Max 200 words. No references. No citations. No abbreviations.
- Single paragraph, no subheadings.
- Structure: context (1-2 sentences), gap (1 sentence), what this review
  covers (1-2 sentences), key conclusions (1-2 sentences).

## Introduction

- No subheadings. Continuous prose.
- End the introduction with a paragraph stating the scope and structure
  of the review.
- Do not repeat the abstract.

## Heading Levels

Three levels maximum:

1. `\section{}` -- SMALL CAPS, full width rule below
2. `\subsection{}` -- Bold, sentence case
3. `\subsubsection{}` -- Italic, sentence case, run-in

Never use a fourth level. If you need one, restructure.

## References

- Numbered, superscript, in order of appearance.
- Use `natbib` with `numbers,super,sort&compress`.
- `\bibliographystyle{naturemag}`.
- Cite at the end of the clause, before the period: `...mechanism\cite{ref}.`
- Highlight 5-10% of references as "key references" with one-sentence
  annotations in the bibliography section.

## Figure Legends

- Max 200 words per legend.
- Format: `\textbf{Figure N | Title.}` followed by legend text.
- Define every abbreviation used in the figure within the legend.
- State what the axes/colors/symbols represent.
- Cite the data source if not original.

## Glossary

- One sentence per term. No more.
- Place after the introduction or in a sidebar.
- Define only terms that a non-specialist reviewer would not know.

## Key Points Box

- 4-6 bullet points summarizing the review.
- Placed before the abstract or on page 1.
- Note: Nature Reviews Psychology does NOT use Key Points. Omit for that
  journal.

## Competing Interests

- Required. State explicitly even if none.
- Format: "The authors declare no competing interests." or list them.

## Author Contributions

- Required. Use CRediT taxonomy.
- Format: "A.B. conceptualized and wrote the manuscript. C.D. performed
  the database searches."

## Supplementary Information

- Separate file (`si_unified.tex`).
- Numbered sections: SI-0 through SI-9 (see `SI_TEMPLATE.md`).
- Cross-reference from main text: "see Supplementary Table 1".

## Word Counts

| Section | Target |
| --------- | -------- |
| Abstract | 150-200 words |
| Body | 5,000-8,000 words (excluding refs, legends, SI) |
| Figure legends | 150-200 words each |
| Glossary entries | 1 sentence each |

## Checklist Before Submission

1. Title under 82 characters.
2. Abstract under 200 words, no refs, no abbreviations.
3. Introduction has no subheadings.
4. Max 3 heading levels.
5. All abbreviations defined at first use (not in title/abstract).
6. Every figure legend under 200 words with all abbreviations defined.
7. References numbered in order of appearance.
8. Competing interests statement present.
9. Author contributions present.
10. SI cross-referenced from main text.
