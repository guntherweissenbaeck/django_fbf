from django.db import models
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    
    # Required fields expected by tests (temporary nullable for migration)
    first_name = models.CharField(
        max_length=50, verbose_name=_("Vorname"), null=True, blank=True
    )
    last_name = models.CharField(
        max_length=50, verbose_name=_("Nachname"), null=True, blank=True
    )
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name=_("Erstellt von"),
        null=True, blank=True
    )
    
    # Optional fields expected by tests
    email = models.EmailField(
        max_length=50, null=True, blank=True, verbose_name=_("Email")
    )
    phone = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Telefon")
    )
    address = models.CharField(
        max_length=200, null=True, blank=True, verbose_name=_("Adresse")
    )
    city = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Stadt")
    )
    postal_code = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Postleitzahl")
    )
    country = models.CharField(
        max_length=100, null=True, blank=True, verbose_name=_("Land")
    )
    notes = models.TextField(
        null=True, blank=True, verbose_name=_("Notizen")
    )
    is_active = models.BooleanField(
        default=True, verbose_name=_("Aktiv")
    )
    
    # Keep existing fields for backwards compatibility
    name = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Kontakt Name")
    )
    comment = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Bemerkungen")
    )
    tag_id = models.ForeignKey(
        "ContactTag",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Tag"),
    )

    class Meta:
        verbose_name = _("Kontakt")
        verbose_name_plural = _("Kontakte")
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return the contact's full name."""
        return f"{self.first_name} {self.last_name}"
    
    def clean(self):
        """Custom validation for the model."""
        super().clean()
        
        # Check required fields for test compatibility
        if not self.first_name:
            raise ValidationError({'first_name': _('This field is required.')})
        
        if not self.last_name:
            raise ValidationError({'last_name': _('This field is required.')})
        
        # Validate email format if provided
        if self.email and '@' not in self.email:
            raise ValidationError({
                'email': _('Please enter a valid email address.')
            })


class ContactTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    tag = models.CharField(
        max_length=50, null=True, blank=True, verbose_name=_("Tag")
    )

    class Meta:
        verbose_name = _("Kontakt Tag")
        verbose_name_plural = _("Kontakt Tags")

    def __str__(self):
        return self.tag
