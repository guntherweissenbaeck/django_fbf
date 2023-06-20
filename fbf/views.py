from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render

from .forms import BirdAddForm, BirdEditForm
from .models import FallenBird
from rescuer.models import Rescuer


@login_required(login_url="account_login")
def bird_create(request):
    # Rescuer for modal usage
    form = BirdAddForm()
    rescuer_id = request.session.get("rescuer_id")
    rescuer = Rescuer.objects.get(id=rescuer_id, user=request.user)

    # just show only related rescuers in select field of the form
    if request.method == "POST":
        form = BirdAddForm(request.POST or None, request.FILES or None)
        rescuer_id = request.session.get('rescuer_id')
        rescuer = Rescuer.objects.get(id=rescuer_id, user=request.user)

        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = request.user
            fs.rescuer_id = rescuer_id
            fs.save()
            request.session["rescuer_id"] = None
            return redirect("bird_all")
    context = {"form": form, "rescuer": rescuer}
    return render(request, "fbf/bird_create.html", context)


@login_required(login_url="account_login")
def bird_all(request):
    birds = FallenBird.objects.all()
    rescuer_modal = Rescuer.objects.all()
    context = {"birds": birds, "rescuer_modal": rescuer_modal}
    # Post came from the modal form
    if request.method == "POST":
        rescuer_id = request._post["rescuer_id"]
        if rescuer_id != "new_rescuer":
            request.session["rescuer_id"] = rescuer_id
            return redirect("bird_create")
        else:
            return redirect("rescuer_create")
    return render(request, "fbf/bird_all.html", context)


@login_required(login_url="account_login")
def bird_recover_all(request):
    return HttpResponse("Show all recovered Birds")


@login_required(login_url="account_login")
def bird_single(request, id):
    bird = FallenBird.objects.get(id=id)
    form = BirdEditForm(
        request.POST or None,
        request.FILES or None,
        instance=bird)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("bird_all")
    context = {"form": form, "bird": bird}
    return render(request, "fbf/bird_single.html", context)


@login_required(login_url="account_login")
def bird_delete(request, id):
    bird = FallenBird.objects.get(id=id)
    if request.method == "POST":
        bird.delete()
        return redirect("bird_all")
    context = {"bird": bird}
    return render(request, "fbf/bird_delete.html", context)


@login_required(login_url="account_login")
def bird_recover(request, id):
    return HttpResponse(f"Show recover with ID {id}")
