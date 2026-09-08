from django.db import models


class Household(models.Model):
    """A group of members who share and split chores. See plan.md §2."""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    """
    A person in a household.

    completed_turns and owed_turns are the two numbers the fairness model
    (plan.md §4) runs on. They are stored counters rather than derived on
    every read, because the assignment algorithm needs to rank members by
    them cheaply and often.

    `name` is a placeholder identity field for now — per the plan's build
    order, per-member accounts/login (§7) are step 5, after the data model
    and assignment logic exist. This will likely become (or gain) a link to
    Django's auth User model at that point.
    """

    DEBT_CAP = 7  # plan.md §5.2 — enforced by the skip flow, not here.

    household = models.ForeignKey(
        Household, on_delete=models.CASCADE, related_name="members"
    )
    name = models.CharField(max_length=100)
    completed_turns = models.PositiveIntegerField(default=0)
    owed_turns = models.PositiveIntegerField(default=0)

    # Tiebreak inputs for the assignment algorithm (plan.md §4.1):
    joined_at = models.DateTimeField(auto_now_add=True)  # earliest join order
    last_assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Null means never assigned, which should rank first "
        "under the 'longest time since last assignment' tiebreak.",
    )

    class Meta:
        ordering = ["joined_at"]

    def __str__(self):
        return f"{self.name} ({self.household})"
