import json

from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.serializers import serialize
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
    jobs = Job.objects.all().order_by("start_time")
    p = Paginator(jobs, 10)
    page = serialize("json", p.page(num).object_list)
    # return JsonResponse(page, safe=False)
    return JsonResponse({"page": page, "number": num,
                         "num_pages": p.num_pages})


@csrf_exempt
def copy(request):
    """
    获取指定Job的conn参数,并跳转到新建Job页面
    :return:
    """
    print(json.loads(request.body.decode("utf-8")))
    job_id = json.loads(request.body.decode("utf-8"))["id"]
    job = serialize("json", [Job.objects.get(id=job_id).sqoopsentence])
    return JsonResponse(job, safe=False)
