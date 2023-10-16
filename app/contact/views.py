from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .models import Contact

@login_required(login_url="account_login")
def contact_all(request):
    contacts = Contact.objects.all()
    context = {"contacts": contacts}
    return render(request, "contact/contact_all.html", context)