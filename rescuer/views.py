from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .forms import RescuerForm
from .models import Rescuer


@login_required(login_url="account_login")
def rescuer_all(request):
    rescuer = Rescuer.objects.all()
    context = {"rescuer": rescuer}
    return render(request, "rescuer/rescuer_all.html", context)


@login_required(login_url="account_login")
def rescuer_single(request, id):
    rescuer = Rescuer.objects.get(id=id)
    context = {"rescuer": rescuer}
    return render(request, "rescuer/rescuer_single.html", context)


@login_required(login_url="account_login")
def rescuer_create(request):
    form = RescuerForm()
    if request.method == 'POST':
        form = RescuerForm(request.POST or None)
        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = request.user
            fs.save()

            # set customer id in session cookie
            # (uuid has to be cast to a string)
            rescuer_id = str(fs.pk)
            request.session['rescuer_id'] = rescuer_id

            return redirect('bird_create')
    context = {
        'form': form
    }
    return render(request, 'rescuer/rescuer_create.html', context)
