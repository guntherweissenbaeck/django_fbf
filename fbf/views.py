from django.shortcuts import render, HttpResponse
from .models import FallenBird


def bird_create(request):
    return HttpResponse("Create a bird")


def bird_all(request):
    birds = FallenBird.objects.all()
    context = {'birds': birds}
    return render(request, 'fbf/birds_all.html', context)


def bird_recover_all(request):
    return HttpResponse("Show all recovered Birds")


def bird_single(request, id):
    return HttpResponse(f"Show bird with ID {id}")


def bird_delete(request, id):
    return HttpResponse(f"Show delete with ID {id}")


def bird_recover(request, id):
    return HttpResponse(f"Show recover with ID {id}")
