"""
The fairness/assignment algorithm from plan.md §4.

Lives here (rather than in the `chores` app) because, at this stage, it
only needs to rank a household's members — it doesn't touch `Chore` at
all. Callers that assign a chore import `pick_member_for_assignment` and
hand it the chore's household.
"""

from django.db.models import F


def pick_member_for_assignment(household):
    """
    Return the member of `household` who should receive the next chore.

    Ranking rule (plan.md §4.1): the member with the lowest completed-turn
    count goes next. Ties are broken, in order:

    1. Longest time since last assignment — a null last_assigned_at (never
       assigned) counts as longer ago than any actual timestamp, so it
       sorts first.
    2. Earliest join order.

    Household state fully determines the result: the same members with the
    same fields always produce the same pick (plan.md §4.1's determinism
    requirement), including the pk tiebreak below for the vanishingly
    unlikely case two members share a joined_at timestamp.
    """
    member = (
        household.members.order_by(
            "completed_turns",
            F("last_assigned_at").asc(nulls_first=True),
            "joined_at",
            "pk",
        )
        .first()
    )
    if member is None:
        raise ValueError(f"{household!r} has no members to assign to")
    return member
