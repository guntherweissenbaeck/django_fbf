from uuid import uuid4

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, ValidationError
from decimal import Decimal

from bird.models import Bird


CHOICE_CATEGORY = [
    ("medical", _("Medizinisch")),
    ("food", _("Nahrung")),
    ("equipment", _("Ausrüstung")),
    ("transport", _("Transport")),
    ("other", _("Sonstiges")),
]


class Costs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    # Main relationship - could be to Bird or FallenBird
    bird = models.ForeignKey(
        Bird,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Vogel"),
        related_name='costs'
    )
    id_bird = models.ForeignKey(
        "bird.FallenBird",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Patient"),
        related_name='costs'
    )
    
    # Cost details
    description = models.CharField(
        max_length=512,
        default="",
        verbose_name=_("Beschreibung")
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name=_("Betrag")
    )
    cost_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Kostendatum")
    )
    category = models.CharField(
        max_length=20,
        choices=CHOICE_CATEGORY,
        default="other",
        verbose_name=_("Kategorie")
    )
    
    # Additional fields expected by tests
    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Rechnungsnummer")
    )
    vendor = models.CharField(
        max_length=256,
        blank=True,
        null=True,
        verbose_name=_("Anbieter")
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notizen")
    )
    
    # Legacy field for backwards compatibility
    costs = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default="0.00",
        verbose_name=_("Betrag (legacy)"))
    created = models.DateField(
        auto_now_add=True,
        verbose_name=_("Gebucht am"))
    comment = models.CharField(
        max_length=512,
        blank=True,
        null=True,
        verbose_name=_("Bemerkungen"))
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='costs_created',
        null=True,
        blank=True,
        verbose_name=_("Erstellt von"))

    class Meta:
        verbose_name = _("Kosten")
        verbose_name_plural = _("Kosten")
        
    def clean(self):
        """Validate that amount is not negative."""
        if self.amount and self.amount < 0:
            raise ValidationError(_("Betrag kann nicht negativ sein."))

    def __str__(self):
        return f"{self.description} - €{self.amount}"
