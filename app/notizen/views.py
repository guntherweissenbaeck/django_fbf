from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from .models import Notiz
from .forms import NotizForm, NotizAttachForm
import markdown


@login_required
def notizen_list(request):
    """List all notes created by the user."""
    notizen = Notiz.objects.filter(erstellt_von=request.user)
    
    # Pagination
    paginator = Paginator(notizen, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'notizen': page_obj,
    }
    return render(request, 'notizen/list.html', context)


@login_required
def notiz_detail(request, pk):
    """Display a single note."""
    notiz = get_object_or_404(Notiz, pk=pk, erstellt_von=request.user)
    
    # Convert markdown to HTML
    html_content = markdown.markdown(notiz.inhalt, extensions=['markdown.extensions.fenced_code'])
    
    context = {
        'notiz': notiz,
        'html_content': html_content,
    }
    return render(request, 'notizen/detail.html', context)


@login_required
def notiz_create(request):
    """Create a new note."""
    if request.method == 'POST':
        form = NotizForm(request.POST)
        if form.is_valid():
            notiz = form.save(commit=False)
            notiz.erstellt_von = request.user
            notiz.save()
            messages.success(request, f'Notiz "{notiz.name}" wurde erfolgreich erstellt.')
            return redirect('notizen:detail', pk=notiz.pk)
    else:
        form = NotizForm()
    
    context = {
        'form': form,
        'title': 'Neue Notiz erstellen',
    }
    return render(request, 'notizen/form.html', context)


@login_required
def notiz_edit(request, pk):
    """Edit an existing note."""
    notiz = get_object_or_404(Notiz, pk=pk, erstellt_von=request.user)
    
    if request.method == 'POST':
        form = NotizForm(request.POST, instance=notiz)
        if form.is_valid():
            form.save()
            messages.success(request, f'Notiz "{notiz.name}" wurde erfolgreich aktualisiert.')
            return redirect('notizen:detail', pk=notiz.pk)
    else:
        form = NotizForm(instance=notiz)
    
    context = {
        'form': form,
        'notiz': notiz,
        'title': f'Notiz "{notiz.name}" bearbeiten',
    }
    return render(request, 'notizen/form.html', context)


@login_required
def notiz_delete(request, pk):
    """Delete a note."""
    notiz = get_object_or_404(Notiz, pk=pk, erstellt_von=request.user)
    
    if request.method == 'POST':
        name = notiz.name
        notiz.delete()
        messages.success(request, f'Notiz "{name}" wurde erfolgreich gelöscht.')
        return redirect('notizen:list')
    
    context = {
        'notiz': notiz,
    }
    return render(request, 'notizen/confirm_delete.html', context)


@login_required
def attach_notiz(request, content_type_id, object_id):
    """Attach a new note to an object."""
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        content_object = content_type.get_object_for_this_type(id=object_id)
    except (ContentType.DoesNotExist, content_type.model_class().DoesNotExist):
        raise Http404("Objekt nicht gefunden")
    
    if request.method == 'POST':
        form = NotizAttachForm(request.POST, content_object=content_object)
        if form.is_valid():
            notiz = form.save(commit=False)
            notiz.erstellt_von = request.user
            notiz.save()
            messages.success(request, f'Notiz "{notiz.name}" wurde erfolgreich an {content_object} angehängt.')
            
            # Redirect back to the object's detail page
            if hasattr(content_object, 'get_absolute_url'):
                return redirect(content_object.get_absolute_url())
            else:
                return redirect('notizen:detail', pk=notiz.pk)
    else:
        form = NotizAttachForm(content_object=content_object)
    
    context = {
        'form': form,
        'content_object': content_object,
        'title': f'Notiz an {content_object} anhängen',
    }
    return render(request, 'notizen/attach_form.html', context)


@login_required
def object_notizen(request, content_type_id, object_id):
    """Display all notes attached to an object."""
    try:
        content_type = ContentType.objects.get(id=content_type_id)
        content_object = content_type.get_object_for_this_type(id=object_id)
    except (ContentType.DoesNotExist, content_type.model_class().DoesNotExist):
        raise Http404("Objekt nicht gefunden")
    
    notizen = Notiz.objects.filter(
        content_type=content_type,
        object_id=object_id
    )
    
    # Convert markdown to HTML for each note
    notizen_with_html = []
    for notiz in notizen:
        html_content = markdown.markdown(notiz.inhalt, extensions=['markdown.extensions.fenced_code'])
        notizen_with_html.append({
            'notiz': notiz,
            'html_content': html_content
        })
    
    context = {
        'content_object': content_object,
        'notizen_with_html': notizen_with_html,
    }
    return render(request, 'notizen/object_notizen.html', context)


@login_required
def attach_page_notiz(request, page_identifier):
    """Attach a note to a specific page/overview."""
    from .models import Page
    
    # Get or create the page object
    page, created = Page.objects.get_or_create(
        identifier=page_identifier,
        defaults={
            'name': page_identifier.replace('_', ' ').title(),
            'description': f'Übersichtsseite für {page_identifier}'
        }
    )
    
    if request.method == 'POST':
        form = NotizAttachForm(request.POST)
        if form.is_valid():
            notiz = form.save(commit=False)
            notiz.erstellt_von = request.user
            notiz.content_object = page
            notiz.save()
            
            messages.success(request, f'Notiz "{notiz.name}" wurde erfolgreich zur Seite "{page.name}" hinzugefügt.')
            
            # Redirect back to the page where the note was added
            redirect_urls = {
                'patient_overview': 'bird_all',
                'aviary_overview': 'aviary_all',
                'contact_overview': 'contact_all',
                'costs_overview': 'costs_all',
            }
            
            redirect_url = redirect_urls.get(page_identifier, 'notizen:list')
            return redirect(redirect_url)
    else:
        form = NotizAttachForm()
    
    context = {
        'form': form,
        'page': page,
        'page_identifier': page_identifier,
    }
    return render(request, 'notizen/attach_page.html', context)
