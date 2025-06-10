from django import template
from django.contrib.contenttypes.models import ContentType
from notizen.models import Notiz
import markdown

register = template.Library()


@register.inclusion_tag('notizen/object_notizen.html', takes_context=True)
def show_object_notizen(context, obj):
    """
    Template tag to display notes attached to an object.
    Usage: {% show_object_notizen object %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    notizen = Notiz.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).order_by('-geaendert_am')
    
    # Convert markdown to HTML for each note
    notizen_with_html = []
    for notiz in notizen:
        html_content = markdown.markdown(notiz.inhalt, extensions=['markdown.extensions.fenced_code'])
        notizen_with_html.append({
            'notiz': notiz,
            'html_content': html_content
        })
    
    return {
        'notizen_with_html': notizen_with_html,
        'content_object': obj,
        'content_type': content_type,
        'user': context['user'],
    }


@register.filter
def content_type_id(obj):
    """
    Filter to get content type ID for an object.
    Usage: {{ object|content_type_id }}
    """
    return ContentType.objects.get_for_model(obj).id


@register.simple_tag
def notiz_attach_url(obj):
    """
    Template tag to generate URL for attaching a note to an object.
    Usage: {% notiz_attach_url object %}
    """
    from django.urls import reverse
    content_type = ContentType.objects.get_for_model(obj)
    return reverse('notizen:attach', kwargs={
        'content_type_id': content_type.id,
        'object_id': obj.pk
    })


@register.simple_tag
def notiz_count_for_object(obj):
    """
    Template tag to get the count of notes for an object.
    Usage: {% notiz_count_for_object object %}
    """
    content_type = ContentType.objects.get_for_model(obj)
    return Notiz.objects.filter(
        content_type=content_type,
        object_id=obj.pk
    ).count()


@register.inclusion_tag('notizen/page_notizen.html', takes_context=True)
def show_page_notizen(context, page_identifier):
    """
    Template tag to display notes attached to a specific page/overview.
    Usage: {% show_page_notizen "patient_overview" %}
    """
    from notizen.models import Page
    
    # Get or create the page object
    page, created = Page.objects.get_or_create(
        identifier=page_identifier,
        defaults={
            'name': page_identifier.replace('_', ' ').title(),
            'description': f'Übersichtsseite für {page_identifier}'
        }
    )
    
    # Get notes attached to this page
    content_type = ContentType.objects.get_for_model(Page)
    notizen = Notiz.objects.filter(
        content_type=content_type,
        object_id=page.pk
    ).order_by('-geaendert_am')
    
    # Convert markdown to HTML for each note
    notizen_with_html = []
    for notiz in notizen:
        html_content = markdown.markdown(notiz.inhalt, extensions=['markdown.extensions.fenced_code'])
        notizen_with_html.append({
            'notiz': notiz,
            'html_content': html_content
        })
    
    return {
        'notizen_with_html': notizen_with_html,
        'page_identifier': page_identifier,
        'page': page,
        'user': context['user'],
    }
