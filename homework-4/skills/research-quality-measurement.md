# Skill: Research Quality Measurement

Use this rubric when verifying `codebase-research.md`.

## Quality Levels
- `A - Reliable`: All claims verified; references and snippets accurate; no material gaps.
- `B - Mostly Reliable`: Minor reference/snippet drift; no incorrect root-cause conclusions.
- `C - Risky`: Multiple mismatches or weak evidence that could mislead planning.
- `D - Unreliable`: Core claims unsupported or incorrect; not usable for planning.

## Scoring Rules
1. Start at `A`.
2. Downgrade one level for each category with issues:
   - incorrect file:line references,
   - non-matching snippets,
   - unsupported causal claims,
   - missing critical references.
3. Minimum level is `D`.

## Required Output Fields
When assigning quality, include:
- `Level` (`A`/`B`/`C`/`D`),
- `Label` (Reliable/Mostly Reliable/Risky/Unreliable),
- `Reasoning` (2-4 concise bullets tied to verified evidence).

