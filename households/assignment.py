"""
The fairness/assignment algorithm from plan.md §4.

Lives here (rather than in the `chores` app) because, at this stage, it
only needs to rank a household's members — it doesn't touch `Chore` at
all. Callers that assign a chore import `pick_member_for_assignment` and
hand it the chore's household.
"""


def pick_member_for_assignment(household):
    """
    Return the member of `household` who should receive the next chore.

    Ranking rule (plan.md §4.1): the member with the lowest completed-turn
    count goes next. This does not yet implement the deterministic
    tiebreaks (longest time since last assignment, then earliest join
    order) — when multiple members are tied on completed_turns, one of
    them is returned, but which one is not yet a documented guarantee.
    """
    member = household.members.order_by("completed_turns", "pk").first()
    if member is None:
        raise ValueError(f"{household!r} has no members to assign to")
    return member
