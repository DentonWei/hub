import os

from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader
from lxml import etree

from hub_migrate.models import Job

# 获取hive默认路径
HIVE_HOME = os.getenv("HIVE_HOME")


def index(request, num=1):
    """
    获取数据库中的所有job记录,并分页返回
    :param request: 请求对象
    :param num: 请求页面序号
    :return 返回页面显示对象 page, 当前页序号num, 总页数num_pages
    """
    jobs = Job.objects.all().order_by("-start_time")
    p = Paginator(jobs, 10)
    cache.set("p", p)
    page = p.page(num).object_list
    return render(request, "hub_migrate/index.html", {"jobs": page, "num": num,
                                                      "page_range": p.page_range})


def new(request, job_id=0):
    if job_id != 0:
        sqoop = Job.objects.get(pk=job_id).sqoopsentence
        return render(request, "hub_migrate/copy.html", {"sqoop": sqoop})
    else:
        template = loader.get_template("hub_migrate/new.html")
        return HttpResponse(template.render())


def progress(request):
    job = Job.objects.get(pk=int(request.GET.get("id")))

    finished_tables = job.finished_table.split(",")
    migrating_table = [job.migrating_table]

    # 获取Job迁移任务中,所有需要进行迁移的table
    sqoop = job.sqoopsentence
    table_list = sqoop.table.split(',')

    # 判断所有表的迁移状态
    job_status = []
    for table in table_list:
        if table in finished_tables:
            job_status.append((table, "finished"))
        elif table in migrating_table:
            job_status.append((table, "migrating"))
        else:
            job_status.append((table, "waiting"))

    return render(request, "hub_migrate/progress.html", {"job_status": job_status})


def result(request):
    job = Job.objects.get(pk=int(request.GET.get("id")))
    tables = job.sqoopsentence.table
    table_list = tables.split(',')
    job_id = int(request.GET.get("id"))

    database = job.sqoopsentence.hive_database
    # 获取hive配置文件路径
    hive_conf = os.path.join(HIVE_HOME, "conf/hive-site.xml")
    # 生成hive配置文件的解析器,并解析文件
    parser = etree.XMLParser()
    xml = etree.parse(hive_conf, parser)
    parse_str = "/configuration/property[name='hive.metastore.warehouse.dir']/value"
    hive_database_dir = xml.xpath(parse_str)[0].text + "/" + database + ".db"

    return render(request, "hub_migrate/result.html", {"tables": table_list, "job_id": job_id,
                                                       "hive_path": hive_database_dir})
