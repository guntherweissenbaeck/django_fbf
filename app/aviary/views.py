from bird.models import FallenBird
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import AviaryEditForm
from .models import Aviary


@login_required(login_url="account_login")
def aviary_all(request):
    aviaries = Aviary.objects.all()
    context = {"aviaries": aviaries}
    return render(request, "aviary/aviary_all.html", context)


@login_required(login_url="account_login")
def aviary_create(request):
    """Create a new aviary."""
    form = AviaryEditForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            aviary = form.save(commit=False)
            if request.user.is_authenticated:
                aviary.created_by = request.user
            aviary.save()
            
            # Handle different save options
            if 'save_and_add' in request.POST:
                return redirect("aviary_create")  # Redirect to create another
            elif 'save_and_continue' in request.POST:
                return redirect("aviary_single", id=aviary.id)  # Redirect to edit the created aviary
            else:
                return redirect("aviary_all")  # Default: go to list

    context = {"form": form, "is_create": True}
    return render(request, "aviary/aviary_form.html", context)


@login_required(login_url="account_login")
def aviary_single(request, id):
    aviary = Aviary.objects.get(id=id)
    birds = FallenBird.objects.filter(aviary_id=id).order_by("created")
    form = AviaryEditForm(request.POST or None, instance=aviary)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("aviary_all")

    context = {"aviary": aviary, "birds": birds, "form": form}
    return render(request, "aviary/aviary_single.html", context)
