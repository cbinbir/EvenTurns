# EvenTurns Backlog

Tasks are ordered to roughly follow the build order in `_docs/plan.md` §8.
Each one is scoped to a single session and references the plan sections it
implements, so it can be picked up without reading the other tasks.

## 1. Data model integrity constraints
Goal: Make the existing models reject invalid states instead of relying on callers to be careful.
Description: Add model-level or database-level validation so a `Member.owed_turns` above 7 (plan.md §5.2) and a recurring `Chore` with no `frequency` (plan.md §3) cannot be saved. Cover both cases with tests that attempt to save an invalid instance and assert it is rejected.

## 2. Assignment ranking function
Goal: Given a household, determine which member a new chore should go to.
Description: Implement a function that takes a household (or its members) and returns the member with the lowest `completed_turns`. This is the core of plan.md §4.1 — no tiebreaks or side effects yet, just the ranking, with unit tests covering a clear-winner case and a tied case.

## 3. Assignment tiebreak logic
Goal: Make the ranking function deterministic when multiple members are tied on completed turns.
Description: Extend the ranking function from Task 2 to break ties first by longest time since last assignment, then by earliest join order (plan.md §4.1). Add unit tests with constructed households where each tiebreak level is needed to reach a unique answer, since the plan requires the same household state to always produce the same result.

## 4. New-member starting balance
Goal: Give a member who joins an established household a fair starting point.
Description: When a member is added to a household that already has other members, set their `completed_turns` to the household's current average rather than zero (plan.md §4.2). Write tests covering a household with an even average, an uneven average requiring rounding, and a household with no existing members.

## 5. Ad-hoc chore creation flow
Goal: Let someone add a one-off chore and have it assigned immediately.
Description: Build the flow for creating an ad-hoc `Chore` (plan.md §3) that, on creation, calls the assignment ranking logic to create its first `Assignment`. Should work standalone against whatever ranking function exists at the time (Task 2), without depending on recurring-chore scheduling.

## 6. Recurring chore occurrence generator
Goal: Turn a recurring chore's schedule into actual assignable occurrences.
Description: Build the process that, for each recurring `Chore` (daily or weekly, plan.md §3), creates a new `Assignment` when its next occurrence is due, using the assignment ranking logic. Decide and document how "due" is determined (e.g., time since the last occurrence's creation) since the plan does not specify it.

## 7. Completion action
Goal: Let a member mark an assigned chore done in one step.
Description: Build the action that marks an `Assignment` completed (plan.md §6): set its status and `completed_at`, increment the member's `completed_turns`, and decrement their `owed_turns` if they have any. No confirmation step or proof requirement — completion is self-reported by design.

## 8. Skip action
Goal: Let a member decline an assigned chore with a reason.
Description: Build the action that closes out an `Assignment` as skipped, requires and stores a reason on a `Skip` record, gives the skipper +1 `owed_turns`, and creates a new `Assignment` for the next member via the ranking logic (plan.md §5). The skipper's `completed_turns` must not change.

## 9. Debt cap enforcement on skipping
Goal: Stop a member from skipping once they've hit the owed-turn cap.
Description: When a member's `owed_turns` is already at 7, prevent the skip action from Task 8 and surface a clear message explaining why (plan.md §5.2). Include a test that a member at the cap cannot accumulate an 8th owed turn through the skip action.

## 10. Member balance view
Goal: Show a member their own completed-turns and owed-turns counts.
Description: Build a simple read-only view/page for a member showing their current `completed_turns` and `owed_turns`, and their household's per-member breakdown for comparison. This is what makes the fairness claim in plan.md §1 "visible," independent of any specific action (completing/skipping).

## 11. Household activity history
Goal: Show a verifiable log of what's happened in a household over time.
Description: Build a view listing a household's chores with their assignment history — who had each chore, when it was completed or skipped, and any skip reasons. This is the "tracking" half of plan.md §1 and should read from existing `Assignment`/`Skip` records without changing how they're created.

## 12. Household creation and joining
Goal: Let someone start a new household or add themselves to an existing one.
Description: Build the flow for creating a `Household` and adding a `Member` to it, enforcing that each account belongs to exactly one household (plan.md §2, §7). New members added to a non-empty household should hand off to the starting-balance logic from Task 4.

## 13. Per-member accounts and login
Goal: Give members real authenticated identities instead of a placeholder name field.
Description: Wire up login for members (plan.md §7), replacing or backing the current `Member.name` placeholder with an authenticated account. Existing `Member` rows and their turn counts must carry over — this task should not require resetting any household's data.

## 14. Upcoming-chore notifications
Goal: Warn a member before a chore they're assigned comes due.
Description: Build a notification (in-app or push, per plan.md §6/§7) sent to a member some fixed lead time before their assigned chore's due date. Scope to recurring chores first, since they're the ones with a predictable schedule.

## 15. Overdue-chore handling
Goal: Decide and implement what happens when an assigned chore passes its due date.
Description: Plan.md §9 leaves open whether overdue chores are reassigned automatically or simply flagged — pick one, document the reasoning, and implement it (a flag/badge plus a notification, or an automatic re-run of the assignment logic). Should not require the notification system from Task 14 to already exist if flagging is chosen.

## 16. Recurring-chore skip semantics
Goal: Decide and implement what skipping a recurring chore actually does.
Description: Plan.md §9 leaves open whether a skip affects only the current occurrence or removes the member from the whole series — pick one, document the reasoning, and implement it on top of the skip action from Task 8. Add a test for a member skipping one occurrence and confirm whether they're still eligible for the series' next occurrence per the chosen rule.

## 17. Member departure and outstanding debt
Goal: Decide and implement what happens to owed turns when a member leaves a household.
Description: Plan.md §9 leaves open whether a member can leave with outstanding `owed_turns` and what happens to that debt — pick a rule (e.g., forfeited, redistributed, or blocking departure until cleared), document the reasoning, and implement the leave flow accordingly.

## 18. Production deployment settings
Goal: Make the project safe to deploy instead of only safe to run locally.
Description: Move `SECRET_KEY` out of source control into an environment variable, set `DEBUG = False` with a real `ALLOWED_HOSTS`, and configure static file serving for production. This is infrastructure hardening independent of any feature work above.
