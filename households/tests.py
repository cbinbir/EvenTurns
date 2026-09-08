from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

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
