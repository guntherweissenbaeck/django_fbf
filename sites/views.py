from django.shortcuts import redirect, render


def index(request):
    return render(request, "sites/index.html")


def privacy(request):
    return render(request, "sites/privacy.html")


def impress(request):
    return render(request, "sites/impress.html")
