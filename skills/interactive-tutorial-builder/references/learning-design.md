# Learning Design Contract

Use this reference when creating or restructuring an interactive technical course.

## 1. Define The Learner Delta

Write the learning contract before the page outline:

| Field | Question |
|---|---|
| Starting capability | What can the learner already explain or execute without help? |
| Target capability | What observable task should they complete independently? |
| Prerequisites | Which concepts and operations must already be available? |
| Authentic context | Where does this capability matter in a real system? |
| Success evidence | What artifact, behavior, test, or explanation demonstrates it? |
| Boundary | What will this lesson deliberately not claim or teach? |

Use observable verbs. “Understand concurrency” is not testable; “identify a race, reproduce it, then make the fixed test pass” is.

## 2. Build A Prerequisite Graph

Represent dependencies explicitly instead of assuming chapter order is correct. A unit may be freely browsable while the recommended path still shows missing prerequisites.

Check for:

- terms used before introduction;
- exercises requiring syntax or tools not yet practiced;
- an advanced abstraction that hides the mechanism the learner is meant to learn;
- optional branches that silently become mandatory later;
- duplicated units that teach the same rule under different labels.

When refactoring an existing course, retain stable IDs or provide a migration map for saved progress and inbound links.

## 3. Define Each Unit

A useful unit contract contains:

```yaml
id: stable-unit-id
prerequisites: [earlier-unit]
new_capability: one observable capability
reused_knowledge: [known-concept]
context: the problem or failure that creates a reason to learn
mechanism: the accurate rule and its important boundary
actions:
  - observe
  - predict
  - change
  - run
  - explain
  - transfer
proof_policy:
  required: [prediction, changed_run, trusted_test]
  optional: [explanation, transfer]
capability_boundary: local trusted subset, not a production service
```

This is a conceptual contract, not a required serialization format. Adapt it to the project's schema.

The interface can group these actions into fewer tasks. Avoid simultaneous navigation systems that compete for control, such as a chapter outline, step tabs, anchor cards, and completion links all moving the learner independently.

## 4. Use A Graduated Exercise Ladder

Move responsibility from the tutorial to the learner:

1. Read a small example and predict an output or failure.
2. Change one meaningful variable and compare the result.
3. Fill the central operation while scaffolding remains.
4. Diagnose a realistic broken example.
5. Implement a bounded task from a contract and tests.
6. Transfer the rule to a new object or context.

Not every unit needs all six levels. Across a route, however, running prewritten code cannot be the highest level of practice.

Keep changes small enough that feedback points to the new concept. If a lesson introduces several tightly coupled concepts, state why they cannot be separated and provide intermediate checkpoints.

## 5. Design Feedback Without Giving Away The Task

Feedback should progress through four levels:

1. Result: actual versus expected behavior.
2. Location: the smallest relevant file, expression, query, state, or step.
3. Concept: the violated rule or invariant.
4. Direction: the next experiment, not the completed answer.

Offer hints progressively. Record whether the learner revealed a full solution; a revealed solution may permit continuation but should not be labeled independent completion.

Wrong-answer choices should represent plausible misconceptions and explain why they fail. Avoid trivia, wording traps, or distractors that are obviously unrelated.

## 6. Preserve A Continuous Workflow

The learner should be able to move through:

`read the problem -> predict -> try -> see precise feedback -> revise -> pass -> explain or transfer`

without losing their code, place, result, or mental context.

Recommended invariants:

- running code keeps the current unit and relevant editor in view;
- task or pane switches do not mutate the route;
- returning from optional material restores the logical source location;
- saved drafts survive refresh, while stale async results cannot overwrite newer edits;
- controls disable only for a clear reason and unlock after errors;
- desktop and mobile expose the same learning contract, even when layout differs.

## 7. Refactor Safely

For an existing tutorial:

1. Map every current unit to its target capability and evidence.
2. Find gaps, duplicates, and out-of-order prerequisites.
3. Choose a representative vertical slice and preserve a legacy entry when the information architecture changes substantially.
4. Change source/generator contracts before generated output.
5. Rebuild and verify the affected route before scaling.
6. Re-run full-course navigation and content checks after global changes.

Visual polish cannot compensate for a broken learning sequence. Fix information architecture, action ownership, and feedback quality first.
