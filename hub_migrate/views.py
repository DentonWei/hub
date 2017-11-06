import os

from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from lxml import etree

from hub_migrate.models import Job


def index(request):
    jobs = Job.objects.all()
    return render(request, "hub_migrate/index.html", {"jobs": jobs})


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
    job_id = int(request.GET.get("id"))
    # 获取已经迁移完的和正在进行数据迁移的table
    job = Job.objects.get(pk=job_id)
    finished_tables = job.finished_table.split(",")
    migrating_table = [job.migrating_table]
    # 获取总共的迁移列表
    sqoop = job.sqoopsentence
    table_list = sqoop.table.split(',')[:-1]
    # 判断所有表的迁移状态
    is_finished = []
    for table in table_list:
        if table in finished_tables:
            is_finished.append((table, "finished"))
        elif table in migrating_table:
            is_finished.append((table, "migrating"))
        else:
            is_finished.append((table, "waiting"))
    return render(request, "hub_migrate/progress.html", {"tables": is_finished})


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
