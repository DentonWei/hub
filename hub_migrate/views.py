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

    tableList = []

    # if request.GET.get("id") is not None:
    #     id = int(request.GET.get("id"))
    #     job = Job.objects.get(id = id)
    #     tableStr = job.sqoopsentence["table"]
    #     tableList = tableStr.split(',')

    id = 51
    job = Job.objects.get(pk=id)
    tableStr = job.sqoopsentence.table
    tableList = tableStr.split(',')
    database = job.sqoopsentence.hive_database
    # 获取hive配置文件路径
    HIVE_HOME = os.getenv("HIVE_HOME")
    hive_conf = os.path.join(HIVE_HOME, "conf/hive-site.xml")
    # 生成hive配置文件的解析器,并解析文件
    parser = etree.XMLParser()
    xml = etree.parse(hive_conf, parser)
    parse_str = "/configuration/property[name='hive.metastore.warehouse.dir']/value"
    hive_database_dir = xml.xpath(parse_str)[0].text + "/" + database + ".db"
    # print(hive_database_dir)

    return render(request, "hub_migrate/result.html",
                  {"tableList": tableList, "id": id, "hive_path": hive_database_dir})
