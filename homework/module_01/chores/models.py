from django.db import models


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

    household = models.ForeignKey(Household, on_delete=models.CASCADE, related_name="chores")
    name = models.CharField(max_length=100)
    cadence = models.CharField(max_length=10, choices=Cadence.choices)
    current_holder = models.ForeignKey(Member, on_delete=models.PROTECT, related_name="chores")
    last_completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.household})"
