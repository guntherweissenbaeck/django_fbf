from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Aviary


@login_required(login_url="account_login")
def aviary_all(request):
    aviaries = Aviary.objects.all()
    context = {"aviaries": aviaries}
    return render(request, "aviary/aviary_all.html", context)
