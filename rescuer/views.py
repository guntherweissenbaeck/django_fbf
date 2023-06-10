from django.shortcuts import render
from .models import Rescuer


def rescuer_all(request):
    rescuer = Rescuer.objects.all()
    context = {"rescuer": rescuer}
    return render(request, "rescuer/rescuer_all.html", context)


def rescuer_single(request, id):
    rescuer = Rescuer.objects.get(id=id)
    context = {"rescuer": rescuer}
    return render(request, "rescuer/rescuer_single.html", context)
