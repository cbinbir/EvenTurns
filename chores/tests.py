from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from households.models import Household

from .models import Chore


class RecurringChoreRequiresFrequencyTests(TestCase):
    """plan.md §3 — a recurring chore must specify a frequency."""

    def setUp(self):
        self.household = Household.objects.create(name="Test Household")

    def test_recurring_chore_with_frequency_is_allowed(self):
        chore = Chore.objects.create(
            household=self.household,
            name="Dishes",
            chore_type=Chore.RECURRING,
            frequency=Chore.DAILY,
        )
        self.assertEqual(chore.frequency, Chore.DAILY)

    def test_adhoc_chore_without_frequency_is_allowed(self):
        chore = Chore.objects.create(
            household=self.household, name="Fix the fence", chore_type=Chore.ADHOC
        )
        self.assertEqual(chore.frequency, "")

    def test_recurring_chore_without_frequency_is_rejected_at_save(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Chore.objects.create(
                    household=self.household,
                    name="Dishes",
                    chore_type=Chore.RECURRING,
                )

    def test_recurring_chore_without_frequency_is_rejected_by_full_clean(self):
        chore = Chore(
            household=self.household, name="Dishes", chore_type=Chore.RECURRING
        )
        with self.assertRaises(ValidationError):
            chore.full_clean()
