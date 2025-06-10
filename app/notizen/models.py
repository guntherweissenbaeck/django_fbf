from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django_ckeditor_5.fields import CKEditor5Field


class Page(models.Model):
    """
    Model to represent overview pages that can have notes attached.
    """
    identifier = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Seiten-Identifier",
        help_text="Eindeutige Kennung für diese Seite"
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name="Seitenname",
        help_text="Anzeigename für diese Seite"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Beschreibung",
        help_text="Beschreibung der Seite"
    )
    
    class Meta:
        verbose_name = "Seite"
        verbose_name_plural = "Seiten"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Notiz(models.Model):
    """
    Model for user notes that can be attached to different objects.
    """
    name = models.CharField(
        max_length=200,
        verbose_name="Name der Notiz",
        help_text="Bezeichnung für diese Notiz"
    )
    
    inhalt = CKEditor5Field(
        verbose_name="Inhalt",
        help_text="Inhalt der Notiz in Markdown-Format",
        config_name='extends'
    )
    
    # Generic foreign key to attach notes to any model
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Objekttyp"
    )
    object_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Objekt ID",
        help_text="ID des verknüpften Objekts (unterstützt sowohl Integer als auch UUID)"
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Metadata
    erstellt_von = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Erstellt von"
    )
    erstellt_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Erstellt am"
    )
    geaendert_am = models.DateTimeField(
        auto_now=True,
        verbose_name="Geändert am"
    )
    
    class Meta:
        verbose_name = "Notiz"
        verbose_name_plural = "Notizen"
        ordering = ['-geaendert_am']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('notizen:detail', kwargs={'pk': self.pk})
    
    def get_edit_url(self):
        return reverse('notizen:edit', kwargs={'pk': self.pk})
    
    @property
    def attached_to_model_name(self):
        """Return human-readable model name this note is attached to."""
        if self.content_type:
            return self.content_type.model_class()._meta.verbose_name
        return None
    
    @property
    def attached_to_object_str(self):
        """Return string representation of attached object."""
        if self.content_object:
            return str(self.content_object)
        return None
