---
name: interactive-tutorial-builder
description: Build or refactor browser-based interactive technical tutorials with prerequisite sequencing, runnable exercises, evidence-backed progress, responsive learner workflows, and content/runtime/browser/pedagogy verification. Use for web-based coding courses or hands-on browser labs; not for static documentation, PDF-only books, CLI/notebook/hardware labs, or standalone UI mockups.
---

# Interactive Tutorial Builder

Build a coherent learning system, not a collection of pages. Preserve the target project's stack and content ownership unless the user asks to replace them.

## Inspect Before Designing

Read the source material, current course model, generator, runtime, navigation, tests, and existing evidence. Identify:

- the learner's actual starting knowledge;
- the observable capability they should gain;
- the current source of truth versus generated output;
- which interactions are static, simulated, locally executed, or backed by a real service;
- where completion state comes from and whether it can be forged.

For a refactor that crosses multiple ownership boundaries such as curriculum data, generator, runtime, and learner UI, write a project-local spec and task list before implementation. Keep source edits, generated artifacts, and evidence distinct.

## Establish The Learning Contract

Model prerequisites before ordering pages. Each unit should declare a focused new capability, reused knowledge, a learner action, and evidence of success. Align the scene or question, accurate mechanism, example, exercise, feedback, and completion proof around the same technical object.

Do not encode a universal number of UI steps. The semantic learning loop may include observing, predicting, changing, running, explaining, debugging, and transferring; project the subset that the current lesson needs into a small number of clear interface tasks.

Read [references/learning-design.md](references/learning-design.md) when creating the curriculum graph, lesson contracts, exercise ladder, feedback policy, or continuity model.

## Build A Thin Vertical Slice

Before scaling the course, implement representative units that exercise the hardest boundaries: one beginner unit, one failure/debugging unit, one real runtime unit, and one cross-unit return path when applicable.

When completion claims that learner code actually ran, use a real execution path for the declared capability level. For executable exercises:

- require the starter to demonstrate the intended failure or incomplete behavior;
- require the reference solution to pass trusted tests;
- keep learner-visible examples separate from hidden acceptance tests;
- return diagnostic feedback without leaking the full solution;
- bind successful runs to the unit, submitted content, and verifier version; add expiration or nonce policy when proofs cross sessions, devices, users, or security boundaries.

Completion must be earned from the unit's declared proof policy. A click, route visit, client-side flag, or unverified saved value is not execution evidence.

## Preserve Interaction Continuity

Keep one primary action clear at a time. Separate cross-unit navigation from within-unit task or pane changes.

Within-unit actions such as running, checking, requesting a hint, or switching explanation/practice views must not unexpectedly change the route, whole-page scroll, or focus. Cross-unit navigation must update the URL, title, active directory item, and restore target consistently. Hidden mobile panes must not remain keyboard-focusable.

Persist drafts and position only where that helps the learner resume. Treat persisted state as a convenience, not trusted proof.

## State Runtime Capabilities Honestly

Define an adapter boundary for every executable domain. Report whether evidence comes from a static parser, fake provider, local trusted subset, operating-system sandbox, container, remote sandbox, or real service. Never promote one level's result into a stronger claim.

Bound input, output, time, concurrency, filesystem, network, process cleanup, and dependency access in proportion to the code being executed. Do not invent a sandbox when the target environment lacks one; report the missing isolation as a risk.

## Verify Four Independent Layers

Read [references/acceptance-and-evidence.md](references/acceptance-and-evidence.md) before implementing acceptance or claiming completion.

Verify separately:

1. Content: schema, prerequisites, identifiers, examples, answers, feedback, and coverage.
2. Runtime: starter failure, solution success, realistic failures, limits, cleanup, and proof binding.
3. Browser: responsive reading, navigation, keyboard access, editor behavior, persistence, and the full try-feedback-retry-complete path.
4. Pedagogy: prerequisite gaps, cognitive load, distractors, hint leakage, independent practice, and transfer.

Bind all reports to the same candidate artifacts. Use `scripts/verify_tutorial_evidence.py` when the project adopts the documented manifest. The verifier proves evidence consistency, not teaching effectiveness.

Use independent review for book-length, multi-route, high-risk, or consequential courses. Scale review effort down for a small tutorial; do not impose a publication pipeline that exceeds the task's risk.

## Deliver Precisely

Report what changed, the learner path now supported, commands and artifacts used as evidence, and residual risks. Distinguish automated proxies from human learning data. Do not claim retention, transfer, production safety, or domain accuracy unless the corresponding evidence exists.
