from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hub_migrate.models import Job


@csrf_exempt
def get_job_status(request):
    """
    获取指定Job当前迁移任务进行状态
    :param request: 请求获取Job的id,即pk
    :return: 返回一个数组, 数组记录当前Job中每个表的迁移状态
    """
    req = request.body.decode("utf-8")
    job = Job.objects.get(pk=int(req))

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
    
    return JsonResponse([job_status], safe=False)
