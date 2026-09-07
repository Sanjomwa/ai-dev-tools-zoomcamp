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
