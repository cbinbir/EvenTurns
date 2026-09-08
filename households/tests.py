from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

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

    def test_tied_members_return_one_of_the_tied_members(self):
        tied = [
            Member.objects.create(
                household=self.household, name="A", completed_turns=2
            ),
            Member.objects.create(
                household=self.household, name="B", completed_turns=2
            ),
        ]
        Member.objects.create(
            household=self.household, name="High", completed_turns=9
        )

        self.assertIn(pick_member_for_assignment(self.household), tied)

    def test_household_with_no_members_raises(self):
        with self.assertRaises(ValueError):
            pick_member_for_assignment(self.household)
