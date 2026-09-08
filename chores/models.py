from django.db import models


class Chore(models.Model):
    """A task a household needs done. See plan.md §3."""

    RECURRING = "recurring"
    ADHOC = "adhoc"
    CHORE_TYPE_CHOICES = [
        (RECURRING, "Recurring"),
        (ADHOC, "Ad-hoc"),
    ]

    DAILY = "daily"
    WEEKLY = "weekly"
    FREQUENCY_CHOICES = [
        (DAILY, "Daily"),
        (WEEKLY, "Weekly"),
    ]

    household = models.ForeignKey(
        "households.Household", on_delete=models.CASCADE, related_name="chores"
    )
    name = models.CharField(max_length=100)
    chore_type = models.CharField(max_length=10, choices=CHORE_TYPE_CHOICES)
    # Only meaningful when chore_type == RECURRING.
    frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Assignment(models.Model):
    """
    One member's turn at one chore.

    A skip does not edit this row — it closes it out as SKIPPED and a new
    Assignment is created for the next member (plan.md §5). That keeps full
    history: you can always see who a chore passed through and why.
    """

    ASSIGNED = "assigned"
    COMPLETED = "completed"
    SKIPPED = "skipped"
    STATUS_CHOICES = [
        (ASSIGNED, "Assigned"),
        (COMPLETED, "Completed"),
        (SKIPPED, "Skipped"),
    ]

    chore = models.ForeignKey(
        Chore, on_delete=models.CASCADE, related_name="assignments"
    )
    member = models.ForeignKey(
        "households.Member", on_delete=models.CASCADE, related_name="assignments"
    )
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=ASSIGNED
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.chore} → {self.member} ({self.status})"


class Skip(models.Model):
    """
    A record of one member declining one assignment.

    One-to-one with Assignment: a given assignment is skipped at most once
    (skipping it closes it and creates a new Assignment for the next
    member). The reason is required by plan.md §5.
    """

    assignment = models.OneToOneField(
        Assignment, on_delete=models.CASCADE, related_name="skip"
    )
    reason = models.TextField()
    skipped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Skip of {self.assignment}"
