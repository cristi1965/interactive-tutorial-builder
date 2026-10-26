# Acceptance And Evidence

Use this reference when implementing a runner, completion policy, browser audit, release gate, or delivery claim.

## Four Acceptance Layers

### Content

Check schema validity, stable identifiers, prerequisite edges, links, code syntax, expected outputs, answer keys, feedback, and coverage. Validate meaningful invariants rather than only counting pages.

### Runtime

Execute the exact learner submission path and trusted tests in an isolated workspace appropriate to the risk. Cover:

- intended starter failure or incompleteness;
- reference solution success;
- realistic compile, assertion, timeout, and resource failures;
- bounded input and output;
- process-tree cleanup;
- network, filesystem, and dependency policy;
- stale, expired, replayed, or cross-unit proof rejection.

### Browser

Test the actual served candidate, not only source files. Cover desktop and mobile reading, route/title/directory agreement, keyboard and focus behavior, editor changes, pending states, error recovery, saved drafts, refresh, and the complete learner loop.

Accessibility automation is necessary but incomplete. Include heading order, accessible names, focus visibility, hidden-pane focusability, reduced motion, zoom/reflow, and touch target checks appropriate to the product.

### Pedagogy

Use a fresh reviewer or evaluation context to inspect prerequisite gaps, overloaded explanations, analogy accuracy, exercise independence, distractor quality, hint leakage, and whether the target capability can be performed without copying the answer.

Automated behavior is a proxy. Human time-on-task, retention, hint dependency, and transfer require actual learner evidence.

## Capability Levels

Label runtime claims explicitly:

| Level | What it can support | What it cannot support by itself |
|---|---|---|
| Static parser | Syntax or constrained structural feedback | Real engine semantics or side effects |
| Fake provider | Application boundary and deterministic failure paths | External provider behavior or reliability |
| Local trusted subset | Real compiler/test behavior under stated local limits | Production isolation or distributed behavior |
| OS/container sandbox | Stronger execution isolation under documented policy | Safety beyond configured boundaries |
| Remote sandbox | Hosted isolation and reproducible runtime contract | Production readiness without operational evidence |
| Real service | Integration behavior for the tested environment | Other environments, load levels, or untested failure modes |

## Evidence Manifest

The included verifier accepts a JSON manifest shaped like this:

```json
{
  "version": 1,
  "candidate": {
    "sha256": "<digest of the sorted artifact path and digest records>",
    "artifacts": [
      {"path": "dist/index.html", "sha256": "<file digest>"}
    ]
  },
  "layers": {
    "content": {
      "status": "pass",
      "candidate_sha256": "<candidate digest>",
      "report": "evidence/content.json",
      "report_sha256": "<report digest>"
    },
    "runtime": {"status": "pass", "candidate_sha256": "<candidate digest>", "report": "evidence/runtime.json", "report_sha256": "<report digest>"},
    "browser": {"status": "pass", "candidate_sha256": "<candidate digest>", "report": "evidence/browser.json", "report_sha256": "<report digest>"},
    "pedagogy": {"status": "pass", "candidate_sha256": "<candidate digest>", "report": "evidence/pedagogy.json", "report_sha256": "<report digest>"}
  }
}
```

All paths are relative to the manifest directory. The candidate digest is SHA-256 over sorted UTF-8 records of the form `path`, a NUL byte, the file digest, and a newline. The verifier rejects absolute paths and paths that escape the manifest directory.

Run:

```sh
python3 skills/interactive-tutorial-builder/scripts/verify_tutorial_evidence.py path/to/evidence-manifest.json
```

Each report file must itself be a JSON object containing `status: "pass"` and the same `candidate_sha256`. Passing means the four declared reports exist, declare success, bind the same candidate, and still match their recorded hashes. It does not inspect the reports' methodology or prove their conclusions.

Minimal report body:

```json
{
  "status": "pass",
  "candidate_sha256": "<same candidate digest as the manifest>",
  "checks": [
    {"id": "project-defined-check", "status": "pass"}
  ],
  "limitations": ["What this report does not prove"]
}
```

Only `status` and `candidate_sha256` are required by the verifier. The project owns the schema and quality of the remaining evidence.

## Review Scale

- Small, low-risk tutorial: focused content/runtime checks plus one browser and pedagogy pass.
- Multi-route or book-length course: two independent review passes, with the second using a fresh context to find regressions.
- Regulated or safety-relevant subject: qualified domain review and explicit ownership of professional claims.

Any content, runner, UI, or audit change creates a new candidate. Rebuild evidence instead of editing old hashes.

## Claim Discipline

Report each result with its scope:

- “All declared unit schemas passed” is not “the curriculum is complete.”
- “The local runner passed fixed tests” is not “the code is production ready.”
- “No automated accessibility violations were found” is not “the site is fully accessible.”
- “Independent pedagogy review passed” is not “learners will retain and transfer the skill.”

List unavailable checks and residual risk rather than silently treating them as passes.
