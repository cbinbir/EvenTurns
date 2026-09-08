from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from .assignment import pick_member_for_assignment
from .models import Household, Member


class MemberOwedTurnsDebtCapTests(TestCase):
    """plan.md §5.2 — owed_turns must never exceed the debt cap of 7."""

    def setUp(self):
        self.household = Household.objects.create(name="Test Household")

    def test_owed_turns_at_cap_is_allowed(self):
        member = Member.objects.create(
            household=self.household, name="Alex", owed_turns=Member.DEBT_CAP
        )
        self.assertEqual(member.owed_turns, Member.DEBT_CAP)

    def test_owed_turns_above_cap_is_rejected_at_save(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Member.objects.create(
                    household=self.household,
                    name="Sam",
                    owed_turns=Member.DEBT_CAP + 1,
                )

    def test_owed_turns_above_cap_is_rejected_by_full_clean(self):
        member = Member(
            household=self.household, name="Sam", owed_turns=Member.DEBT_CAP + 1
        )
        with self.assertRaises(ValidationError):
            member.full_clean()


class PickMemberForAssignmentTests(TestCase):
    """plan.md §4.1 — assign to the member with the lowest completed_turns."""

    def setUp(self):
        self.household = Household.objects.create(name="Test Household")

    def test_clear_winner_is_picked(self):
        low = Member.objects.create(
            household=self.household, name="Low", completed_turns=1
        )
        Member.objects.create(
            household=self.household, name="High", completed_turns=5
        )

        self.assertEqual(pick_member_for_assignment(self.household), low)

    def test_tie_on_completed_turns_is_broken_by_last_assigned_at(self):
        # "Recently assigned" joins first (earlier joined_at), so if join
        # order were consulted before last_assigned_at, it would win.
        # It shouldn't: "Never assigned" has waited longer.
        Member.objects.create(
            household=self.household,
            name="Recently assigned",
            completed_turns=3,
            last_assigned_at=timezone.now(),
        )
        never_assigned = Member.objects.create(
            household=self.household, name="Never assigned", completed_turns=3
        )

        self.assertEqual(
            pick_member_for_assignment(self.household), never_assigned
        )

    def test_tie_on_completed_turns_is_broken_by_oldest_last_assigned_at(self):
        now = timezone.now()
        # Created in the order that would pick the wrong member if join
        # order were consulted before last_assigned_at.
        Member.objects.create(
            household=self.household,
            name="Assigned yesterday",
            completed_turns=4,
            last_assigned_at=now - timedelta(days=1),
        )
        assigned_long_ago = Member.objects.create(
            household=self.household,
            name="Assigned 10 days ago",
            completed_turns=4,
            last_assigned_at=now - timedelta(days=10),
        )

        self.assertEqual(
            pick_member_for_assignment(self.household), assigned_long_ago
        )

    def test_tie_on_completed_turns_and_last_assigned_at_is_broken_by_join_order(
        self,
    ):
        earliest = Member.objects.create(
            household=self.household, name="Earliest", completed_turns=2
        )
        Member.objects.create(
            household=self.household, name="Latest", completed_turns=2
        )

        self.assertEqual(pick_member_for_assignment(self.household), earliest)

    def test_household_with_no_members_raises(self):
        with self.assertRaises(ValueError):
            pick_member_for_assignment(self.household)
