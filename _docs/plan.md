# Shared Household Chores — Project Spec

## 1. Purpose

A multi-user application for households that assigns chores fairly and records
what has been done. The goal is to make workload balance visible and verifiable
so it does not have to be argued about.

The two core jobs of the tool are:

1. **Fair assignment** — decide who does what next.
2. **Tracking** — record completed chores, which is what makes the fairness
   claim credible.

## 2. Household model

- A household has multiple members.
- Each member has an account and belongs to exactly one household.
- Every member has a running count of **completed turns**.

## 3. Chores

Chores enter the system two ways:

| Type | Description |
|------|-------------|
| Recurring | Repeats on a fixed schedule (daily or weekly) |
| Ad-hoc | Added manually as one-off tasks |

Both types count equally toward a member's turn balance. An ad-hoc chore is not
worth less than a scheduled one.

## 4. Fairness model

Fairness is defined as **equal turns**: over time, every member should have
completed roughly the same number of chores. Chores are not weighted by
difficulty or duration.

### 4.1 Assignment rule

A chore is assigned to the member with the **lowest completed-turn count**.

Ties are broken deterministically, in this order:

1. Longest time since last assignment
2. Earliest join order

Determinism matters here — the same household state must always produce the
same assignment, so the scheduler can be unit-tested.

### 4.2 New members

A member joining an established household starts at the household's **current
average completed-turn count**, not at zero. Starting at zero would bury a new
member under every open chore until they caught up.

## 5. Skipping

A member may decline an assigned chore by skipping it. A skip requires a stated
reason.

When a skip occurs:

- The chore passes to the next member by the standard assignment rule
  (lowest completed-turn count, then tiebreaks).
- The skipper gains **+1 owed turn**.
- The reason is recorded with the skip.

### 5.1 Owed turns and ranking

Owed turns do **not** affect assignment ranking. Ranking uses completed turns
only.

This is deliberate and self-correcting: skipping leaves the skipper's completed
count untouched, so they remain low in the ranking and are assigned again
shortly. If owed turns counted as completed, skipping would be free and the
equal-turns guarantee would break.

### 5.2 Debt cap

Owed turns are capped at **7**.

At the cap, the skip button is disabled and shows a message explaining why. An
uncapped debt lets one member accumulate an unrecoverable backlog, at which
point the schedule stops meaning anything.

## 6. Completion

Completion is **self-reported**: one tap marks a chore done. There is no
confirmation step, photo proof, or dispute mechanism.

The tradeoff is deliberate — the app trusts its members in exchange for very low
friction. Verification layers reliably reduce logging, and unlogged chores break
the fairness math worse than the occasional false report does.

Marking a chore done increments the member's completed-turn count. If the member
has owed turns, this also decrements the debt.

## 7. Platform scope

- Per-member accounts with login
- One household per account
- Notifications for upcoming and overdue chores

## 8. Suggested build order

1. Data model (members, chores, assignments, skips)
2. Assignment algorithm, including tiebreaks and new-member averaging
3. Completion logging and turn counts
4. Skip flow, owed turns, and the debt cap
5. Accounts and authentication
6. Notifications

Steps 1–4 form a coherent, demonstrable system on their own. If the schedule
tightens, push notifications can be replaced with in-app badges at the smallest
cost to the project's substance.

## 9. Open decisions

Nothing blocking, but worth deciding before or during implementation:

- Whether skipping a recurring chore skips one occurrence or unassigns the
  member from the series
- Whether overdue chores are reassigned automatically or simply flagged
- Whether a member can leave a household with outstanding owed turns, and what
  happens to that debt
