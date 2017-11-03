from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from hub_migrate.interface.common import get_sqoop


def index(request):
    print(request.GET)
    template = loader.get_template("hub_migrate/index.html")
    return HttpResponse(template.render())


def new(request):
    if request.GET.get("id") is not None:
        id = int(request.GET.get("id"))
        print(id)
        sqoop = get_sqoop(id)
        return render(request, "hub_migrate/copy.html", {"sqoop": sqoop})
    else:
        template = loader.get_template("hub_migrate/new.html")
        return HttpResponse(template.render())


def progress(request):
    template = loader.get_template("hub_migrate/progress.html")
    return HttpResponse(template.render())


def result(request):
    template = loader.get_template("hub_migrate/result.html")
    return HttpResponse(template.render())
