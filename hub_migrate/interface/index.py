import json

from django.core.cache import cache
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from hub_migrate.models import *


@csrf_exempt
def get_job(request, num=1):
    """
    获取数据库中的所有job记录,并分页返回
    :param request: 请求对象
    :param num: 请求页面序号
    :return 返回页面显示对象 page, 当前页序号num, 总页数num_pages
    """
    p = cache.get("p")
    print(p.page_range, num)
    page = p.page(num).object_list
    return render(request, "hub_migrate/index.html", {"jobs": page, "num": num,
                                                      "page_range": p.page_range})


@csrf_exempt
def copy(request):
    print(json.loads(request.body.decode("utf-8")))
    job_id = json.loads(request.body.decode("utf-8"))["id"]
    job = serialize("json", [Job.objects.get(id=job_id).sqoopsentence])
    return JsonResponse(job, safe=False)
