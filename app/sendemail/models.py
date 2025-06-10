from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

from bird.models import Bird


class Emailadress(models.Model):
    email_address = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Benutzer"),
    )
    
    # New notification category fields
    is_naturschutzbehoerde = models.BooleanField(
        default=True,
        verbose_name=_("Naturschutzbehörde")
    )
    is_jagdbehoerde = models.BooleanField(
        default=False,
        verbose_name=_("Jagdbehörde")
    )
    is_wildvogelhilfe_team = models.BooleanField(
        default=True,
        verbose_name=_("Wildvogelhilfe-Team")
    )

    def __str__(self):
        return self.email_address

    class Meta:
        verbose_name = _("Emailadresse")
        verbose_name_plural = _("Emailadressen")


class BirdEmail(models.Model):
    bird = models.ForeignKey(
        Bird, on_delete=models.CASCADE, verbose_name=_("Vogel")
    )
    email = models.ForeignKey(
        Emailadress, on_delete=models.CASCADE, verbose_name=_("Emailadresse")
    )

    def __str__(self):
        return f"{self.bird} - {self.email}"

    class Meta:
        verbose_name = _("Vogel-Email")
        verbose_name_plural = _("Vogel-Emails")
