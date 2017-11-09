import os

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from lxml import etree

from hub_migrate.models import Job


def index(request):
    template = loader.get_template("hub_migrate/index.html")
    return HttpResponse(template.render())


def new(request):
    if request.GET.get("id") is not None:
        job_id = int(request.GET.get("id"))
        print(id)
        sqoop = Job.objects.get(pk=job_id).sqoopsentence
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
