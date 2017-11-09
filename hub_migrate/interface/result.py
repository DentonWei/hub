import json
import os

from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from lxml import etree
from pyspark.sql import SparkSession

from hub_migrate.models import Job

DATADETAIL = None
DATACOLUMNS = None
PAGETEMP = None
PAGE = None

# 获取hive默认路径
HIVE_HOME = os.getenv("HIVE_HOME")


@csrf_exempt
def get_table_info(request):
    # initialize parameter
    global DATADETAIL, PAGETEMP, PAGE, DATACOLUMNS

    # print(request.POST)
    json_temp = json.loads(request.body.decode("utf-8"))
    job_id = json_temp["job_id"]
    table_name = json_temp["tableName"]

    # 获取请求Job对象
    job = Job.objects.get(pk=job_id)

    if table_name:
        # get hive database name
        database_name = job.sqoopsentence.hive_database

        # set spark configuration
        spark = SparkSession.builder \
            .appName("getHiveData") \
            .master("local") \
            .config("spark.some.cofig.option", "some-value") \
            .enableHiveSupport() \
            .getOrCreate()

        # set hive database
        spark.sql("use " + database_name)

        # get the table data
        data_frame = spark.table(table_name)
        # cache.set("dataframe", data_frame)
        
        DATACOLUMNS = data_frame.columns
        data_column_name_list = DATACOLUMNS
        data_detail = data_frame.select('*').collect()

        # initialize global parameter
        DATADETAIL = [dataTemp.asDict() for dataTemp in data_detail]
        p = Paginator(DATADETAIL, 20)
        cache.set("result_page", p)

        # return data
        PAGE = 1
        data_detail_dic_list = p.page(PAGE).object_list

    # return column name, first 20 rows data and table list of the job
    a = {"success": 1, "column": data_column_name_list, "dataList": data_detail_dic_list}

    return JsonResponse(a)


@csrf_exempt
def get_nextPage_info(request):
    global DATADETAIL, PAGETEMP, PAGE

    if PAGETEMP.page(PAGE).has_next() == True:
        PAGE += 1
    else:
        PAGE = PAGETEMP.num_pages

    dataDetailDicList = PAGETEMP.page(PAGE).object_list
    dataColumnNameList = DATACOLUMNS

    a = {"column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)


@csrf_exempt
def get_previousPage_info(request):
    global DATADETAIL, PAGETEMP, PAGE

    if PAGETEMP.page(PAGE).has_previous() == True:
        PAGE -= 1
    else:
        PAGE = 1

    dataDetailDicList = PAGETEMP.page(PAGE).object_list
    dataColumnNameList = DATACOLUMNS

    a = {"column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)