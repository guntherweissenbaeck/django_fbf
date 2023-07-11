import names
from django.contrib.auth.decorators import login_required
from django.shortcuts import HttpResponse, redirect, render
from rescuer.models import Rescuer

from .forms import BirdAddForm, BirdEditForm
from .models import FallenBird, Bird


@login_required(login_url="account_login")
def bird_create(request):
    form = BirdAddForm(initial={"bird_identifier": names.get_first_name()})
    # Rescuer for modal usage
    rescuer_id = request.session.get("rescuer_id")
    rescuer = Rescuer.objects.get(id=rescuer_id, user=request.user)

    # Just show only related rescuers in select field of the form.
    if request.method == "POST":
        form = BirdAddForm(request.POST or None, request.FILES or None)
        # circumstances = Circumstance.objects.all()
        rescuer_id = request.session.get("rescuer_id")
        rescuer = Rescuer.objects.get(id=rescuer_id, user=request.user)

        if form.is_valid():
            # if form.cleaned_data["find_circumstances_new"]:
            #     circumstance = form.cleaned_data["find_circumstances_new"]
            #     if Circumstance.objects.filter(description=circumstance).exists():
            #         print("is in circumstances")

            fs = form.save(commit=False)
            fs.user = request.user
            fs.rescuer_id = rescuer_id
            fs.save()
            request.session["rescuer_id"] = None
            return redirect("bird_all")
    context = {"form": form, "rescuer": rescuer}
    return render(request, "bird/bird_create.html", context)


@login_required(login_url="account_login")
def bird_help(request):
    birds = Bird.objects.all()
    context = {"birds": birds}
    return render(request, "bird/bird_help.html", context)


@login_required(login_url="account_login")
def bird_all(request):
    birds = FallenBird.objects.all()
    # Sum all costs per bird from json
    for bird in birds:
        costs_per_bird = float()
        for item in bird.costs:
            costs_per_bird += float(item["cost_entry"])
            if costs_per_bird == 0.0:
                costs_per_bird = ""
        bird.costs = costs_per_bird

    rescuer_modal = Rescuer.objects.all()
    context = {"birds": birds, "rescuer_modal": rescuer_modal}
    # Post came from the modal form.
    if request.method == "POST":
        rescuer_id = request._post["rescuer_id"]
        if rescuer_id != "new_rescuer":
            request.session["rescuer_id"] = rescuer_id
            return redirect("bird_create")
        else:
            return redirect("rescuer_create")
    return render(request, "bird/bird_all.html", context)


@login_required(login_url="account_login")
def bird_recover_all(request):
    return HttpResponse("Show all recovered Birds")


@login_required(login_url="account_login")
def bird_single(request, id):
    bird = FallenBird.objects.get(id=id)
    form = BirdEditForm(request.POST or None, request.FILES or None, instance=bird)
    if request.method == "POST":
        if form.is_valid():
            fs = form.save(commit=False)
            if fs.status.description != "In Auswilderung":
                fs.aviary = None
            fs.save()
            return redirect("bird_all")
    context = {"form": form, "bird": bird}
    return render(request, "bird/bird_single.html", context)


@login_required(login_url="account_login")
def bird_delete(request, id):
    bird = FallenBird.objects.get(id=id)
    if request.method == "POST":
        bird.delete()
        return redirect("bird_all")
    context = {"bird": bird}
    return render(request, "bird/bird_delete.html", context)


@login_required(login_url="account_login")
def bird_recover(request, id):
    return HttpResponse(f"Show recover with ID {id}")
