# Validated skill optimization results

Date: 2026-10-28. Best validated version: R87.
Baseline: `8e863ebaac6dda4c8ea786daaa58942ef92584b3`.

The seven skills were optimized through isolated candidates, independent review,
regression checks, and parent integration. The committed skill tree matches the
validated R87 snapshot across all 168 non-cache files. R88 proposals are excluded.

## Benchmark

Counts use Python 3.11.15, tiktoken 0.14.0, and `o200k_base`. Entrypoint counts
sum seven separately loaded skills. Linked closure recursively follows local
Markdown links per entrypoint. These are static input-size comparisons, not
measured model billing, execution latency, or proof of model adherence.

| Surface | Baseline | R87 | Reduction |
| --- | ---: | ---: | ---: |
| Seven entrypoints | 13,580 tokens | 10,891 tokens | 2,689 / 19.80% |
| Linked Markdown closure | 59,382 tokens | 57,094 tokens | 2,288 / 3.85% |
| All skill Markdown | 62,337 tokens | 59,144 tokens | 3,193 / 5.12% |
| All skill Markdown bytes | 297,941 | 282,978 | 14,963 / 5.02% |

| Skill entrypoint | Baseline tokens | R87 tokens |
| --- | ---: | ---: |
| Boxing Me | 714 | 702 |
| Expressive Motion | 1,137 | 958 |
| Fabric Mod Development | 2,050 | 1,658 |
| Iris Shader Development | 1,200 | 885 |
| PaperMC Plugin Development | 2,729 | 2,381 |
| B/W Grid PDF | 2,115 | 1,467 |
| Thai Docs | 3,635 | 2,840 |

Inventory grows from 161 to 168 usable files and from 153 to 160 bundled
resources. Existing resources are retained; seven helpers/references are added.
Markdown grows from 70 to 72 files while aggregate Markdown tokens decrease.
Conditional source changes include correctness fixes and are not counted as
prompt savings. Machine-readable measurements are in
[optimization-benchmark.json](optimization-benchmark.json).

## Changes

- All seven skills: shorten repeated instructions, clarify task routing, retain
  technical gates, and load detailed references when needed.
- Expressive Motion: reuse spring, math, hash, reveal-shape and shader helpers;
  improve shader fetch errors, resource cleanup, transactional cache/framebuffer
  replacement, repeated-open behavior, and Qt export evidence handling.
- Fabric: inspect nested Gradle modules and Kotlin sources, distinguish actual
  test source sets from production package names, and tighten version/rendering
  reference routing.
- Paper: share descriptor parsing, improve project/build/artifact inspection,
  handle YAML comments and placeholders consistently, and retain explicit
  compatibility and validation claims.
- Thai Docs: improve DOCX/PDF text, citation, font and evidence checks; add audit
  and cross-machine references; remove an unavailable Hermes skill prerequisite.
- B/W Grid PDF: simplify instructions/CSS and align the template's monochrome
  colors, weights and row dividers with its documented rules.
- Boxing Me: fix conditional `any` readiness and reuse safe JSON serialization;
  retain decision schema examples and add focused regression coverage.

## Verification

Final pre-commit checks on the exact R87 source tree:

- Skill Creator validator: 7/7 skills PASS.
- Python suites: Expressive Motion 14/14 and Boxing Me 9/9 PASS.
- Expressive bundle: 17 links and 11 wrappers PASS.
- Node checks: 150 card-edge checks, 81 spring oracle samples, 210 motion
  comparisons plus 13 checks, and 336 source-adapter plus 16 panel checks PASS.
- R87 independent composite QA: 8 bounded groups PASS, 0 FAIL, 0 BLOCKED;
  100 local Markdown links resolve; exact inventory and heading parity with R86.
- Working skill files match the saved R87 snapshot; `git diff --check` PASS.

Prior accepted rounds also exercised synthetic Paper/Fabric project fixtures,
descriptor/JAR parsing, DOCX/PDF fixtures, and fake-WebGL failure paths. Numeric
or synthetic checks do not establish real renderer or server behavior.

## Remaining limits

Live skill-loader/model behavior, real Fabric/Minecraft and Paper runtimes,
browser GPU/compositor behavior, and document generation/rendering across target
machines remain untested by this final commit check. No full-runtime success or
optimization convergence is claimed.

R88 found a reproducible LiquidBackdrop constructor resource leak when a later
shader fails. Its proposed fix and other R88 candidates were interrupted by
agent credit exhaustion before independent QA, so they remain outside this
validated version. R87 is the best-known validated fallback.
