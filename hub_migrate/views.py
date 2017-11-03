from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from hub_migrate.interface.common import get_sqoop
from hub_migrate.models import Job, SqoopSentence


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

    tableList = []

    # if request.GET.get("id") is not None:
    #     id = int(request.GET.get("id"))
    #     job = Job.objects.get(id = id)
    #     tableStr = job.sqoopsentence["table"]
    #     tableList = tableStr.split(',')

    id = 40
    job = Job.objects.get(pk=id)
    tableStr = job.sqoopsentence.table
    tableList = tableStr.split(',')

    return render(request, "hub_migrate/result.html", {"tableList": tableList, "id": id})
