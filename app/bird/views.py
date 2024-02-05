import environ
import names

from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.shortcuts import redirect, render, HttpResponse
from django.core.mail import send_mail, BadHeaderError
from smtplib import SMTPException

from .forms import BirdAddForm, BirdEditForm
from .models import Bird, FallenBird

from sendemail.models import BirdEmail
from sendemail.message import messagebody

env = environ.Env()


@login_required(login_url="account_login")
def bird_create(request):
    form = BirdAddForm(initial={"bird_identifier": names.get_first_name()})
    rescuer_id = None

    # Just show only related rescuers in select field of the form.
    if request.method == "POST":
        form = BirdAddForm(request.POST or None, request.FILES or None)
        rescuer_id = None

        if form.is_valid():
            fs = form.save(commit=False)
            fs.user = request.user
            fs.rescuer_id = rescuer_id
            fs.save()
            request.session["rescuer_id"] = None

            # Send email to all related email addresses
            email_addresses = BirdEmail.objects.filter(bird=fs.bird_id)
            bird = Bird.objects.get(id=fs.bird_id)
            try:
                send_mail(
                    subject="Wildvogel gefunden!",
                    message=messagebody(
                        fs.date_found, bird, fs.place, fs.diagnostic_finding
                    ),
                    from_email=env("DEFAULT_FROM_EMAIL"),
                    recipient_list=[
                        email.email.email_address for email in email_addresses
                    ],
                )
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            except SMTPException as e:
                print("There was an error sending an email: ", e)

            return redirect("bird_all")
    context = {"form": form}
    return render(request, "bird/bird_create.html", context)


@login_required(login_url="account_login")
def bird_help(request):
    birds = Bird.objects.all().order_by("name")
    context = {"birds": birds}
    return render(request, "bird/bird_help.html", context)


@login_required(login_url="account_login")
def bird_help_single(request, id):
    bird = Bird.objects.all().get(id=id)
    context = {"bird": bird}
    return render(request, "bird/bird_help_single.html", context)


@login_required(login_url="account_login")
def bird_all(request):
    birds = (
        FallenBird.objects.filter(Q(status="1") | Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_all.html", context)


@login_required(login_url="account_login")
def bird_inactive(request):
    birds = (
        FallenBird.objects.filter(~Q(status="1") & ~Q(status="2"))
        .annotate(total_costs=Sum("costs__costs"))
        .order_by("date_found")
    )
    context = {"birds": birds}
    return render(request, "bird/bird_inactive.html", context)


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
