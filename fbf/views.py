from django.shortcuts import render, HttpResponse


def bird_create(request):
    return HttpResponse("Create a bird")


def bird_all(request):
    return HttpResponse("Show all Birds")


def bird_single(request, id):
    return HttpResponse(f"Show bird with ID {id}")
