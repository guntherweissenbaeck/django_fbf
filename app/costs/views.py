from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Costs
from .forms import CostsForm

@login_required(login_url="account_login")
def costs_all(request):
    costs = Costs.objects.all()
    context = {"costs": costs}
    return render(request, "costs/costs_all.html", context)


@login_required(login_url="account_login")
def costs_edit(request, id):
    costs = Costs.objects.get(id=id)
    form = CostsForm(request.POST or None, instance=costs)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("costs_all")

    context = {"costs": costs, "form": form}
    return render(request, "costs/costs_edit.html", context)

@login_required(login_url="account_login")
def costs_delete(request, id):
    costs = Costs.objects.get(id=id)
    form = CostsForm(request.POST or None, instance=costs)
    if request.method == "POST":
        costs.delete()
        return redirect("costs_all")
    context = {"costs": costs}
    return render(request, "costs/costs_delete.html", context)

@login_required(login_url="account_login")
def costs_create(request):
    form = CostsForm()
    if request.method == "POST":
        form = CostsForm(request.POST or None)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = request.user
            fs.save()
    return render(request, "costs/costs_all.html")