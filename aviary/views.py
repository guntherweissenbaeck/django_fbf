from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import Aviary
from .forms import AviaryEditForm


@login_required(login_url="account_login")
def aviary_all(request):
    aviaries = Aviary.objects.all()
    context = {"aviaries": aviaries}
    return render(request, "aviary/aviary_all.html", context)


@login_required(login_url="account_login")
def aviary_single(request, id):
    aviary = Aviary.objects.get(id=id)
    form = AviaryEditForm(request.POST or None, instance=aviary)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("aviary_all")

    context = {"aviary": aviary, "form": form}
    return render(request, "aviary/aviary_single.html", context)
