import datetime
import json
import multiprocessing as mp

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hub_migrate.interface.implements import new_func
from hub_migrate.models import *


@csrf_exempt
def test(request):
    if request.method == "POST":
        # 解析json字符串
        req_json = json.loads(request.body.decode("utf-8"))
        sqoop_str_list = new_func.gen_sqoop_str_list(req_json, sqoop_tool="list-tables")
        responce_dict = new_func.analyse_dict(sqoop_str_list, test=True)
        return JsonResponse(responce_dict)
    else:
        aaa = {"kkk": 200}
        return JsonResponse(aaa)


@csrf_exempt
def create(request):
    if request.method == "POST":
        # 解析json字符串
        req_json = json.loads(request.body.decode("utf-8"))
        # 获取并完善connect_dict
        connect_dict = req_json["conn"]
        connect_dict["driver"] = "com.ibm.as400.access.AS400JDBCDriver"
        connect_dict["hive-import"] = True
        # connect_dict["connect"] = "jdbc:as400://" + connect_dict["host"] + "/" + connect_dict["database"]
        # 处理存入数据库中的 table字段,原始数据为List,转换为String
        table_str = ""
        for table in connect_dict["table"]:
            table_str += (str(table) + ',')
        connect_dict["table"] = table_str
        sqoop_tool = "import"
        # 将连接参数存储到数据库
        sqoop_sentence = SqoopSentence(sqoop_tool=sqoop_tool, driver=connect_dict["driver"], host=connect_dict["host"],
                                       database=connect_dict["database"], username=connect_dict["username"],
                                       password=connect_dict["password"], table=connect_dict["table"],
                                       hive_database=connect_dict["hive-database"],
                                       fields_terminated_by=connect_dict["fields-terminated-by"],
                                       hive_overwrite=connect_dict["hive-overwrite"],
                                       num_mappers=connect_dict["num-mappers"],
                                       remarks=connect_dict["remarks"])
        sqoop_sentence.save()
        # 将Job信息存储到数据库
        job_info = req_json["job"]
        job_info["starttime"] = datetime.datetime.now()
        job = Job(name=job_info["name"], status=job_info["status"], type=job_info["type"],
                  start_time=job_info["starttime"], finished_table="", sqoopsentence=sqoop_sentence)
        job.save()
        # 启动导入hive子进程
        p = mp.Process(target=new_func.create_job, args=(connect_dict, sqoop_tool, job))
        p.start()
        # 不等待子进程执行完,返回JsonResponse
        success = {'success': 1}
        return JsonResponse(success)
    else:
        aaa = {"kkk": 200}
        return JsonResponse(aaa)


def get_sqoop(job_id):
    sqoop = Job.objects.get(pk=job_id).sqoopsentence
    print(sqoop)
    return sqoop
