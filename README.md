# EvenTurns

A multi-user household chore tracker built around one idea: **fairness means
equal turns**. EvenTurns assigns chores to whoever has completed the fewest so
far, tracks completions, and makes workload balance visible and verifiable —
so it doesn't have to be argued about.

## How it works

- **Assignment.** Every chore — recurring or ad-hoc — goes to the household
  member with the lowest completed-turn count. Ties break deterministically:
  longest time since last assignment, then earliest join order.
- **New members** start at the household's current average turn count, not
  zero, so they aren't buried under a backlog on day one.
- **Skipping.** A member can decline an assigned chore with a stated reason.
  The chore moves on to the next member by the same rule, and the skipper
  gains +1 *owed* turn. Owed turns don't affect assignment ranking — only
  completed turns do — which is what makes skipping self-correcting instead
  of free. Owed turns are capped at 7.
- **Completion** is self-reported: one tap marks a chore done, incrementing
  the completed-turn count and paying down any owed-turn debt.

Full spec: [`_docs/plan.md`](_docs/plan.md).

## Status

Early development. Build order follows the spec:

1. Data model (members, chores, assignments, skips)
2. Assignment algorithm (tiebreaks, new-member averaging)
3. Completion logging and turn counts
4. Skip flow, owed turns, debt cap
5. Accounts and authentication
6. Notifications

## Project

Homework 1 for [DataTalksClub's AI Dev Tools Zoomcamp 2026](https://github.com/DataTalksClub).
