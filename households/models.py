from django.core.exceptions import ValidationError
from django.db import models

DEBT_CAP = 7  # plan.md §5.2 — module-level so both Member and its Meta
              # (a separate class scope) can reference the same number.


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

    DEBT_CAP = DEBT_CAP  # exposed on the model too, e.g. Member.DEBT_CAP

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
        constraints = [
            models.CheckConstraint(
                check=models.Q(owed_turns__lte=DEBT_CAP),
                name="member_owed_turns_lte_debt_cap",
                violation_error_message=f"owed_turns cannot exceed the debt "
                f"cap of {DEBT_CAP} (plan.md §5.2).",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.household})"

    def clean(self):
        if self.owed_turns > self.DEBT_CAP:
            raise ValidationError(
                {
                    "owed_turns": f"Owed turns cannot exceed the debt cap "
                    f"of {self.DEBT_CAP} (plan.md §5.2)."
                }
            )
