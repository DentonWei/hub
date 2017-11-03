import json

from django.http import JsonResponse
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt

from hub_migrate.models import *


@csrf_exempt
def get_job(request):
    # 获取数据库中 status 字段不为4 的记录
    job = serialize("json", Job.objects.exclude(status=4))
    return JsonResponse(job, safe=False)


@csrf_exempt
def copy(request):
    print(json.loads(request.body.decode("utf-8")))
    job_id = json.loads(request.body.decode("utf-8"))["id"]
    job = serialize("json", [Job.objects.get(id=job_id).sqoopsentence])
    return JsonResponse(job, safe=False)
