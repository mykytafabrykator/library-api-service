from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "HARD", _("Hard")
        SOFT = "SOFT", _("Soft")

    title = models.CharField(max_length=250)
    author = models.CharField(max_length=250)
    cover = models.CharField(max_length=4, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        unique_together = ("title", "author")
        ordering = ("title", "author")
