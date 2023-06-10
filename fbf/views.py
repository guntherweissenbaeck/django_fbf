from django.shortcuts import render, HttpResponse, redirect
from .models import FallenBird
from .forms import BirdForm


def bird_create(request):
    return HttpResponse("Create a bird")


def bird_all(request):
    birds = FallenBird.objects.all()
    context = {"birds": birds}
    return render(request, "fbf/bird_all.html", context)


def bird_recover_all(request):
    return HttpResponse("Show all recovered Birds")


def bird_single(request, id):
    bird = FallenBird.objects.get(id=id)
    form = BirdForm(request.POST or None, request.FILES or None, instance=bird)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("bird_all")
    context = {"form": form, "bird": bird}
    return render(request, "fbf/bird_single.html", context)


def bird_delete(request, id):
    bird = FallenBird.objects.get(id=id)
    if request.method == "POST":
        bird.delete()
        return redirect("bird_all")
    context = {"bird": bird}
    return render(request, "fbf/bird_delete.html", context)


def bird_recover(request, id):
    return HttpResponse(f"Show recover with ID {id}")
