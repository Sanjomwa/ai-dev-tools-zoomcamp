from datetime import timedelta

from django.db import models
from django.utils import timezone


class Household(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Member(models.Model):
    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="members")
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(
        editable=False,
        help_text="Rotation position; set automatically by creation order.",
    )

    class Meta:
        ordering = ["order"]

    def save(self, *args, **kwargs):
        if self.pk is None and self.order is None:
            last = Member.objects.filter(household=self.household).order_by("-order").first()
            self.order = (last.order + 1) if last else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.household})"


class Chore(models.Model):
    class Cadence(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"
        MONTHLY = "monthly", "Monthly"

    # Rolling time windows per cadence (issue #7): elapsed time since a reference
    # timestamp, not calendar-day boundaries.
    CADENCE_WINDOWS = {
        Cadence.DAILY: timedelta(hours=24),
        Cadence.WEEKLY: timedelta(hours=7 * 24),
        Cadence.MONTHLY: timedelta(hours=30 * 24),
    }

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
    name = models.CharField(max_length=100)
    cadence = models.CharField(max_length=10, choices=Cadence.choices)
    current_holder = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="chores")
    last_completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.household})"

    @property
    def is_overdue(self):
        # Reference point: when the chore was last completed, or its creation
        # time if it has never been completed.
        reference = self.last_completed_at or self.created_at
        return timezone.now() - reference > self.CADENCE_WINDOWS[self.cadence]
