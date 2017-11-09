import datetime
import json
import multiprocessing as mp

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from hub_migrate.interface.implements.common_func import SqoopCommand
from hub_migrate.models import *


@csrf_exempt
def test(request):
    """
    测试是否能够连接as400
    :return: {"success": 1}或者后台错误代码
    """
    req_json = json.loads(request.body.decode("utf-8"))
    sqoop_command = SqoopCommand(req_json, sqoop_tool="list-tables")
    responce_dict = sqoop_command.conn_as400(test=True)
    return JsonResponse(responce_dict)


@csrf_exempt
def submit(request):
    """
    提交连接参数获取对应as400数据库中的表
    :param request Json_String
    :return: Json对象,当正确返回时 [{"stdout": [table_list]}]
                     当执行错误时 [{"stdout": "后台错误代码"]}]
    """
    req_json = json.loads(request.body.decode("utf-8"))
    sqoop_command = SqoopCommand(req_json, sqoop_tool="list-tables")
    # sqoop_str_seq = sqoop_command.get_sqoop_str_seq()
    responce_dict = sqoop_command.conn_as400(test=False)
    return JsonResponse(responce_dict)


@csrf_exempt
def create(request):
    """
    创建并执行sqoop import 任务Job
    :return: Json Object connect_dict
    """
    # 解析json字符串
    req_json = json.loads(request.body.decode("utf-8"))
    
    sc = SqoopCommand(req_json, sqoop_tool="import")
    print("导入的表为:{}".format(sc.conn["table"]))
    
    # 将连接参数存储到数据库
    sqoop_sentence = SqoopSentence(sqoop_tool=sc.sqoop_tool, driver=sc.conn["driver"], host=sc.conn["host"],
                                   database=sc.conn["database"], username=sc.conn["username"],
                                   password=sc.conn["password"], table=sc.conn["table"],
                                   hive_database=sc.conn["hive-database"],
                                   fields_terminated_by=sc.conn["fields-terminated-by"],
                                   hive_overwrite=sc.conn["hive-overwrite"],
                                   num_mappers=sc.conn["num-mappers"],
                                   remarks=sc.conn["remarks"])
    sqoop_sentence.save()
    
    # 将Job信息存储到数据库
    job_info = req_json["job"]
    job_info["starttime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    job = Job(name=job_info["name"], status=job_info["status"], type=job_info["type"],
              start_time=job_info["starttime"], finished_table="", sqoopsentence=sqoop_sentence)
    job.save()
    print("job saved")
    
    # 在后台启动导入hive子进程
    p = mp.Process(target=sc.create_job, args=(job,))
    p.start()
    
    # 不等待子进程执行完,返回JsonResponse
    return JsonResponse({"success": 1})
