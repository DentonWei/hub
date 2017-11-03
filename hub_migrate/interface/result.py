import json
import os, sys
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from pyspark.sql import SparkSession, Row
from hub_migrate.models import Job

os.environ["SPARK_HOME"] = "/home/why/app/spark-2.0.2-bin-hadoop2.6"
os.environ["PYSPARK_PYTHON"] = "python3"


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
    print(request.POST)
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
        spark.sql("use " + dataBaseName)

        # get the table data
        dataFrame = spark.table(tableName)
        dataColumnNameList = dataFrame.columns
        dataDetail = dataFrame.select('*').limit(20).collect()
        dataDetailDicList = [dataTemp.asDict() for dataTemp in dataDetail]

    # return column name, first 20 rows data and table list of the job
    a = {"success": 1, "column": dataColumnNameList, "dataList": dataDetailDicList}

    return JsonResponse(a)
