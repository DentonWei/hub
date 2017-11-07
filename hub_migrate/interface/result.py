import json
import os

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyspark.sql import SparkSession, Row
from django.core.paginator import Paginator
from hub_migrate.models import Job

DATADETAIL = None
DATACOLUMNS = None
PAGETEMP = None
PAGE = None

@csrf_exempt
def get_job_info(request):

    # initialize parameter
    id = json.loads(request.body.decode("utf-8"))["id"]

    # 获取请求Job对象
    job = Job.objects.get(id=id)
    tables = job.sqoopsentence.table
    # split tables on the base of ','
    tableList = tables.split(',')
    
    # return table list of the job
    a = {"success": 1, "tableList": tableList}

    return JsonResponse(a)


@csrf_exempt
def get_table_info(request):
    # initialize parameter
    global DATADETAIL, PAGETEMP, PAGE, DATACOLUMNS
    
    # print(request.POST)
    jsonTemp = json.loads(request.body.decode("utf-8"))
    id = jsonTemp["id"]
    tableName = jsonTemp["tableName"]
    dataColumnNameList = []
    dataDetailDicList = []

    # 获取请求Job对象
    job = Job.objects.get(pk=id)

    if tableName:
        # get hive database name
        dataBaseName = job.sqoopsentence.hive_database

        # set spark configuration
        spark = SparkSession.builder \
            .appName("getHiveData") \
            .master("local") \
            .config("spark.some.cofig.option", "some-value") \
            .enableHiveSupport() \
            .getOrCreate()

        # set hive database
        spark.sql("use " + "default")

        # get the table data
        dataFrame = spark.table(tableName)
        DATACOLUMNS = dataFrame.columns
        dataColumnNameList = DATACOLUMNS
        dataDetail = dataFrame.select('*').collect()

        # initialize global parameter
        DATADETAIL = [dataTemp.asDict() for dataTemp in dataDetail]
        PAGETEMP = Paginator(DATADETAIL, 20)

        # return data
        PAGE = 1
        dataDetailDicList = PAGETEMP.page(PAGE).object_list

    # return column name, first 20 rows data and table list of the job
    a = {"success": 1, "column": dataColumnNameList, "dataList": dataDetailDicList}

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