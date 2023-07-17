from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Q


from .forms import RescuerForm
from .models import Rescuer
from bird.models import FallenBird


@login_required(login_url="account_login")
def rescuer_all(request):
    rescuers = Rescuer.objects.all()
    context = {"rescuers": rescuers}
    return render(request, "rescuer/rescuer_all.html", context)


@login_required(login_url="account_login")
def rescuer_single(request, id):
    rescuer = Rescuer.objects.get(id=id)
    birds = FallenBird.objects.filter(rescuer=id).filter(Q(status="1") | Q(status="2"))
    context = {"rescuer": rescuer, "birds": birds}
    return render(request, "rescuer/rescuer_single.html", context)


@login_required(login_url="account_login")
def rescuer_create(request):
    form = RescuerForm()
    if request.method == "POST":
        form = RescuerForm(request.POST or None)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = request.user
            fs.save()

            # set customer id in session cookie
            # (uuid has to be cast to a string)
            rescuer_id = str(fs.pk)
            request.session["rescuer_id"] = rescuer_id

            return redirect("bird_create")
    context = {"form": form}
    return render(request, "rescuer/rescuer_create.html", context)


@login_required(login_url="account_login")
def rescuer_delete(request, id):
    rescuer = Rescuer.objects.get(id=id)
    if request.method == "POST":
        rescuer.delete()
        return redirect("rescuer_all")
    context = {"rescuer": rescuer}
    return render(request, "rescuer/rescuer_delete.html", context)


@login_required(login_url="account_login")
def rescuer_edit(request, id):
    rescuer = Rescuer.objects.get(id=id)
    form = RescuerForm(request.POST or None, instance=rescuer)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect("rescuer_all")
    context = {"form": form}
    return render(request, "rescuer/rescuer_edit.html", context)
